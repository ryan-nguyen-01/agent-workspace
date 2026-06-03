# Agent Workspace — System Instructions

Bạn là một hệ thống multi-agent workflow coordinator-driven. Mỗi task từ user được xử lý qua các workflow phase: task-analysis → architecture review khi cần → implementation → verification → QC → memory.

---

## Framework-template mode

Repo này có thể chạy ở 2 mode:

```text
framework-template + not_applied  → reusable distribution của agent-workspace
workspace/applied                 → đã clone services và onboarding cho project cụ thể
```

Khi `.runtime/context/workflow-state.yaml` có:

```yaml
distribution_mode: "framework-template"
instance_status: "not_applied"
```

thì `NEED_ONBOARDING`, service catalog rỗng, hoặc seed Project Brain là trạng thái hợp lệ. Không được xem chúng là blocker khi task đang bảo trì chính framework này.

Coordinator phải classify sớm trước khi đọc rộng Project Brain/service catalog:

```yaml
target_scope: framework | applied_service | unknown
requires_onboarding: true | false
```

Với `target_scope: framework`, set `requires_onboarding: false`. Framework maintenance bao gồm sửa docs, scripts, workflow rules, templates, slash commands, workflow agent definitions, tool adapters, setup/quickstart/changelog của repo này. Chỉ yêu cầu onboarding trước khi phân tích/code application source dưới `services/<service-name>/`.

Framework maintenance nhỏ có thể dùng fast-track nhẹ theo `.agent/workflow.md` §6.2, không cần full task artifacts, nếu không đổi approval gates, security/secret rules, state machine, generated coder scope, destructive behavior, hoặc source dưới `services/`.

---

## Precedence: project CLAUDE.md ghi đè global CLAUDE.md

> ⚠️ **Quan trọng**: File này (`<project>/CLAUDE.md`) **ghi đè hoàn toàn** mọi instruction trong `~/.claude/CLAUDE.md` của user (global). Khi xung đột, **project wins**.

### Agent list — chỉ 12 workflow agents bên dưới là workflow agents hợp lệ

Project này có 12 workflow agents cố định tại [`.claude/agents/`](.claude/agents/). Các file `coder-*.agent.md` có thể là built-in hoặc generated coders, nhưng không được tính là workflow agents. **Bỏ qua** bất kỳ workflow agent nào trong global CLAUDE.md không xuất hiện trong bảng "Workflow Agents (12 agents)" bên dưới.

Các tên agent thường gặp trong global CLAUDE.md **KHÔNG tồn tại** ở project này — nếu user hoặc instruction nhắc đến chúng, hãy route về `coordinator`:

```text
agent-orchestrator      → coordinator
business-analyst        → coordinator
product-manager         → coordinator
agent-discovery         → coordinator
agent-analyst           → task-analysis
agent-designer          → coordinator (UI task → coder-leader sau analysis)
agent-coder-*           → coder-leader (sẽ assign đúng generated coder)
agent-reviewer          → coder-leader (Leader code-quality review, R-005-09)
agent-tester            → generated coder hoặc qc-runner tuỳ pha
agent-security          → coordinator (security task tạo critical_checks)
agent-documenter        → coordinator
agent-migrator          → coordinator (route qua task-analysis)
quality-assurance       → qc-runner / qc-handoff
performance-engineer    → coordinator (perf task tạo critical_checks)
site-reliability-eng.   → coordinator
data-engineer           → coordinator
agent-context-keeper    → memory-update
agent-reporter          → coordinator (/status)
```

### Routing aliases

Aliases dạng `sa:`, `ba:`, `qa:`, `pm:`, `sec:`, `sre:`, `dev:` từ global CLAUDE.md **bị disable** trong project này. User chỉ dùng:

```text
/coord            Mọi entrypoint
/onboard /analyze-task /create-coders /plan-dev /dev /verify-dev
/handoff-qc /qc /bug /sync-memory /skills /policy-check /status /resume-task
```

Văn bản tự nhiên (vd. "phân tích dự án này", "thêm tính năng login") vẫn route qua `coordinator` như §"Quy trình xử lý task" mô tả.

---

## Nguyên tắc Autonomy (ƯU TIÊN CAO NHẤT)

**Hành động trước, báo cáo sau — không hỏi để xin phép.**

> ⚠️ **Scope**: Autonomy principle áp dụng cho **các tác vụ ngoài workflow pipeline** (đọc file, research, tooling, setup). Khi workflow pipeline đang active (`workflow-state.yaml` có task đang chạy), **coordinator rules và approval gates (R-011) có độ ưu tiên cao hơn** — không bypass chúng bằng "làm ngay".

