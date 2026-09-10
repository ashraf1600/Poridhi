#!/usr/bin/env bash
set -eo pipefail

cd /app

echo "=================================================="
echo "Starting Feast Service Container"
echo "=================================================="

# 1. Generate Parquet data if missing
if [ ! -f "data/driver_stats.parquet" ]; then
    echo "Parquet data not found. Generating synthetic dataset..."
    python3 generate_data.py
else
    echo "Found existing Parquet dataset."
fi

# 2. Register Feature Store definitions
echo "Applying feature definitions to registry..."
feast apply

# 3. Materialize features into SQLite if requested
if [ "${MATERIALIZE:-false}" = "true" ]; then
    echo "Materializing features to SQLite online store..."
    feast materialize-incremental "$(date -u +"%Y-%m-%dT%H:%M:%S")"
    echo "Materialization complete."
fi

# 4. Route commands
case "$1" in
    "serve")
        echo "Launching Feast Feature Server on 0.0.0.0:6566..."
        exec feast serve -h 0.0.0.0 -p 6566
        ;;
    "ui")
        echo "Launching Feast Web Dashboard on 0.0.0.0:8888..."
        exec feast ui -h 0.0.0.0 -p 8888
        ;;
    *)
        exec "$@"
        ;;
esac
