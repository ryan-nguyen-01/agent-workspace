# Service: {{SERVICE_NAME}}

> Per-service brain. Fill bởi onboarding, update bởi context-keeper sau mỗi task.

## Metadata

- **Name:** {{service-name}}
- **Scope (path):** `{{working-dir}}`
- **Purpose:** {{1-2 câu}}
- **Owner agent:** {{agent-coder-project-service-tech}} (fill by builder)
- **Last synced:** {{ISO timestamp}}

## Tech stack

- Language: {{language}}
- Framework: {{framework}}
- Database: {{database}}
- ORM: {{orm}}
- Other: {{queue, cache, auth, ...}}

## Architecture within service

```
{{path}}
├── controllers/     (entry points: HTTP routes)
├── services/        (business logic)
├── repositories/    (data access)
└── ...
```

Pattern: {{layered | feature | clean | hexagonal}}

## API endpoints

| Method | Path | Handler | Auth | Purpose |
|--------|------|---------|------|---------|
| GET | /api/v1/... | ... | JWT | ... |
| POST | /api/v1/... | ... | Public | ... |

N/A nếu service không expose HTTP.

## Events (emitted / consumed)

**Emitted:**
- `{{event_name}}` — khi X xảy ra, payload `{...}`

**Consumed:**
- `{{event_name}}` — xử lý bởi `{{handler}}`

## Schema (database)

Tables / collections / entities owned by this service:

- `{{table_name}}`
  - columns: id, ...
  - relations: ...

## Dependencies

**External packages (critical):**
- `package-name@version` — purpose

**Internal (other services called into):**
- `{{other-service}}` — via {{HTTP / event / shared DB}}

## Common patterns in this service

- {{pattern 1 — ref to conventions.md}}
- {{pattern 2 specific to service}}

## Known tech debt

- {{debt 1}}
- {{debt 2}}

---

## Change log (service-level)

| Date | Task | Change |
|------|------|--------|
| {{date}} | TASK-... | +POST /api/v1/refund |
| {{date}} | TASK-... | schema: add `refund_id` column |
