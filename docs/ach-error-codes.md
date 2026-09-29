# ACH return codes (NACHA)

Use these codes when interpreting **ExamplePay** ACH failures. Map gateway `error_code` to customer-facing guidance.

| Code | Meaning | Typical cause |
|------|---------|----------------|
| R01 | Insufficient funds | Available balance lower than debit amount |
| R02 | Account closed | Bank account no longer active |
| R03 | No account / unable to locate | Routing or account number mismatch |
| R04 | Invalid account number | Account number failed validation at RDFI |
| R05 | Unauthorized debit | Customer revoked authorization |
| R07 | Authorization revoked | Stop payment or revocation on file |
| R08 | Payment stopped | Stop order on this debit |
| R10 | Customer advises not authorized | Dispute initiated by account holder |

## Investigation hints

- **R01** — Confirm amount and retry policy; do not treat as an application bug unless validation skipped limits.
- **R02–R04** — Verify customer bank details before any retry; update payment method if needed.
- **R05–R10** — Do not retry without customer action; escalate if repeat attempts occur.

## Sources

Internal payments team reference aligned with NACHA return reason codes (simplified for operations).
