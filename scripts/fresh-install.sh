#!/usr/bin/env bash
# Wipe the Postgres volume and run a full bootstrap (destructive).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "Stopping containers and removing postgres_data volume..."
docker compose down -v

bash "$ROOT/scripts/bootstrap.sh"
