# agent-platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Agents](https://img.shields.io/badge/Agents-11-blue)](#11-workflow-agents)
[![Skills](https://img.shields.io/badge/Skills-227-green)](#227-skills)
[![Stars](https://img.shields.io/github/stars/ryan-nguyen-01/agent-platform?style=social)](https://github.com/ryan-nguyen-01/agent-platform)

> **Language / Ngôn ngữ**: Tài liệu framework viết bằng **tiếng Việt**, dành cho teams Việt Nam. Agents và skills hoạt động với cả prompt tiếng Việt lẫn tiếng Anh.

Hệ thống multi-agent AI hoạt động theo **workflow coordinator-driven**. Từ task analysis đến implementation, verification, QC, và memory — tất cả được điều phối bởi 11 workflow agents với 227 skills.

---

## Vì sao project này ra đời

### Vấn đề với AI coding hiện tại

Khi sử dụng AI assistant (Claude, GPT, Copilot…) để viết code trong thực tế, có một số vấn đề lặp đi lặp lại:

- **AI không nhớ context** — Mỗi conversation là một tờ giấy trắng. AI không biết project bạn đang làm gì, quy ước code ra sao, team đã quyết định gì trước đó.
- **AI không có quy trình** — AI trả lời ngay lập tức mà không phân tích yêu cầu, không kiểm tra impact, không verify kết quả. Kết quả là code không nhất quán, thiếu test, bỏ qua edge case.
- **AI không biết giới hạn** — AI sẵn sàng sửa bất kỳ file nào trong project, kể cả những file không liên quan. Điều này dẫn đến side effects khó kiểm soát.
- **Không có gate kiểm soát chất lượng** — Không có verification bắt buộc trước khi "xong", không có QC pass trước khi giao, không có bug classification rõ ràng.
- **Không học được từ sai lầm** — AI không ghi nhớ pattern nào đã fail, anti-pattern nào cần tránh trong project của bạn.

### Giải pháp: Workflow coordinator-driven

`agent-platform` được thiết kế để giải quyết đúng các vấn đề trên:

| Vấn đề                 | Giải pháp                                                                                       |
| ---------------------- | ----------------------------------------------------------------------------------------------- |
| AI không nhớ context   | **Project Brain** — memory file được build một lần, tái sử dụng mọi conversation                |
| AI không có quy trình  | **11 workflow agents** với role rõ ràng, không agent nào làm việc của agent khác                |
| AI không biết giới hạn | **Generated service coders** với `allowed_write_paths` và `forbidden_paths` scoped theo service |
| Không có quality gate  | **Dev Verification** (≥80% score + critical checks) và **QC Runner** bắt buộc trước DONE        |
| Không học từ sai lầm   | **Memory Update** ghi pattern, anti-pattern, bug root cause sau mỗi workflow event              |

### Mục tiêu thiết kế

```
Không phải "AI viết code nhanh hơn"
Mà là "AI viết code đúng quy trình, có kiểm soát, có thể audit"
```

Project này không dành cho prototype nhanh. Nó dành cho **team** cần consistency, **codebase** cần maintainability, và **AI workflow** cần governance.

---

## Kiến trúc hệ thống

![System overview](.claude/docs/diagrams/01-system-overview.svg)

> Chi tiết tất cả sơ đồ workflow: [visual-flow.md](.claude/docs/visual-flow.md)

---

## Thống kê

| Metric           | Số lượng                          |
| ---------------- | --------------------------------- |
| Workflow agents  | 11                                |
| Skills           | 227 (12 workflow + 215 technical) |
| Rules            | 15                                |
| Templates        | 13                                |
| Commands         | 15                                |
| Generated agents | Unlimited (per project)           |

---

## Cấu trúc thư mục

```
agent-platform/
├── CLAUDE.md                          ← Entry point (Claude đọc file này đầu tiên)
├── GUIDELINES.md                      ← Cách dùng nhanh + semantics
├── SETUP.md                           ← Hướng dẫn cài đặt chi tiết
├── README.md                          ← File này
└── .claude/
    ├── agents/                        ← 11 workflow agent definitions
    │   ├── coordinator.agent.md
    │   ├── onboarding.agent.md
    │   ├── agent-factory.agent.md
    │   ├── task-analysis.agent.md
    │   ├── coder-leader.agent.md
    │   ├── dev-verification.agent.md
    │   ├── qc-handoff.agent.md
    │   ├── qc-runner.agent.md
    │   ├── bug-router.agent.md
    │   ├── memory-update.agent.md
    │   └── workflow-policy.agent.md
    │
    ├── skills/                        ← 227 skill definitions
    │   ├── skill-project-brain/SKILL.md
    │   ├── skill-task-analysis/SKILL.md
    │   ├── react/SKILL.md
    │   ├── docker/SKILL.md
    │   └── ... (227 skills)
    │
    ├── rules/                         ← 15 workflow rules (00-14)
    │   ├── 00-core-rules.md
    │   ├── 01-project-brain-rules.md
    │   └── ...
    │
    ├── templates/                     ← 13 artifact templates
    │   ├── task-analysis.template.yaml
    │   ├── dev-verification.template.yaml
    │   └── ...
    │
    ├── commands/                      ← 15 workflow commands
    │   ├── onboard.md
    │   ├── analyze-task.md
    │   ├── dev.md
    │   └── ...
    │
    ├── docs/                          ← Documentation + visual diagrams
    │   ├── visual-flow.md             ← All workflow diagrams (entry point)
    │   ├── folder-guide.md            ← Full .claude folder reference
    │   ├── deep-onboarding.md         ← Deep onboarding standard
    │   ├── skill-composition.md       ← Skill composition standard
    │   ├── external-skills.md         ← Installed external skills registry
    │   └── diagrams/                  ← 8 SVG workflow diagrams
    │       ├── 01-system-overview.svg
    │       ├── 02-bootstrap-flow.svg
    │       ├── 03-task-execution-flow.svg
    │       ├── 04-qc-bug-routing.svg
    │       ├── 05-state-machine.svg
    │       ├── 06-folder-structure.svg
    │       ├── 07-deep-onboarding.svg
    │       └── 08-skill-composition.svg
    │
    └── context/                       ← Runtime context (per project, auto-generated)
        ├── project-brain.yaml
        ├── service-catalog.yaml
        ├── agent-registry.yaml
        └── services/
```

---

## 11 Workflow Agents

| Agent                | File                      | Vai trò                                                                      |
| -------------------- | ------------------------- | ---------------------------------------------------------------------------- |
| **Coordinator**      | coordinator.agent.md      | Central router — routes tasks, checks project brain, enforces approval gates |
| **Onboarding**       | onboarding.agent.md       | Scans project → builds project brain, service catalog, test policy           |
| **Agent Factory**    | agent-factory.agent.md    | Creates service-specific coder agents (requires user approval)               |
| **Task Analysis**    | task-analysis.agent.md    | Normalizes HLD/LLD/tickets/bugs into structured task spec                    |
| **Coder Leader**     | coder-leader.agent.md     | Coordinates generated service coders — plans, assigns, integrates            |
| **Dev Verification** | dev-verification.agent.md | Evaluates Code Done: critical checks, test policy, ≥80% score                |
| **QC Handoff**       | qc-handoff.agent.md       | Creates mandatory Dev-to-QC handoff document after Code Done                 |
| **QC Runner**        | qc-runner.agent.md        | Runs QC tests from handoff, stops on blocker bugs                            |
| **Bug Router**       | bug-router.agent.md       | Classifies defects as blocker/non-blocker, routes fixes                      |
| **Memory Update**    | memory-update.agent.md    | Persists durable learnings after meaningful workflow events                  |
| **Workflow Policy**  | workflow-policy.agent.md  | Validates state transitions, approval gates, policy compliance               |

---

## Workflow chính

### Flow 1: Onboarding (dự án mới / chưa có context)

```
User mở project → gõ task bất kỳ
  │
  ├─ coordinator        → Phát hiện chưa có project brain
  ├─ onboarding         → Scan code, detect stack, build project brain
  ├─ agent-factory      → Đề xuất coder agents (cần user approval)
  │
  └─ Ready → coordinator xử lý task
```

### Flow 2: Implement feature (full workflow)

```
User: "Thêm tính năng login bằng Google OAuth"
  │
  ├─ 1. coordinator     → Route task
  ├─ 2. task-analysis   → Normalize → task-analysis.yaml
  ├─ 3. coder-leader    → Plan + assign service coders
  ├─ 4. [service coders]→ Implement code (scoped per service)
  ├─ 5. dev-verification→ Check Code Done (≥80%, critical checks pass)
  ├─ 6. qc-handoff      → Create handoff document
  ├─ 7. qc-runner       → Run QC tests
  ├─ 8. bug-router      → Route any defects found
  ├─ 9. memory-update   → Persist learnings
  │
  └─ DONE
```

### Flow 3: Bug fix loop

```
QC Runner phát hiện bug
  │
  ├─ bug-router         → Classify: blocker / non-blocker
  │  ├─ Blocker         → Stop QC, route to coder-leader
  │  └─ Non-blocker     → QC continues on unaffected cases
  │
  ├─ coder-leader       → Assign fix to service coder
  ├─ dev-verification   → Re-verify
  ├─ qc-runner          → Retest
  │
  └─ All clear → memory-update
```

---

## Generated Service Coders

`agent-factory` tạo coder agents riêng cho từng service sau khi onboarding hoàn tất và user approve.

### Đặc điểm

- Mỗi coder có **allowed_read_paths**, **allowed_write_paths**, **forbidden_paths**
- Mỗi coder có **test_policy** và **escalation rules**
- Không tạo full-repo coders — mỗi coder chỉ cover 1 service
- Scope expansion cần user approval

### Naming Convention

```
coder-<service-slug>.agent.md
```

### Ví dụ: Project e-commerce

```
Detected: NestJS + React + PostgreSQL + Redis

Generated:
  coder-api.agent.md          ← Backend API service
  coder-web.agent.md          ← Frontend React app
  coder-shared.agent.md       ← Shared packages
```

---

## 15 Workflow Rules

Rules tại `.claude/rules/` định nghĩa constraints và governance cho workflow:

| Rule  | File                          | Mô tả                                                 |
| ----- | ----------------------------- | ----------------------------------------------------- |
| R-000 | 00-core-rules.md              | Core: read workflow first, no coding without analysis |
| R-001 | 01-project-brain-rules.md     | Project brain as first memory source                  |
| R-002 | 02-onboarding-rules.md        | Onboarding scans only, no code modification           |
| R-003 | 03-agent-factory-rules.md     | Agent creation requires user approval                 |
| R-004 | 04-task-analysis-rules.md     | Every task normalized before coding                   |
| R-005 | 05-coder-leader-rules.md      | Multi-service coordination rules                      |
| R-006 | 06-service-coder-rules.md     | Scoped writes, escalation on cross-service            |
| R-007 | 07-dev-verification-rules.md  | Code Done requires ≥80% score + critical checks       |
| R-008 | 08-qc-rules.md                | QC starts after handoff, stops on blockers            |
| R-009 | 09-bug-routing-rules.md       | Blocker vs non-blocker classification                 |
| R-010 | 10-memory-rules.md            | When and how to persist learnings                     |
| R-011 | 11-approval-gates.md          | User approval required before key actions             |
| R-012 | 12-artifact-contracts.md      | Required artifacts per workflow state                 |
| R-013 | 13-security-secret-rules.md   | No real secrets in artifacts                          |
| R-014 | 14-skill-composition-rules.md | Skills are capabilities, not agent identities         |

---

## 227 Skills

### 12 Workflow Skills (skill-\* prefix)

| Skill                    | Mô tả                                   |
| ------------------------ | --------------------------------------- |
| skill-project-brain      | Manage reusable project brain files     |
| skill-project-onboarding | Build initial project brain by scanning |
| skill-agent-factory      | Generate service-specific coder agents  |
| skill-task-analysis      | Convert tasks into normalized spec      |
| skill-coder-leader       | Coordinate service coders               |
| skill-service-coder      | Implement code within scoped boundaries |
| skill-dev-verification   | Evaluate Code Done status               |
| skill-qc-handoff         | Create Dev-to-QC handoff document       |
| skill-qc-runner          | Run QC and record test results          |
| skill-bug-routing        | Classify and route defects              |
| skill-memory-update      | Persist durable learnings               |
| skill-workflow-policy    | Validate transitions and gates          |

### 215 Technical Skills

| Category            | Ví dụ skills                                                                      |
| ------------------- | --------------------------------------------------------------------------------- |
| Frontend Frameworks | react, angular, vue, svelte, next-best-practices, astro                           |
| Backend Frameworks  | fastapi-python, nestjs-clean-typescript, java-spring-development, ruby-rails      |
| Databases & ORM     | postgresql-best-practices, prisma, drizzle-orm, supabase, redis-best-practices    |
| Mobile              | flutter, building-native-ui, expo-\*, android-development                         |
| Cloud & DevOps      | aws-cloud-services, docker, cloudformation, lambda, azure-kubernetes              |
| Testing             | playwright-best-practices, python-testing, rspec                                  |
| Go Language         | go-concurrency, go-testing, go-error-handling, golang-pro                         |
| CSS & Styling       | tailwindcss, scss-best-practices, styled-components-best-practices, shadcn        |
| Architecture        | api-design-principles, microservices, loom-event-driven, cloud-solution-architect |
| State Management    | redux-toolkit, zustand-state-management, react-query                              |
| Payment             | stripe-best-practices, payment-integration, paypal-integration                    |
| Knowledge Patches   | \*-knowledge-patch (latest framework/library updates)                             |

---

## 15 Commands

| Command        | File             | Mô tả                      |
| -------------- | ---------------- | -------------------------- |
| /onboard       | onboard.md       | Scan project, tạo context  |
| /analyze-task  | analyze-task.md  | Normalize task thành spec  |
| /create-coders | create-coders.md | Tạo service coder agents   |
| /plan-dev      | plan-dev.md      | Lên plan implementation    |
| /dev           | dev.md           | Implement code             |
| /verify-dev    | verify-dev.md    | Check Code Done            |
| /handoff-qc    | handoff-qc.md    | Create QC handoff document |
| /qc            | qc.md            | Run QC tests               |
| /bug           | bug.md           | Route bug report           |
| /sync-memory   | sync-memory.md   | Update memory              |
| /policy-check  | policy-check.md  | Validate workflow policy   |
| /coord         | coord.md         | Coordinator direct         |
| /status        | status.md        | Check workflow status      |
| /resume-task   | resume-task.md   | Resume interrupted task    |

---

## Context System (.claude/context/)

Runtime context tự động tạo bởi onboarding, duy trì bởi memory-update:

```
.claude/context/
├── project-brain.yaml        ← Project memory (architecture, stack, conventions)
├── service-catalog.yaml      ← Service inventory
├── agent-registry.yaml       ← Active coder agents
├── test-policy.yaml          ← Test requirements per service
├── services/                 ← Per-service brain files
│   └── <service>.yaml
└── feedback/
    ├── patterns.md           ← Good patterns to reuse
    └── anti-patterns.md      ← Mistakes to avoid
```

---

## Task Artifacts (.claude/tasks/)

Mỗi task tạo ra folder artifacts theo workflow:

```
.claude/tasks/<task-id>/
├── task-input.md             ← Original task description
├── task-analysis.yaml        ← Normalized task spec
├── implementation-plan.yaml  ← Coder leader\\u0027s plan
├── service-assignments.yaml  ← Which coder does what
├── coder-results.yaml        ← Implementation results
├── dev-verification.yaml     ← Code Done evaluation
├── qc-handoff.md             ← Handoff to QC
├── qc-test-results.yaml      ← QC test outcomes
├── bugs.yaml                 ← Bug tracking
└── memory-updates.yaml       ← Learnings to persist
```

---

## Coverage Matrix

### Scale readiness

| Scale                  | Supported     |
| ---------------------- | ------------- |
| MVP (< 100 users)      | Full coverage |
| Startup (100-1K users) | Full coverage |
| Growth (1K-10K users)  | Full coverage |
| Scale (10K+ users)     | Full coverage |

### Tech stack coverage

| Category            | Supported                                                                             |
| ------------------- | ------------------------------------------------------------------------------------- |
| Web (SPA, SSR, SSG) | React, Next.js, Vue, Nuxt, Angular, Svelte, SvelteKit, Astro, HTMX                    |
| Mobile              | React Native, Expo, Flutter                                                           |
| Backend API         | NestJS, Express, Fastify, FastAPI, Django, Spring Boot, Gin, Axum, Ruby on Rails, Koa |
| Database            | PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch, DynamoDB, Supabase                  |
| ORM                 | Prisma, Drizzle, TypeORM, SQLAlchemy                                                  |
| Message Queue       | Kafka, RabbitMQ, BullMQ, AWS SQS                                                      |
| Infrastructure      | Docker, Kubernetes, GitHub Actions, AWS, Azure                                        |
| Cloud               | AWS (S3, Lambda, DynamoDB, CloudFormation, Cognito), Azure (AKS, Functions, Foundry)  |

### Security coverage

| Layer        | Skills                                                      |
| ------------ | ----------------------------------------------------------- |
| Architecture | Defense in depth, zero-trust, encryption, STRIDE            |
| Application  | OWASP Top 10, injection, IDOR, CSRF, SSRF, mass assignment  |
| API          | GraphQL depth/complexity, rate limiting, OpenAPI validation |
| Auth         | JWT, OAuth2, RBAC, Better Auth                              |
| Container    | Image scanning, non-root, read-only FS, supply chain        |
| Payment      | Stripe, PayPal integration, PCI compliance                  |

---

## Prerequisites

Trước khi dùng agent-platform, bạn cần một trong các IDE/tool sau hỗ trợ Claude:

| Tool                          | Cách tích hợp                                                                       |
| ----------------------------- | ----------------------------------------------------------------------------------- |
| **Claude Code** (khuyên dùng) | Đặt `CLAUDE.md` + `.claude/` vào root project, Claude Code đọc tự động              |
| **VS Code + GitHub Copilot**  | Đặt `CLAUDE.md` vào `.github/copilot-instructions.md` hoặc dùng custom instructions |
| **Cursor**                    | Đặt `CLAUDE.md` vào `.cursorrules` hoặc project rules                               |
| **Windsurf**                  | Đặt `CLAUDE.md` vào `.windsurfrules`                                                |

> Không cần cài package hay server riêng — agent-platform là tập hợp markdown files mà AI đọc và tuân theo.

---

## Getting Started

> Cài đặt chi tiết: **[SETUP.md](SETUP.md)**
> Cách dùng nhanh: **[GUIDELINES.md](GUIDELINES.md)**

### 1. Setup

```bash
# Clone repo
git clone <repo-url> ~/Downloads/agent-platform

# Local (per project)
cp -r agent-platform/.claude <your-project>/
cp agent-platform/CLAUDE.md <your-project>/

# Hoặc Global (tất cả projects)
mkdir -p ~/.claude
cp -r agent-platform/.claude/* ~/.claude/
cp agent-platform/CLAUDE.md ~/.claude/
```

### 2. Ví dụ nhanh

**Trước** (AI thuần túy, không có platform):

```
User: "Thêm API tạo order"
AI:   → Viết code ngay, không hỏi, không phân tích, không test
      → Side effects: sửa cả file không liên quan
      → Không verify, không QC
```

**Sau** (với agent-platform):

```
User:          "Thêm API tạo order"
coordinator:   → đọc project brain, route đến task-analysis
task-analysis: → phân tích impact, risks, acceptance criteria
               → [chờ user approve]
coder-leader:  → assign coder-order (chỉ write src/orders/**)
coder-order:   → implement, theo conventions đã học
dev-verif.:    → check critical checks, test policy, score ≥80%
qc-runner:     → chạy test cases, stop nếu blocker
memory-update: → ghi learnings vào project brain
               → DONE ✅
```

### 3. Sử dụng

Mở project trong IDE tích hợp Claude và gõ bằng ngôn ngữ tự nhiên:

```
"Phân tích dự án này"                    → onboarding
"Implement API /orders"                  → coordinator → task-analysis → coder-leader
"Kiểm tra code đã sẵn sàng chưa"        → dev-verification
```

Hoặc dùng commands:

```
/onboard                                 → Scan project, build brain
/analyze-task                            → Normalize task
/dev                                     → Implement
/verify-dev                              → Check Code Done
/qc                                      → Run QC
```

### 3. Workflow tự động

```
coordinator → onboarding (nếu project mới)
           → task-analysis → coder-leader → [service coders]
           → dev-verification → qc-handoff → qc-runner
           → memory-update → DONE
```

> **Lưu ý**: `@` trong Claude Code dùng để reference files, không phải gọi agents.

---

## File References

| File                                 | Mô tả                                                              |
| ------------------------------------ | ------------------------------------------------------------------ |
| `CLAUDE.md`                          | **Entry point** — Claude đọc file này đầu tiên, chứa routing logic |
| `.claude/agents/{role}.agent.md`     | Definition cho từng workflow agent                                 |
| `.claude/skills/{skill}/SKILL.md`    | Definition cho từng skill                                          |
| `.claude/rules/{nn}-{name}.md`       | Workflow rules và constraints                                      |
| `.claude/templates/*.template.*`     | Artifact templates                                                 |
| `.claude/commands/*.md`              | Workflow commands                                                  |
| `.claude/docs/visual-flow.md`        | **Visual diagrams** — sơ đồ workflow bằng SVG                      |
| `.claude/docs/folder-guide.md`       | Giải thích chi tiết từng folder/file trong `.claude`               |
| `.claude/docs/deep-onboarding.md`    | Tiêu chuẩn deep onboarding                                         |
| `.claude/docs/skill-composition.md`  | Tiêu chuẩn skill composition                                       |
| `.claude/docs/external-skills.md`    | Registry external skills đã cài                                    |
| `.claude/docs/architecture-guide.md` | **System architecture** — layers, data flow, security model        |
| `.claude/docs/workflow-reference.md` | **Workflow reference** — states, transitions, commands, gates      |
| `.claude/docs/agent-catalog.md`      | **Agent catalog** — all 11 agents + generated coders               |
| `.claude/docs/skill-guide.md`        | **Skill guide** — 227 skills, categories, composition              |
| `.claude/docs/diagrams/*.svg`        | 8 SVG workflow diagrams + legacy full flow                         |

---

_Built with 11 workflow agents, 227 skills, 15 rules, and a coordinator-driven workflow._

---

## License

MIT License — xem [LICENSE](LICENSE) để biết thêm chi tiết.

Project này là **open framework** — bạn có thể:

- ✅ Dùng trong dự án thương mại
- ✅ Fork và tùy chỉnh cho team
- ✅ Thêm skills/agents riêng
- ✅ Đóng góp ngược lại qua Pull Request
