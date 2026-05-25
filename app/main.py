import sys

from pathlib import Path
from fastapi import FastAPI

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models.dtos.request.fraud_score import FraudScoreRequest
from models.dtos.response.fraud_score import FraudScoreResponse

@app.get("/")
def main_route():
    return {"Hello": "World"}

@app.get("/ready")
def ready():
    return {"status": 200}

@app.post("/fraud-score")
def fraud_score(request: FraudScoreRequest) -> FraudScoreResponse:
    return FraudScoreResponse(approved=False, fraud_score=0.0)
