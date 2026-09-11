import requests
import json
from pprint import pprint
from tabulate import tabulate

SERVER_URL = "http://localhost:6566/get-online-features"

# Global fallback defaults for missing entities (imputation defense)
GLOBAL_DEFAULTS = {
    "conv_rate": 0.18,
    "acc_rate": 0.82,
    "avg_daily_trips": 20
}

def query_online_features(driver_ids):
    payload = {
        "features": [
            "driver_hourly_stats:conv_rate",
            "driver_hourly_stats:acc_rate",
            "driver_hourly_stats:avg_daily_trips",
        ],
        "entities": {
            "driver_id": driver_ids
        }
    }

    print("=" * 65)
    print(f"QUERYING FEAST FEATURE SERVER FOR DRIVERS: {driver_ids}")
    print("=" * 65)

    try:
        response = requests.post(SERVER_URL, json=payload, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")
        print("Verify feast-server is running on port 6566.")
        return

    data = response.json()
    metadata = data.get("metadata", {})
    results = data.get("results", [])

    print("\nRaw Server Response:")
    pprint(data)

    # Transform into clean client-side inference vector with defensive imputation
    feature_names = [f.split(":")[-1] for f in payload["features"]]
    table_rows = []

    for idx, d_id in enumerate(driver_ids):
        row_values = {"driver_id": d_id}
        statuses = []
        
        for f_idx, f_name in enumerate(feature_names):
            val = results[f_idx]["values"][idx]
            status = results[f_idx]["statuses"][idx]
            statuses.append(status)
            
            if status == "PRESENT" and val is not None:
                row_values[f_name] = round(val, 4) if isinstance(val, float) else val
            else:
                # Defensive imputation fallback
                row_values[f_name] = f"{GLOBAL_DEFAULTS[f_name]} (imputed)"

        status_summary = "PRESENT" if all(s == "PRESENT" for s in statuses) else "NOT_FOUND"
        table_rows.append([
            d_id,
            status_summary,
            row_values["conv_rate"],
            row_values["acc_rate"],
            row_values["avg_daily_trips"]
        ])

    headers = ["Driver ID", "Status", "Conv Rate", "Acc Rate", "Avg Daily Trips"]
    print("\nProcessed Inference Feature Vectors (With Imputation):")
    print(tabulate(table_rows, headers=headers, tablefmt="fancy_grid"))

if __name__ == "__main__":
    # Test valid entities alongside an unknown entity (9999)
    query_online_features([1001, 1002, 9999])
