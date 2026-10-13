#!/usr/bin/env bash
# First-time (or re-)install: env file, Postgres, Python deps, migrations, seed, frontend deps.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

need() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Required command not found: $1"
    exit 1
  }
}

need docker
need python3
need npm

if [[ ! -f .env ]]; then
  echo "Creating .env from .env.example"
  cp .env.example .env
fi

echo "Starting PostgreSQL (docker compose up -d --wait)..."
docker compose up -d --wait

if [[ ! -d .venv ]]; then
  echo "Creating Python virtualenv in .venv"
  python3 -m venv .venv
fi

echo "Installing backend dependencies..."
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -r backend/requirements.txt

echo "Running migrations and seed data..."
(
  cd backend
  ../.venv/bin/alembic upgrade head
  ../.venv/bin/python -m app.seed
)

echo "Installing frontend dependencies..."
npm install --prefix frontend

echo ""
bash "$ROOT/scripts/verify-setup.sh"

echo ""
echo "Next steps:"
echo "  Terminal 1: npm run dev:api"
echo "  Terminal 2: npm run dev:web"
echo "  Open http://localhost:5173 and search for PAY-1001"
