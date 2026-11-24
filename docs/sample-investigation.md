# Sample investigation — PAY-1001 (ACH R01)

This walkthrough matches the seeded demo payment **PAY-1001** (insufficient funds / **R01**). With `LLM_PROVIDER=stub`, the agent uses deterministic tool steps and RCA output—no API key required.

## 1. Find the payment

In the UI, search for `PAY-1001` or open:

`GET /api/payments/PAY-1001`

| Field | Value |
| --- | --- |
| Status | `FAILED` |
| Method | `ACH` |
| Gateway | `ExamplePay` |
| Error code | `R01` |

## 2. Start investigation

**UI:** Payment detail → **Investigate**

**API:**

```bash
curl -s -X POST http://127.0.0.1:8000/api/investigations \
  -H 'Content-Type: application/json' \
  -d '{"payment_id":"PAY-1001","question":"Why did this payment fail?"}' | jq
```

Streaming progress (SSE):

```bash
curl -N -X POST http://127.0.0.1:8000/api/investigations/stream \
  -H 'Content-Type: application/json' \
  -d '{"payment_id":"PAY-1001"}'
```

## 3. What the agent does

1. **`get_payment`** — confirms `FAILED` and `R01`
2. Optional **`get_payment_events`** / **`search_logs`** — timeline and gateway messages
3. **`search_payment_docs`** — retrieves ACH / retry guidance (RAG over `docs/`)
4. **RCA** — structured JSON: root cause, evidence, sources, recommendation

## 4. Example response (stub LLM)

```json
{
  "payment_id": "PAY-1001",
  "question": "Why did this payment fail?",
  "root_cause": "Insufficient funds",
  "confidence": "high",
  "evidence": [
    "Gateway returned error code R01",
    "Payment status is FAILED"
  ],
  "recommendation": "Do not retry immediately; notify the customer to fund the account.",
  "sources": ["ach-error-codes.md"],
  "steps": [
    {
      "tool": "get_payment",
      "arguments": { "payment_id": "PAY-1001" },
      "result": {
        "status": "FAILED",
        "error_code": "R01",
        "amount": "2450.00",
        "gateway": "ExamplePay"
      }
    }
  ],
  "model": "stub",
  "provider": "stub",
  "insufficient_evidence": false
}
```

## 5. Operator takeaway

| Item | Value |
| --- | --- |
| **Root cause** | Insufficient funds (ACH R01) |
| **Source** | `ach-error-codes.md` |
| **Recommendation** | Do not retry immediately; customer should fund the account |

Other seeded scenarios: **PAY-1002** (gateway timeout), **PAY-1003** (application error before gateway). See `docs/payment-processing.md` failure patterns table.
