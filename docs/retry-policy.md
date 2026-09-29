# Payment retry policy

FinPilot applies retries only when failure is **transient** and **customer impact** is acceptable.

## Retry allowed

| Scenario | Max attempts | Minimum wait |
|----------|--------------|--------------|
| Gateway timeout (HTTP 504 / read timeout) | 3 | 5 minutes, exponential backoff |
| `processing_error` (card) | 2 | 1 hour |
| Rate limit from gateway (429) | 3 | Per `Retry-After` header or 15 minutes |

Backoff: 5m → 15m → 45m (cap 2 hours between attempts).

## Do not retry

- ACH **R01** within 2 business days (same amount to same account).
- ACH **R02–R10** without updated bank details or authorization.
- Card **lost_card**, **stolen_card**, **fraud** flags.
- Payments already in terminal state **SUCCESS** or **REFUNDED**.
- Application validation errors (invalid amount, blocked customer).

## Operations

1. Check `status` and latest `GATEWAY_RESPONSE` event before scheduling retry.
2. Log each retry attempt with `retry_count` in metadata.
3. After max attempts, mark **FAILED** and surface recommendation to support.

## ExamplePay note

ExamplePay may return retry hints in response metadata (`retryable: true|false`). Prefer gateway hint over generic policy when present.
