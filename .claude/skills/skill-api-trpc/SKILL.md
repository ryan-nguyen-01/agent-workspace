---
name: skill-api-trpc
description: Best practices tRPC — router design, input validation (Zod), auth context, error formatting, batching, client integration, testing, và production concerns.
---

# Skill: tRPC

## Khi nào dùng

- Fullstack TypeScript muốn type-safe API (no OpenAPI requirement)
- Monorepo với shared types giữa web + api

---

## Router design

- Group by domain: `auth`, `users`, `orders`, `billing`
- Keep procedures thin: validate → call service → return DTO
- Avoid leaking DB models directly

---

## Input validation

- Zod schemas for every procedure
- Normalize error response format
- Pagination schema: cursor/limit with cap

---

## Auth & context

- Build `ctx` with user/tenant
- Enforce authorization inside procedures or middleware
- Prevent IDOR: scope queries by `tenantId/userId`

---

## Errors

- Use `TRPCError` with correct codes
- Map to consistent client-friendly messages
- Hide internal details in production

---

## Client integration

- React Query integration (recommended)
- Batching enabled, but cap batch size
- SSR/Next.js: create server-side caller where appropriate

---

## Testing

- Unit test services
- Integration test routers with `createCaller`
- E2E via http adapter if needed

---

## Production concerns

- Observability: logging + tracing per procedure
- Rate limiting per user/procedure
- Input size limits

