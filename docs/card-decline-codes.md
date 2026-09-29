# Card decline codes

Card payments through **ExamplePay** return ISO-style decline codes in `error_code` or gateway metadata.

| Code | Meaning | Retry? |
|------|---------|--------|
| `insufficient_funds` | Not enough balance or credit | Sometimes, after 24h |
| `do_not_honor` | Generic bank decline | No immediate retry |
| `expired_card` | Card past expiration | No — update card |
| `incorrect_cvc` | CVC mismatch | Yes, after customer fixes |
| `lost_card` / `stolen_card` | Pickup / fraud flags | Never retry |
| `processing_error` | Transient issuer error | Yes, with backoff |

## Soft vs hard declines

**Soft declines** may succeed on retry (issuer timeout, temporary limit). **Hard declines** need a new payment method or customer contact.

## Matching logs

Search logs for `decline`, `issuer response`, or the raw code string. Cross-check `GATEWAY_RESPONSE` events for the canonical code.