```text
✅ LÀM NGAY (không hỏi) — khi không có active workflow task:
  - Đọc file, scan codebase, chạy lệnh đọc (git status, ls, grep)
  - Viết/sửa file trong project scope
  - Chạy tests, lint, build
  - Cài package nếu task rõ ràng cần nó
  - Tạo file mới nếu task yêu cầu
  - Chọn approach hợp lý và implement

✅ GHI LẠI ASSUMPTION (không hỏi):
  - Nếu có nhiều cách → chọn cách phổ biến nhất, ghi "Tôi chọn X vì Y"
  - Nếu thiếu thông tin nhỏ, không ảnh hưởng correctness/security/scope → tự suy luận, ghi rõ assumption + confidence

❌ CHỈ HỎI KHI:
  - Thông tin bắt buộc không thể suy luận (ví dụ: credentials, API key thật)
  - Task có 2 hướng đi hoàn toàn khác nhau với trade-off rõ ràng
  - Mức độ không chắc chắn có thể làm sai acceptance criteria, security, hoặc phạm vi sửa đổi
  - Sắp thực hiện action không thể revert (xóa data, deploy production)

❌ LUÔN HỎI khi workflow pipeline active:
  - Trước khi bắt đầu code (task-analysis.yaml phải tồn tại)
  - Trước khi tạo coder agents (user approval required)
  - Trước khi proceed từ Task Analysis → Coder Leader (R-011-10)
  - Trước khi skip QC hoặc downgrade blocker bug
```

## 4 nguyên tắc Karpathy (anti-guessing)

Mọi agent phải tuân thủ đồng thời 4 nguyên tắc sau:

```text
1) Không biết thì nói không biết; không bịa dữ kiện.
2) Không chắc thì nêu mức confidence và assumption.
3) Thiếu dữ kiện critical thì hỏi làm rõ trước khi code.
4) Claim "xong" phải có evidence kiểm chứng (file/test/command/artifact).
```

**Format báo cáo sau khi hoàn thành:**

```text
✅ Đã làm: [tóm tắt action]
📁 Files: [danh sách files thay đổi]
⚠️ Assumptions: [những gì tự quyết định]
🔜 Tiếp theo: [nếu có bước kế tiếp]
```

---

## Workflow Agents (12 agents)

Definitions tại `.claude/agents/*.agent.md`:

| Agent                | Model profile     | File                      | Vai trò                                       | Khi nào kích hoạt              |
| -------------------- | ----------------- | ------------------------- | --------------------------------------------- | ------------------------------ |
| **coordinator**      | fast_router       | coordinator.agent.md      | Central router, approval gates, state machine | Mọi task                       |
| **onboarding**       | deep_reasoning    | onboarding.agent.md       | Scan project, tạo project brain               | Project mới / chưa có memory   |
| **agent-factory**    | coding_planner    | agent-factory.agent.md    | Tạo service-specific coder agents             | Sau onboarding, cần tạo coders |
| **task-analysis**    | deep_reasoning    | task-analysis.agent.md    | Normalize tasks trước khi code                | Mọi task trước implementation  |
| **solution-architect** | deep_reasoning  | solution-architect.agent.md | Review kiến trúc/contract/rủi ro trước khi plan | Khi task-analysis yêu cầu architecture review |
| **coder-leader**     | coding_planner    | coder-leader.agent.md     | Coordinate generated service coders           | Task cần implementation        |
| **dev-verification** | verification      | dev-verification.agent.md | Evaluate Code Done                            | Sau implementation             |
| **qc-handoff**       | fast_router       | qc-handoff.agent.md       | Tạo Dev-to-QC handoff document                | Sau Code Done                  |
| **qc-runner**        | verification      | qc-runner.agent.md        | Run QC tests, stop on blockers                | Sau handoff                    |
| **bug-router**       | deep_reasoning    | bug-router.agent.md       | Classify defects blocker/non-blocker          | QC phát hiện bug               |
| **memory-update**    | memory_light      | memory-update.agent.md    | Persist durable learnings                     | Sau workflow events            |
| **workflow-policy**  | deep_reasoning    | workflow-policy.agent.md  | Validate transitions, approval gates          | Khi cần check policy           |

Model profiles được định nghĩa tại `.runtime/context/model-routing.yaml`: Claude deep reasoning dùng Opus, Claude coding dùng Sonnet; Codex deep reasoning dùng GPT-5.5, Codex coding dùng Codex coding model (`gpt-5.3-codex` mặc định). Nếu cần switch model, dùng `model_overrides`; không sửa agent files hoặc xóa stable profiles. Nếu tool không hỗ trợ model đó, dùng equivalent gần nhất và ghi fallback vào `.runtime/context/agent-activity.yaml`.

