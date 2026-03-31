---
name: skill-arch-audit-log
description: Best practices audit logging — immutable event log, who-did-what-when trail, GDPR compliance, data access tracking, change history, retention policies, và query patterns cho compliance reporting.
---

# Skill: Audit Logging

## Khi nào cần Audit Log

```yaml
MUST have:
  - "App xử lý dữ liệu nhạy cảm (PII, financial, medical)"
  - "Multi-tenant SaaS (tenant admin cần xem activity)"
  - "Compliance requirements (GDPR, SOC2, HIPAA, PCI-DSS)"
  - "Admin/operator actions (role changes, data deletion)"

SHOULD have:
  - "App > 1000 users (debugging, support investigation)"
  - "B2B SaaS (customers expect audit trail)"
  - "Internal tools (who approved what)"

Audit log ≠ Application log:
  application_log: "Technical events for debugging (errors, performance)"
  audit_log: "Business events for compliance (who changed what, when)"
```

---

## Audit Event Structure

```typescript
interface AuditEvent {
  // Identity
  id: string                    // unique event ID
  timestamp: string             // ISO 8601 UTC
  traceId?: string              // correlate with request trace

  // Who
  actor: {
    type: 'user' | 'system' | 'api_key' | 'service'
    id: string
    email?: string
    ip?: string
    userAgent?: string
  }

  // What
  action: string                // 'user.created', 'order.deleted', 'role.assigned'
  category: string              // 'auth', 'data', 'admin', 'system'
  outcome: 'success' | 'failure' | 'denied'

  // Where
  resource: {
    type: string                // 'User', 'Order', 'Setting'
    id: string
    tenantId?: string
  }

  // Context
  changes?: {
    field: string
    oldValue: any
    newValue: any
  }[]
  metadata?: Record<string, any>
  reason?: string               // for destructive actions
}
```

### Example Events

```json
{
  "id": "evt_abc123",
  "timestamp": "2026-03-30T10:15:30.000Z",
  "actor": {
    "type": "user",
    "id": "usr_456",
    "email": "admin@acme.com",
    "ip": "192.168.1.100"
  },
  "action": "user.role_changed",
  "category": "admin",
  "outcome": "success",
  "resource": { "type": "User", "id": "usr_789", "tenantId": "tenant_acme" },
  "changes": [
    { "field": "role", "oldValue": "member", "newValue": "admin" }
  ],
  "reason": "Promoted to admin per manager request"
}
```

```json
{
  "id": "evt_def456",
  "timestamp": "2026-03-30T10:20:00.000Z",
  "actor": { "type": "user", "id": "usr_999", "ip": "10.0.0.5" },
  "action": "auth.login_failed",
  "category": "auth",
  "outcome": "failure",
  "resource": { "type": "User", "id": "usr_999" },
  "metadata": { "reason": "invalid_password", "attempt": 3 }
}
```

---

## Data Model

```sql
-- Append-only audit log table
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  trace_id VARCHAR(64),

  -- Actor
  actor_type VARCHAR(20) NOT NULL,
  actor_id VARCHAR(100) NOT NULL,
  actor_email VARCHAR(255),
  actor_ip INET,
  actor_user_agent TEXT,

  -- Action
  action VARCHAR(100) NOT NULL,
  category VARCHAR(50) NOT NULL,
  outcome VARCHAR(20) NOT NULL DEFAULT 'success',

  -- Resource
  resource_type VARCHAR(50) NOT NULL,
  resource_id VARCHAR(100) NOT NULL,
  tenant_id UUID,

  -- Details
  changes JSONB,
  metadata JSONB,
  reason TEXT
);

-- CRITICAL: No UPDATE or DELETE on this table
-- Enforce via RLS or application permissions
REVOKE UPDATE, DELETE ON audit_logs FROM app_user;

-- Indexes for common queries
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_actor ON audit_logs(actor_id, timestamp DESC);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id, timestamp DESC);
CREATE INDEX idx_audit_tenant ON audit_logs(tenant_id, timestamp DESC);
CREATE INDEX idx_audit_action ON audit_logs(action, timestamp DESC);

-- Partitioning by month (for retention + performance)
CREATE TABLE audit_logs (
  -- same columns
) PARTITION BY RANGE (timestamp);

CREATE TABLE audit_logs_2026_01 PARTITION OF audit_logs
  FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
CREATE TABLE audit_logs_2026_02 PARTITION OF audit_logs
  FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
-- Auto-create partitions via pg_partman or cron
```

---

## Implementation

### Audit Service

