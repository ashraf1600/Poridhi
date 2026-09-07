"""
Test client to query Feast Feature Server via HTTP POST /get-online-features.
"""
import requests

FEAST_URL = "http://localhost:6566/get-online-features"

request_payload = {
    "features": [
        "driver_hourly_stats:conv_rate",
        "driver_hourly_stats:acc_rate",
        "driver_hourly_stats:avg_daily_trips"
    ],
    "entities": {
        "driver_id": [1001, 1002, 1003, 1004, 1005]
    }
}

def main():
    print(f"Querying Feast Feature Server at {FEAST_URL} ...")
    try:
        response = requests.post(FEAST_URL, json=request_payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            cols = [r["values"] for r in data.get("results", [])]
            # cols[0]: driver_id, cols[1]: conv_rate, cols[2]: avg_daily_trips, cols[3]: acc_rate
            
            print("Connected successfully. Features retrieved from Redis:")
            print("=" * 65)
            print(f"{'DRIVER ID':<12} | {'CONV RATE':<12} | {'ACC RATE':<12} | {'DAILY TRIPS':<12}")
            print("=" * 65)
            
            for driver_id, conv_rate, daily_trips, acc_rate in zip(*cols):
                conv_str = f"{conv_rate:<12.4f}" if conv_rate is not None else f"{'None':<12}"
                acc_str = f"{acc_rate:<12.4f}" if acc_rate is not None else f"{'None':<12}"
                trips_str = f"{daily_trips:<12}" if daily_trips is not None else f"{'None':<12}"
                print(f"{driver_id:<12} | {conv_str} | {acc_str} | {trips_str}")
                
            print("=" * 65)
        else:
            print(f"Error {response.status_code}: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Could not connect to Feast Server. Ensure docker compose is running.")

if __name__ == "__main__":
    main()