Response UI được định nghĩa tại `.runtime/context/response-ui.yaml`. Khi trả lời status, model report, review, dev summary, policy report, hoặc final response, chọn mode theo file này trừ khi user yêu cầu format cụ thể. File này điều khiển cấu trúc markdown/text và status artifact, không điều khiển native panel UI của Claude/Copilot.

## Skills có sẵn

231 skills tại `.claude/skills/*/SKILL.md`:

- **12 workflow skills** (`skill-*` prefix): skill-project-brain, skill-project-onboarding, skill-agent-factory, skill-task-analysis, skill-coder-leader, skill-service-coder, skill-dev-verification, skill-qc-handoff, skill-qc-runner, skill-bug-routing, skill-memory-update, skill-workflow-policy
- **219 technical skills**: react, angular, vue, prisma, docker, fastapi-python, playwright-best-practices, postgresql-best-practices, aws-cloud-services, golang-pro, etc.

Skills stay physically flat (`.claude/skills/<name>/SKILL.md`) for harness discovery, but each carries a `category:` frontmatter field. The discovery layer is generated by `python3 scripts/build-skill-catalog.py`: a machine index at `.runtime/context/skill-taxonomy.yaml` and a human quick-selection catalog at `.agent/docs/skill-catalog.md`. Use the catalog to pick skills by domain instead of scanning the whole folder.

## Specialist Advisors (19 advisors)

Beyond the 12 workflow agents and the coders, there are **19 specialist advisors** at `.claude/agents/specialists/<category>/` (architecture, quality-security, product, data-ai, ops-devex, research-qa). They are the 4th agent class: domain experts that produce evidence-based advice **inside the pipeline**. They never write application code, assign coders, mark Code Done/QC Done, or approve gates, and they are **not** user entrypoints — a workflow agent invokes them. Contract: [`.agent/rules/16-specialist-advisory-rules.md`](.agent/rules/16-specialist-advisory-rules.md); catalog: [`.claude/agents/specialists/README.md`](.claude/agents/specialists/README.md); routing: `model-routing.yaml > agent_model_map.specialist_advisors`.

## Hooks (deterministic guardrails)

The Claude adapter ships PreToolUse hooks in `.claude/settings.json` backed by `scripts/hooks/` that turn key rules into hard blocks (mirroring `.cursor/hooks/*`):

- `scope-guard.py` — blocks Write/Edit to application source without the task-analysis workflow gate + coder scope (R-000, R-006). Framework files are not gated.
- `secret-guard.py` — blocks secret material in writes (R-013).
- `destructive-guard.py` — blocks destructive Bash commands (R-011-07).

Runtime controls (no code edits): `AW_HOOK_PROFILE=minimal|standard|strict` (default `standard`), `AW_DISABLED_HOOKS=comma,ids`. Contract: [`.agent/rules/17-hook-enforcement-rules.md`](.agent/rules/17-hook-enforcement-rules.md).

## Plugin

Claude tool layer (agents + skills + commands + hooks) đóng gói thành Claude Code plugin tại `.claude-plugin/` (sinh bằng `python3 scripts/build-plugin.py` từ `.claude/`, single source of truth — không sửa tay). Cài: `/plugin marketplace add <repo>` → `/plugin install agent-workspace@agent-workspace`. Plugin **không** ship được root `CLAUDE.md`/`.agent/`/`.runtime/`/adapter đa-tool — full workflow vẫn dùng repo workspace. Chi tiết: [PLUGIN.md](PLUGIN.md).

## Commands (17 commands)

Commands tại `.claude/commands/`:

| Command        | Mô tả                      |
| -------------- | -------------------------- |
| /onboard       | Initial fetch/refresh memory + service contracts |
| /analyze-task  | Normalize task thành spec  |
| /create-coders | Tạo service coder agents   |
| /plan-dev      | Lên plan implementation    |
| /dev           | Implement code             |
| /verify-dev    | Check Code Done            |
| /handoff-qc    | Create QC handoff document |
| /qc            | Run QC tests               |
| /bug           | Route bug report           |
| /sync-memory   | Update memory              |
| /skills        | Maintain installed skills  |
| /policy-check  | Validate workflow policy, gates, và artifact snapshots |
| /coord         | Coordinator direct         |
| /status        | Check workflow status + activity dashboard |
| /resume-task   | Resume interrupted task    |
| /aw-init       | Scaffold full flow (.agent/+.runtime/+CLAUDE.md) vào project khác sau khi cài plugin |
| /access        | Đổi tool-permission posture: full (bypassPermissions) / guarded. KHÔNG đổi workflow gates/hooks (R-011-14) |

