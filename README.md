# agent-platform

Multi-agent AI system hoạt động như một **công ty phần mềm hoàn chỉnh**. Từ ý tưởng thô đến production code, testing, security review, deployment và vận hành — tất cả được xử lý bởi 21 agents chuyên biệt với 127 skills.

---

## Kiến trúc hệ thống

```
User
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AGENT SYSTEM                               │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   ORCHESTRATOR                           │    │
│  │          Điều phối mọi agent, error handling             │    │
│  └──────────────────────┬──────────────────────────────────┘    │
│                         │                                        │
│    ┌────────┬───────────┼───────────┬──────────┬──────────┐     │
│    ▼        ▼           ▼           ▼          ▼          ▼     │
│ PRODUCT  ENGINEER    QUALITY    SECURITY    OPS       INFRA     │
│ 4 agents 6 agents   3 agents   1 agent    2 agents  5 agents   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    127 SKILLS                            │    │
│  │   Languages · Frameworks · DB · Auth · Testing · UI      │    │
│  │   Architecture · DevOps · Security · Observability       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌──────────┐  ┌──────────────┐                                  │
│  │ .agent/  │  │  Feedback    │                                  │
│  │ Context  │  │  Loop        │                                  │
│  └──────────┘  └──────────────┘                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Thống kê

| Metric               | Số lượng                                                                                   |
| -------------------- | ------------------------------------------------------------------------------------------ |
| Core agents          | 21                                                                                         |
| Skills               | 127                                                                                        |
| Generated agents     | Unlimited (per project)                                                                    |
| Departments          | 7                                                                                          |
| Supported languages  | 13 (TypeScript, Python, Java, Go, Rust, Kotlin, Swift, C#, PHP, Elixir, Ruby, Dart, Scala) |
| Supported frameworks | 27 (BE: 11, FE: 10, Mobile: 3, DB ORM: 3)                                                  |

---

## Cấu trúc thư mục

```
agent-platform/
├── CLAUDE.md                          ← Entry point (Claude đọc file này đầu tiên)
├── GUIDELINES.md                      ← Single source of truth (cách dùng + alias + semantics)
├── README.md                          ← file này
└── .claude/                           ← Agent/skill definitions (ship kèm repo)
    ├── agents/                        ← 20 core agent definitions
    │   ├── README.md                  ← handbook nội bộ
    │   ├── agent-orchestrator/SKILL.md
    │   ├── agent-sa/SKILL.md
    │   ├── agent-ba/SKILL.md
    │   ├── agent-builder/SKILL.md
    │   ├── agent-coder-*/             ← generated per project
    │   └── ... (20 agents)
    │
    └── skills/                        ← 106 skill definitions
        ├── skill-lang-typescript/SKILL.md
        ├── skill-framework-nestjs/SKILL.md
        ├── skill-arch-microservices/SKILL.md
        ├── skill-security-hardening/SKILL.md
        └── ... (106 skills)
```

Runtime context (tạo trong từng project khi dùng):

```
.agent/                                ← runtime context (thường không commit)
└── context/...
```

---

## Sơ đồ tổ chức (7 phòng ban)

```
                           ┌──────────────────┐
                           │  EXECUTIVE OFFICE │
                           │  orchestrator     │
                           │  reporter         │
                           └────────┬─────────┘
                                    │
    ┌──────────┬──────────┬─────────┼─────────┬──────────┬──────────┐
    ▼          ▼          ▼         ▼         ▼          ▼          ▼
