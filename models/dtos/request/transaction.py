from datetime import datetime
from pydantic import BaseModel, Field

class Transaction(BaseModel):
    amount: float = Field(..., description="Transaction value")
    installments: int = Field(..., description="Number of installments")
    requested_at: datetime = Field(..., description="UTC timestamp of the request")
