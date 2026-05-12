import os

BASE_DIR = r"C:\Users\Abhishek Shandilya\Desktop\suraksha"

MODEL_PATH = os.path.join(BASE_DIR, "models", "isolation_forest.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "models", "scaler.pkl")
FEATURE_COLUMNS_PATH = os.path.join(BASE_DIR, "models", "feature_columns.pkl")
SHAP_IMPORTANCE_PATH = os.path.join(BASE_DIR, "models", "shap_importance.csv")
SCORED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "transactions_scored.csv")
USER_PROFILES_PATH = os.path.join(BASE_DIR, "data", "synthetic", "user_profiles.csv")

FRAUD_THRESHOLD_REVIEW = 0.5
FRAUD_THRESHOLD_BLOCK = 0.8

API_HOST = "0.0.0.0"
API_PORT = 8000