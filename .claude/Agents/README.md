# AI Company — Agent System Handbook

## Tổng quan

Hệ thống gồm **20 core agents** + **106 skills** + **feedback loop** + **blueprints** + **unlimited generated agents**, hoạt động như một công ty phần mềm hoàn chỉnh. Từ ý tưởng đến production và vận hành.

---

## Sơ đồ tổ chức

```
                           ┌──────────────────┐
                           │  EXECUTIVE OFFICE │
                           │  orchestrator     │ ← điều phối mọi thứ
                           │  reporter         │ ← báo cáo tiến độ
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

## Danh sách agents

### Product (ý tưởng → backlog)

| Agent | Vai trò | Khi nào dùng |
|-------|---------|-------------|
| **agent-discovery** | Phân tích vấn đề, thị trường, MVP scope | Có ý tưởng mới cần validate |
| **agent-sa** | Thiết kế kiến trúc, domain model, API | Sau discovery, cần bản thiết kế |
| **agent-ba** | User stories, acceptance criteria, backlog | Sau SA, cần backlog cho dev |
| **agent-pm** | Roadmap, sprint planning, release management | Quản lý delivery và đo lường |

### Engineering (design → code → review)

| Agent | Vai trò | Khi nào dùng |
|-------|---------|-------------|
| **agent-analyst** | Breakdown task thành subtasks atomic | Task phức tạp cần phân tích |
| **agent-designer** | UI/UX: design tokens, wireframes, components | Feature có giao diện |
| **agent-coder-*** | Viết code (generated, per-project) | Mọi task viết code |
| **agent-reviewer** | Review code: quality, conventions, correctness | Sau khi code xong |
| **agent-documenter** | Cập nhật docs + API docs + changelog | Sau review pass |
| **agent-migrator** | Migration, refactor lớn, version upgrade | Đổi stack, nâng version |

### Quality & Reliability (test → release)

| Agent | Vai trò | Khi nào dùng |
|-------|---------|-------------|
| **agent-tester** | Viết + chạy unit/integration/e2e tests | Sau code, song song reviewer |
| **agent-qa** | Test strategy, accessibility, release sign-off | Trước release |
| **agent-perf** | Load testing, profiling, bundle analysis | Trước release hoặc optimization |
| **agent-security** | OWASP review, threat model, dependency audit | Mọi PR có security concern |

### Operations (deploy → monitor → respond)

| Agent | Vai trò | Khi nào dùng |
|-------|---------|-------------|
| **agent-sre** | Monitoring, SLI/SLO, incident response | Setup monitoring, incident |
| **agent-devops-*** | Docker, CI/CD, K8s (generated) | Setup/update infra |

### Data

| Agent | Vai trò | Khi nào dùng |
|-------|---------|-------------|
| **agent-data** | Data pipelines, event taxonomy, data quality | Analytics, tracking setup |

### Infrastructure (internal)

| Agent | Vai trò | Khi nào dùng |
|-------|---------|-------------|
| **agent-orchestrator** | Điều phối, spawn agents, error handling | Entry point mọi task |
| **agent-onboarding** | Scan project, tạo .agent/ context | Lần đầu vào project |
| **agent-builder** | Detect stack, tạo generated agents | Sau onboarding |
| **agent-context-keeper** | Sync .agent/ context khi code thay đổi | Chạy nền |
| **agent-reporter** | Báo cáo tiến độ, escalate blockers | Chạy nền |

---

## Workflows

### Flow 1: Dự án mới từ đầu

```
User: "Tôi muốn xây app quản lý todo"
  │
  ├─ agent-discovery    → docs/discovery-report.md
  ├─ agent-sa           → docs/architecture.md, domain-model.md, api-design.md
  ├─ agent-ba           → docs/user-stories/, backlog.md
  ├─ agent-pm           → docs/roadmap.md, sprint-1.md
  ├─ agent-designer     → docs/ui-design/
  ├─ agent-builder      → tạo agent-coder-todo-api-nestjs, agent-coder-todo-web-react
  ├─ agent-data         → docs/event-taxonomy.md
  ├─ agent-sre          → docs/observability.md, slo.md
  │
  └─ Sẵn sàng sprint 1 → agent-orchestrator bắt đầu phân task
```

### Flow 2: Join project đang phát triển

```
User: mở project có code → gõ bất kỳ task nào
  │
  ├─ agent-orchestrator  → Bootstrap Guard: .agent/ chưa có
  ├─ agent-onboarding    → Mode B: scan code, detect stack, reverse-engineer
  ├─ agent-builder       → tạo generated agents phù hợp
  │
  └─ Sẵn sàng → orchestrator xử lý task ban đầu
```

### Flow 3: Implement feature (sprint bình thường)

```
User: "Thêm tính năng login bằng Google OAuth"
  │
  ├─ agent-analyst       → breakdown: 5 subtasks
  ├─ agent-designer      → login page wireframe (nếu có UI)
  ├─ agent-coder-*       → viết code (parallel nếu BE + FE)
  ├─ [agent-reviewer + agent-security + agent-tester]  → song song
  ├─ agent-documenter    → cập nhật docs
  │
  └─ ✅ Done → agent-context-keeper sync, agent-reporter báo user
```

### Flow 4: Pre-release

```
agent-pm: "Chuẩn bị release v1.0"
  │
  ├─ agent-qa         → test strategy review + accessibility audit
  ├─ agent-perf       → load test + bundle analysis
  ├─ agent-security   → final security audit + dependency scan
  ├─ agent-sre        → production readiness review
  ├─ agent-qa         → release sign-off: GO / NO-GO
  │
  └─ agent-pm         → release notes + stakeholder comms
