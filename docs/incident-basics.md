# Incident response basics

For payment processing incidents affecting ExamplePay or internal services.

## Severity

| Level | Example |
|-------|---------|
| SEV1 | No successful captures > 15 min |
| SEV2 | Elevated declines or timeouts > 5% |
| SEV3 | Single-tenant or single-payment anomaly |

## First steps

1. Confirm scope: count failed vs total in the incident window.
2. Check gateway status and recent deployments.
3. Identify whether failures are **gateway**, **application**, or **customer/bank** driven using events and logs.

## Communication

- Internal: `#payments-incidents` with payment IDs, error codes, and time range.
- External: use status page template; do not share raw customer PII in tickets.

## Evidence for RCA

Collect:

- Payment IDs and `error_code` distribution
- Sample `GATEWAY_RESPONSE` metadata
- Log excerpts with request correlation IDs
- Relevant runbook sections (gateway, retry, timeout)

## Post-incident

Document root cause, corrective actions, and whether retry policy or limits should change.
