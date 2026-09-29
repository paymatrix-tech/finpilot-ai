# Payment processing lifecycle

Standard flow for ACH and card payments in the FinPilot demo stack.

## States

```text
CREATED → VALIDATED → SUBMITTED → (SUCCESS | FAILED)
```

Optional: `PROCESSING` while awaiting gateway callback.

## Events (typical order)

1. `PAYMENT_CREATED` — record inserted, amount and method captured.
2. `VALIDATED` — risk and field validation passed.
3. `SUBMITTED` — outbound request sent to ExamplePay.
4. `GATEWAY_RESPONSE` — final or interim gateway outcome.

## Logs

- **payments-api** — validation, submission, gateway I/O.
- **webhooks-worker** — asynchronous status updates (if enabled).

When investigating, always correlate **payment row**, **events**, and **logs** for the same `payment_id`.

## Failure patterns in seed data

| Payment ID | Pattern |
|------------|---------|
| PAY-1001 | ACH R01 insufficient funds |
| PAY-1002 | Gateway timeout |
| PAY-1003 | Application error before gateway |
| PAY-1004–PAY-1018 | Gateway outage cluster |

Use tools to fetch payment, events, and targeted log search rather than assuming the pattern from ID alone.
