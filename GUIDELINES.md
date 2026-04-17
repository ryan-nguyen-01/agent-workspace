# Guidelines — agent-platform (Single Source of Truth)

Mục tiêu của file này: **giảm nhầm lẫn khi dùng thực tế** và thống nhất cách hiểu giữa:

- `.claude/` (definitions: agents, skills, rules, templates, commands + runtime context)
- `CLAUDE.md` (entrypoint + workflow routing)

---

## Quick start (cách dùng nhanh nhất)

Bạn có 2 cách gọi:

### 1) Slash commands (khuyến nghị nhất)

Dùng commands tại `.claude/commands/`:

```
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
/policy-check      → Validate workflow policy
/coord             → Coordinator direct
/status            → Check workflow status
/resume-task       → Resume interrupted task
```

### 2) Ngôn ngữ tự nhiên

Coordinator tự route đến đúng workflow agent:

```
"Phân tích dự án này"                    → coordinator → onboarding
"Thêm tính năng login"                  → coordinator → task-analysis → coder-leader → ...
"Kiểm tra code sẵn sàng chưa"           → coordinator → dev-verification
"Test tính năng vừa implement"           → coordinator → qc-runner
"Report bug trong payment module"        → coordinator → bug-router
```

> Lưu ý: `@` trong Claude Code dùng để **reference files**, không phải gọi agent.

---

## File/folder semantics (đúng khái niệm)

### `.claude/` — definitions (ship kèm repo / có thể cài global)

```
.claude/
├── agents/*.agent.md          ← 11 workflow agent definitions
├── skills/*/SKILL.md          ← 227 skill definitions
├── rules/{nn}-{name}.md       ← 15 workflow rules
├── templates/*.template.*     ← 13 artifact templates
├── commands/*.md              ← 15 workflow commands
├── docs/                      ← Documentation + 8 SVG workflow diagrams
├── context/                   ← Runtime context (per project, auto-generated)
├── tasks/                     ← Task tracking + artifacts
└── bugs/                      ← Bug tracking
```

- Có thể:
  - **Local**: copy vào project để mọi người dùng chung
  - **Global**: copy vào `~/.claude/` (hoặc `C:\Users\<user>\.claude\`)

### `CLAUDE.md` — entrypoint + routing

- Claude đọc file này trước để hiểu workflow, routing, và nguyên tắc autonomy.
- Chứa: bảng agents, workflow phases, commands, rules, context system.

### `.claude/context/` — runtime context (per project, tự sinh)

- **Tự sinh ra** khi onboarding agent scan project.
- Chứa context giúp agents làm việc:
  - `project-brain.yaml` — Project memory
  - `service-catalog.yaml` — Service inventory
  - `agent-registry.yaml` — Active coder agents
  - `test-policy.yaml` — Test requirements
  - `services/` — Per-service brains
  - `feedback/` — Patterns + anti-patterns
- Khuyến nghị: ignore trong git.

---

## Routing — nguyên tắc

- **Coordinator là central router** — mọi task đi qua coordinator
- Coordinator đọc project brain → xác định workflow phase → route đến agent phù hợp
- Workflow tuần tự: task-analysis → coder-leader → dev-verification → QC → memory-update
- **Approval gates**: tạo coder agents, expand scope, skip QC cần user approval
- **Task-analysis trước code**: không có task-analysis.yaml = không code

---

## Token & context policy (context-first)

Mục tiêu: **ít token, vẫn đúng** — đọc `.claude/context/` trước khi scan repo.

### Coordinator

- Đọc theo thứ tự: `project-brain.yaml` → `service-catalog.yaml` → `agent-registry.yaml`
- Chỉ scan source code khi context files không đủ thông tin
- Route đến đúng agent dựa trên task type

### Service coders (generated)

- Chỉ nhận scoped context từ coder-leader
- Chỉ write trong allowed paths (scoped per service)
- Đọc service brain trước khi implement

Chi tiết: `.claude/agents/coordinator.agent.md`, `.claude/agents/coder-leader.agent.md`

---

## Generated agents (service coders)

- Chỉ **agent-factory** được quyền tạo generated coder agents
- Cần **user approval** trước khi tạo
- Generated coders ghi vào `.claude/agents/coder-{service}.agent.md`
- Service brains ghi vào `.claude/context/services/{service}-brain.yaml`
- Mỗi coder scoped: chỉ write trong allowed paths của service đó

---

## Khi nào sửa file nào?

- **Muốn đổi workflow routing / nguyên tắc** → sửa `CLAUDE.md`
- **Muốn đổi vai trò agent** → sửa `.claude/agents/{role}.agent.md`
- **Muốn đổi workflow rules** → sửa `.claude/rules/{nn}-{name}.md`
- **Muốn đổi best practices chuyên môn** → sửa `.claude/skills/{skill}/SKILL.md`
- **Muốn đổi cách setup cho người dùng** → sửa `SETUP.md`
- **Muốn overview ngắn** → sửa `README.md`

---

## Maintenance checklist (để docs không bị lệch)

### Khi thêm/sửa workflow agent

- Thêm/sửa `.claude/agents/{role}.agent.md`
- Cập nhật bảng agents trong `CLAUDE.md`
- Nếu có command mới → thêm `.claude/commands/{name}.md`
- Nếu có rule mới → thêm `.claude/rules/{nn}-{name}.md`

### Khi thêm/sửa skill

- Thêm/sửa `.claude/skills/{skill}/SKILL.md`
- Workflow skills dùng prefix `skill-`, technical skills dùng tên gốc

### Khi thêm/sửa rule

- Thêm/sửa `.claude/rules/{nn}-{name}.md`
- Đảm bảo numbered prefix liên tục (00-14)
- Cập nhật rules table trong `CLAUDE.md`

### Khi thay đổi context system

- Cập nhật `.claude/agents/onboarding.agent.md` (nếu đổi cách scan)
- Cập nhật templates tương ứng trong `.claude/templates/`
- Cập nhật context tree trong `CLAUDE.md` và `GUIDELINES.md`

### Khi đổi counts (thêm/xóa resources)

- Sync counts across: `README.md`, `CLAUDE.md`, `SETUP.md`, `GUIDELINES.md`
- Hiện tại: 11 agents, 227 skills, 15 rules (16 files including README), 13 templates, 15 commands
