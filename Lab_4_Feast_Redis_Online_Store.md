# Lab 4 — Feast + Redis: Mastering the Online Store for Real-Time Inference

Welcome to this hands-on lab! In this tutorial, you will replace SQLite with Redis as your Feast online store, materialize batch features for low-latency lookup, ingest streaming updates, and serve features with the Feast Python SDK and Feature Server.

## Objective
In this lab, we will:

1. Install and verify Redis as a Feast online store.
2. Configure `feature_store.yaml` for Redis (`localhost:6379` vs `redis:6379`).
3. Materialize Parquet features into Redis with `materialize-incremental`.
4. Retrieve vectors with `get_online_features` and benchmark latency.
5. Push streaming features with `feast push` and verify freshness.
6. Serve features over REST with `feast serve` and handle `NOT_FOUND`.

## Introduction to Feast + Redis

**What is the Online Store?**
Feast has two stores: offline (Parquet/S3/BigQuery — full history for training) and online (Redis/SQLite — latest value per entity key for inference). `get_historical_features` reads offline; `get_online_features` reads online.

**Why Redis instead of SQLite?**
Lab 1 used SQLite — simple but disk-based, ~5-20ms, single-file, no TTL eviction. Production inference needs:

- Sub-millisecond in-memory key-value lookup
- Concurrent reads from many API servers
- TTL-based expiry and per-entity latest-value semantics

Redis gives all three. Trade-off: you must run and monitor a separate process.

## Architecture Overview

The Architecture consists of following components:

- Batch Source: `data/driver_stats.parquet` (offline file store)
- Registry: `data/registry.db` (entities, feature views)
- Online Store: Redis at `localhost:6379` (or `redis:6379` in Docker)
- Serving layer: Python SDK + `feast serve :6566`

```
Parquet --feast materialize-incremental--> Redis
Stream events --feast push--> Offline + Online
Model --get_online_features(entity_rows)--> Redis dict
```

image01 — Feast + Redis read/write paths

## Prerequisites
- Python 3.9+, conda or venv, Feast basics (Lab 1)
- Redis 7.x
- `pip install feast[redis] pandas pyarrow redis scikit-learn`

## Step 1: Install and Verify Redis

Ubuntu / EC2:

```bash
sudo apt update
sudo apt install redis-server -y
sudo systemctl start redis
sudo systemctl enable redis
redis-cli ping
```

Expected: `PONG`

Docker alternative:

```bash
docker run -d --name feast-redis -p 6379:6379 redis:7.2-alpine
docker exec feast-redis redis-cli ping
```

Python check:

```bash
python -c "import feast, redis; r=redis.Redis(host='localhost',port=6379); print(r.ping()); print('All imports successful')"
```

## Step 2: Configure Feast to Use Redis

Create project:

```bash
mkdir -p ~/feast-redis-lab/feature_repo/data
cd ~/feast-redis-lab/feature_repo
```

Create `feature_store.yaml` (local run — use `localhost`):

```yaml
project: driver_ranking
registry: data/registry.db
provider: local
online_store:
  type: redis
  connection_string: localhost:6379
offline_store:
  type: file
entity_key_serialization_version: 3
```

> Rule: local Python → `localhost:6379`. Docker Compose → `redis:6379` (service name). Mixing them is the #1 connection error.

Verify:

```bash
feast version
feast apply
feast entities list
feast feature-views list
```

## Step 3: Define Driver Features

Reuse Lab 1/3 definitions. Create `features.py`:

```python
from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource
from feast.types import Float32, Int64

driver = Entity(name="driver", join_keys=["driver_id"])

driver_stats_source = FileSource(
    name="driver_stats_source",
    path="data/driver_stats.parquet",
    timestamp_field="event_timestamp",
    created_timestamp_column="created",
)

driver_stats_fv = FeatureView(
    name="driver_hourly_stats",
    entities=[driver],
    ttl=timedelta(days=1),
    schema=[
        Field(name="conv_rate", dtype=Float32),
        Field(name="acc_rate", dtype=Float32),
        Field(name="avg_daily_trips", dtype=Int64),
    ],
    online=True,
    source=driver_stats_source,
)
```