┌────────┐┌────────┐┌─────────┐┌────────┐┌────────┐┌────────┐┌────────┐
│PRODUCT ││ENGINEER││ QUALITY ││SECURITY││  OPS   ││  DATA  ││INFRA   │
│        ││        ││         ││        ││        ││        ││        │
│discover││analyst ││ qa      ││security││ sre    ││ data   ││onboard │
│sa      ││designer││ tester  ││        ││devops* ││        ││builder │
│ba      ││coder-* ││ perf    ││        ││        ││        ││ctx-keep│
│pm      ││reviewer││         ││        ││        ││        ││        │
│        ││document││         ││        ││        ││        ││        │
│        ││migrator││         ││        ││        ││        ││        │
└────────┘└────────┘└─────────┘└────────┘└────────┘└────────┘└────────┘
```

---

## 21 Core Agents

### Product (ý tưởng → backlog)

| Agent               | Vai trò                                        | Skills chính                                                                                   |
| ------------------- | ---------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| **agent-discovery** | Phân tích vấn đề, thị trường, MVP scope        | problem-analysis, market-analysis, mvp-scope, risk-assessment                                  |
| **agent-sa**        | Thiết kế kiến trúc hệ thống, domain model, API | arch-solution, write-hld, domain-model, microservices, scalability, security, + 25 arch skills |
| **agent-ba**        | User stories, acceptance criteria, backlog     | write-user-stories, domain-model                                                               |
| **agent-pm**        | Roadmap, sprint planning, release management   | context-read, write-docs                                                                       |

### Engineering (design → code → review)

| Agent                | Vai trò                                                           | Skills chính                                            |
| -------------------- | ----------------------------------------------------------------- | ------------------------------------------------------- |
| **agent-analyst**    | Breakdown task phức tạp → subtasks atomic                         | breakdown-tasks                                         |
| **agent-designer**   | UI/UX: design tokens, wireframes, components (không có Figma URL) | ui-figma, ui-accessibility, ui-tailwind/shadcn/mui/antd |
| **agent-figma**      | Extract specs từ Figma URL; review UI thực vs Figma sau khi code  | ui-figma, role-ui-review, write-docs                    |
| **agent-coder-\***   | Viết production code (generated per project)                      | lang-_, framework-_, database-_, api-_, auth-\*         |
| **agent-reviewer**   | Review code: quality, conventions, correctness                    | code-review, security-hardening, feedback-loop          |
| **agent-documenter** | Cập nhật docs, API docs, changelog                                | write-docs, context-write                               |
| **agent-migrator**   | Migration, refactor lớn, version upgrade                          | database-migration, detect-stack, scan-project          |

### Quality & Reliability (test → release)

| Agent              | Vai trò                                              | Skills chính                                          |
| ------------------ | ---------------------------------------------------- | ----------------------------------------------------- |
| **agent-tester**   | Viết + chạy unit/integration/e2e tests               | testing-jest/vitest/pytest/junit/playwright, fixtures |
| **agent-qa**       | Test strategy, accessibility audit, release sign-off | ui-accessibility, testing-playwright                  |
| **agent-perf**     | Load testing, profiling, bundle analysis             | testing-load, arch-scalability                        |
| **agent-security** | OWASP review, threat model, dependency audit         | security-hardening, security-graphql, arch-security   |

### Operations (deploy → monitor → respond)

| Agent               | Vai trò                                    | Skills chính                                                                       |
| ------------------- | ------------------------------------------ | ---------------------------------------------------------------------------------- |
| **agent-sre**       | Monitoring, SLI/SLO, incident response, DR | arch-monitoring, arch-disaster-recovery, arch-finops                               |
| **agent-devops-\*** | Docker, CI/CD, K8s (generated per project) | devops-docker, devops-github-actions, devops-kubernetes, devops-container-security |

### Data

| Agent          | Vai trò                                      | Skills chính             |
| -------------- | -------------------------------------------- | ------------------------ |
| **agent-data** | Data pipelines, event taxonomy, data quality | context-read, write-docs |

### Infrastructure (internal — không tương tác trực tiếp với user)

| Agent                    | Vai trò                                       | Skills chính                              |
| ------------------------ | --------------------------------------------- | ----------------------------------------- |
| **agent-orchestrator**   | Entry point, điều phối, error handling, retry | inject-context, feedback-loop             |
| **agent-onboarding**     | Scan project, tạo .agent/ context             | scan-project, detect-stack, context-write |
| **agent-builder**        | Detect stack, tạo generated agents            | scan-project, detect-stack, context-write |
| **agent-context-keeper** | Sync .agent/ context khi code thay đổi        | context-sync-delta, context-write         |
| **agent-reporter**       | Báo cáo tiến độ, escalate blockers            | report-progress                           |

---

## 127 Skills (Full Catalog)

### Languages (13)

| Skill                   | Mô tả                                                           |
| ----------------------- | --------------------------------------------------------------- |
| `skill-lang-typescript` | TypeScript strict mode, generics, utility types                 |
| `skill-lang-python`     | Python typing, async, packaging                                 |
| `skill-lang-java`       | Java patterns, Stream API, records                              |
| `skill-lang-go`         | Go modules, goroutines, interfaces                              |
| `skill-lang-rust`       | Ownership, lifetimes, traits, error handling                    |
| `skill-lang-kotlin`     | Coroutines, sealed classes, data classes, null safety           |
| `skill-lang-swift`      | Optionals, actors, async/await, protocols                       |
| `skill-lang-csharp`     | Records, nullable, LINQ, .NET 8+ patterns                       |
| `skill-lang-php`        | PHP 8.3+, enums, fibers, match, readonly                        |
| `skill-lang-elixir`     | Pattern matching, GenServer, OTP, Ecto                          |
| `skill-lang-ruby`       | Blocks, mixins, Data.define, pattern matching                   |
| `skill-lang-dart`       | Null safety, streams, sealed classes                            |
| `skill-lang-scala`      | Case classes, Cats Effect, for-comprehensions, pattern matching |

### Backend Frameworks (11)

| Skill                         | Mô tả                                                        |
| ----------------------------- | ------------------------------------------------------------ |
| `skill-framework-nestjs`      | DI, modules, guards, pipes, interceptors                     |
| `skill-framework-express`     | Middleware, routing, error handling                          |
| `skill-framework-fastify`     | Plugins, schema validation, TypeBox, hooks                   |
| `skill-framework-elysia`      | Bun framework, Eden Treaty, lifecycle hooks                  |
| `skill-framework-fastapi`     | Pydantic, dependency injection, async                        |
| `skill-framework-django`      | ORM, views, serializers, admin                               |
| `skill-framework-spring-boot` | Beans, JPA, security, actuator                               |
| `skill-framework-gin`         | Handlers, middleware, binding                                |
| `skill-framework-fiber`       | Fast HTTP, middleware chain                                  |
| `skill-framework-axum`        | Rust Axum — routing, extractors, Tower middleware            |
| `skill-framework-encore`      | Built-in API/PubSub/Cron/Secrets/DB, type-safe service calls |

### Frontend Frameworks (10)

| Skill                            | Mô tả                                                  |
| -------------------------------- | ------------------------------------------------------ |
| `skill-framework-react`          | Hooks, Server Components, performance                  |
| `skill-framework-nextjs`         | App Router, Server Actions, ISR                        |
| `skill-framework-vuejs`          | Composition API, reactivity, composables               |
| `skill-framework-nuxtjs`         | Auto-imports, server routes, Nitro                     |
| `skill-framework-angular`        | Signals, standalone components, OnPush                 |
| `skill-framework-solidstart`     | SolidJS, routeLoader$, server functions, streaming SSR |
| `skill-framework-qwik`           | Resumability, routeAction$, QwikCity routing           |
| `skill-framework-tanstack-start` | TanStack Router, createServerFn, type-safe loaders     |
| `skill-framework-fresh`          | Deno Islands, file-based routing, zero build step      |
| `skill-framework-htmx`           | Hypermedia UI, hx-\* attributes, server-side patterns  |

### Mobile Frameworks (3)

| Skill                          | Mô tả                                               |
| ------------------------------ | --------------------------------------------------- |
| `skill-framework-react-native` | Expo Router, SecureStore, FlatList, OTA updates     |
| `skill-framework-expo`         | Expo Router, EAS Build, OTA updates, native modules |
| `skill-framework-flutter`      | Dart, Riverpod, GoRouter, platform channels         |

### Databases & ORM (10)

| Skill                          | Mô tả                                                                            |
| ------------------------------ | -------------------------------------------------------------------------------- |
| `skill-database-postgresql`    | Indexes, partitioning, CTEs, JSON                                                |
| `skill-database-mysql`         | InnoDB, replication, optimization                                                |
| `skill-database-mongodb`       | Aggregation, indexes, schema design                                              |
| `skill-database-redis`         | Data structures, pub/sub, Lua scripts                                            |
| `skill-database-elasticsearch` | Mappings, analyzers, aggregations                                                |
| `skill-database-turso`         | Edge SQLite (LibSQL), Drizzle integration, embedded replicas, Cloudflare Workers |
| `skill-database-prisma`        | Schema, migrations, relations, raw queries                                       |
| `skill-database-typeorm`       | Entities, repositories, query builder                                            |
| `skill-database-sqlalchemy`    | ORM, Core, Alembic integration                                                   |
| `skill-database-migration`     | Zero-downtime migrations, Flyway, Alembic, expand-contract                       |

### Auth & Security (6)

| Skill                             | Mô tả                                                      |
| --------------------------------- | ---------------------------------------------------------- |
| `skill-auth-jwt`                  | Token lifecycle, refresh rotation, HttpOnly cookies        |
| `skill-auth-oauth2`               | Authorization code, PKCE, social login                     |
| `skill-auth-rbac`                 | Permission-based access, guards, policies                  |
| `skill-security-hardening`        | OWASP Top 10, injection, IDOR, CSRF, SSRF, mass assignment |
| `skill-security-graphql`          | Query depth, complexity, introspection, persisted queries  |
| `skill-devops-container-security` | Image scanning, non-root, read-only FS, supply chain       |

### Testing (7)

| Skill                      | Mô tả                                       |
| -------------------------- | ------------------------------------------- |
| `skill-testing-jest`       | Mocking, snapshots, coverage                |
| `skill-testing-vitest`     | Fast unit tests, ESM support                |
| `skill-testing-pytest`     | Fixtures, parametrize, async                |
| `skill-testing-junit`      | Assertions, Mockito, Spring Test            |
| `skill-testing-playwright` | E2E, visual regression, a11y                |
| `skill-testing-load`       | k6, Artillery, smoke/load/stress/spike/soak |
| `skill-testing-fixtures`   | Factories, seeders, fake data, DB isolation |

### UI Libraries (6)

| Skill                    | Mô tả                                               |
| ------------------------ | --------------------------------------------------- |
| `skill-ui-tailwind`      | Design tokens, responsive, dark mode                |
| `skill-ui-shadcn`        | Component composition, theming                      |
| `skill-ui-mui`           | Material theming, sx patterns                       |
| `skill-ui-antd`          | Ant Design patterns, layout                         |
| `skill-ui-figma`         | Design-to-code, token extraction, component mapping |
| `skill-ui-accessibility` | WCAG 2.2, ARIA, keyboard nav, contrast              |

### Frontend (3)

| Skill                       | Mô tả                                                        |
| --------------------------- | ------------------------------------------------------------ |
| `skill-fe-state-management` | Redux Toolkit, Zustand, Pinia, TanStack Query                |
| `skill-fe-tanstack-query`   | useQuery, useMutation, queryOptions, optimistic updates, SSR |
| `skill-fe-i18n`             | i18next, vue-i18n, Intl API, RTL support                     |

### API Design (4)

| Skill               | Mô tả                                                 |
| ------------------- | ----------------------------------------------------- |
| `skill-api-rest`    | Resource design, pagination, versioning, error format |
| `skill-api-graphql` | Schema, resolvers, DataLoader, subscriptions          |
| `skill-api-grpc`    | Protobuf, streaming, interceptors, error codes        |
| `skill-api-openapi` | Contract-first, Swagger, SDK generation               |

### Message Queues (3)

| Skill                  | Mô tả                                 |
| ---------------------- | ------------------------------------- |
| `skill-queue-bullmq`   | Job queues, scheduling, rate limiting |
| `skill-queue-rabbitmq` | Exchanges, routing, dead letter       |
| `skill-queue-kafka`    | Topics, consumer groups, exactly-once |

### DevOps (4)

| Skill                             | Mô tả                                     |
| --------------------------------- | ----------------------------------------- |
| `skill-devops-docker`             | Multi-stage builds, compose, optimization |
| `skill-devops-github-actions`     | Workflows, matrix, caching, secrets       |
| `skill-devops-kubernetes`         | Deployments, services, ingress, HPA       |
| `skill-devops-container-security` | Trivy, non-root, resource limits, SBOM    |

### Observability (2)

| Skill                         | Mô tả                                       |
| ----------------------------- | ------------------------------------------- |
| `skill-observability-logging` | Structured logging, log levels, correlation |
| `skill-observability-tracing` | OpenTelemetry, distributed traces, spans    |

### Architecture (26)

| Skill                              | Mô tả                                                |
| ---------------------------------- | ---------------------------------------------------- |
| `skill-arch-solution`              | Architecture styles, trade-off analysis, ADR         |
| `skill-arch-write-hld`             | High-level design document                           |
| `skill-arch-domain-model`          | Bounded contexts, entities, ERD                      |
| `skill-arch-microservices`         | Service decomposition, Saga, resilience              |
| `skill-arch-event-driven`          | Event Sourcing, CQRS, choreography/orchestration     |
| `skill-arch-transactional`         | ACID, isolation levels, locking, outbox, idempotency |
| `skill-arch-multi-tenancy`         | SaaS isolation, RLS, tenant routing                  |
| `skill-arch-feature-flags`         | Gradual rollout, A/B testing, kill switch            |
| `skill-arch-notification`          | Multi-channel delivery, templates, digest            |
| `skill-arch-audit-log`             | Immutable logs, compliance trail, GDPR               |
| `skill-arch-background-jobs`       | Cron, scheduling, dedup, recurring tasks             |
| `skill-arch-email-delivery`        | DKIM/SPF/DMARC, bounce handling, warm-up             |
| `skill-arch-finops`                | Cloud cost optimization, right-sizing                |
| `skill-arch-disaster-recovery`     | RTO/RPO, backup, failover, DR runbooks               |
| `skill-arch-scalability`           | Load balancing, sharding, caching, CDN               |
| `skill-arch-distributed-systems`   | CAP theorem, consistency, distributed locks          |
| `skill-arch-security`              | Defense in depth, zero-trust, encryption, STRIDE     |
| `skill-arch-realtime`              | WebSocket scaling, pub/sub, push, SSE                |
| `skill-arch-search`                | Indexing pipeline, Elasticsearch, autocomplete       |
| `skill-arch-storage`               | Object storage, CDN, media processing, backup        |
| `skill-arch-monitoring`            | Prometheus, Grafana, SLI/SLO, alerting               |
| `skill-discovery-problem-analysis` | Problem framing, root cause                          |
| `skill-discovery-market-analysis`  | Competitor analysis, positioning                     |
| `skill-discovery-mvp-scope`        | Feature prioritization, MVP definition               |
| `skill-discovery-risk-assessment`  | Technical + business risk evaluation                 |

### Storage (1)

| Skill              | Mô tả                                    |
| ------------------ | ---------------------------------------- |
| `skill-storage-s3` | S3 operations, presigned URLs, lifecycle |

### Context Management (4)

| Skill                      | Mô tả                                   |
| -------------------------- | --------------------------------------- |
| `skill-context-read`       | Read .agent/ context efficiently        |
| `skill-context-write`      | Write/update .agent/ context            |
| `skill-context-compress`   | Compress docs into minimal YAML context |
| `skill-context-sync-delta` | Incremental context sync on changes     |

### Workflow & Quality (10)

| Skill                           | Mô tả                                                                                           |
| ------------------------------- | ----------------------------------------------------------------------------------------------- |
| `skill-role-breakdown-tasks`    | Decompose requirements into atomic subtasks                                                     |
| `skill-role-code-review`        | Review diff for quality, correctness, security                                                  |
| `skill-role-inject-context`     | Extract and package context for agents                                                          |
| `skill-role-scan-project`       | Scan project structure, entry points                                                            |
| `skill-role-detect-stack`       | Detect tech stack from config files                                                             |
| `skill-role-write-docs`         | Update docs matching existing format                                                            |
| `skill-role-write-user-stories` | Write user stories with acceptance criteria                                                     |
| `skill-role-report-progress`    | Progress tracking and reporting                                                                 |
| `skill-role-feedback-loop`      | Capture good patterns and anti-patterns                                                         |
| `skill-role-blueprints`         | Patterns CRUD/auth/upload/… (nội dung inline trong `SKILL.md`, không cần thư mục `blueprints/`) |

### Tooling (6)

| Skill                          | Mô tả                                                             |
| ------------------------------ | ----------------------------------------------------------------- |
| `skill-tooling-git`            | Branching, commits, merge strategies                              |
| `skill-tooling-linting`        | ESLint, Prettier, auto-fix                                        |
| `skill-tooling-env`            | Environment variables, .env management                            |
| `skill-tooling-packagemanager` | npm, pnpm, yarn, pip, go modules                                  |
| `skill-tooling-bundler`        | Vite, Webpack, esbuild configuration                              |
| `skill-tooling-zod`            | Schema validation, z.infer, safeParse, transforms, env validation |

---

## Workflows

### Flow 1: Dự án mới từ đầu

```
User: "Tôi muốn xây app quản lý đơn hàng"
  │
  ├─ 1. agent-discovery    → Phân tích vấn đề, thị trường, risks
  ├─ 2. agent-sa           → Kiến trúc hệ thống, domain model, API design
  ├─ 3. agent-ba           → User stories, acceptance criteria, backlog
  ├─ 4. agent-pm           → Roadmap, sprint planning
  ├─ 5. agent-designer     → Design system, wireframes, component hierarchy
  ├─ 6. agent-builder      → Detect stack → tạo generated agents (coder, devops)
  ├─ 7. agent-data         → Event taxonomy, tracking plan
  ├─ 8. agent-sre          → Monitoring setup, SLO definitions
  │
  └─ Sprint 1 ready → agent-orchestrator phân task tự động
