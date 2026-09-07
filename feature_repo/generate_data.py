"""
Synthetic data generator for Feast offline store (Parquet).
Generates historical stats for rideshare drivers.
"""
import os
from datetime import datetime, timedelta, timezone
import numpy as np
import pandas as pd

def generate_driver_data():
    now = datetime.now(timezone.utc)
    # Generate 24 hours of hourly historical stats
    timestamps = [now - timedelta(hours=i) for i in range(24)]
    
    driver_ids = [1001, 1002, 1003, 1004, 1005]
    records = []

    np.random.seed(42)  # For reproducible demo values

    for driver_id in driver_ids:
        for ts in timestamps:
            records.append({
                "driver_id": driver_id,
                "conv_rate": float(np.random.uniform(0.2, 0.95)),
                "acc_rate": float(np.random.uniform(0.6, 0.99)),
                "avg_daily_trips": int(np.random.randint(15, 85)),
                "event_timestamp": ts,
                "created": now,
            })

    df = pd.DataFrame(records)
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, "driver_stats.parquet")
    df.to_parquet(file_path, index=False)
    print(f" Generated {len(df)} records at {file_path}")

if __name__ == "__main__":
    generate_driver_data()
