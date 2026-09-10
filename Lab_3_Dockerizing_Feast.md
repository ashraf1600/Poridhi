# Lab 3 — Dockerizing Feast: Building a Portable Local Feature Store with Docker and Redis

Welcome to this hands-on lab! In this tutorial, you will containerize Feast into a reproducible, portable feature store that runs identically on any machine. You will pair a Parquet offline store with a Redis online store and expose features through a REST API and Web UI.

## Objective
In this lab, we will:

1. Configure a Feast repository to use Parquet (offline) + Redis (online) inside Docker.
2. Build a custom Feast Docker image with all dependencies.
3. Orchestrate Redis, Feast Server, and Feast UI with Docker Compose.
4. Materialize batch features into Redis and serve them for real-time inference.
5. Validate everything with a Python client and the Feast Web UI.

## Introduction to Dockerizing Feast

**What is Dockerizing Feast?**
Dockerizing means packaging Feast, its Python dependencies, feature definitions, and startup logic into an immutable Docker image. Instead of installing Feast manually on every laptop or EC2 instance, you run `docker compose up` and get the same environment everywhere.

**Why do we use Docker for Feature Stores?**
In Lab 1 you used SQLite on localhost. In Lab 2 you installed Feast manually on EC2. Both break easily: `localhost` works on your laptop but fails inside a container, package versions drift, and `feast apply` is forgotten. Docker solves this by:

- Freezing Python + Feast versions in a `Dockerfile`
- Automating `feast apply + materialize` in an `entrypoint.sh`
- Isolating Redis, Server, and UI in one network with health checks

## Architecture Overview

The Architecture consists of following components:

- Redis container (`feast-redis:6379`) — in-memory online store
- Feast Server container (`feast-server:6566`) — REST API `POST /get-online-features`
- Feast UI container (`feast-ui:8888`) — catalog dashboard
- Mounted volume `./feature_repo:/app` — `feature_store.yaml`, `features.py`, `driver_stats.parquet`, `registry.db`

```
Client (test_client.py) --POST :6566--> Feast Server --read--> Redis (:6379)
Browser --GET :8888--> Feast UI
Parquet (offline) ==materialize==> Redis (online)
```

image01 — Dockerized Feast architecture (Client, Server, UI, Redis, Parquet)

## Prerequisites
- Docker Desktop + Docker Compose installed
- Python 3.10, Feast SDK basics (Lab 1)
- Familiarity with REST APIs

Check Docker:

```bash
docker --version
docker compose version
docker ps
```

## Step 1: Create Project Structure

```bash
mkdir -p feast-docker-lab/feature_repo/data
cd feast-docker-lab
```

Final structure:

```text
feast-docker-lab/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── entrypoint.sh
├── test_client.py
└── feature_repo/
    ├── feature_store.yaml
    ├── features.py
    ├── generate_data.py
    └── data/
        ├── driver_stats.parquet
        └── registry.db
```

## Step 2: Configure Feast for Docker Networking

Create `feature_repo/feature_store.yaml`:

```yaml
project: driver_ranking
registry: data/registry.db
provider: local
online_store:
  type: redis
  connection_string: redis:6379
offline_store:
  type: file
entity_key_serialization_version: 3
```

> Important: Use `redis:6379`, not `localhost:6379`. Inside a container, `localhost` means the container itself. Containers in the same Compose network resolve each other by service name (`redis`).

This config uses SQLite file for registry (metadata catalog), Parquet files for offline store (training), and Redis for online store (real-time).

## Step 3: Define Entities, Sources and Feature Views

Create `feature_repo/generate_data.py`:

```python
import os
from datetime import datetime, timedelta, timezone
import numpy as np
import pandas as pd

def generate_driver_data():
    now = datetime.now(timezone.utc)
    timestamps = [now - timedelta(hours=i) for i in range(24)]
    driver_ids = [1001, 1002, 1003, 1004, 1005]
    records = []
    np.random.seed(42)
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
    os.makedirs("data", exist_ok=True)
    df.to_parquet("data/driver_stats.parquet", index=False)
    print(f"Generated {len(df)} records")

if __name__ == "__main__":
    generate_driver_data()
```

Create `feature_repo/features.py`:

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
    ttl=timedelta(days=7),
    schema=[
        Field(name="conv_rate", dtype=Float32),
        Field(name="acc_rate", dtype=Float32),
        Field(name="avg_daily_trips", dtype=Int64),
    ],
    online=True,
    source=driver_stats_source,
)
```

`online=True` tells Feast to materialize this view into Redis. `ttl=7 days` prevents serving stale data.

## Step 4: Containerize — Requirements, Entrypoint, Dockerfile

Create `requirements.txt`:

```text
feast[redis]==0.38.0
pandas>=2.0.0
pyarrow>=12.0.0
fastapi>=0.100.0
uvicorn>=0.22.0
requests>=2.31.0
grpcio
grpcio-health-checking
grpcio-reflection
```

Create `entrypoint.sh`:

```bash
#!/usr/bin/env bash
set -eo pipefail
cd /app

