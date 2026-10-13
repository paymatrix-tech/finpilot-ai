# FinPilot AI

AI payment investigation assistant (30-day MVP). Week 1 milestone: browse failed payments, open a payment, and inspect its timeline, events, and logs end-to-end.

## Stack

- **Frontend:** React, TypeScript, Vite, TanStack Query
- **Backend:** FastAPI, SQLAlchemy, Alembic
- **Database:** PostgreSQL (Docker Compose)

## Quick start

1. Copy environment variables:

   ```bash
   cp .env.example .env
   ```

2. Start PostgreSQL:

   ```bash
   docker compose up -d
   ```

3. Create a Python virtualenv, install backend deps, migrate, and seed:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   cd backend && alembic upgrade head && python -m app.seed && cd ..
   ```

4. Run the API (terminal 1):

   ```bash
   npm run dev:api
   ```

5. Run the UI (terminal 2):

   ```bash
   cd frontend && npm install && npm run dev
   ```

6. Open [http://localhost:5173](http://localhost:5173) and search for `PAY-1001`.

The Vite dev server proxies `/api` and `/health` to `http://127.0.0.1:8000`. The header shows **API connected** when the backend and database are healthy.

## Useful commands

| Command | Description |
| --- | --- |
| `npm run db:up` | Start PostgreSQL |
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
- **RAG eval** — 18 known doc questions + investigation answer checks *(current)*
