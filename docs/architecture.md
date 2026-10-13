# FinPilot architecture

FinPilot is a **modular monolith**: one FastAPI service, one React SPA, and PostgreSQL with **pgvector** for documentation RAG. The investigation agent calls **read-only tools** and returns structured RCA JSON with evidence and sources.

## System context

```mermaid
flowchart LR
  User[Operator browser]
  UI[React + Vite]
  API[FastAPI]
  DB[(PostgreSQL + pgvector)]
  LLM[LLM provider or stub]

  User --> UI
  UI -->|REST / SSE| API
  API --> DB
  API --> LLM
```

## Investigation flow

```mermaid
sequenceDiagram
  participant UI as Frontend
  participant API as FastAPI
  participant Agent as InvestigationAgent
  participant Tools as PaymentToolExecutor
  participant DB as PostgreSQL
  participant LLM as LLM

  UI->>API: POST /api/investigations
  API->>DB: Verify payment exists
  API->>Agent: investigate(payment_id, question)
  loop Tool gathering
    Agent->>LLM: chat + tool definitions
    LLM-->>Agent: tool_calls
    Agent->>Tools: get_payment / events / logs / docs
    Tools->>DB: read-only queries
    Tools-->>Agent: tool results
  end
  Agent->>LLM: structured RCA prompt
  LLM-->>Agent: root_cause, evidence, sources
  Agent-->>API: InvestigationQueryResponse
  API->>DB: persist investigation
  API-->>UI: JSON or SSE stream
```

## Backend layout

| Layer | Responsibility |
| --- | --- |
| `routers/` | HTTP API (payments, investigations, dev LLM chat) |
| `services/` | Investigation agent, RCA, evidence rules, payment service |
| `tools/` | Read-only tool executor (`get_payment`, events, logs, doc search) |
| `repositories/` | SQLAlchemy data access |
| `documentation/` | Markdown corpus, chunking, embeddings index |
| `llm/` | Provider routing, stubs, rate limits |

## Data stored

- **Payments** — amount, status, gateway, `error_code`
- **Events** — lifecycle (`PAYMENT_CREATED` → `GATEWAY_RESPONSE`)
- **Logs** — service messages for search
- **Documents + chunks** — ops docs with vector embeddings
- **Investigations** — saved RCA runs per payment

## Security (MVP)

- No auth on local API; see [SECURITY.md](../SECURITY.md).
- Payment IDs and payloads validated; tools cannot write to the database.
- Secrets only in `.env`, never committed.