```typescript
class AuditService {
  constructor(
    private readonly db: PrismaClient,
    private readonly queue: AuditQueue,  // async write for performance
  ) {}

  async log(event: Omit<AuditEvent, 'id' | 'timestamp'>): Promise<void> {
    const auditEvent: AuditEvent = {
      id: uuid(),
      timestamp: new Date().toISOString(),
      ...event,
    }

    // Async write — don't block business logic
    await this.queue.add(auditEvent)
  }

  // For critical events (auth, deletion) — sync write
  async logSync(event: Omit<AuditEvent, 'id' | 'timestamp'>): Promise<void> {
    await this.db.auditLog.create({
      data: {
        ...event,
        actor: event.actor as any,
        resource: event.resource as any,
      },
    })
  }
}
```

### Interceptor / Middleware Pattern

```typescript
// NestJS — automatic audit logging for mutations
@Injectable()
export class AuditInterceptor implements NestInterceptor {
  constructor(private readonly audit: AuditService) {}

  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const req = context.switchToHttp().getRequest()
    const method = req.method

    // Only audit mutations
    if (['GET', 'HEAD', 'OPTIONS'].includes(method)) return next.handle()

    const startTime = Date.now()

    return next.handle().pipe(
      tap(async (response) => {
        await this.audit.log({
          actor: {
            type: 'user',
            id: req.user?.id ?? 'anonymous',
            email: req.user?.email,
            ip: req.ip,
            userAgent: req.headers['user-agent'],
          },
          action: this.extractAction(req),
          category: 'data',
          outcome: 'success',
          resource: {
            type: this.extractResourceType(req),
            id: response?.id ?? req.params.id ?? 'unknown',
            tenantId: req.tenant?.id,
          },
          metadata: { duration: Date.now() - startTime },
        })
      }),
      catchError(async (error) => {
        await this.audit.log({
          actor: { type: 'user', id: req.user?.id ?? 'anonymous', ip: req.ip },
          action: this.extractAction(req),
          category: 'data',
          outcome: error.status === 403 ? 'denied' : 'failure',
          resource: { type: this.extractResourceType(req), id: req.params.id ?? 'unknown' },
          metadata: { error: error.message },
        })
        throw error
      }),
    )
  }

  private extractAction(req: Request): string {
    const resource = req.path.split('/')[2] // /api/users → users
    const method = req.method
    const actionMap = { POST: 'created', PUT: 'updated', PATCH: 'updated', DELETE: 'deleted' }
    return `${resource}.${actionMap[method] ?? method.toLowerCase()}`
  }
}
```

### Change Tracking

```typescript
// Track field-level changes for sensitive data
function trackChanges(
  oldEntity: Record<string, any>,
  newEntity: Record<string, any>,
  sensitiveFields: string[] = [],
): AuditEvent['changes'] {
  const changes: AuditEvent['changes'] = []

  for (const key of Object.keys(newEntity)) {
    if (oldEntity[key] !== newEntity[key]) {
      changes.push({
        field: key,
        oldValue: sensitiveFields.includes(key) ? '[REDACTED]' : oldEntity[key],
        newValue: sensitiveFields.includes(key) ? '[REDACTED]' : newEntity[key],
      })
    }
  }

  return changes.length > 0 ? changes : undefined
}

// Usage
async function updateUser(id: string, dto: UpdateUserDto) {
  const oldUser = await prisma.user.findUniqueOrThrow({ where: { id } })
  const updatedUser = await prisma.user.update({ where: { id }, data: dto })

  await audit.log({
    actor: currentActor(),
    action: 'user.updated',
    category: 'data',
    outcome: 'success',
    resource: { type: 'User', id },
    changes: trackChanges(oldUser, updatedUser, ['password', 'ssn']),
  })

  return updatedUser
}
```

---

## Events to Audit

```yaml
always_audit:
  auth:
    - "auth.login_success"
    - "auth.login_failed"
    - "auth.logout"
    - "auth.password_changed"
    - "auth.mfa_enabled"
    - "auth.mfa_disabled"
    - "auth.api_key_created"
    - "auth.api_key_revoked"

  admin:
    - "user.role_changed"
    - "user.suspended"
    - "user.deleted"
    - "tenant.settings_changed"
    - "billing.plan_changed"
    - "permission.granted"
    - "permission.revoked"

  data_sensitive:
    - "pii.accessed"           # someone viewed PII data
    - "pii.exported"           # data export
    - "pii.deleted"            # GDPR deletion
    - "payment.processed"
    - "payment.refunded"

  system:
    - "system.config_changed"
    - "system.maintenance_mode"
    - "system.data_migration"

optional_audit:
  - "resource.created"         # new order, new product
  - "resource.updated"         # any entity update
  - "resource.deleted"         # any entity deletion
  - "search.executed"          # who searched what (privacy concern)
```

