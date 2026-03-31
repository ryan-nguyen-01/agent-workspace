---
name: skill-arch-multi-tenancy
description: Best practices multi-tenancy cho SaaS — tenant isolation strategies (shared DB, schema-per-tenant, DB-per-tenant), Row-Level Security, tenant routing, noisy-neighbor prevention, tenant-aware caching/rate-limiting, và data migration.
---

# Skill: Multi-Tenancy Architecture

## Isolation Strategies

```
┌──────────────────┬──────────────────┬──────────────────┬──────────────────┐
│                  │ Shared DB +      │ Schema per       │ Database per     │
│                  │ Shared Schema    │ Tenant           │ Tenant           │
├──────────────────┼──────────────────┼──────────────────┼──────────────────┤
│ Isolation        │ Low (RLS)        │ Medium           │ High             │
│ Cost             │ Lowest           │ Medium           │ Highest          │
│ Complexity       │ Low              │ Medium           │ High             │
│ Max tenants      │ 10K+             │ ~1000            │ ~100             │
│ Data migration   │ Easy             │ Medium           │ Hard             │
│ Compliance       │ Harder (shared)  │ Good             │ Best (isolated)  │
│ Noisy neighbor   │ Risk (shared)    │ Lower            │ None             │
│ Backup/restore   │ All or nothing   │ Per schema       │ Per tenant       │
├──────────────────┼──────────────────┼──────────────────┼──────────────────┤
│ Best for         │ B2C SaaS,        │ Mid-market SaaS, │ Enterprise,      │
│                  │ many small       │ moderate data     │ regulated        │
│                  │ tenants          │ isolation need    │ industries       │
└──────────────────┴──────────────────┴──────────────────┴──────────────────┘
```

### Decision Guide

```yaml
choose_shared_db_shared_schema:
  when:
    - "B2C SaaS (nhiều tenants nhỏ: 100-10K+ orgs)"
    - "Data isolation qua RLS là đủ"
    - "Muốn đơn giản hoá ops (1 DB, 1 migration)"
  examples: "Slack, Notion, Linear, Todoist"

choose_schema_per_tenant:
  when:
    - "Mid-market SaaS (100-1000 tenants)"
    - "Tenant cần custom schema (thêm fields riêng)"
    - "Compliance yêu cầu logical isolation"
  examples: "Salesforce, HubSpot (hybrid)"

choose_db_per_tenant:
  when:
    - "Enterprise SaaS (< 100 tenants)"
    - "Regulation yêu cầu physical isolation (healthcare, finance)"
    - "Tenant trả tiền nhiều, yêu cầu dedicated resources"
  examples: "AWS accounts per customer, dedicated instances"
```

---

## Shared DB + RLS (Recommended cho hầu hết SaaS)

### Tenant Column

```sql
-- Mọi table có tenant_id
CREATE TABLE orders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id),
  customer_name VARCHAR(255) NOT NULL,
  total_amount DECIMAL(12,2) NOT NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'pending',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_orders_tenant ON orders(tenant_id);
CREATE INDEX idx_orders_tenant_status ON orders(tenant_id, status);
```

### PostgreSQL Row-Level Security

```sql
-- Enable RLS
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- Policy: tenant chỉ thấy data của mình
CREATE POLICY tenant_isolation ON orders
  USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

-- Force RLS cho app user (bypass cho admin)
ALTER TABLE orders FORCE ROW LEVEL SECURITY;

-- App sets tenant context per request
SET app.current_tenant_id = 'tenant-uuid-here';
SELECT * FROM orders; -- chỉ trả về orders của tenant đó
```

### Application-Level Implementation

