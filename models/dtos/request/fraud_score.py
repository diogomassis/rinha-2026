from pydantic import BaseModel, Field

from models.dtos.request.customer import Customer
from models.dtos.request.last_transaction import LastTransaction
from models.dtos.request.merchant import Merchant
from models.dtos.request.terminal import Terminal
from models.dtos.request.transaction import Transaction

class FraudScoreRequest(BaseModel):
    id: str = Field(..., description="Transaction identifier (e.g., tx-1329056812)")
    transaction: Transaction = Field(..., description="Details of the current transaction, including amount, currency, timestamp and payment method")
    customer: Customer = Field(..., description="Customer profile and behavioral attributes used to assess fraud risk")
    merchant: Merchant = Field(..., description="Merchant information such as merchant id, category and location")
    terminal: Terminal = Field(..., description="Terminal or POS device details where the transaction originated")
    last_transaction: LastTransaction | None = Field(None, description="Optional most recent prior transaction for this customer, if available")