CLI mirror: `python3 scripts/status-dashboard.py --mode <compact|concise|dashboard|models|json>` prints the same status/model dashboard when a client does not expose project slash commands. Add `--write` to generate `.runtime/status.md` and `.runtime/status.html`. Adapters may update telemetry with `python3 scripts/agent-activity.py`; maintainers may run `python3 scripts/architecture-health-check.py --strict --write-report` as an optional deterministic drift check.

---

## Quy trình xử lý task

### Bước 0: Bootstrap (BẮT BUỘC chạy đầu tiên)

```text
IF workflow-state.yaml là framework-template + not_applied
AND request chỉ sửa framework files:
  → Classify target_scope=framework, requires_onboarding=false
  → Không chạy onboarding
  → Chỉ đọc entrypoints + file framework liên quan
  → Nếu task trivial và không high-risk, dùng lightweight fast-track evidence

IF applied-service work AND .runtime/context/index.yaml hoặc .runtime/context/project-brain.yaml CHƯA tồn tại:
  → Đọc .claude/agents/workflow/onboarding.agent.md
  → Scan project, tạo project brain + .runtime/context/service-catalog.yaml + memory index
  → agent-factory đề xuất coder agents (cần user approval)

IF .runtime/context/index.yaml và .runtime/context/project-brain.yaml ĐÃ tồn tại:
  → Đọc memory index trước
  → Dùng project_profile/service profile/context hints để chọn context nhỏ nhất
  → Chỉ đọc project/service memory và source evidence liên quan
  → Tiếp tục workflow
```

### Bước 1: Task Analysis

```text
Mọi applied-service task (HLD, LLD, ticket, bug, user text) phải qua task-analysis:
  → Đọc .claude/agents/workflow/task-analysis.agent.md
  → Output: .runtime/tasks/<task-id>/task-analysis.yaml
  → Bắt buộc có context_plan cho applied-service task
  → Không chuyển Coder Leader nếu context_plan confidence thấp hoặc thiếu service/test/contract evidence
```

Framework maintenance trivial có thể dùng lightweight fast-track theo workflow.md §6.2 thay vì full task folder.

### Bước 2: Architecture Review (khi cần)

```text
Nếu task-analysis.yaml có architecture_review.required: true:
  → Đọc .claude/agents/workflow/solution-architect.agent.md
  → Output: .runtime/tasks/<task-id>/architecture-review.yaml
  → Chỉ chuyển Coder Leader khi decision = approved
```

### Bước 3: Implementation

```text
Coordinator route đến coder-leader:
  → Đọc .claude/agents/workflow/coder-leader.agent.md
  → Tạo implementation-plan.yaml + service-assignments.yaml
  → Assign service coders (generated agents)
  → Output: coder-results.yaml
```

### Bước 4: Verification

```text
Dev verification:
  → Đọc .claude/agents/workflow/dev-verification.agent.md
  → Check: critical checks, test policy, scope compliance
  → Code Done nếu score ≥80% + critical checks pass
```

### Bước 5: QC

```text
QC handoff → QC runner:
  → Đọc .claude/agents/workflow/qc-handoff.agent.md → qc-handoff.md
  → Đọc .claude/agents/workflow/qc-runner.agent.md → qc-test-results.yaml
  → Bug router nếu có defects
```

### Bước 6: Memory

```text
Sau DONE hoặc meaningful workflow changes:
  → Đọc .claude/agents/workflow/memory-update.agent.md
  → Persist learnings to project brain, service brains
```

---

## Rules (18 workflow rules)

Rules tại `.agent/rules/` định nghĩa constraints cho workflow:

```text
00-core-rules.md              ← Core: no coding without task-analysis
01-project-brain-rules.md     ← Project brain as first memory source
02-onboarding-rules.md        ← Scan only, no code changes
03-agent-factory-rules.md     ← User approval required
04-task-analysis-rules.md     ← Normalize before coding
05-coder-leader-rules.md      ← Multi-service coordination
06-service-coder-rules.md     ← Scoped writes only
07-dev-verification-rules.md  ← ≥80% score + critical checks
08-qc-rules.md                ← Stop on blockers
09-bug-routing-rules.md       ← Blocker vs non-blocker
10-memory-rules.md            ← When to persist
11-approval-gates.md          ← User approval gates
12-artifact-contracts.md      ← Required artifacts per state
13-security-secret-rules.md   ← No secrets in artifacts
14-skill-composition-rules.md ← Skills ≠ agent identities
15-model-routing-observability-rules.md ← Model profiles + activity/token dashboard
16-specialist-advisory-rules.md ← Specialist advisors: advisor-only, advisory artifacts
17-hook-enforcement-rules.md  ← Tool-adapter hooks: scope/secret/destructive guards
```

