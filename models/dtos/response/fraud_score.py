from pydantic import BaseModel, Field

class FraudScoreResponse(BaseModel):
    approved: bool = Field(description="Whether the transaction was approved")
    fraud_score: float = Field(description="Fraud risk score between 0 and 1")
    