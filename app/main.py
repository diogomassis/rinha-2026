import sys
import logging
import time

from services.ann.ann_engine import EXPECTED_INPUT_SIZE

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models.dtos.request.fraud_score import FraudScoreRequest
from models.dtos.response.fraud_score import FraudScoreResponse
from models.normalization.mcc_risk import MccRiskConfig
from models.normalization.normalization import NormalizationConfig
from services.vector.vector_engine import VectorEngine
from services.ann.ann_engine import AnnEngine

_RESOURCES_DIR = Path(__file__).resolve().parents[1] / "resources"
_REFERENCES_PATH = _RESOURCES_DIR / "references.json.gz"

# Colored logging setup (green for normal/info, red for errors)
class ColorFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[36m',
        'INFO': '\033[32m',
        'WARNING': '\033[33m',
        'ERROR': '\033[31m',
        'CRITICAL': '\033[1;31m',
    }
    RESET = '\033[0m'

    def format(self, record):
        message = super().format(record)
        color = self.COLORS.get(record.levelname, '')
        if color:
            return f"{color}{message}{self.RESET}"
        return message

handler = logging.StreamHandler()
handler.setFormatter(ColorFormatter("%(asctime)s %(levelname)s %(message)s"))
root_logger = logging.getLogger()
if not root_logger.handlers:
    root_logger.addHandler(handler)
root_logger.setLevel(logging.INFO)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

mcc_risk_path = str(_RESOURCES_DIR / "mcc_risk.json")
mcc_risk = MccRiskConfig(mcc_risk_path)

normalization_path = str(_RESOURCES_DIR / "normalization.json")
normalization = NormalizationConfig(normalization_path)

knn_engine = VectorEngine(normalization, mcc_risk)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.ann_engine = AnnEngine.load(_REFERENCES_PATH)
        app.state.health = True
        logging.info(f"Loaded ANN engine from {_REFERENCES_PATH}")
        # Warm-up ANN engine to force any lazy loading or disk IO now
        try:
            warmup_vec = [0.0] * EXPECTED_INPUT_SIZE
            t0 = time.perf_counter()
            app.state.ann_engine.predict(warmup_vec)
            t1 = time.perf_counter()
            logging.info(f"ANN warmup completed in {t1 - t0:.3f}s")
        except Exception:
            logging.exception("ANN warmup failed (non-fatal)")
    except Exception as e:
        app.state.health = False
        logging.exception(f"Failed to load ANN engine: {e}")
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/ready")
def ready():
    if not app.state.health:
        raise HTTPException(status_code=500, detail="Service unhealthy")
    return {"status": "healthy"}

@app.post("/fraud-score")
def fraud_score(request: FraudScoreRequest) -> FraudScoreResponse:
    try:
        t0 = time.perf_counter()
        vector = knn_engine.vectorization(request=request)
        t1 = time.perf_counter()
        ann_engine: AnnEngine = app.state.ann_engine
        approved, fraud_score = ann_engine.predict(vector)
        t2 = time.perf_counter()
        return FraudScoreResponse(approved=approved, fraud_score=fraud_score)
    except Exception as e:
        logging.exception(f"Error processing /fraud-score: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
