from models.dtos.request.customer import Customer
from models.dtos.request.fraud_score import FraudScoreRequest
from models.dtos.request.last_transaction import LastTransaction
from models.dtos.request.merchant import Merchant
from models.dtos.request.terminal import Terminal
from models.dtos.request.transaction import Transaction
from models.normalization.mcc_risk import MccRiskConfig
from models.normalization.normalization import NormalizationConfig

class VectorEngine:
    def __init__(self, normalization: NormalizationConfig, mcc_risk: MccRiskConfig):
        self.normalization = normalization
        self.mcc_risk_config = mcc_risk

    def vectorization(self, request: FraudScoreRequest) -> list[float]:
        return [
            self._amount(request.transaction),
            self._installments(request.transaction),
            self._amount_vs_avg(request.transaction, request.customer),
            self._hour_of_day(request.transaction),
            self._day_of_week(request.transaction),
            self._minutes_since_last_tx(request.transaction, request.last_transaction),
            self._km_from_last_tx(request.last_transaction),
            self._km_from_home(request.terminal),
            self._tx_count_24h(request.customer),
            self._is_online(request.terminal),
            self._card_present(request.terminal),
            self._unknown_merchant(request.merchant, request.customer),
            self._mcc_risk(request.merchant),
            self._merchant_avg_amount(request.merchant)
        ]
    
    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, value))
    
    def _amount(self, transaction: Transaction) -> float:
        return self._clamp(transaction.amount / self.normalization.max_amount)
    
    def _installments(self, transaction: Transaction) -> float:
        return self._clamp(transaction.installments / self.normalization.max_installments)
    
    def _amount_vs_avg(self, transaction: Transaction, customer: Customer) -> float:
        return self._clamp((transaction.amount / customer.avg_amount) / self.normalization.amount_vs_avg_ratio)
    
    def _hour_of_day(self, transaction: Transaction) -> float:
        return float(transaction.requested_at.hour) / 23.0
    
    def _day_of_week(self, transaction: Transaction) -> float:
        return float(transaction.requested_at.weekday()) / 6.0
    
    def _minutes_since_last_tx(self, transaction: Transaction, last_transaction: LastTransaction) -> float:
        if not last_transaction:
            return -1.0
        elapsed_minutes = (transaction.requested_at - last_transaction.timestamp).total_seconds() / 60.0
        return self._clamp(elapsed_minutes / self.normalization.max_minutes)

    def _km_from_last_tx(self, last_transaction: LastTransaction) -> float:
        if not last_transaction:
            return -1.0
        return self._clamp(last_transaction.km_from_current / self.normalization.max_km)
    
    def _km_from_home(self, terminal: Terminal) -> float:
        return self._clamp(terminal.km_from_home / self.normalization.max_km)
    
    def _tx_count_24h(self, customer: Customer) -> float:
        return self._clamp(customer.tx_count_24h / self.normalization.max_tx_count_24h)
    
    def _is_online(self, terminal: Terminal) -> float:
        return 1.0 if terminal.is_online else 0.0
    
    def _card_present(self, terminal: Terminal) -> float:
        return 1.0 if terminal.card_present else 0.0
    
    def _unknown_merchant(self, merchant: Merchant, customer: Customer) -> float:
        return 1.0 if merchant.id not in customer.known_merchants else 0.0
    
    def _mcc_risk(self, merchant: Merchant) -> float:
        mcc_risk = self.mcc_risk_config.get(merchant.mcc, 0.5)
        return 0.5 if mcc_risk is None else mcc_risk
    
    def _merchant_avg_amount(self, merchant: Merchant) -> float:
        return self._clamp(merchant.avg_amount / self.normalization.max_merchant_avg_amount)