```

### Flow 5: Incident response

```
Alert fires hoặc user report bug
  │
  ├─ agent-sre        → triage + severity classification
  ├─ agent-coder-*    → hotfix code
  ├─ agent-tester     → verify fix
  ├─ agent-sre        → verify monitoring stable
  │
  └─ agent-sre        → postmortem (trong 48h)
```

---

## Naming Convention

### Core agents (cố định)
```
agent-{role}
Ví dụ: agent-orchestrator, agent-reviewer, agent-tester
```

### Generated agents (theo project)
```
agent-{role}-{project}-{scope}-{tech}
Ví dụ: agent-coder-shopee-api-nestjs, agent-devops-medapp-infra-docker
```

---

## Context System (.agent/)

```
.agent/
├── context/
│   ├── summary.md              ← project overview
│   ├── architecture.md         ← modules, dependencies, patterns
│   ├── conventions.md          ← coding style (auto-detected)
│   ├── available-agents.md     ← list agents + skills
│   ├── existing-docs.md        ← compressed existing docs
│   ├── git-insights.md         ← hot files, recent activity
│   ├── ci-cd.md                ← pipelines, deploy targets
│   ├── feedback/               ← lessons learned (feedback loop)
│   │   ├── patterns.md         ← good patterns to reuse
│   │   └── anti-patterns.md    ← mistakes to avoid
│   └── modules/
│       └── <module>.md         ← per-module context
├── blueprints/                 ← reusable templates
│   ├── crud-module.md
│   ├── auth-flow.md
│   └── ...
├── task-board.md
├── progress.md
├── dirty-flags.md
└── changelog.md
```

---

## Skill Categories (106 skills)

| Category | Count | Examples |
|----------|-------|---------|
| Languages | 5 | typescript, python, java, go, rust |
| Frameworks BE | 7 | nestjs, express, fastapi, django, spring, gin, fiber |
| Frameworks FE | 5 | react, nextjs, vuejs, nuxtjs, angular |
| Frameworks Mobile | 2 | **react-native**, **flutter** |
| Databases | 9 | postgresql, mysql, mongodb, redis, elasticsearch, prisma, typeorm, sqlalchemy, **migration** |
| Auth & Security | 6 | jwt, oauth2, rbac, hardening, **graphql-security**, **container-security** |
| Testing | 7 | jest, vitest, pytest, junit, playwright, **load-testing**, **fixtures** |
| UI Libraries | 6 | tailwind, shadcn, mui, antd, **figma**, **accessibility** |
| Frontend | 2 | state-management (Redux, Zustand, Pinia), **i18n** (i18next, vue-i18n) |
| DevOps | 4 | docker, github-actions, kubernetes, **container-security** |
| Queues | 3 | bullmq, rabbitmq, kafka |
| Observability | 2 | logging, tracing |
| API Design | 4 | rest, graphql, grpc, **openapi** |
| Architecture | 26 | solution, write-hld, domain-model, microservices, event-driven, transactional, multi-tenancy, feature-flags, notification, audit-log, **background-jobs**, **email-delivery**, **finops**, **disaster-recovery**, scalability, distributed-systems, security, realtime, search, storage, monitoring, + 4 discovery + 1 mvp-scope |
| Context | 4 | read, write, compress, sync-delta |
| Role/Workflow | 10 | breakdown-tasks, code-review, inject-context, scan-project, feedback-loop, blueprints, ... |
| Tooling | 5 | git, linting, env, packagemanager, bundler |
| Storage | 1 | s3 |

---

## Feedback Loop System

Hệ thống "bộ nhớ dài hạn" — agents học từ lịch sử review, test, và security.

```
Review complete → reviewer ghi praise/issues → feedback/patterns.md + anti-patterns.md
                                                      ↓
                               Orchestrator inject kèm context cho agents
                                                      ↓
                        Coder tránh anti-patterns, Reviewer check patterns
```

Files:
- `.agent/context/feedback/patterns.md` — good patterns + code examples
- `.agent/context/feedback/anti-patterns.md` — mistakes + fixes
- `.agent/context/feedback/stats.md` — top issues, trends

Skill: `skill-role-feedback-loop`

---

## Blueprints System

Templates cho coding patterns phổ biến — agents dùng blueprints thay vì viết từ đầu.

| Blueprint | Mô tả | Complexity |
|-----------|--------|------------|
| BLUEPRINT-001 | CRUD Module (entity + validation + pagination) | medium |
| BLUEPRINT-002 | Authentication Flow (login, register, tokens) | complex |
| BLUEPRINT-003 | File Upload (S3/local + validation + resize) | medium |
| BLUEPRINT-004 | Payment Integration (Stripe checkout + webhooks) | complex |
| BLUEPRINT-005 | Real-time Features (WebSocket + notifications) | medium |
| BLUEPRINT-006 | Search & Filter (full-text + autocomplete) | medium |
| BLUEPRINT-007 | Caching Strategy (cache-aside + invalidation) | medium |

Workflow:
```
analyst: detect task match blueprint → attach ref vào subtask
orchestrator: inject blueprint vào context cho coder
coder: đọc blueprint → customize theo project → implement
```

Skill: `skill-role-blueprints`

---

## Getting Started

```
1. Mở project trong IDE
2. Gõ bất kỳ yêu cầu nào
3. Hệ thống tự động:
   - Onboarding (nếu lần đầu)
   - Tạo agents phù hợp
   - Phân tích task → breakdown → spawn agents → deliver
4. Ngồi uống cà phê ☕
```
