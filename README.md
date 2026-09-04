# SuRaksha — Real-Time Fraud Detection System

A production-grade, full-stack fraud detection platform that detects anomalous banking transactions in real time using unsupervised machine learning, explainable AI, and automated regulatory compliance tooling.

**API:** http://3.6.98.160:8000/docs  
**Developed by:** Abhishek Shandilya — VIT Bhopal University

---

## What It Does

SuRaksha monitors banking transactions in real time. When a transaction arrives, it is scored against a behavioral baseline learned from the user's historical activity. Anomalous transactions are automatically flagged, explained, and actioned — all within milliseconds.

The system does not use static rules. It learns what normal looks like for each individual user and flags deviations — catching fraud that rule-based systems miss.

---

## Architecture

Transaction Input
↓
Feature Engineering (15 behavioral features)
↓
Isolation Forest Model (ROC-AUC: 0.9826)
↓
Risk Scoring → Approve / Step-up Auth / Block
↓
SHAP Explainability → Why was this flagged?
↓
STR Report Generation (FIU-IND format)
↓
PostgreSQL (persistent audit trail)


---

## Model Validation

| Dataset | Transactions | ROC-AUC |
|---------|-------------|---------|
| Synthetic Indian Banking Data | 78,299 | 0.9826 |
| Kaggle Credit Card Fraud (real, unseen) | 284,807 | 0.9016 |

The model was trained on synthetic data and validated on 284,807 real European credit card transactions without retraining — confirming that the behavioral feature engineering captures universal fraud signals.

---

## Features

**Detection**
- Unsupervised Isolation Forest ensemble
- 15 behavioral features: velocity, location delta, device fingerprint, amount deviation, time anomaly
- Sub-100ms scoring latency
- Automatic remediation: approve, step-up authentication, or block

**Explainability**
- SHAP feature importance for every flagged transaction
- Per-transaction explanation of what triggered the anomaly
- Fully auditable decisions for regulatory compliance

**Compliance**
- Auto-generated Suspicious Transaction Reports in FIU-IND format (PDF)
- Customer consent portal compliant with DPDP Act 2023
- Full data access audit log per customer
- One-click consent revocation

**Operations**
- Shadow Mode for safe model testing without blocking real transactions
- Real-time model drift monitoring across 6 behavioral features
- No-code transaction simulator for testing fraud scenarios

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React.js, Recharts |
| Backend | FastAPI, Python 3.11 |
| ML Model | Isolation Forest, scikit-learn |
| Explainability | SHAP |
| Database | PostgreSQL |
| PDF Generation | ReportLab |
| Cloud | AWS EC2, AWS S3, AWS CloudFront |
| Containerization | Docker |

---

## Model Performance

| Metric | Value |
|--------|-------|
| ROC-AUC (synthetic) | 0.9826 |
| ROC-AUC (real Kaggle data) | 0.9016 |
| Overall Accuracy | 98% |
| Fraud Recall | 67% |
| False Positive Rate | 1.4% |
| Training Samples | 78,299 |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | System status |
| GET | /health | Health check |
| POST | /transaction/score | Score a transaction in real time |
| GET | /transactions | List all transactions |
| GET | /transactions/flagged | List flagged transactions |
| GET | /transactions/{id} | Transaction detail |
| GET | /transactions/{id}/report | Download STR PDF report |
| GET | /users/{id} | User profile |
| GET | /users/{id}/transactions | User transaction history |
| GET | /dashboard/stats | Dashboard statistics |
| GET | /audit/{id} | User audit log |
| POST | /consent/revoke | Revoke data access |
| GET | /consent/{id} | Consent status |
| GET | /drift/report | Model drift report |
| GET | /shadow-mode | Shadow mode status |
| POST | /shadow-mode/toggle | Toggle shadow mode |

---

## Local Setup

### Prerequisites
- Python 3.11
- Node.js 20+
- PostgreSQL
- Anaconda

### Backend

```bash
conda create -n suraksha python=3.11
conda activate suraksha
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```bash
cd frontend/suraksha-ui
npm install
npm start
```

---

## Dataset

Synthetic dataset of 78,299 transactions across 500 users simulating 90 days of Indian banking activity. Three behavioral personas: normal users, compromised accounts, and professional fraudsters. Fraud injection rate: 1.69%.

Validated on the Kaggle Credit Card Fraud Detection dataset — 284,807 real transactions with 492 confirmed fraud cases.

---

## Regulatory Compliance

- Prevention of Money Laundering Act (PMLA) 2002
- Digital Personal Data Protection Act (DPDP) 2023
- Financial Intelligence Unit India (FIU-IND) STR format

---

## Project Structure

suraksha/
├── main.py — FastAPI application, 16 endpoints
├── config.py — Environment configuration
├── scorer.py — Model loading and transaction scoring
├── database.py — PostgreSQL data layer
├── models.py — Pydantic request/response models
├── str_report.py — FIU-IND STR PDF generation
├── drift_detector.py — Model drift monitoring
├── train_model.py — Model training pipeline
└── requirements.txt — Python dependencies
