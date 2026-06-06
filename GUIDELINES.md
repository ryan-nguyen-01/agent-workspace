# Guidelines — agent-workspace (Single Source of Truth)

Mục tiêu của file này: **giảm nhầm lẫn khi dùng thực tế** và thống nhất cách hiểu giữa các lớp chính:

- `.agent/` (workflow source: workflow, rules, templates, docs)
- `.runtime/` (runtime memory, task artifacts, bug records)
- `.claude/` (Claude adapter: agents, skills, commands, settings)
- `CLAUDE.md` (entrypoint + workflow routing)

---

## Quick start (cách dùng nhanh nhất)

Bạn có 2 cách gọi:

### 1) Slash commands (khuyến nghị nhất)

Dùng commands tại [COMMAND.md](COMMAND.md):

```text
/onboard           → Scan project, tạo project brain
/analyze-task      → Normalize task thành spec
/create-coders     → Tạo service coder agents
/plan-dev          → Lên plan implementation
/dev               → Implement code
/verify-dev        → Check Code Done
/handoff-qc        → Tạo QC handoff document
/qc                → Run QC tests
/bug               → Route bug report
/sync-memory       → Update memory
/skills            → Maintain installed skills
/policy-check      → Validate workflow policy
/coord             → Coordinator direct
/status            → Check workflow status + agent activity dashboard
/resume-task       → Resume interrupted task
```

### 2) Ngôn ngữ tự nhiên

Coordinator tự route đến đúng workflow agent:

```text
"Phân tích dự án này"                    → coordinator → onboarding
"Thêm tính năng login"                  → coordinator → task-analysis → coder-leader → ...
"Kiểm tra code sẵn sàng chưa"           → coordinator → dev-verification
"Test tính năng vừa implement"           → coordinator → qc-runner
"Report bug trong payment module"        → coordinator → bug-router
```

> Lưu ý: `@` trong Claude Code dùng để **reference files**, không phải gọi agent.

---

## File/folder semantics (đúng khái niệm)

### `.agent/` — workflow source

```text
.agent/
├── workflow.md                ← End-to-end workflow policy
├── rules/{nn}-{name}.md       ← 19 workflow rules
├── templates/*.template.*     ← 22 artifact templates
└── docs/                      ← Documentation + SVG workflow diagrams
```

### `.runtime/` — runtime memory + artifacts

```text
.runtime/
├── context/                   ← Project brain, service contracts, workflow state, model/status/response UI telemetry
├── tasks/                     ← Task tracking + artifacts
└── bugs/                      ← Bug tracking
```

### `.claude/` — Claude adapter

```text
.claude/
├── agents/*.agent.md          ← 12 workflow agents + built-in/generated coders
├── skills/*/SKILL.md          ← 231 skill definitions
├── commands/*.md              ← 17 workflow commands
└── settings.json              ← Claude Code settings
```

- Không copy `.claude/`, `.agent/`, hoặc `.runtime/` sang từng service repo.
- Mở chính workspace `agent-workspace`; clone application repositories vào `services/<service-name>/`.
- `.runtime/` chứa context/task artifacts của workspace điều phối, không phải `.claude/`.

### `CLAUDE.md` — entrypoint + routing

- Claude đọc file này trước để hiểu workflow, routing, và nguyên tắc autonomy.
- Chứa: bảng agents, workflow phases, commands, rules, context system.

### Tool-specific entrypoints

- `AGENTS.md` — entrypoint chung cho Codex, Cursor, Gemini, Aider, Continue, Cody.
- `.codex/AGENTS.md` — Codex-specific routing and task contract.
- `.cursor/rules/agent-workspace.mdc` — Cursor always-on rule.
- `.gemini/GEMINI.md` — Gemini-specific routing and task contract.
- `.github/copilot-instructions.md` — GitHub Copilot instructions.

### `.runtime/context/` — agent brain + service control plane

- **Tự sinh ra** khi onboarding agent scan project.
- Chứa memory và registry giúp agents làm việc:
  - `index.yaml` — đọc trước để chọn đúng memory file, tránh đọc toàn bộ
  - `project-brain.yaml` — Project memory
  - `service-catalog.yaml` — service.path, boundaries, agent candidates
  - `agent-registry.yaml` — Active coder agents
  - `test-policy.yaml` — Test requirements
  - `skill-registry.yaml` — Skill selection registry
  - `workflow-state.yaml` — Current workflow state
  - `services/<service>.yaml` — Per-service brains
  - `feedback/` — Patterns + anti-patterns

### `inputs/` — user-provided reference docs

- User drop tài liệu project-level (PRD, HLD, ADR, OpenAPI specs, domain glossary, runbooks) vào đây.
- Onboarding scan recursively, cite source vào `.runtime/context/project-brain.yaml` + `inputs-index.yaml`.
- Subdirs: `product/`, `architecture/`, `api/`, `domain/`, `runbooks/`, `misc/`. Có thể để rỗng.
- Khi nội dung thay đổi: chạy `/sync-memory --refresh-index` để agent re-scan.
- **Khác với** `.runtime/tasks/<id>/task-input.md` (input theo từng task).

### `services/` — local clone workspace

