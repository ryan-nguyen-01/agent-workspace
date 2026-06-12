---
id: "{{PROJECT_KEY}}-ERR-{{NNN}}"
title: "Error Code Catalog"
status: draft            # draft | approved
updated_at: "{{UPDATED_AT}}"
---

# Error Code Catalog

The single source of truth for error codes shared by backend and frontend. Backend returns these codes;
frontend maps them to user-facing messages/states. Keep codes stable; never reuse a retired code.

## Conventions

```text
- Code format: <DOMAIN>_<REASON> (e.g. AUTH_INVALID_CREDENTIALS, ORDER_NOT_FOUND).
- Every error has a stable code, an HTTP status, a category, a default message, and an i18n key.
- Backend response shape: { "error": { "code": "<CODE>", "message": "<safe message>", "details": {...} } }.
- Messages are user-safe (no stack traces, secrets, or internal identifiers).
```

## Catalog

| Code | HTTP | Category | Default message | i18n key | Retryable | When it occurs |
|------|------|----------|-----------------|----------|-----------|----------------|
| `AUTH_INVALID_CREDENTIALS` | 401 | auth | Invalid email or password | `errors.auth.invalid_credentials` | no | login with wrong credentials |
| `AUTH_FORBIDDEN` | 403 | auth | You do not have access | `errors.auth.forbidden` | no | missing permission |
| `VALIDATION_FAILED` | 422 | validation | Some fields are invalid | `errors.validation.failed` | no | request fails validation (details[] lists fields) |
| `RESOURCE_NOT_FOUND` | 404 | resource | Not found | `errors.resource.not_found` | no | entity id does not exist |
| `RATE_LIMITED` | 429 | throttle | Too many requests | `errors.throttle.rate_limited` | yes | rate limit hit |
| `INTERNAL_ERROR` | 500 | server | Something went wrong | `errors.server.internal` | yes | unhandled server error |

## Validation detail shape (for VALIDATION_FAILED)

```json
{ "error": { "code": "VALIDATION_FAILED", "message": "Some fields are invalid",
  "details": [ { "field": "email", "code": "INVALID_FORMAT" } ] } }
```

## Frontend mapping

```text
- Map each code -> i18n message + UI state (inline field error, toast, full-page error).
- Unknown/unhandled code -> generic INTERNAL_ERROR message; never show raw server text.
- Retryable codes may show a retry affordance.
```

## Ownership

```text
Backend (service coders) emit these codes; frontend renders them; coder-data/QC use them to test error
paths. Changes are reviewed (R-018 precedence) — this catalog is the contract for error handling.
```