if [ ! -f "data/driver_stats.parquet" ]; then
  echo "Dataset not found. Generating..."
  python3 generate_data.py
fi

echo "Applying feature definitions..."
feast apply

if [ "${MATERIALIZE:-false}" = "true" ]; then
  echo "Materializing to Redis..."
  feast materialize-incremental "$(date -u +"%Y-%m-%dT%H:%M:%S")"
fi

case "$1" in
  "serve") exec feast serve -h 0.0.0.0 -p 6566 ;;
  "ui") exec feast ui -h 0.0.0.0 -p 8888 ;;
  *) exec "$@" ;;
esac
```

```bash
chmod +x entrypoint.sh
```

> Why `feast apply` in entrypoint, not in `docker build`? At build time Redis and mounted volumes do not exist. At runtime the network is ready.

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends curl gcc python3-dev dos2unix && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY feature_repo/ /app/
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN dos2unix /usr/local/bin/entrypoint.sh && chmod +x /usr/local/bin/entrypoint.sh
EXPOSE 6566 8888
ENTRYPOINT ["entrypoint.sh"]
```

## Step 5: Orchestrate with Docker Compose

Create `docker-compose.yml`:

```yaml
services:
  redis:
    image: redis:7.2-alpine
    container_name: feast-redis
    ports: ["6379:6379"]
    volumes: [redis-storage:/data]
    networks: [feast-net]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 3s
      timeout: 2s
      retries: 5
    restart: unless-stopped

  feast-server:
    build: { context: ., dockerfile: Dockerfile }
    container_name: feast-server
    command: ["serve"]
    environment: [MATERIALIZE=true]
    ports: ["6566:6566"]
    volumes: ["./feature_repo:/app"]
    depends_on:
      redis: { condition: service_healthy }
    networks: [feast-net]

  feast-ui:
    build: { context: ., dockerfile: Dockerfile }
    container_name: feast-ui
    command: ["ui"]
    environment: [MATERIALIZE=false]
    ports: ["8888:8888"]
    volumes: ["./feature_repo:/app"]
    depends_on:
      redis: { condition: service_healthy }
    networks: [feast-net]

networks: { feast-net: { driver: bridge } }
volumes: { redis-storage: }
```

`condition: service_healthy` is critical — plain `depends_on` only waits for container start, not for Redis to answer `PING`.

## Step 6: Build, Run and Verify

```bash
docker compose up --build -d
docker compose ps
docker compose logs -f feast-server
```

Expected `ps` output:

```text
feast-redis   Up (healthy)  0.0.0.0:6379->6379/tcp
feast-server  Up            0.0.0.0:6566->6566/tcp
feast-ui      Up            0.0.0.0:8888->8888/tcp
```

Logs should show `feast apply` success + `Materializing to Redis`.

## Step 7: Test Real-Time Retrieval

cURL:

```bash
curl -X POST http://localhost:6566/get-online-features \
  -H "Content-Type: application/json" \
  -d '{"features": ["driver_hourly_stats:conv_rate","driver_hourly_stats:acc_rate","driver_hourly_stats:avg_daily_trips"], "entities": {"driver_id": [1001,1002]}}'
```

Python client `test_client.py`:

```python
import requests
FEAST_URL = "http://localhost:6566/get-online-features"
payload = {
    "features": ["driver_hourly_stats:conv_rate","driver_hourly_stats:acc_rate","driver_hourly_stats:avg_daily_trips"],
    "entities": {"driver_id": [1001,1002,1003,1004,1005]}
}
data = requests.post(FEAST_URL, json=payload).json()
cols = [r["values"] for r in data.get("results", [])]
print("Connected. Features from Redis:")
for row in zip(*cols):
    print(row)
```

```bash
python test_client.py
```

Expected: 5 rows of floats, e.g. `1001 | 0.4809 | 0.9708 | 75`.

Test missing key:

```bash
curl -X POST http://localhost:6566/get-online-features -H "Content-Type: application/json" -d '{"features":["driver_hourly_stats:conv_rate"],"entities":{"driver_id":[9999]}}'
```

Returns `NOT_FOUND` + null — your inference code must impute defaults.

## Step 8: Browse UI and Teardown

Open `http://localhost:8888` — verify `driver` entity, `driver_hourly_stats` view, and `data/driver_stats.parquet` source.

```bash
docker compose down -v
```

## Conclusion
By completing this lab, you built a portable Feast deployment where Parquet powers training and Redis powers sub-millisecond inference. You automated registration and materialization in Docker, enforced startup order with health checks, and served features over REST. This is the foundation for Lab 4 (Redis deep-dive) and Lab 5 (full ML pipeline). Next: add on-demand transforms, swap Parquet for S3, and front the server with FastAPI inference.
