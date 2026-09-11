import os
from datetime import datetime, timedelta, timezone
import numpy as np
import pandas as pd

def generate_driver_stats():
    os.makedirs("data", exist_ok=True)
    
    driver_ids = [1001, 1002, 1003, 1004, 1005]
    end_date = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    timestamps = [end_date - timedelta(hours=i) for i in range(24)]
    
    records = []
    np.random.seed(42)
    
    for driver_id in driver_ids:
        base_conv = 0.15 + (driver_id % 10) * 0.05
        base_acc = 0.80 + (driver_id % 10) * 0.02
        base_trips = 15 + (driver_id % 10) * 5
        
        for ts in timestamps:
            conv_rate = float(np.clip(base_conv + np.random.normal(0, 0.02), 0.01, 1.0))
            acc_rate = float(np.clip(base_acc + np.random.normal(0, 0.01), 0.50, 1.0))
            avg_daily_trips = int(max(1, np.random.poisson(base_trips)))
            
            records.append({
                "driver_id": driver_id,
                "conv_rate": np.float32(conv_rate),
                "acc_rate": np.float32(acc_rate),
                "avg_daily_trips": np.int64(avg_daily_trips),
                "event_timestamp": ts,
                "created": ts,
            })
            
    df = pd.DataFrame(records)
    output_path = "data/driver_stats.parquet"
    df.to_parquet(output_path, index=False)
    print(f"Generated {len(df)} feature records across {len(driver_ids)} drivers.")
    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    generate_driver_stats()
