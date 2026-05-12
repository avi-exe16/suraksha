import pandas as pd
import json
from datetime import datetime
from config import SCORED_DATA_PATH, USER_PROFILES_PATH

def load_data():
    if os.path.exists(SCORED_DATA_PATH):
        df = pd.read_csv(SCORED_DATA_PATH)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    else:
        df = pd.DataFrame(columns=[
            "txn_id", "user_id", "timestamp", "amount", "city",
            "lat", "lon", "device_id", "merchant_category",
            "km_from_last_txn", "minutes_from_last_txn", "impossible_speed",
            "is_fraud", "hour", "day_of_week", "is_weekend", "is_night",
            "txn_count_1hr", "txn_count_24hr", "amount_sum_1hr",
            "amount_sum_24hr", "amount_vs_user_avg", "is_new_device",
            "device_count_7d", "is_new_merchant_category",
            "anomaly_score_raw", "anomaly_score", "predicted_fraud"
        ])
    return df


def load_users():
    if os.path.exists(USER_PROFILES_PATH):
        return pd.read_csv(USER_PROFILES_PATH)
    return pd.DataFrame(columns=["user_id", "name", "email"])


df_transactions = load_data()
df_users = load_users()
audit_log = []
consent_registry = {}
flagged_transactions = []


def get_transactions(limit: int = 100, risk_level: str = None) -> list:
    df = df_transactions.copy()

    if risk_level == "high":
        df = df[df["anomaly_score"] >= 0.8]
    elif risk_level == "medium":
        df = df[(df["anomaly_score"] >= 0.5) & (df["anomaly_score"] < 0.8)]
    elif risk_level == "low":
        df = df[df["anomaly_score"] < 0.5]

    df = df.sort_values("timestamp", ascending=False).head(limit)
    return df.to_dict(orient="records")


def get_transaction_by_id(txn_id: str) -> dict:
    result = df_transactions[df_transactions["txn_id"] == txn_id]
    if result.empty:
        return None
    return result.iloc[0].to_dict()


def get_user_transactions(user_id: str) -> list:
    result = df_transactions[df_transactions["user_id"] == user_id]
    result = result.sort_values("timestamp", ascending=False)
    return result.to_dict(orient="records")


def get_user_profile(user_id: str) -> dict:
    result = df_users[df_users["user_id"] == user_id]
    if result.empty:
        return None
    return result.iloc[0].to_dict()


def log_audit_entry(user_id: str, accessor: str, access_type: str, purpose: str):
    entry = {
        "user_id": user_id,
        "accessor": accessor,
        "access_type": access_type,
        "purpose": purpose,
        "timestamp": datetime.now().isoformat(),
    }
    audit_log.append(entry)


def get_audit_log(user_id: str) -> list:
    return [entry for entry in audit_log if entry["user_id"] == user_id]


def revoke_consent(user_id: str, accessor: str):
    key = f"{user_id}_{accessor}"
    consent_registry[key] = {
        "user_id": user_id,
        "accessor": accessor,
        "revoked_at": datetime.now().isoformat(),
        "status": "revoked",
    }


def get_consent_status(user_id: str) -> list:
    result = []
    for key, value in consent_registry.items():
        if value["user_id"] == user_id:
            result.append(value)
    return result


def store_flagged_transaction(txn: dict):
    flagged_transactions.append(txn)


def get_flagged_transactions(limit: int = 50) -> list:
    return flagged_transactions[-limit:]


def get_risk_stats() -> dict:
    total = len(df_transactions)
    high = len(df_transactions[df_transactions["anomaly_score"] >= 0.8])
    medium = len(df_transactions[
        (df_transactions["anomaly_score"] >= 0.5) &
        (df_transactions["anomaly_score"] < 0.8)
    ])
    low = total - high - medium

    return {
        "total_transactions": total,
        "high_risk": high,
        "medium_risk": medium,
        "low_risk": low,
        "fraud_rate": round(high / total * 100, 2),
        "amount_saved": round(
            df_transactions[df_transactions["anomaly_score"] >= 0.8]["amount"].sum(), 2
        ),
    }