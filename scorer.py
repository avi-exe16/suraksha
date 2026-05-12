import joblib
import numpy as np
import pandas as pd
from config import (
    MODEL_PATH,
    SCALER_PATH,
    FEATURE_COLUMNS_PATH,
    SHAP_IMPORTANCE_PATH,
    FRAUD_THRESHOLD_REVIEW,
    FRAUD_THRESHOLD_BLOCK,
)

iso_forest = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
FEATURE_COLUMNS = joblib.load(FEATURE_COLUMNS_PATH)
shap_importance = pd.read_csv(SHAP_IMPORTANCE_PATH)


def score_transaction(txn: dict) -> dict:
    features = pd.DataFrame([txn])[FEATURE_COLUMNS]
    scaled = scaler.transform(features)

    raw_score = iso_forest.decision_function(scaled)[0]
    min_score = -0.5
    max_score = 0.5
    normalized = (raw_score - min_score) / (max_score - min_score)
    anomaly_score = round(float(1 - np.clip(normalized, 0, 1)), 4)

    if anomaly_score >= FRAUD_THRESHOLD_BLOCK:
        action = "blocked"
        risk_level = "high"
    elif anomaly_score >= FRAUD_THRESHOLD_REVIEW:
        action = "step_up_auth"
        risk_level = "medium"
    else:
        action = "approved"
        risk_level = "low"

    top_features = shap_importance.sort_values(
        "shap_importance", ascending=False
    ).head(5)

    explanation_parts = []
    for _, row in top_features.iterrows():
        feature = row["feature"]
        importance = row["shap_importance"]
        value = txn.get(feature, 0)
        explanation_parts.append({
            "feature": feature,
            "value": value,
            "importance": round(float(importance), 4),
        })

    return {
        "anomaly_score": anomaly_score,
        "risk_level": risk_level,
        "action": action,
        "explanation": explanation_parts,
    }


def get_risk_summary(scored_df: pd.DataFrame) -> dict:
    total = len(scored_df)
    high_risk = len(scored_df[scored_df["anomaly_score"] >= FRAUD_THRESHOLD_BLOCK])
    medium_risk = len(scored_df[
        (scored_df["anomaly_score"] >= FRAUD_THRESHOLD_REVIEW) &
        (scored_df["anomaly_score"] < FRAUD_THRESHOLD_BLOCK)
    ])
    low_risk = total - high_risk - medium_risk

    return {
        "total_transactions": total,
        "high_risk": high_risk,
        "medium_risk": medium_risk,
        "low_risk": low_risk,
        "fraud_rate": round(high_risk / total * 100, 2),
    }