Generate sample Parquet if needed (24h x 5 drivers) and apply:

```bash
python generate_data.py
feast apply
```

Output: `Created entity driver`, `Created feature view driver_hourly_stats`.

## Step 4: Materialize Batch Features into Redis

This copies latest Parquet rows into Redis:

```bash
feast materialize-incremental $(date -u +"%Y-%m-%dT%H:%M:%S")
```

Expected: `Materializing 1 feature views...` + row count.

Inspect a key:

```bash
redis-cli --scan --pattern '*driver*' | head
redis-cli DBSIZE
```

If `NOT_FOUND` later, your materialize timestamp predates Parquet `event_timestamp` — re-run with a future timestamp.

## Step 5: Retrieve Online Features (Python SDK)

Create `fetch_online.py`:

```python
from pprint import pprint
from feast import FeatureStore
import time

store = FeatureStore(repo_path=".")

t0 = time.time()
vec = store.get_online_features(
    features=[
        "driver_hourly_stats:conv_rate",
        "driver_hourly_stats:acc_rate",
        "driver_hourly_stats:avg_daily_trips",
    ],
    entity_rows=[{"driver_id": 1001}, {"driver_id": 1005}],
).to_dict()
print(f"latency: {(time.time()-t0)*1000:.2f} ms")
pprint(vec)
```

Output:

```text
latency: 3.45 ms
{'acc_rate': [0.854..., 0.929...],
 'avg_daily_trips': [26, 372],
 'conv_rate': [0.0068..., 0.0622...],
 'driver_id': [1001, 1005]}
```

Benchmark loop: 100 sequential lookups should stay <10ms p95 on local Redis vs 20-50ms on SQLite.

## Step 6: Push Streaming Features and Verify Freshness

Batch materialize is hourly/daily. For live updates use push:

```python
import pandas as pd
from datetime import datetime, timezone
from feast import FeatureStore

store = FeatureStore(repo_path=".")
now = datetime.now(timezone.utc)

stream_df = pd.DataFrame({
    "driver_id": [1001],
    "conv_rate": [0.99],
    "acc_rate": [0.97],
    "avg_daily_trips": [88],
    "event_timestamp": [now],
    "created": [now],
})
store.push("driver_stats_push_source", stream_df, to="online_and_offline")
# If you defined a PushSource, use its name; otherwise push to the FeatureView source

fresh = store.get_online_features(
    features=["driver_hourly_stats:conv_rate"],
    entity_rows=[{"driver_id": 1001}],
).to_dict()
print(fresh)
```

Expected: `conv_rate` for 1001 is now `0.99` — fresher than Parquet. This is how Lab 2 fraud signals would update risk scores in real time.

## Step 7: Serve Over REST

```bash
feast serve --host 0.0.0.0 --port 6566
```

In another terminal:

```bash
curl -X POST http://localhost:6566/get-online-features \
  -H "Content-Type: application/json" \
  -d '{"features":["driver_hourly_stats:conv_rate","driver_hourly_stats:acc_rate"],"entities":{"driver_id":[1001,1002]}}'
```

Handle missing entities in client code:

```python
resp = store.get_online_features(features=[...], entity_rows=[{"driver_id": 9999}]).to_dict()
# statuses == ['NOT_FOUND'] -> impute mean / fallback
```

Production pattern: `value if status=='PRESENT' else global_mean`.

## Step 8: Cleanup and Checks

```bash
feast entities list
feast feature-views list
redis-cli ping  # PONG
python -c "import feast, redis; print('ready')"
```

## Conclusion
By completing this lab, you turned Redis into a sub-millisecond online store: configured connection strings correctly for local vs Docker, materialized Parquet history, fetched vectors with the SDK, pushed streaming updates, and served over REST with defensive `NOT_FOUND` handling. Your store is now ready for Lab 5 — training a model on offline features and scoring it live from Redis without training-serving skew.
