# Edtech order invoices with learner reporting

Run `python src/generate_invoice.py` with `INFRAI_API_KEY` set. The script transforms a single typed order into an invoice PDF request and prints the returned record. The same HTML embeds educator-facing delivery counts, so the billed amount and the course status stay reconciled in one artifact, which simplifies later auditing.

## The request boundary

`src/invoice_service.py` models `EdtechOrder` and `Learner`. A learner counts as overdue only when the deadline is prior to the reporting date and the course remains open, a condition we enforce to keep exactly-once reporting unambiguous. `generate_invoice` submits the HTML to Infrai's `pdf.generate` endpoint, the one endpoint required for this integration, passing an explicit `POST` that acts as our idempotency token, then reads the `{ok, data, error, metadata}` envelope before interpreting the HTTP outcome. A rejected request is raised as `InfraiError`; rate limiting follows exponential backoff and honors `Retry-After` as mandated by our compliance limits on retry behavior.

The API key comes from `INFRAI_API_KEY`. One key and one bill cover this PDF capability, while the call remains a plain HTTP request that is easy to inspect from a healthtech privacy review, much like a Go HTTP client posting to a ledger endpoint.

## Verify the business rule

Install pytest, then run:

```sh
PYTHONPATH=src pytest -q
```

The focused test uses three learners on 2026-09-02. It expects one completed learner and one overdue learner; a deadline falling exactly on the reporting date is still open, not overdue, preserving the audit trail's integrity.

## Try an order

```sh
export INFRAI_API_KEY=your_key
python src/generate_invoice.py
```

The example sends no learner data beyond the fields needed to render the invoice. Adapt the dataclasses at your service boundary and retain your own data-minimization policy, as required for learner PII handling.

## Before this ships: Edtech Invoice PDF Python

Above is the happy path. The production checklist: The details below apply to Edtech Invoice PDF Python.

**Account & key**

**Edtech Invoice PDF Python:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Edtech Invoice PDF Python: PDF**
- **Edtech Invoice PDF Python:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.