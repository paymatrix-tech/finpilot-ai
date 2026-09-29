# ExamplePay gateway runbook

**Gateway name in data:** `ExamplePay`  
**Environments:** production uses `api.examplepay.com`; sandbox uses `sandbox.examplepay.com`.

## Timeout

**Symptoms:** Payment stuck in `PROCESSING`, logs show `read timeout` or `connection reset`.  
**Events:** May lack `GATEWAY_RESPONSE` or show `TIMEOUT` status.  
**Action:** Follow retry policy for timeouts; if outage window matches known incident, pause retries.

## Gateway rejection

**Symptoms:** `GATEWAY_RESPONSE` with `DECLINED` or `FAILED` and an `error_code`.  
**Action:** Map code using ACH or card decline docs; do not retry hard declines.

## Gateway unavailable

**Symptoms:** HTTP 503, `service_unavailable`, elevated error rate across many payments (see `PAY-1004`–`PAY-1018` style bursts).  
**Action:** Enable circuit breaker, notify status page, drain queue; no customer-visible retries until health checks pass.

## Response mapping

| Gateway field | Stored as |
|---------------|-----------|
| `decline_code` / ACH return | `payments.error_code` |
| `status` | Event `status` on `GATEWAY_RESPONSE` |
| Raw JSON | `metadata` on `GATEWAY_RESPONSE` event |

## Escalation

Page payments-oncall if error rate > 5% for 10 minutes or if reconciliation lag exceeds 30 minutes.