```typescript
// Middleware: extract tenant from request
@Injectable()
export class TenantMiddleware implements NestMiddleware {
  constructor(private readonly tenantService: TenantService) {}

  async use(req: Request, res: Response, next: NextFunction) {
    const tenantId = this.extractTenantId(req)
    if (!tenantId) throw new UnauthorizedException('Tenant not identified')

    const tenant = await this.tenantService.findById(tenantId)
    if (!tenant || !tenant.isActive) throw new ForbiddenException('Tenant suspended')

    req.tenant = tenant
    next()
  }

  private extractTenantId(req: Request): string | null {
    // Strategy 1: Subdomain — acme.myapp.com
    const host = req.hostname
    const subdomain = host.split('.')[0]
    if (subdomain !== 'www' && subdomain !== 'app') {
      return this.tenantService.findBySlug(subdomain)?.id
    }

    // Strategy 2: Header — X-Tenant-ID
    return req.headers['x-tenant-id'] as string

    // Strategy 3: JWT claim — tenant_id in token payload
    // return req.user?.tenantId
  }
}

// Prisma extension: auto-filter by tenant
const prismaWithTenant = prisma.$extends({
  query: {
    $allOperations({ args, query, operation, model }) {
      if (['findMany', 'findFirst', 'count', 'aggregate'].includes(operation)) {
        args.where = { ...args.where, tenantId: currentTenantId }
      }
      if (['create', 'createMany'].includes(operation)) {
        if (Array.isArray(args.data)) {
          args.data = args.data.map(d => ({ ...d, tenantId: currentTenantId }))
        } else {
          args.data = { ...args.data, tenantId: currentTenantId }
        }
      }
      return query(args)
    },
  },
})
```

```python
# SQLAlchemy — tenant filter mixin
class TenantMixin:
    tenant_id = Column(UUID, ForeignKey('tenants.id'), nullable=False, index=True)

class Order(Base, TenantMixin):
    __tablename__ = 'orders'
    id = Column(UUID, primary_key=True, default=uuid4)
    customer_name = Column(String(255), nullable=False)

# Query filter — auto-applied
class TenantQuery(Query):
    def get(self, ident):
        obj = super().get(ident)
        if obj and hasattr(obj, 'tenant_id') and obj.tenant_id != g.tenant_id:
            return None
        return obj

    def __iter__(self):
        return super().filter_by(tenant_id=g.tenant_id).__iter__()
```

---

## Tenant Routing

```yaml
strategies:
  subdomain:
    pattern: "{tenant}.myapp.com"
    pros: "Clean URL, easy CDN routing"
    cons: "SSL wildcard cert needed, DNS setup per tenant"
    implementation: |
      // Nginx
      server {
        server_name ~^(?<tenant>.+)\.myapp\.com$;
        location / {
          proxy_set_header X-Tenant-Slug $tenant;
          proxy_pass http://app;
        }
      }

  path_prefix:
    pattern: "myapp.com/t/{tenant}/..."
    pros: "Simple, single domain, no DNS"
    cons: "Less clean URLs"

  header:
    pattern: "X-Tenant-ID: {uuid}"
    pros: "API-friendly, no URL changes"
    cons: "Not visible in browser, needs client setup"

  jwt_claim:
    pattern: "token.tenant_id"
    pros: "No extra header, tied to auth"
    cons: "Can't switch tenant without new token"

recommendation:
  web_app: "subdomain (best UX)"
  api: "JWT claim + header fallback"
  internal: "header"
```

---

## Noisy Neighbor Prevention

