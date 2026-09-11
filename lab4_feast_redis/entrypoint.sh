#!/usr/bin/env bash
set -e

cd /app

echo "Waiting for Redis to become available..."
until redis-cli -h redis ping | grep -q PONG; do
  echo "Redis not reachable yet. Retrying in 2 seconds..."
  sleep 2
done
echo "Redis connection verified."

if [ "$1" = "server" ]; then
  echo "Applying Feast definitions to registry..."
  feast apply

  echo "Materializing historical batch features to Redis..."
  feast materialize-incremental "$(date -u +"%Y-%m-%dT%H:%M:%S")"

  echo "Starting Feast feature server on port 6566..."
  exec feast serve --host 0.0.0.0 --port 6566

elif [ "$1" = "ui" ]; then
  echo "Starting Feast Web UI on port 8888..."
  exec feast ui --host 0.0.0.0 --port 8888

else
  exec "$@"
fi
