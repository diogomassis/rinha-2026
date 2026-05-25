from pydantic import BaseModel, Field

class Terminal(BaseModel):
    is_online: bool = Field(..., description="Online transaction (true) or in-person (false)")
    card_present: bool = Field(..., description="Whether the physical card is present at the terminal")
    km_from_home: float = Field(..., description="Distance (km) from the cardholder's address")
    