```yaml
problem: "1 tenant runs heavy queries → all tenants slow down"

solutions:
  rate_limiting_per_tenant:
    implementation: |
      // Redis — per-tenant rate limit
      const key = `rate:${tenantId}:${endpoint}`
      const limit = tenant.plan === 'enterprise' ? 1000 : 100 // per minute
      const current = await redis.incr(key)
      if (current === 1) await redis.expire(key, 60)
      if (current > limit) throw new TooManyRequestsException()

  resource_quotas:
    storage: "Max 10GB per tenant (free), 100GB (pro)"
    api_calls: "1000/min (free), 10000/min (pro)"
    seats: "5 users (free), unlimited (enterprise)"
    implementation: |
      // Check quota before resource-intensive operations
      async function checkStorageQuota(tenantId: string, fileSize: number) {
        const usage = await getStorageUsage(tenantId)
        const limit = await getTenantLimit(tenantId, 'storage')
        if (usage + fileSize > limit) {
          throw new QuotaExceededException('Storage limit reached. Upgrade plan.')
        }
      }

  query_timeout_per_tenant:
    implementation: |
      -- PostgreSQL: statement timeout per session
      SET statement_timeout = '5s';  -- free tier
      SET statement_timeout = '30s'; -- enterprise tier

  connection_pool_per_tier:
    free: "Shared pool, max 2 connections per tenant"
    pro: "Shared pool, max 10 connections"
    enterprise: "Dedicated pool, 50 connections"

  background_job_priority:
    free: "Low priority queue"
    pro: "Normal priority"
    enterprise: "High priority + dedicated workers"
```

---

## Tenant-Aware Caching

```typescript
// Cache key PHẢI include tenant_id
// ❌ Cache pollution — tenant A sees tenant B's data
const cacheKey = `users:list`

// ✅ Tenant-scoped cache
const cacheKey = `tenant:${tenantId}:users:list`

// Cache invalidation per tenant
async function invalidateTenantCache(tenantId: string, pattern: string) {
  const keys = await redis.keys(`tenant:${tenantId}:${pattern}`)
  if (keys.length > 0) await redis.del(...keys)
}

// Tenant-specific TTL (enterprise gets longer cache)
function getCacheTTL(tenant: Tenant): number {
  switch (tenant.plan) {
    case 'enterprise': return 3600  // 1 hour
    case 'pro': return 600          // 10 min
    default: return 120             // 2 min
  }
}
```

---

## Tenant Lifecycle

```yaml
provisioning:
  create_tenant:
    1. "Create tenant record"
    2. "Create default admin user"
    3. "Seed default data (settings, roles, permissions)"
    4. "Setup billing (Stripe customer)"
    5. "Send welcome email"

  onboarding:
    - "Setup wizard: company name, logo, timezone"
    - "Invite team members"
    - "Import existing data (CSV, API)"

suspension:
  trigger: "Payment failed 3x, ToS violation, manual"
  behavior:
    - "Block write operations (reads still allowed for data export)"
    - "Show banner: 'Account suspended. Contact support.'"
    - "Grace period: 30 days before data deletion"

deletion:
  soft_delete: "Mark tenant inactive, schedule hard delete after 90 days"
  hard_delete:
    - "Delete all tenant data from all tables"
    - "Delete uploaded files (S3)"
    - "Delete cache entries"
    - "Delete from search index"
    - "Audit log: retain for compliance (anonymized)"
  gdpr: "Must complete within 30 days of request"
```

---

## Anti-patterns

```yaml
missing_tenant_filter:
  bad: "SELECT * FROM orders WHERE status = 'pending' — no tenant filter"
  fix: "ALWAYS filter by tenant_id. Use RLS as safety net."

tenant_in_url_for_api:
  bad: "PATCH /tenants/123/users/456 — tenant in path but user belongs to different tenant"
  fix: "Derive tenant from auth token, not URL. URL tenant only for admin APIs."

shared_cache_keys:
  bad: "Cache key 'dashboard:stats' — shared across tenants"
  fix: "Always prefix: 'tenant:{id}:dashboard:stats'"

no_quota_enforcement:
  bad: "1 free tenant uploads 100GB, costs you $50/month in S3"
  fix: "Enforce quotas at every resource boundary"

cross_tenant_joins:
  bad: "JOIN orders o ON o.id = items.order_id — no tenant constraint on JOIN"
  fix: "JOIN must include tenant_id: ON o.id = items.order_id AND o.tenant_id = items.tenant_id"
```
