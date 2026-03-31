# BLUEPRINT-004 — Payment Integration

**Goal**: Checkout + webhook xử lý idempotent, support one-time hoặc subscription, có audit trail.

---

## When to use

- Thanh toán one-time
- Subscription (SaaS)
- Billing/invoice + webhooks

---

## Provider assumptions

This blueprint assumes Stripe-like providers:
- Checkout Session (redirect)
- Webhooks (signed)
- Subscription objects

You can adapt to other providers by swapping SDK + webhook semantics.

---

## Core principles

- **Idempotency everywhere**:
  - Client create-checkout must accept idempotency key
  - Webhook handler must dedupe events by `eventId`
- **Never trust client “paid = true”**:
  - Payment status is driven by provider webhooks
- **Store raw webhook payload** (for audit/debug)

---

## Data model (minimum)

```yaml
Payment:
  id: uuid
  userId: uuid
  tenantId: uuid?
  provider: stripe
  providerPaymentIntentId: string?
  providerCheckoutSessionId: string?
  amount: number
  currency: string
  status: created|pending|succeeded|failed|refunded
  idempotencyKey: string
  createdAt: datetime
  updatedAt: datetime

WebhookEvent:
  id: uuid
  provider: stripe
  providerEventId: string (unique)
  type: string
  receivedAt: datetime
  payloadJson: json
  processedAt: datetime?
  processStatus: ok|failed
  error: string?

Subscription (if needed):
  id: uuid
  userId: uuid
  providerSubscriptionId: string (unique)
  planId: string
  status: active|past_due|canceled
  currentPeriodEnd: datetime
```

---

## API contract (REST)

- `POST /payments/checkout`
  - input: `{ items, successUrl, cancelUrl, idempotencyKey }`
  - output: `{ checkoutUrl }`
- `POST /payments/webhook` (provider calls)
- `GET /billing/portal` (optional)

---

## Checkout flow

1) Client calls `POST /payments/checkout` with `idempotencyKey`
2) Server creates checkout session via provider SDK
3) Server persists `Payment(status=pending)` linked to session
4) Client redirects to provider
5) Provider sends webhook events
6) Server webhook updates Payment/Subscription status

---

## Webhook handling (must-have)

Checklist:
- Verify signature using provider secret
- Parse event
- Dedupe by `providerEventId` (unique index)
- Process in transaction:
  - Insert `WebhookEvent` first
  - Update local `Payment`/`Subscription`
  - Mark processed

Idempotency rules:
- If event already exists → return 200 OK (no reprocessing)

Failure strategy:
- If processing fails → store error, return 500 to trigger provider retry

---

## Security & compliance notes

- Secrets: store webhook secret in secret manager (not in repo)
- Do not log full card/customer PII
- Consider audit-log entries for payment status transitions

---

## Tests (minimum)

- create checkout happy path
- create checkout idempotency: same key returns same session
- webhook signature invalid → 400
- webhook dedupe: same eventId twice → process once
- webhook updates status: `succeeded`, `failed`, `refunded`
