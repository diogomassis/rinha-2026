from pydantic import BaseModel, Field

class Merchant(BaseModel):
    id: str = Field(..., description="Merchant identifier")
    mcc: str = Field(..., description="MCC (Merchant Category Code), a code that identifies the merchant's line of business")
    avg_amount: float = Field(..., description="Merchant's average ticket")