```

### Flow 2: Join project đang phát triển

```
User: mở project có code → gõ yêu cầu bất kỳ
  │
  ├─ agent-orchestrator    → Phát hiện .agent/ chưa tồn tại
  ├─ agent-onboarding      → Scan code, detect stack, reverse-engineer architecture
  ├─ agent-builder         → Tạo generated agents phù hợp với project
  │
  └─ Ready → orchestrator xử lý task
```

### Flow 3: Implement feature

```
User: "Thêm tính năng login bằng Google OAuth"
  │
  ├─ agent-analyst         → Breakdown: 5 subtasks
  ├─ agent-designer        → Login page wireframe
  ├─ agent-coder-*         → Viết code (BE + FE parallel)
  ├─ [reviewer + security + tester]  → Review song song
  ├─ agent-documenter      → Cập nhật docs
  │
  └─ Done → context-keeper sync, reporter báo user
```

### Flow 4: Pre-release

```
agent-pm: "Chuẩn bị release v1.0"
  │
  ├─ agent-qa              → Test strategy review + accessibility audit
  ├─ agent-perf            → Load test (k6) + bundle analysis
  ├─ agent-security        → Security audit + dependency scan
  ├─ agent-sre             → Production readiness review
  ├─ agent-qa              → Release sign-off: GO / NO-GO
  │
  └─ agent-pm              → Release notes
