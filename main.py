from drift_detector import compute_drift_report
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from datetime import datetime
from typing import Optional

from models import TransactionInput, ConsentRevocation
from scorer import score_transaction, get_risk_summary
from str_report import generate_str_report
from database import (
    get_transactions,
    get_transaction_by_id,
    get_user_transactions,
    get_user_profile,
    log_audit_entry,
    get_audit_log,
    revoke_consent,
    get_consent_status,
    store_flagged_transaction,
    get_flagged_transactions,
    get_risk_stats,
    df_transactions,
)

shadow_mode = {"enabled": False}

app = FastAPI(
    title="SuRaksha Fraud Detection API",
    description="Real-time transaction anomaly detection system for Canara Bank",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "system": "SuRaksha Fraud Detection API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/transaction/score")
def score_new_transaction(txn: TransactionInput):
    txn_dict = txn.model_dump()
    result = score_transaction(txn_dict)

    response = {
        "txn_id": txn.txn_id,
        "user_id": txn.user_id,
        "amount": txn.amount,
        "anomaly_score": result["anomaly_score"],
        "risk_level": result["risk_level"],
        "action": result["action"],
        "explanation": result["explanation"],
        "timestamp": datetime.now().isoformat(),
    }

    if result["risk_level"] in ["medium", "high"]:
        store_flagged_transaction(response)
        log_audit_entry(
            user_id=txn.user_id,
            accessor="fraud_detection_engine",
            access_type="anomaly_scan",
            purpose="Automated fraud detection scan",
        )

    return response


@app.get("/transactions")
def list_transactions(
    limit: int = Query(100, ge=1, le=500),
    risk_level: Optional[str] = Query(None),
):
    transactions = get_transactions(limit=limit, risk_level=risk_level)
    return {
        "count": len(transactions),
        "transactions": transactions,
    }


@app.get("/transactions/flagged")
def list_flagged_transactions(limit: int = Query(50, ge=1, le=200)):
    flagged = get_flagged_transactions(limit=limit)
    return {
        "count": len(flagged),
        "transactions": flagged,
    }


@app.get("/transactions/{txn_id}")
def get_transaction(txn_id: str):
    txn = get_transaction_by_id(txn_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    log_audit_entry(
        user_id=str(txn.get("user_id", "unknown")),
        accessor="bank_officer",
        access_type="transaction_view",
        purpose="Transaction detail review",
    )
    return txn


@app.get("/users/{user_id}")
def get_user(user_id: str):
    profile = get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return profile


@app.get("/users/{user_id}/transactions")
def get_user_transaction_history(user_id: str):
    transactions = get_user_transactions(user_id)
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found for user")
    return {
        "user_id": user_id,
        "count": len(transactions),
        "transactions": transactions,
    }


@app.get("/dashboard/stats")
def get_dashboard_stats():
    stats = get_risk_stats()
    return stats


@app.get("/audit/{user_id}")
def get_user_audit_log(user_id: str):
    entries = get_audit_log(user_id)
    return {
        "user_id": user_id,
        "count": len(entries),
        "entries": entries,
    }


@app.post("/consent/revoke")
def revoke_user_consent(revocation: ConsentRevocation):
    revoke_consent(
        user_id=revocation.user_id,
        accessor=revocation.accessor,
    )
    log_audit_entry(
        user_id=revocation.user_id,
        accessor=revocation.accessor,
        access_type="consent_revocation",
        purpose="User revoked data access",
    )
    return {
        "status": "success",
        "user_id": revocation.user_id,
        "accessor": revocation.accessor,
        "revoked_at": datetime.now().isoformat(),
    }


@app.get("/consent/{user_id}")
def get_user_consent(user_id: str):
    consents = get_consent_status(user_id)
    return {
        "user_id": user_id,
        "consents": consents,
    }

@app.get("/transactions/{txn_id}/report")
def download_str_report(txn_id: str):
    txn = get_transaction_by_id(txn_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    log_audit_entry(
        user_id=str(txn.get("user_id", "unknown")),
        accessor="compliance_team",
        access_type="str_report_generation",
        purpose="Suspicious Transaction Report generated for FIU-IND submission",
    )

    pdf_bytes = generate_str_report(txn)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=STR_{txn_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
        }
    )

@app.get("/shadow-mode")
def get_shadow_mode():
    return {"shadow_mode": shadow_mode["enabled"]}


@app.post("/shadow-mode/toggle")
def toggle_shadow_mode():
    shadow_mode["enabled"] = not shadow_mode["enabled"]
    return {
        "shadow_mode": shadow_mode["enabled"],
        "message": "Shadow mode enabled. Model running silently." if shadow_mode["enabled"] else "Shadow mode disabled. Model acting on transactions.",
    }

@app.get("/drift/report")
def get_drift_report():
    report = compute_drift_report(df_transactions)
    return report