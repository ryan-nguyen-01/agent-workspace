# BLUEPRINT-001 — CRUD Module

**Goal**: Tạo CRUD hoàn chỉnh cho 1 entity/resource với validation, pagination, error handling, tests, và doc ngắn.

---

## When to use

- Tạo module mới quản lý entity (Product, Order, Lesson, Course, …)
- Thêm CRUD endpoints cho service hiện có

---

## Inputs (customization)

```yaml
entity:
  singular: Product
  plural: Products
  route: /products
  id_type: uuid
fields:
  - { name: name, type: string, required: true, searchable: true }
  - { name: status, type: enum, required: true, filterable: true }
  - { name: createdAt, type: datetime, required: true, filterable: true }
relations:
  - { type: belongs_to, entity: Tenant, field: tenantId, required: true }
constraints:
  soft_delete: true
  unique:
    - [tenantId, name]
pagination:
  type: offset
  default_limit: 20
authz:
  required: true
  policy: owner_or_admin
```

---

## Output contract (recommended)

### List (paginated)

```json
{
  "data": [{ "...": "..." }],
  "meta": { "total": 123, "page": 1, "limit": 20, "totalPages": 7 }
}
```

### Errors (minimum)

- **400** validation error (field-level)
- **401** unauthenticated
- **403** forbidden (authz)
- **404** not found
- **409** conflict (unique)

---

## Steps

### Step 1 — Define data model

- Define DB schema/model
- Add indexes for query patterns
- Add unique constraints

### Step 2 — Define DTO / validation

- Create DTOs:
  - `Create<Entity>`
  - `Update<Entity>` (partial)
  - `Query<Entity>` (pagination + sort + filters)
- Decide how to validate:
  - **TS**: Zod / class-validator
  - **Python**: Pydantic
  - **Java**: Bean Validation

### Step 3 — Implement service layer

Minimum methods:
- `create(dto, actor)`
- `list(query, actor)`
- `getById(id, actor)`
- `update(id, dto, actor)`
- `delete(id, actor)` (soft/hard)

Rules:
- Scope queries by tenant/owner if applicable (avoid IDOR)
- Make list query safe: limit cap, stable ordering
- Use transactions for create/update if writing related records

### Step 4 — Implement API layer

Endpoints (REST):
- `POST   {route}`
- `GET    {route}`
- `GET    {route}/{id}`
- `PATCH  {route}/{id}`
- `DELETE {route}/{id}`

### Step 5 — Tests

Minimum test matrix:
- Create: happy + validation fail + conflict
- List: pagination + filter + authz scope
- Get: happy + not found + forbidden
- Update: happy + validation + not found + forbidden
- Delete: happy + not found + forbidden

### Step 6 — Docs (short)

- Add README snippet (endpoints + payload example)

---

## Reference skeletons

### NestJS + Prisma (TypeScript)

- Controller: map HTTP ↔ DTO ↔ service
- Service: use Prisma with scoped `where` clauses
- Query: `skip/take`, `orderBy`, filters, `count()`

### FastAPI + SQLAlchemy (Python)

- Router: dependency injection for auth/tenant
- Service/repo: query builder with limit cap
- Pydantic schemas for request/response

### Spring Boot (Java/Kotlin)

- Controller + Service + Repository
- Pageable + Specification (filters)
- @Valid DTOs

---

## Common pitfalls

- Missing authz scoping in `getById/update/delete` (IDOR)
- Unbounded `limit` causing load spikes
- Sorting by non-indexed fields on large tables
- Soft-delete not applied consistently (list/get)

