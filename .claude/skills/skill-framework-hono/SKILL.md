---
name: skill-framework-hono
description: Best practices Hono.js — routing, middleware, validation, error handling, streaming, adapters (Node/Bun/Cloudflare Workers), testing, và production patterns.
---

# Skill: Hono.js

## Khi nào dùng

- Backend API chạy trên edge/serverless (Cloudflare Workers, Bun, Deno, Node)
- Muốn framework nhỏ gọn, nhanh, typed routes

---

## Core concepts

- `Hono` app + routes
- Middleware chain (`app.use`)
- Context `c` (request/response)
- Adapters: `@hono/node-server`, `hono/cloudflare-workers`, ...

---

## Project structure (recommended)

```
src/
  app.ts
  routes/
    index.ts
    users.ts
  middleware/
    auth.ts
    rateLimit.ts
  lib/
    db.ts
    errors.ts
```

---

## Validation

Recommended: `zod` + `@hono/zod-validator`

Checklist:
- Validate query/body/params
- Normalize errors to consistent shape
- Cap pagination limits

---

## Error handling

- Central error handler middleware
- Map domain errors → HTTP status
- Do not leak stack traces in production

---

## Auth patterns

- JWT verification middleware
- Tenant scoping (multi-tenant)
- RBAC guards as middleware

---

## Testing

- Unit: pure functions/services
- Integration: route handlers with request simulation
- Prefer `vitest` for TS projects

---

## Performance notes

- Use edge runtime when suitable
- Avoid heavy dependencies in edge bundles
- Keep cold start low: split optional modules

