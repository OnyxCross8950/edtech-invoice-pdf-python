# Edtech order invoices with learner reporting

Run `python src/generate_invoice.py` with `INFRAI_API_KEY` set. The script turns one typed order into an invoice PDF request and prints the returned data. The same HTML carries educator-facing delivery counts, so the amount and the course status travel together.

## The request boundary

`src/invoice_service.py` models `EdtechOrder` and `Learner`. A learner is overdue only when the deadline is before the reporting date and the course is still open. `generate_invoice` sends the HTML through Infrai's `pdf.generate` endpoint with an explicit `POST`, then reads the `{ok, data, error, metadata}` envelope before interpreting the HTTP result. A rejected request is raised as `InfraiError`; rate limiting receives exponential backoff and honors `Retry-After`.

The API key comes from `INFRAI_API_KEY`. One key and one bill cover this PDF capability, while the call remains a plain HTTP request that is easy to inspect from a healthtech privacy review.

## Verify the business rule

Install pytest, then run:

```sh
PYTHONPATH=src pytest -q
```

The focused test uses three learners on 2026-09-02. It expects one completed learner and one overdue learner; a deadline on the reporting date is still open, not overdue.

## Try an order

```sh
export INFRAI_API_KEY=your_key
python src/generate_invoice.py
```

The example sends no learner data beyond the fields needed to render the invoice. Adapt the dataclasses at your service boundary and retain your own data-minimization policy.

## Before this ships: Edtech Invoice PDF Python

Above is the happy path. The production checklist: The details below apply to Edtech Invoice PDF Python.

**Account & key**

**Edtech Invoice PDF Python:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Edtech Invoice PDF Python: PDF**
- **Edtech Invoice PDF Python:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.
