from datetime import datetime
from pydantic import BaseModel, Field

class LastTransaction(BaseModel):
    timestamp: datetime = Field(..., description="UTC timestamp of the previous transaction")
    km_from_current: float = Field(..., description="Distance (km) between the previous transaction and the current one")