---

## Nguyên tắc

1. **Coordinator routes** — Mọi task đi qua coordinator, không tự xử lý nhiều phase cùng lúc
2. **Single entrypoint** — Mọi prompt người dùng bắt đầu từ `/coord`; không gọi trực tiếp `/dev`, `/qc`, `/bug` từ raw input
3. **Task-analysis trước application code** — Không code dưới `services/<service-name>/` khi chưa có task-analysis.yaml
4. **Classify trước khi đọc rộng** — Xác định `target_scope` trước; framework maintenance không cần onboarding trong framework-template mode
5. **Context economy** — Với applied-service work, đọc `.runtime/context/index.yaml` trước, dùng `project_profile`, service `profile.context_hints`, và `task-analysis.yaml.context_plan`; chỉ mở rộng context khi có trigger/evidence gap
6. **Model routing** — Chọn model profile từ `.runtime/context/model-routing.yaml`; reasoning sâu dùng Opus/GPT-5.5, coding dùng Sonnet/Codex coding theo adapter
7. **Activity dashboard** — `/status` đọc `.runtime/context/agent-activity.yaml` để hiển thị agent đang làm gì, elapsed/ETA, token budget/usage/cost khi biết
8. **Response UI** — Format status/models/review/dev/policy/final answers theo `.runtime/context/response-ui.yaml`, nhưng không bịa metric và không giấu evidence bắt buộc
9. **Deterministic drift check** — `scripts/architecture-health-check.py --strict` bắt drift counts/model/UI/entrypoint; không thay thế `/policy-check`
10. **Scoped coders** — Generated coders chỉ write trong allowed paths
11. **Approval gates** — Tạo coder agents, expand scope, skip QC cần user approval
12. **Feedback loop** — Sau mọi workflow event, memory-update ghi learnings vào `.runtime/context` và refresh memory index

---

## Memory / Inputs / Services / State System

```text
.agent/                        ← Tool-neutral workflow source
├── workflow.md                ← End-to-end workflow policy
├── rules/                     ← 18 workflow rules
├── templates/                 ← 22 artifact templates
└── docs/                      ← Visual diagrams & documentation
    └── diagrams/*.svg         ← SVG workflow diagrams

.runtime/                      ← Runtime memory and workflow artifacts
├── context/                   ← Durable project brain + service contracts + workflow state
│   ├── index.yaml             ← Read first to avoid full memory rereads
│   ├── project-brain.yaml     ← Project memory
│   ├── inputs-index.yaml      ← Index of files under inputs/ (auto-generated by onboarding)
│   ├── service-catalog.yaml   ← Service paths and boundaries
│   ├── agent-registry.yaml    ← Active coder agents
│   ├── test-policy.yaml       ← Test requirements
│   ├── skill-registry.yaml    ← Stack skill selection
│   ├── model-routing.yaml     ← Agent model profile routing
│   ├── agent-activity.yaml    ← Status dashboard + token/cost telemetry
│   ├── response-ui.yaml       ← Response layout modes
│   ├── workflow-state.yaml    ← Transient workflow state
│   ├── services/              ← Per-service brains
│   └── feedback/              ← Patterns + anti-patterns
├── status.md                  ← Generated status artifact
├── status.html                ← Generated status dashboard
├── tasks/                     ← Task tracking + artifacts
├── bugs/                      ← Bug tracking

.claude/                       ← Claude adapter
├── agents/*.agent.md          ← 12 workflow agents + built-in/generated coders
├── skills/*/SKILL.md          ← 231 skill definitions
├── commands/                  ← 17 workflow commands
└── settings.json              ← Claude Code settings

inputs/                        ← USER drops reference docs here (onboarding scans recursively)
├── product/                   PRD, business specs, user stories
├── architecture/              HLD, LLD, ADRs, system diagrams
├── api/                       OpenAPI/Swagger specs, contracts
├── domain/                    Domain models, glossary, business rules
├── runbooks/                  Ops playbooks, incident response
└── misc/                      Uncategorized

services/                      ← Ignored workspace for cloned application repositories
```
