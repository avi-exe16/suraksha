from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TransactionInput(BaseModel):
    txn_id: str
    user_id: str
    amount: float
    city: str
    lat: float
    lon: float
    device_id: str
    merchant_category: str
    km_from_last_txn: float
    minutes_from_last_txn: float
    impossible_speed: int
    hour: int
    is_weekend: int
    is_night: int
    txn_count_1hr: int
    txn_count_24hr: int
    amount_sum_1hr: float
    amount_sum_24hr: float
    amount_vs_user_avg: float
    is_new_device: int
    device_count_7d: int
    is_new_merchant_category: int


class TransactionResult(BaseModel):
    txn_id: str
    user_id: str
    amount: float
    anomaly_score: float
    risk_level: str
    action: str
    explanation: List[dict]
    timestamp: str


class RiskSummary(BaseModel):
    total_transactions: int
    high_risk: int
    medium_risk: int
    low_risk: int
    fraud_rate: float


class AuditLogEntry(BaseModel):
    user_id: str
    accessor: str
    access_type: str
    timestamp: str
    purpose: str


class ConsentRevocation(BaseModel):
    user_id: str
    accessor: str