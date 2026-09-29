# Timeout handling

Timeouts occur when ExamplePay does not return within the configured client deadline (default **30 seconds**).

## Detection

- Log messages containing `timeout`, `deadline exceeded`, or `read timed out`.
- Missing `GATEWAY_RESPONSE` within 2 minutes of `SUBMITTED`.
- Payment `status` may remain `PROCESSING` until reconciliation job runs.

## Reconciliation

A background job (`reconciliation-worker`) polls gateway status for stale `PROCESSING` payments:

- After **15 minutes**, first poll.
- After **1 hour**, mark **FAILED** if still unknown unless gateway confirms success.

## Customer messaging

Do not tell the customer the payment succeeded until `GATEWAY_RESPONSE` or reconciliation confirms **SUCCESS**.

## Retry

See **retry-policy.md** — gateway timeouts are retryable up to 3 times with backoff unless an active outage is declared in **gateway-runbook.md**.
