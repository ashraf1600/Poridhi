# Lab 5 — Feast Pipeline: From Batch Features to Trained Model to Live Inference

Welcome to this hands-on lab! In this tutorial, you will build a complete ML pipeline on Feast: ingest batch data, generate point-in-time training datasets, train a scikit-learn model, batch-score history, and serve live predictions from the online store — with zero training-serving skew.

## Objective
In this lab, we will:

1. Model fraud/driver features with Entities, FileSources, FeatureViews and a FeatureService.
2. Add an on-demand transform for request-time features.
3. Build a correct training dataset with `get_historical_features`.
4. Train and save a scikit-learn classifier.
5. Materialize to Redis and run batch scoring + real-time inference with the same features.

## Introduction to Feast Pipelines

**What is a Feast Pipeline?**
A pipeline is the closed loop: `Register → Store → Train (offline) → Materialize → Serve (online) → Monitor`. Feast guarantees the features used in `get_historical_features` (training) and `get_online_features` (inference) come from one definition.

**Why pipelines instead of notebooks?**
Without Feast, data scientists join Parquet in notebooks while engineers re-write SQL in production — classic training-serving skew. Feast fixes this with:

- Point-in-time joins (no future leakage)
- One `features.py` as source of truth
- `materialize` sync from offline to online
- FeatureServices to version the exact feature set a model needs

## Architecture Overview

Components:

- Batch Source: `data/driver_stats.parquet` + labels
- Transforms: on-demand `transformed_conv_rate` (`conv_rate + val`)
- Offline retrieval: `get_historical_features(entity_df)`
- Model: `model.pkl` (LogisticRegression / RandomForest)
- Online: Redis + `feast serve :6566` + `get_online_features`

```
Parquet + entity_df --point-in-time join--> training_df --fit--> model.pkl
Parquet --materialize--> Redis --get_online_features--> model.predict (live)
```

image01 — End-to-end pipeline diagram

## Prerequisites
- Labs 1, 3, 4 completed (Feast repo + Redis running)
- `pip install feast[redis] pandas pyarrow scikit-learn joblib`

## Step 1: Setup Feature Repository

```bash
feast init fraud-pipeline
cd fraud-pipeline/feature_repo
```

`feature_store.yaml` (local + Redis):

```yaml
project: fraud_detection_features
registry: data/registry.db
provider: local
online_store:
  type: redis
  connection_string: localhost:6379
offline_store:
  type: file
entity_key_serialization_version: 3
```

## Step 2: Define Pipeline Features

`features.py` — entity + batch view + on-demand view + service:

```python
from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource, FeatureService, RequestSource, OnDemandFeatureView
from feast.types import Float32, Float64, Int64
from feast.on_demand_feature_view import RequestDataSource
import pandas as pd

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

# Request-time inputs (come with inference request, not from store)
vals = RequestDataSource(
    name="vals",
    schema=[Field(name="val_to_add", dtype=Float64), Field(name="val_to_add_2", dtype=Float64)],
)

def transform_fn(inputs: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame()
    out["conv_rate_plus_val1"] = inputs["conv_rate"] + inputs["val_to_add"]
    out["conv_rate_plus_val2"] = inputs["conv_rate"] + inputs["val_to_add_2"]
    return out

transformed = OnDemandFeatureView(
    name="transformed_conv_rate",
    sources=[driver_stats_fv, vals],
    schema=[Field(name="conv_rate_plus_val1", dtype=Float64), Field(name="conv_rate_plus_val2", dtype=Float64)],
    mode="python",
    udf=transform_fn,
)

svc = FeatureService(
    name="driver_ranking_svc",
    features=[driver_stats_fv, transformed],
)
```

```bash
feast apply
```

## Step 3: Generate Point-in-Time Training Dataset

Create `build_training.py`:

