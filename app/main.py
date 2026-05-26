import sys

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
    except Exception as e:
        app.state.health = False
        print(f"Failed to load ANN engine: {e}")
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/ready")
def ready():
    if not app.state.health:
        raise HTTPException(status_code=500, detail="Service unhealthy")
    return {"status": "healthy"}

@app.post("/fraud-score")
def fraud_score(request: FraudScoreRequest) -> FraudScoreResponse:
    vector = knn_engine.vectorization(request=request)
    ann_engine: AnnEngine = app.state.ann_engine
    approved, fraud_score = ann_engine.predict(vector)
    return FraudScoreResponse(approved=approved, fraud_score=fraud_score)