```

### Flow 5: Incident response

```
Alert fires / user reports bug
  │
  ├─ agent-sre             → Triage + severity classification
  ├─ agent-coder-*         → Hotfix
  ├─ agent-tester          → Verify fix
  ├─ agent-sre             → Verify monitoring stable
  │
  └─ agent-sre             → Postmortem (48h)
```

---

## Generated Agents (Dynamic)

`agent-builder` tự động tạo agents riêng cho từng project dựa trên tech stack.

### Naming Convention

```
Core (cố định):     agent-{role}
Generated (động):   agent-{role}-{project}-{scope}-{tech}
```

### Ví dụ: Project "medapp" (microservices)

```
Detected: NestJS + Go/Gin + FastAPI + React + React Native + Docker + K8s

Generated:
  agent-coder-medapp-api-nestjs          ← User API (TypeScript)
  agent-coder-medapp-payment-gin         ← Payment service (Go)
  agent-coder-medapp-ml-fastapi          ← ML pipeline (Python)
  agent-coder-medapp-web-react           ← Web frontend
  agent-coder-medapp-mobile-rn           ← Mobile app
  agent-devops-medapp-infra-docker       ← Containers
  agent-devops-medapp-pipeline-gha       ← CI/CD
  agent-devops-medapp-iac-k8s            ← Kubernetes
