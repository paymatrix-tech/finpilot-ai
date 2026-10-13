# FinPilot security notes (MVP)

This is a local portfolio MVP, not a production payments system. These practices keep the demo safe to run and share.

## Secrets and configuration

- Copy `.env.example` to `.env` for local use. **Never commit `.env`.**
- API keys (`GROQ_API_KEY`, `GEMINI_API_KEY`, `OPENAI_API_KEY`, `LLM_API_KEY`) are read from the environment via `app.config.Settings` only.
- Defaults use `LLM_PROVIDER=stub` and `EMBEDDING_PROVIDER=stub` so the app runs without keys.

## Input validation

- Payment IDs must match `PAY-…` (alphanumeric segments, max 64 chars) on API paths and investigation requests.
- Investigation questions and search queries are length-bounded.
- Payment list / log search escapes SQL `LIKE` wildcards (`%`, `_`) so filters cannot be widened accidentally.

## Read-only investigation tools

The agent may only call these tools (no writes, deletes, or SQL):

- `get_payment`
- `get_payment_events`
- `search_logs`
- `search_payment_docs`

Unknown or write-sounding tool names are rejected in `PaymentToolExecutor`.

## API surface

- CORS is limited to local Vite dev/preview origins.
- `/api/llm/chat` is intended for development; message count and total size are capped.
- There is no authentication on the MVP API—do not expose it to the public internet without adding auth and hardening.

## Before sharing the repo

```bash
git check-ignore -v .env   # should show .gitignore rule
git ls-files .env          # should print nothing
```