- Thư mục rỗng/ignored để user `cd services` rồi clone source service vào.
- Không cần file scaffold trong `services/`; framework template vẫn hợp lệ khi thư mục này rỗng.
- Không lưu memory, registry, hoặc workflow state ở đây.
- Không đẩy source code service lên repo `agent-workspace`.

---

## Routing — nguyên tắc

- **Coordinator là central router** — mọi task đi qua coordinator
- Coordinator đọc memory index + project brain khi cần → xác định workflow phase → route đến agent phù hợp
- Workflow tuần tự: task-analysis → coder-leader → dev-verification → QC → memory-update
- **Không chắc thì hỏi, không đoán** — nếu thiếu dữ kiện ảnh hưởng correctness/security/scope thì hỏi user, không bịa facts/evidence
- **Approval gates**: tạo coder agents, expand scope, skip QC cần user approval
- **Task-analysis trước code**: không có task-analysis.yaml = không code
- **Model routing/status/response UI**: model profile lấy từ `.runtime/context/model-routing.yaml`, `/status` đọc `.runtime/context/agent-activity.yaml`, response format đọc `.runtime/context/response-ui.yaml`; `scripts/agent-activity.py` cập nhật telemetry, `scripts/status-dashboard.py --write` tạo `.runtime/status.md/.html`, `scripts/architecture-health-check.py --strict` bắt drift deterministic

---

## Token & memory policy (memory-first)

Mục tiêu: **ít token, vẫn đúng** — đọc `.runtime/context/index.yaml` trước khi mở memory chi tiết hoặc scan repo.

### Coordinator

- Đọc theo thứ tự: `.runtime/context/index.yaml` → `.runtime/context/workflow-state.yaml` → `.runtime/context/project-brain.yaml` khi cần → `.runtime/context/service-catalog.yaml` / `.runtime/context/agent-registry.yaml` khi task cần code
- Chỉ scan source code khi memory/service files không đủ thông tin hoặc bị stale
- Route đến đúng agent dựa trên task type

### Service coders (generated)

- Chỉ nhận scoped memory/task context từ coder-leader
- Chỉ write trong allowed paths (scoped per service)
- Đọc service brain trước khi implement, nhưng chỉ service liên quan

Chi tiết: `.claude/agents/workflow/coordinator.agent.md`, `.claude/agents/workflow/coder-leader.agent.md`

---

## Generated agents (service coders)

- Chỉ **agent-factory** được quyền tạo generated coder agents
- Cần **user approval** trước khi tạo
- Generated coders ghi vào `.claude/agents/coders/coder-{service}.agent.md`
- Service brains ghi vào `.runtime/context/services/{service}.yaml`
- Service coding contracts ghi vào `.runtime/context/`
- Mỗi coder scoped: chỉ write trong allowed paths của service đó

---

## Khi nào sửa file nào?

- **Muốn đổi workflow routing / nguyên tắc** → sửa `CLAUDE.md`
- **Muốn đổi vai trò agent** → sửa `.claude/agents/{role}.agent.md`
- **Muốn đổi workflow rules** → sửa `.agent/rules/{nn}-{name}.md`
- **Muốn đổi best practices chuyên môn** → dùng `/skills update <skill>` để sửa skill + lock/registry liên quan
- **Muốn đổi cách setup cho người dùng** → sửa `SETUP.md`
- **Muốn overview ngắn** → sửa `README.md`

---

## Maintenance checklist (để docs không bị lệch)

### Khi thêm/sửa workflow agent

- Thêm/sửa `.claude/agents/{role}.agent.md`
- Cập nhật bảng agents trong `CLAUDE.md`
- Nếu có command mới → thêm `.claude/commands/{name}.md`
- Nếu có rule mới → thêm `.agent/rules/{nn}-{name}.md`

### Khi thêm/sửa skill

- Dùng `/skills status` hoặc `/skills audit` trước khi sửa
- Dùng `/skills update <skill>` cho skill hiện có, hoặc `/skills refresh-registry` sau khi thêm skill mới
- Cập nhật `skills-lock.json`, `.runtime/context/skill-registry.yaml`, `.agent/docs/external-skills.md`, và `CHANGELOG.md` nếu behavior/risk thay đổi
- Workflow skills dùng prefix `skill-`, technical skills dùng tên gốc

### Khi thêm/sửa rule

- Thêm/sửa `.agent/rules/{nn}-{name}.md`
- Đảm bảo numbered prefix liên tục (00-18)
- Cập nhật rules table trong `CLAUDE.md`

### Khi thay đổi .runtime/context/ system

- Cập nhật `.claude/agents/workflow/onboarding.agent.md` (nếu đổi cách scan)
- Cập nhật templates tương ứng trong `.agent/templates/`
- Cập nhật runtime tree trong `CLAUDE.md` và `GUIDELINES.md`

### Khi đổi counts (thêm/xóa resources)

- Sync counts across: `README.md`, `CLAUDE.md`, `SETUP.md`, `GUIDELINES.md`
- Hiện tại: 12 workflow agents + 2 built-in coders + 19 specialist advisors, 231 skills, 19 rules (20 files including README), 22 templates, 17 commands
