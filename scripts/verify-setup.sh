#!/usr/bin/env bash
# Smoke-check database and (optionally) the API after setup.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
  echo "Missing .env — run: cp .env.example .env"
  exit 1
fi

if ! docker compose ps --status running --services 2>/dev/null | grep -qx postgres; then
  echo "Postgres is not running — run: npm run db:up"
  exit 1
fi

if [[ ! -x .venv/bin/python ]]; then
  echo "Missing .venv — run: npm run setup"
  exit 1
fi

echo "Checking database connection..."
(
  cd backend
  ../.venv/bin/python - <<'PY'
from app.db import check_database

if not check_database():
    raise SystemExit("Database check failed. Is Postgres healthy? Try: docker compose ps")
print("Database: ok")
PY
)

if curl -sf --max-time 3 "http://127.0.0.1:8000/health" >/dev/null 2>&1; then
  echo "API health:"
  curl -sf "http://127.0.0.1:8000/health"
  echo ""
  echo "Sample payment:"
  curl -sf "http://127.0.0.1:8000/api/payments/PAY-1001" | head -c 200
  echo "..."
else
  echo "API not running on :8000 (optional). Start with: npm run dev:api"
fi

echo "Setup verification passed."
