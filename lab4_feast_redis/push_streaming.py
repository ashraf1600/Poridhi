import os
import sys
from datetime import datetime, timezone
import pandas as pd
from feast import FeatureStore

def main():
    repo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "feature_repo"))
    
    # Allow host override of redis host (default redis:6379 inside container, localhost:6379 on host)
    redis_conn = os.environ.get("REDIS_CONNECTION_STRING")
    if not redis_conn:
        # If running on host, check if localhost:6379 is reachable
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(("localhost", 6379))
            sock.close()
            if result == 0:
                os.environ["REDIS_CONNECTION_STRING"] = "localhost:6379"
        except Exception:
            pass

    store = FeatureStore(repo_path=repo_path)
    now = datetime.now(timezone.utc)

    # High-freshness streaming event: Driver 1001 surges in conversion and acceptance rate
    stream_df = pd.DataFrame({
        "driver_id": [1001],
        "conv_rate": [0.99],
        "acc_rate": [0.98],
        "avg_daily_trips": [88],
        "event_timestamp": [now],
        "created": [now],
    })

    print("=" * 60)
    print("REAL-TIME STREAMING FEATURE PUSH (FEAST + REDIS)")
    print("=" * 60)
    print("Stream Event Payload:")
    print(stream_df[["driver_id", "conv_rate", "acc_rate", "avg_daily_trips", "event_timestamp"]].to_string(index=False))

    print("\nExecuting store.push('driver_stats_push_source', stream_df)...")
    try:
        store.push("driver_stats_push_source", stream_df, to="online_and_offline")
        print("Push completed successfully.")

        # Immediately query Redis online store to verify freshness
        fresh_features = store.get_online_features(
            features=[
                "driver_hourly_stats_push:conv_rate",
                "driver_hourly_stats_push:acc_rate",
                "driver_hourly_stats_push:avg_daily_trips",
            ],
            entity_rows=[{"driver_id": 1001}],
        ).to_dict()

        print("\nVerified Fresh Online Features in Redis:")
        for k, v in fresh_features.items():
            print(f"  {k}: {v}")
            
    except Exception as e:
        print(f"Push operation note: {e}")
        print("If running on the host machine, ensure port 6379 is forwarded and dependencies are installed,")
        print("or execute inside the container: docker exec -it feast-server python /app/push_streaming.py")

if __name__ == "__main__":
    main()