```

Mỗi generated agent được gán tối đa **10 skills** phù hợp với stack của nó.

---

## Context System (.agent/)

Mỗi project có một `.agent/` directory chứa context được tự động duy trì bởi `agent-context-keeper`.

```
.agent/
├── context/
│   ├── summary.md                ← Project overview
│   ├── architecture.md           ← Modules, dependencies, patterns
│   ├── conventions.md            ← Coding style (auto-detected)
│   ├── available-agents.md       ← Active agents + skills
│   ├── existing-docs.md          ← Compressed existing docs
│   ├── git-insights.md           ← Hot files, recent activity
│   ├── ci-cd.md                  ← Pipeline config
│   ├── feedback/
│   │   ├── patterns.md           ← Good patterns to reuse
│   │   ├── anti-patterns.md      ← Mistakes to avoid
│   │   └── stats.md              ← Trends
│   └── modules/
│       └── <module>.md           ← Per-module context
├── task-board.md
├── progress.md
├── dirty-flags.md
└── changelog.md
```

---

## Feedback Loop

Hệ thống "bộ nhớ dài hạn" — agents học từ kết quả review, test, và security audit.

```
Code review → Reviewer ghi patterns/issues → feedback/patterns.md + anti-patterns.md
                                                     ↓
                              Orchestrator inject context cho agents tiếp theo
                                                     ↓
                       Coder tránh lỗi cũ, Reviewer check patterns đã biết
