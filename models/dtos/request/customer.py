from pydantic import BaseModel, Field

class Customer(BaseModel):
    avg_amount: float = Field(..., description="Cardholder's historical spending average")
    tx_count_24h: int = Field(..., description="Cardholder's transactions in the last 24h")
    known_merchants: list[str] = Field(..., description="Merchants already used by the cardholder")
