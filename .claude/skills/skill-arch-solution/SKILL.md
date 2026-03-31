---
name: skill-arch-solution
description: Thiết kế kiến trúc hệ thống high-level: chọn architecture style, vẽ component diagram, xác định data flow, infrastructure và viết Architecture Decision Records (ADR).
---

# Skill: Solution Architecture Design

## Chọn Architecture Style

```
Decision framework:

Team size ≤ 5, deadline gấp, domain chưa rõ?
→ Modular Monolith (default lựa chọn an toàn)

Cần scale độc lập từng service, team lớn (> 10)?
→ Microservices (chỉ khi thực sự cần — complexity cao)

CRUD app đơn giản, không có background jobs phức tạp?
→ Monolith

Realtime, event-driven, audit log quan trọng?
→ Event-Driven / CQRS

Mobile-first, nhiều client type?
→ API-first với BFF (Backend for Frontend) pattern
```

## High-Level Diagram (Mermaid)

```markdown
### Ví dụ — Modular Monolith

\`\`\`mermaid
graph TD
    Client[Web/Mobile Client]
    API[API Server\nNestJS]
    DB[(PostgreSQL)]
    Cache[(Redis)]
    Queue[BullMQ]
    Worker[Background Worker]
    Storage[S3/MinIO]

    Client -->|HTTPS| API
    API --> DB
    API --> Cache
    API --> Queue
    Queue --> Worker
    Worker --> DB
    Worker --> Storage
    API --> Storage
\`\`\`

### Ví dụ — Microservices

\`\`\`mermaid
graph TD
    Client --> Gateway[API Gateway]
    Gateway --> AuthSvc[Auth Service]
    Gateway --> UserSvc[User Service]
    Gateway --> OrderSvc[Order Service]
    OrderSvc --> Kafka[Kafka]
    Kafka --> NotifSvc[Notification Service]
    AuthSvc --> AuthDB[(Auth DB)]
    UserSvc --> UserDB[(User DB)]
    OrderSvc --> OrderDB[(Order DB)]
\`\`\`
```

## Component Breakdown Template

```markdown
| Component | Responsibility | Technology | Scale Strategy |
|-----------|---------------|------------|----------------|
| API Server | Handle HTTP requests, auth, validation | NestJS | Horizontal (stateless) |
| Database | Persistent storage | PostgreSQL | Read replicas |
| Cache | Session, hot data, rate limit counters | Redis | Cluster mode |
| Queue | Async jobs, emails, notifications | BullMQ | Multiple workers |
| Storage | File uploads, media | S3/MinIO | CDN in front |
| Search | Full-text search | Elasticsearch | Dedicated nodes |
```

## Data Flow Pattern

```markdown
### Request Flow (Synchronous)
1. Client → API Gateway (auth check, rate limit)
2. API Gateway → Service (validated request)
3. Service → Repository (DB query)
4. Service → Cache (read-through / write-through)
5. Service → Response

### Event Flow (Asynchronous)
1. Service publishes event to Queue
2. Queue delivers to Worker(s)
3. Worker processes (retry nếu fail)
4. Worker updates DB / sends notification

### File Upload Flow
1. Client requests presigned URL từ API
2. API generates presigned PUT URL → return to client
3. Client uploads directly to S3 (bypass API server)
4. Client notifies API with objectKey
5. API verifies + saves reference to DB
```

## ADR Template

```markdown
## ADR-[NNN]: [Tiêu đề quyết định]

**Date:** YYYY-MM-DD
**Status:** Proposed | Accepted | Deprecated | Superseded

### Context
[Bối cảnh — tại sao cần đưa ra quyết định này?
Constraints, requirements, hoặc vấn đề đang gặp phải.]

### Options Considered
1. **[Option A]** — [mô tả ngắn]
   - Pros: ...
   - Cons: ...

2. **[Option B]** — [mô tả ngắn]
   - Pros: ...
   - Cons: ...

### Decision
Chọn **[Option X]** vì [lý do chính].

### Rationale
[Giải thích chi tiết trade-offs đã cân nhắc.
Tại sao các options khác bị loại.]

### Consequences
**Tốt:**
- [Benefit 1]
- [Benefit 2]

**Xấu / Cần chú ý:**
- [Trade-off 1]
- [Mitigation plan]
```

## Infrastructure Checklist

```markdown
### Development
- [ ] Docker Compose cho local dev (DB, Redis, S3/MinIO)
- [ ] .env.example với tất cả required vars
- [ ] Makefile hoặc npm scripts cho common tasks

### Production
- [ ] Container orchestration (K8s / ECS / Fly.io)
- [ ] Managed DB với automated backups
- [ ] CDN cho static assets
- [ ] Secrets management (Vault / AWS Secrets Manager)
- [ ] Monitoring + alerting (Grafana / Datadog)
- [ ] Log aggregation (Loki / CloudWatch)
- [ ] Distributed tracing (Jaeger / Tempo)
```

## Anti-patterns

```
❌ Microservices khi team < 5 người — distributed system complexity không worth it
❌ Event sourcing cho mọi thứ — chỉ cần khi audit trail là core requirement
❌ Chọn tech theo hype — chọn theo team familiarity và use case fit
❌ Thiếu ADR — quyết định không có context → tech debt vô hình
❌ Over-architect MVP — start simple, refactor khi có data thực
```
