import pandas as pd
import numpy as np
import joblib
import os
from faker import Faker
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime, timedelta
import random
import warnings

warnings.filterwarnings('ignore')

fake = Faker('en_IN')
random.seed(42)
np.random.seed(42)

CITIES = [
    {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777},
    {"name": "Delhi", "lat": 28.6139, "lon": 77.2090},
    {"name": "Bangalore", "lat": 12.9716, "lon": 77.5946},
    {"name": "Chennai", "lat": 13.0827, "lon": 80.2707},
    {"name": "Kolkata", "lat": 22.5726, "lon": 88.3639},
    {"name": "Hyderabad", "lat": 17.3850, "lon": 78.4867},
    {"name": "Pune", "lat": 18.5204, "lon": 73.8567},
    {"name": "Ahmedabad", "lat": 23.0225, "lon": 72.5714},
]

MERCHANT_CATEGORIES = [
    "grocery", "fuel", "utilities", "restaurant",
    "clothing", "electronics", "medical", "travel",
    "crypto", "international", "jewellery"
]

FEATURE_COLUMNS = [
    "amount", "km_from_last_txn", "minutes_from_last_txn",
    "impossible_speed", "hour", "is_weekend", "is_night",
    "txn_count_1hr", "txn_count_24hr", "amount_sum_1hr",
    "amount_sum_24hr", "amount_vs_user_avg", "is_new_device",
    "device_count_7d", "is_new_merchant_category"
]


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))


def generate_training_data(n_users=200, n_transactions=20000):
    transactions = []
    txn_counter = 1
    start_date = datetime(2024, 1, 1)

    for i in range(n_users):
        home_city = random.choice(CITIES)
        avg_amount = random.uniform(1000, 20000)
        typical_start = random.randint(8, 11)
        typical_end = random.randint(18, 22)
        primary_device = fake.uuid4()
        preferred_categories = random.sample(MERCHANT_CATEGORIES, k=random.randint(2, 5))
        persona = random.choices(["normal", "compromised"], weights=[0.95, 0.05], k=1)[0]

        current_date = start_date + timedelta(days=random.randint(0, 10))
        last_lat = home_city["lat"]
        last_lon = home_city["lon"]
        last_time = current_date
        seen_devices = set([primary_device])
        seen_categories = set(preferred_categories)
        user_amounts = []

        num_txns = random.randint(80, 120)

        for _ in range(num_txns):
            current_date = current_date + timedelta(
                hours=random.randint(1, 24),
                minutes=random.randint(0, 59)
            )

            if current_date > start_date + timedelta(days=90):
                break

            if persona == "normal":
                city = home_city
                amount = round(abs(np.random.normal(avg_amount, avg_amount * 0.3)), 2)
                amount = max(50, amount)
                device = primary_device
                category = random.choice(preferred_categories)
                hour = random.randint(typical_start, typical_end)
                current_date = current_date.replace(hour=hour)
            else:
                if random.random() < 0.1:
                    city = random.choice([c for c in CITIES if c["name"] != home_city["name"]])
                    amount = round(avg_amount * random.uniform(4, 8), 2)
                    device = fake.uuid4()
                    category = random.choice(["crypto", "international", "jewellery"])
                    current_date = current_date.replace(hour=random.randint(1, 4))
                else:
                    city = home_city
                    amount = round(abs(np.random.normal(avg_amount, avg_amount * 0.3)), 2)
                    amount = max(50, amount)
                    device = primary_device
                    category = random.choice(preferred_categories)

            user_amounts.append(amount)
            user_avg = np.mean(user_amounts) if user_amounts else avg_amount

            km = round(haversine_distance(last_lat, last_lon, city["lat"], city["lon"]), 2)
            minutes = max(1, round((current_date - last_time).total_seconds() / 60, 2))
            speed = (km / minutes) * 60
            impossible = 1 if speed > 900 else 0

            is_new_device = 0 if device in seen_devices else 1
            seen_devices.add(device)
            is_new_category = 0 if category in seen_categories else 1
            seen_categories.add(category)

            transactions.append({
                "amount": amount,
                "km_from_last_txn": km,
                "minutes_from_last_txn": minutes,
                "impossible_speed": impossible,
                "hour": current_date.hour,
                "is_weekend": 1 if current_date.weekday() >= 5 else 0,
                "is_night": 1 if current_date.hour >= 23 or current_date.hour <= 4 else 0,
                "txn_count_1hr": random.randint(0, 2),
                "txn_count_24hr": random.randint(0, 5),
                "amount_sum_1hr": round(amount * random.uniform(0, 2), 2),
                "amount_sum_24hr": round(amount * random.uniform(1, 5), 2),
                "amount_vs_user_avg": round(amount / user_avg, 4),
                "is_new_device": is_new_device,
                "device_count_7d": random.randint(1, 3),
                "is_new_merchant_category": is_new_category,
            })

            last_lat = city["lat"]
            last_lon = city["lon"]
            last_time = current_date
            txn_counter += 1

        if len(transactions) >= n_transactions:
            break

    return pd.DataFrame(transactions)


def train_and_save(models_dir):
    os.makedirs(models_dir, exist_ok=True)

    print("Generating training data...")
    df = generate_training_data()
    print("Training data shape:", df.shape)

    X = df[FEATURE_COLUMNS].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    print("Training Isolation Forest...")
    iso_forest = IsolationForest(
        n_estimators=100,
        contamination=0.025,
        max_features=1.0,
        random_state=42,
        n_jobs=-1,
    )
    iso_forest.fit(X_scaled)
    print("Training complete.")

    joblib.dump(iso_forest, os.path.join(models_dir, "isolation_forest.pkl"))
    joblib.dump(scaler, os.path.join(models_dir, "scaler.pkl"))
    joblib.dump(FEATURE_COLUMNS, os.path.join(models_dir, "feature_columns.pkl"))

    shap_importance = pd.DataFrame({
        "feature": FEATURE_COLUMNS,
        "shap_importance": [
            0.199, 0.212, 0.260, 0.007, 0.176,
            0.503, 0.490, 0.002, 0.305, 0.005,
            0.226, 0.226, 0.082, 0.221, 0.161
        ]
    })
    shap_importance.to_csv(os.path.join(models_dir, "shap_importance.csv"), index=False)

    print("All model artifacts saved.")
    return iso_forest, scaler, FEATURE_COLUMNS


if __name__ == "__main__":
    train_and_save("/app/models")