```

---

## Coverage Matrix

### Scale readiness

| Scale                  | Supported                                        |
| ---------------------- | ------------------------------------------------ |
| MVP (< 100 users)      | Full coverage                                    |
| Startup (100-1K users) | Full coverage                                    |
| Growth (1K-10K users)  | Full coverage                                    |
| Scale (10K+ users)     | Full coverage (multi-tenancy, CDN, sharding, DR) |

### Tech stack coverage

| Category            | Supported                                                                                       |
| ------------------- | ----------------------------------------------------------------------------------------------- |
| Web (SPA, SSR, SSG) | React, Next.js, Vue, Nuxt, Angular, SolidStart, Qwik, TanStack Start, Fresh (Deno), HTMX        |
| Mobile              | React Native, Expo, Flutter                                                                     |
| Backend API         | NestJS, Express, Fastify, Elysia, FastAPI, Django, Spring Boot, Gin, Fiber, Axum (Rust), Encore |
| Database            | PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch, Turso (LibSQL)                                |
| Message Queue       | BullMQ, RabbitMQ, Kafka                                                                         |
| Infrastructure      | Docker, Kubernetes, GitHub Actions                                                              |
| Cloud               | AWS (S3, SES, RDS, ECS/EKS), GCP, Azure concepts                                                |

### Security coverage

| Layer        | Skills                                                      |
| ------------ | ----------------------------------------------------------- |
| Architecture | Defense in depth, zero-trust, encryption, STRIDE            |
| Application  | OWASP Top 10, injection, IDOR, CSRF, SSRF, mass assignment  |
| API          | GraphQL depth/complexity, rate limiting, OpenAPI validation |
| Auth         | JWT (RS256/JWKS), OAuth2, RBAC/PBAC                         |
| Container    | Image scanning, non-root, read-only FS, supply chain        |
| Compliance   | GDPR, PCI-DSS, HIPAA basics, audit logging                  |

---

## Getting Started

> Bắt đầu nhanh + nguyên tắc “đúng khái niệm”: **[GUIDELINES.md](GUIDELINES.md)**  
> Cài đặt chi tiết: **[SETUP.md](SETUP.md)**

### 1. Setup

```bash
# Global (1 lần, dùng cho mọi project)
cp agent-platform/CLAUDE.md ~/.claude/
cp -r agent-platform/.claude/* ~/.claude/

# Hoặc Local (per project)
cp agent-platform/CLAUDE.md <your-project>/
cp -r agent-platform/.claude <your-project>/
```

### 2. Sử dụng

Mở project trong IDE có tích hợp Claude (Cursor, VS Code, Claude Code CLI) và gõ bằng ngôn ngữ tự nhiên:

```
"Thiết kế kiến trúc cho hệ thống e-commerce"     → agent-sa
"Thêm tính năng login Google OAuth"               → agent-analyst → agent-coder-*
"Review bảo mật module payment"                    → agent-security
"Phân tích dự án này và cho tôi biết cấu trúc"   → agent-onboarding
```

Hoặc gọi agent cụ thể:

```
"sa: thiết kế microservices cho dự án này"
"qa: viết test plan cho release v2.0"
"sec: review bảo mật module payment"
"dev: implement API /orders + tests"

"agent-sa: thiết kế microservices cho dự án này"
"agent-perf: load test API /orders với 1000 users"
```

### 3. Hệ thống tự động

```
- Onboarding (nếu project mới/chưa có context)
- Tạo generated agents phù hợp với tech stack
- Phân tích → breakdown → spawn agents → deliver → review → docs
```

> **Lưu ý**: `@agent-sa` sẽ không hoạt động vì `@` dùng để reference files. Gọi agents bằng ngôn ngữ tự nhiên.

---

## File References

| File                              | Mô tả                                                              |
| --------------------------------- | ------------------------------------------------------------------ |
| `CLAUDE.md`                       | **Entry point** — Claude đọc file này đầu tiên, chứa routing logic |
| `.claude/agents/README.md`        | Handbook nội bộ (chi tiết workflows, naming, context)              |
| `.claude/agents/{agent}/SKILL.md` | Definition cho từng agent                                          |
| `.claude/skills/{skill}/SKILL.md` | Definition cho từng skill                                          |

---

_Built with 20 agents, 106 skills, and the ambition of a full software company._
