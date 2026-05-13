import pandas as pd
import numpy as np


def compute_drift_report(df: pd.DataFrame) -> dict:
    reference = df.head(int(len(df) * 0.7)).copy()
    current = df.tail(int(len(df) * 0.3)).copy()

    numeric_features = [
        "amount",
        "km_from_last_txn",
        "amount_vs_user_avg",
        "txn_count_24hr",
        "is_new_device",
        "is_night",
    ]

    drift_results = []
    drift_detected = False

    for feature in numeric_features:
        ref_mean = float(reference[feature].mean())
        cur_mean = float(current[feature].mean())
        ref_std = float(reference[feature].std())
        cur_std = float(current[feature].std())

        if ref_mean == 0:
            pct_change = 0.0
        else:
            pct_change = float(abs((cur_mean - ref_mean) / ref_mean) * 100)

        drifted = bool(pct_change > 20.0)

        if drifted:
            drift_detected = True

        drift_results.append({
            "feature": feature,
            "reference_mean": round(ref_mean, 4),
            "current_mean": round(cur_mean, 4),
            "reference_std": round(ref_std, 4),
            "current_std": round(cur_std, 4),
            "pct_change": round(pct_change, 2),
            "drift_detected": drifted,
        })

    ref_fraud_rate = float(reference["predicted_fraud"].mean() * 100) if "predicted_fraud" in reference.columns else 0.0
cur_fraud_rate = float(current["predicted_fraud"].mean() * 100) if "predicted_fraud" in current.columns else 0.0
    fraud_rate_change = float(abs(cur_fraud_rate - ref_fraud_rate))

    return {
        "drift_detected": bool(drift_detected),
        "reference_period_size": int(len(reference)),
        "current_period_size": int(len(current)),
        "reference_fraud_rate": round(ref_fraud_rate, 4),
        "current_fraud_rate": round(cur_fraud_rate, 4),
        "fraud_rate_change": round(fraud_rate_change, 4),
        "recommendation": "Model retraining recommended." if drift_detected else "Model performance stable.",
        "features": drift_results,
    }