```python
from datetime import datetime
import pandas as pd
from feast import FeatureStore

entity_df = pd.DataFrame.from_dict({
    "driver_id": [1001, 1002, 1003],
    "event_timestamp": [
        datetime(2021, 4, 12, 10, 59, 42),
        datetime(2021, 4, 12, 8, 12, 10),
        datetime(2021, 4, 12, 16, 40, 26),
    ],
    "label_driver_reported_satisfaction": [1, 5, 3],
    "val_to_add": [1, 2, 3],
    "val_to_add_2": [10, 20, 30],
})

store = FeatureStore(repo_path=".")
training_df = store.get_historical_features(
    entity_df=entity_df,
    features=[
        "driver_hourly_stats:conv_rate",
        "driver_hourly_stats:acc_rate",
        "driver_hourly_stats:avg_daily_trips",
        "transformed_conv_rate:conv_rate_plus_val1",
        "transformed_conv_rate:conv_rate_plus_val2",
    ],
).to_df()

print(training_df.info())
print(training_df.head())
training_df.to_parquet("data/training.parquet", index=False)
```

Output (like Lab 1): 3 rows, 10 columns, no leakage — Feast joins as-of `event_timestamp`.

## Step 4: Train and Save Model

`train.py`:

```python
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

df = pd.read_parquet("data/training.parquet")
# Toy label: high satisfaction if conv_rate high — replace with fraud label in real data
X = df[["conv_rate","acc_rate","avg_daily_trips","conv_rate_plus_val1","conv_rate_plus_val2"]].fillna(0)
y = (df["label_driver_reported_satisfaction"] >= 4).astype(int)

clf = RandomForestClassifier(n_estimators=50, random_state=42)
clf.fit(X, y)
joblib.dump(clf, "data/model.pkl")
print(f"train accuracy: {clf.score(X, y):.3f}")
```

For a realistic fraud dataset, expand `entity_df` to thousands of rows from your Parquet history before training.

## Step 5: Batch Scoring (Offline Inference)

Update timestamps to now and re-pull — simulates nightly scoring:

```python
entity_df["event_timestamp"] = pd.to_datetime("now", utc=True)
batch_df = store.get_historical_features(entity_df=entity_df, features=[
    "driver_hourly_stats:conv_rate",
    "driver_hourly_stats:acc_rate",
    "driver_hourly_stats:avg_daily_trips",
    "transformed_conv_rate:conv_rate_plus_val1",
    "transformed_conv_rate:conv_rate_plus_val2",
]).to_df()
Xb = batch_df[["conv_rate","acc_rate","avg_daily_trips","conv_rate_plus_val1","conv_rate_plus_val2"]].fillna(0)
batch_df["pred"] = clf.predict(Xb)
print(batch_df[["driver_id","pred"]])
```

## Step 6: Live Inference (Online + Model)

Materialize then serve:

```bash
feast materialize-incremental $(date -u +"%Y-%m-%dT%H:%M:%S")
feast serve --host 0.0.0.0 --port 6566 &
```

`infer.py`:

```python
from feast import FeatureStore
import joblib

store = FeatureStore(repo_path=".")
clf = joblib.load("data/model.pkl")

vec = store.get_online_features(
    features=[
        "driver_hourly_stats:conv_rate",
        "driver_hourly_stats:acc_rate",
        "driver_hourly_stats:avg_daily_trips",
    ],
    entity_rows=[{"driver_id": 1004}, {"driver_id": 1005}],
).to_dict()
print(vec)

import pandas as pd
Xlive = pd.DataFrame({
    "conv_rate": vec["conv_rate"],
    "acc_rate": vec["acc_rate"],
    "avg_daily_trips": vec["avg_daily_trips"],
    "conv_rate_plus_val1": [c+1 for c in vec["conv_rate"]],
    "conv_rate_plus_val2": [c+10 for c in vec["conv_rate"]],
}).fillna(0)
print("live preds:", clf.predict(Xlive))
```

Same feature names as training → no skew. Push new stream rows (`store.push`) and re-query to see predictions update.

## Step 7: Validate Consistency

1. Compare one entity offline vs online — values must match after materialize.
2. Query unknown `driver_id=9999` — expect `NOT_FOUND`; confirm model fallback path works.
3. Open `feast ui --host 0.0.0.0` at `:8888` — confirm service `driver_ranking_svc` lists all 5 features.

## Conclusion
By completing this lab, you closed the loop: defined versioned features once, built leakage-free training data, trained a model, batch-scored history, and served live predictions from Redis using identical features plus on-demand transforms. This pipeline is production-ready scaffolding — swap Parquet for S3/BigQuery, Redis for ElastiCache, wrap `infer.py` in FastAPI, and add monitoring for drift and `NOT_FOUND` rate.
