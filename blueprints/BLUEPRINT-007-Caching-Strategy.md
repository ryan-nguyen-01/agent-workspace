# BLUEPRINT-007 — Caching Strategy (Cache-aside)

**Goal**: Thiết kế cache an toàn (TTL, invalidation) cho read-heavy endpoints, tránh stale/poisoning.

---

## When to use

- Endpoint read-heavy, expensive queries
- Rate-limit external calls
- Reduce DB load

---

## Default pattern: Cache-aside

1) Read from cache  
2) Miss → query source of truth (DB/API)  
3) Write cache with TTL  

---

## Cache key design

```yaml
key:
  prefix: "app:v1"
  tenant: "{tenantId}"
  resource: "product"
  variant: "{id}|{hash(query)}"
ttl_seconds: 60
```

Avoid:
- keys without tenant scoping (multi-tenant leak)
- unbounded cardinality from raw query strings

---

## Invalidation strategies

- **Write-through invalidation**: on update/delete → delete keys
- **Tag-based invalidation** (if supported)
- **Short TTL + stale-while-revalidate** (optional)

---

## Failure modes

- Cache stampede → use singleflight/locking
- Hot key → shard or add local in-memory layer
- Poisoned cache → validate payload schema before write

---

## Tests (minimum)

- Cache hit returns same data
- Update invalidates cache
- Tenant scoping enforced in keys

