"""
Feast Feature Definitions: Entity, Source, and FeatureView.
"""
from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource
from feast.types import Float32, Int64

# 1. Primary Entity (Join Key)
driver = Entity(
    name="driver",
    join_keys=["driver_id"],
    description="Unique identifier for rideshare drivers"
)

# 2. Offline Data Source (Parquet File)
driver_stats_source = FileSource(
    name="driver_stats_source",
    path="data/driver_stats.parquet",
    timestamp_field="event_timestamp",
    created_timestamp_column="created"
)

# 3. Feature View
driver_stats_fv = FeatureView(
    name="driver_hourly_stats",
    entities=[driver],
    ttl=timedelta(days=7),
    schema=[
        Field(name="conv_rate", dtype=Float32, description="Ride booking conversion rate"),
        Field(name="acc_rate", dtype=Float32, description="Driver trip acceptance rate"),
        Field(name="avg_daily_trips", dtype=Int64, description="Average completed trips per day"),
    ],
    online=True,
    source=driver_stats_source,
    tags={"team": "dispatch_ops", "tier": "tier-1"}
)
