---
name: skill-arch-write-hld
description: Viết tài liệu HLD (High-Level Design) hoàn chỉnh: system overview, architecture diagram, component responsibilities, deployment view, security, scalability và integration points. Output là docs/hld.md sẵn sàng để dev team và stakeholder review.
---

# Skill: Write High-Level Design (HLD)

## Output: `docs/hld.md`

---

## Template HLD hoàn chỉnh

```markdown
# High-Level Design — [Project Name]

**Version:** 1.0
**Date:** YYYY-MM-DD
**Author:** Solution Architect
**Status:** Draft | Review | Approved

---

## 1. System Overview

### 1.1 Purpose
[Mô tả mục đích của hệ thống trong 2-3 câu.
Hệ thống giải quyết vấn đề gì, cho ai, theo cách nào.]

### 1.2 Scope
**In Scope:**
- [Capability 1]
- [Capability 2]

**Out of Scope (v1):**
- [Feature X — lý do defer]

### 1.3 Assumptions & Constraints
| # | Assumption / Constraint | Impact |
|---|------------------------|--------|
| A1 | Team size ≤ 5 engineers | Monolith over microservices |
| A2 | Budget: self-hosted | MinIO thay vì S3 |
| C1 | GDPR compliance required | PII encryption at rest |

---

## 2. Architecture Overview

### 2.1 Architecture Style
**Chosen:** [Modular Monolith / Microservices / Event-Driven]
**Rationale:** [1-2 câu lý do — xem ADR-001 để biết chi tiết trade-offs]

### 2.2 High-Level Diagram

\`\`\`mermaid
graph TD
    Client["Web Client\n(React)"]
    Mobile["Mobile Client\n(React Native)"]
    LB["Load Balancer\n(Nginx)"]
    API["API Server\n(NestJS)"]
    DB[("PostgreSQL")]
    Cache[("Redis")]
    Queue["Job Queue\n(BullMQ)"]
    Worker["Background Worker"]
    Storage["Object Storage\n(MinIO/S3)"]
    Email["Email Service\n(SendGrid)"]

    Client --> LB
    Mobile --> LB
    LB --> API
    API --> DB
    API --> Cache
    API --> Queue
    API --> Storage
    Queue --> Worker
    Worker --> DB
    Worker --> Email
    Worker --> Storage
\`\`\`

### 2.3 Component Responsibilities

| Component | Responsibility | Technology | Owner |
|-----------|---------------|------------|-------|
| Load Balancer | TLS termination, routing, rate limit | Nginx | DevOps |
| API Server | Business logic, auth, validation | NestJS + TypeScript | BE Team |
| Database | Persistent storage, ACID transactions | PostgreSQL 16 | BE Team |
| Cache | Session store, hot data, rate counters | Redis 7 | BE Team |
| Job Queue | Async processing, scheduled tasks | BullMQ | BE Team |
| Background Worker | Email, notifications, file processing | NestJS Worker | BE Team |
| Object Storage | File uploads, media assets | MinIO (S3-compatible) | DevOps |
| Web Client | User interface | React + TypeScript | FE Team |

---

## 3. Data Flow

### 3.1 Synchronous Request Flow
\`\`\`
Client → Nginx (SSL, rate limit) → API Server (auth middleware)
→ Controller (validation) → Service (business logic)
→ Repository (DB query) → Response
\`\`\`

### 3.2 Asynchronous Flow (Background Jobs)
\`\`\`
API Server → BullMQ (enqueue job)
→ Worker picks up → Process (retry on fail, max 3 attempts)
→ Update DB / Send notification
\`\`\`

### 3.3 File Upload Flow
\`\`\`
Client → API (request presigned URL)
→ API generates presigned PUT URL → Client
→ Client uploads directly to MinIO/S3
→ Client notifies API with objectKey
→ API verifies object exists → save to DB
\`\`\`

---

## 4. Module Breakdown (Modular Monolith)

| Module | Bounded Context | Exposed APIs | DB Tables |
|--------|----------------|--------------|-----------|
| AuthModule | Identity | /auth/* | users, sessions |
| UserModule | User Profile | /users/* | users, user_profiles |
| [DomainModule] | [Context] | /[domain]/* | [tables] |
| NotificationModule | Messaging | internal only | notifications |

> **Module boundary rule:** Modules communicate qua interfaces/events, không import trực tiếp internal services của nhau.

---

## 5. Security Architecture

### 5.1 Authentication & Authorization
- **Auth mechanism:** JWT (access token 15m + refresh token 7d)
- **Permission model:** RBAC — roles: `admin`, `editor`, `viewer`
- **Token storage:** HttpOnly cookie (no localStorage)

### 5.2 Transport Security
- TLS 1.3 trên tất cả connections
- HSTS header enabled
- Certificate auto-renewal (Let's Encrypt / ACM)

### 5.3 Data Security
- PII fields encrypted at rest (AES-256)
- Passwords: bcrypt (cost factor 12)
- Secrets: environment variables, không commit vào repo
- DB credentials: Vault / AWS Secrets Manager

### 5.4 API Security
- Rate limiting: 100 req/min per IP (unauthenticated), 1000/min (authenticated)
- Input validation: class-validator trên tất cả DTOs
- SQL injection: parameterized queries only (Prisma/TypeORM)
- CORS: whitelist allowed origins

---

## 6. Infrastructure & Deployment

### 6.1 Environments
| Environment | Purpose | Infrastructure |
|-------------|---------|----------------|
| Local | Development | Docker Compose |
| Staging | QA & Testing | [Cloud/VPS] |
| Production | Live | [Cloud/VPS + CDN] |

### 6.2 Deployment Architecture
\`\`\`mermaid
graph TD
    Internet --> CDN["CDN\n(CloudFlare)"]
    CDN --> LB["Load Balancer"]
    LB --> App1["App Instance 1"]
    LB --> App2["App Instance 2"]
    App1 --> DB[("PostgreSQL\nPrimary")]
    App2 --> DB
    DB --> DBReplica[("Read Replica")]
    App1 --> Cache[("Redis Cluster")]
    App2 --> Cache
\`\`\`

### 6.3 Containerization
- Tất cả services chạy trong Docker containers
- Multi-stage builds để giảm image size
- Non-root user trong container
- Health check endpoint: `GET /health`

### 6.4 CI/CD Pipeline
\`\`\`
Push → GitHub Actions → Lint + Test → Build Docker Image
→ Push to Registry → Deploy to Staging (auto)
→ Smoke test → Deploy to Production (manual approval)
\`\`\`

---

## 7. Scalability & Performance

### 7.1 Current Target (MVP)
- Concurrent users: ~[X] users
- Expected RPS: ~[Y] requests/second
- Data volume: ~[Z] GB/year

### 7.2 Scale Strategy
| Bottleneck | Strategy |
|-----------|---------|
| API Server | Horizontal scale (stateless — session in Redis) |
| Database reads | Read replicas + query caching |
| File storage | CDN in front of S3/MinIO |
| Background jobs | Add more Worker instances |

### 7.3 Performance Targets
- API response time: < 200ms at p95
- Page load: < 2s on 3G
- DB query time: < 50ms for hot paths

---

## 8. Observability

| Concern | Tool | What to monitor |
|---------|------|----------------|
| Logging | Pino + Loki | Request logs, error logs, slow queries |
| Metrics | Prometheus + Grafana | RPS, error rate, latency, queue depth |
| Tracing | OpenTelemetry + Tempo | Request traces across services |
| Alerting | Grafana Alerts | Error rate > 1%, p95 > 500ms, queue backlog |

---

## 9. Integration Points

| External System | Purpose | Protocol | Auth |
|----------------|---------|----------|------|
| SendGrid | Transactional email | HTTPS REST | API Key |
| [Payment Gateway] | Payment processing | HTTPS REST | API Key + Webhook |
| [OAuth Provider] | Social login | OAuth 2.0 | Client ID/Secret |

---

## 10. Open Architecture Questions

| # | Question | Impact | Decision needed by |
|---|----------|--------|-------------------|
| Q1 | Có cần multi-tenancy không? | Ảnh hưởng DB schema | Sprint 1 |
| Q2 | Realtime notifications hay polling? | WebSocket vs REST | Sprint 2 |

---

## 11. Related Documents
- Product Brief: `docs/product-brief.md`
- Domain Model: `docs/domain-model.md`
- API Design: `docs/api-design.md`
- ADRs: `docs/adr/`
```

---

## Checklist trước khi finalize HLD

```
[ ] Tất cả components có owner rõ ràng
[ ] Data flow cho use cases quan trọng nhất đã được vẽ
[ ] Security model được review
[ ] Scale strategy match với business target
[ ] Integration points có auth mechanism rõ ràng
[ ] Open questions được list ra (không để ngầm định)
[ ] ADR được tạo cho mọi quyết định không tự nhiên
```