---

## GDPR Compliance

```yaml
data_access_log:
  requirement: "Track who accessed personal data"
  implementation: |
    // Log when PII is viewed (not just modified)
    async function getUserProfile(id: string, requestor: Actor) {
      const user = await prisma.user.findUnique({ where: { id } })

      await audit.log({
        actor: requestor,
        action: 'pii.accessed',
        category: 'data',
        outcome: 'success',
        resource: { type: 'User', id },
        metadata: { fields: ['email', 'phone', 'address'] },
      })

      return user
    }

data_deletion_log:
  requirement: "Prove data was deleted within 30 days of request"
  implementation: |
    await audit.logSync({
      actor: { type: 'system', id: 'gdpr-processor' },
      action: 'pii.deleted',
      category: 'admin',
      outcome: 'success',
      resource: { type: 'User', id: userId },
      metadata: {
        requestDate: deletionRequest.createdAt,
        completedDate: new Date(),
        tablesAffected: ['users', 'orders', 'comments', 'files'],
        rowsDeleted: { users: 1, orders: 15, comments: 42, files: 3 },
      },
      reason: 'GDPR Article 17 — Right to erasure',
    })

retention:
  audit_logs: "Keep for 7 years (SOC2, financial regulations)"
  application_logs: "Keep for 90 days"
  note: "Audit logs are EXEMPT from GDPR deletion — they're legal requirement"
  pii_in_audit: "Anonymize actor email after user deletion, keep actor_id"
```

---

## Query Patterns

```typescript
// Admin API — query audit logs
// GET /admin/audit-logs?actor=usr_456&action=user.*&from=2026-01-01&limit=50

class AuditQueryService {
  async search(filters: AuditFilters): Promise<PaginatedResult<AuditEvent>> {
    return this.db.auditLog.findMany({
      where: {
        ...(filters.actorId && { actorId: filters.actorId }),
        ...(filters.action && { action: { startsWith: filters.action.replace('*', '') } }),
        ...(filters.resourceType && { resourceType: filters.resourceType }),
        ...(filters.resourceId && { resourceId: filters.resourceId }),
        ...(filters.tenantId && { tenantId: filters.tenantId }),
        ...(filters.outcome && { outcome: filters.outcome }),
        timestamp: {
          gte: filters.from ?? subDays(new Date(), 30),
          lte: filters.to ?? new Date(),
        },
      },
      orderBy: { timestamp: 'desc' },
      take: filters.limit ?? 50,
      skip: filters.offset ?? 0,
    })
  }

  // Resource history — all changes to a specific entity
  async getResourceHistory(type: string, id: string) {
    return this.db.auditLog.findMany({
      where: { resourceType: type, resourceId: id },
      orderBy: { timestamp: 'desc' },
    })
  }

  // User activity — everything a user did
  async getUserActivity(userId: string, days: number = 30) {
    return this.db.auditLog.findMany({
      where: {
        actorId: userId,
        timestamp: { gte: subDays(new Date(), days) },
      },
      orderBy: { timestamp: 'desc' },
    })
  }
}
```

---

## Retention & Archival

```yaml
retention_policy:
  hot_storage: "Last 90 days in primary DB (fast queries)"
  warm_storage: "90 days - 1 year in read replica or archive table"
  cold_storage: "1-7 years in S3/Glacier (compliance)"
  deletion: "After retention period expires"

implementation:
  partition_drop: |
    -- Drop partitions older than retention period
    DROP TABLE IF EXISTS audit_logs_2024_01;

  archive_to_s3: |
    -- Export old partitions to S3 as Parquet
    -- Queryable via Athena/BigQuery if needed
    COPY (SELECT * FROM audit_logs_2025_q1) TO 's3://audit-archive/2025-q1.parquet'
```

---

## Anti-patterns

```yaml
mutable_audit_log:
  bad: "UPDATE audit_logs SET outcome = 'success' WHERE id = ..."
  fix: "REVOKE UPDATE/DELETE. Audit logs are append-only."

audit_in_transaction:
  bad: "Business logic + audit write in same transaction → rollback loses audit"
  fix: "Write audit async (queue) or in separate transaction"

pii_in_plain_text:
  bad: "Audit log stores full SSN, credit card number"
  fix: "Redact sensitive fields. Store references, not values."

no_retention:
  bad: "Audit table grows to 500GB, never archived"
  fix: "Partition by month, archive to cold storage, drop old partitions"

audit_everything:
  bad: "Log every GET request → 100x more audit data than useful"
  fix: "Audit mutations + sensitive reads. Not every page view."
```
