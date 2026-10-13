# FinPilot AI

AI payment investigation assistant (30-day MVP). Week 1 milestone: browse failed payments, open a payment, and inspect its timeline, events, and logs end-to-end.

## Stack

- **Frontend:** React, TypeScript, Vite, TanStack Query
- **Backend:** FastAPI, SQLAlchemy, Alembic
- **Database:** PostgreSQL (Docker Compose)

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (OrbStack, Docker Desktop, etc.)
- Python 3.12+ and Node.js 20+

## Quick start (new machine)

One command after cloning (creates `.env`, starts Postgres, venv, migrations, seed, frontend deps):

```bash
npm run setup
```

Then run the app:

```bash
npm run dev:api    # terminal 1
npm run dev:web    # terminal 2
```

Open [http://localhost:5173](http://localhost:5173) and search for `PAY-1001`.

### Manual steps (equivalent)

1. `cp .env.example .env`
2. `npm run db:up` — `docker compose up -d --wait`
3. `python3 -m venv .venv && .venv/bin/pip install -r backend/requirements.txt`
4. `cd backend && ../.venv/bin/alembic upgrade head && ../.venv/bin/python -m app.seed`
5. `npm install --prefix frontend`

### Fresh database (wipe volume)

```bash
npm run setup:fresh
# or: npm run db:reset   # keeps .venv, re-migrates and re-seeds
```

Verify Postgres (and API if running):

```bash
npm run verify
```

The Vite dev server proxies `/api` and `/health` to `http://127.0.0.1:8000`. The header shows **API connected** when the backend and database are healthy.

## Useful commands

| Command | Description |
| --- | --- |
| `npm run setup` | First-time bootstrap (Docker + deps + migrate + seed) |
| `npm run setup:fresh` | Wipe DB volume and bootstrap again |
| `npm run verify` | Smoke-check DB and optional API health |
| `npm run db:up` | Start PostgreSQL (`compose up --wait`) |
| `npm run db:reset` | Drop volume, migrate, and seed |
| `npm run dev:api` | FastAPI with reload |
| `npm run dev:web` | Vite dev server |
| `npm run test:api` | Backend pytest suite (`backend/tests/`) |

Requires PostgreSQL running (`npm run db:up`) and migrations applied. Tests use stub LLM/embeddings by default.

See [SECURITY.md](SECURITY.md) for secrets, validation, and read-only tools.

### Test layout

| Area | Module |
| --- | --- |
| Payments API | `test_payments_api.py` |
| Payment tools | `test_payment_tools.py`, `test_tool_calling.py` |
| Investigations | `test_investigation_*.py` |
| RAG / docs | `test_documentation*.py`, `test_embeddings.py`, `test_rag_evaluation.py` |
| Schema / seed | `test_schema.py`, `test_seed.py` |

## Milestones

- **v0.1** — Payment data (API + seed)
- **v0.2** — Payment UI wired to API
- **v0.7** — Backend test suite
- **RAG eval** — 18 known doc questions + investigation answer checks
- **Fresh install** — `npm run setup` / `docker compose` *(current)*
