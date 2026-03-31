# Guidelines — agent-platform (Single Source of Truth)

Mục tiêu của file này: **giảm nhầm lẫn khi dùng thực tế** và thống nhất cách hiểu giữa:
- `.claude/` (definitions: agents/skills)
- `.agent/` (runtime context per project)
- `CLAUDE.md` (entrypoint + routing)

---

## Quick start (cách dùng nhanh nhất)

Bạn có 3 cách gọi:

### 1) Alias ngắn (khuyến nghị nhất)

Format: `<alias>: <task>`

```
sa: thiết kế kiến trúc + API contract
ba: viết user stories + acceptance criteria
qa: viết test plan + checklist release
pm: lập roadmap + kế hoạch release
sec: threat model / security review
sre: infra/ops/monitoring/incident
dev: implement/build/ship (orchestrator)
```

### 2) Ngôn ngữ tự nhiên

```
"Thiết kế kiến trúc cho hệ thống e-commerce"  → agent-sa
"Review bảo mật module payment"              → agent-security
"Setup monitoring cho production"            → agent-sre
```

### 3) Explicit agent name

```
"agent-sa: thiết kế microservices cho dự án này"
"agent-reviewer: review PR này"
```

> Lưu ý: `@` trong Claude Code dùng để **reference files**, không phải gọi agent.

---

## File/folder semantics (đúng khái niệm)

### `.claude/` — definitions (ship kèm repo / có thể cài global)

- **Chứa definitions**: `.claude/agents/**/SKILL.md`, `.claude/skills/**/SKILL.md`
- Có thể:
  - **Local**: copy vào project để mọi người dùng chung
  - **Global**: copy vào `~/.claude/` (hoặc `C:\Users\<user>\.claude\`)

### `CLAUDE.md` — entrypoint + routing

- Claude đọc file này trước để hiểu “company” và **routing rules**.
- Nơi tốt nhất để đặt:
  - alias (`sa:`, `qa:`, …)
  - rule keyword routing
  - default fallback về `agent-orchestrator`

### `.agent/` — runtime context (per project, thường không commit)

- **Tự sinh ra** khi onboarding/chạy orchestrator.
- Dùng để lưu context ngắn gọn giúp agents làm việc ổn định, ví dụ:
  - `context/summary.md`, `context/conventions.md`, `context/available-agents.md`
- Khuyến nghị: ignore trong git (xem `docs/team-setup-agent-context.md`).

---

## Routing rules — nguyên tắc để tránh hiểu nhầm

- **Ưu tiên**:
  - Alias (`sa:`/`qa:`/...) nên được đặt **trước** các rule keyword chung.
  - Các rule “mơ hồ” (vd `build`, `ship`, `help me`) sẽ route về orchestrator.
- **Khi cần chắc chắn 100%**:
  - Dùng alias hoặc explicit `"agent-xxx: ..."`

---

## Token & context policy (context-first)

Mục tiêu: **ít token, vẫn đúng** — không đọc repo trước khi thử `.agent/`.

### Orchestrator (mặc định hệ thống)

- Đọc theo thứ tự cố định: `summary` → `available-agents` → `conventions` → (đoạn liên quan) `architecture` → `task-board` / `dirty-flags`.
- Nếu `dirty-flags` có `pending_trigger` (từ git hook) hoặc `dirty_sections` → gọi **agent-context-keeper** (delta sync) **trước** breakdown task.
- Chỉ mở source code khi `.agent/` không đủ; task `complex` giới hạn mở rộng có trần (xem `agent-orchestrator/SKILL.md`).

### Worker agents

- Chỉ nhận **injected package** từ orchestrator (400 / 500 / 600 tokens tuỳ complexity), không tự quét toàn repo.

### Git hooks

- Hooks chỉ **đánh dấu** cần sync; **đồng bộ delta** khi context-keeper được invoke (sau commit có thể là bước tiếp theo của orchestrator hoặc lệnh manual).

Chi tiết implement: `.claude/agents/agent-orchestrator/SKILL.md`, `.claude/agents/agent-context-keeper/SKILL.md`.

---

## Generated agents (coder/devops) — đúng chỗ, đúng tên

- Chỉ `agent-builder` được quyền tạo generated agents.
- Generated agents phải được ghi vào:
  - Local: `<project>/.claude/agents/`
  - Global: `~/.claude/agents/`
- Không ghi vào `.agent/agents/` (sai tầng dữ liệu).

---

## Khi nào sửa file nào?

- **Muốn đổi cách gọi / alias / routing** → sửa `CLAUDE.md`
- **Muốn đổi vai trò/quy trình agent** → sửa `.claude/agents/<agent>/SKILL.md`
- **Muốn đổi best practices chuyên môn** → sửa `.claude/skills/<skill>/SKILL.md`
- **Muốn đổi cách setup cho người dùng** → sửa `SETUP.md`
- **Muốn overview ngắn + link tài liệu** → sửa `README.md`

---

## Maintenance checklist (để docs không bị lệch)

### Khi đổi alias / routing

- Cập nhật `CLAUDE.md` (alias + rule)
- Cập nhật ví dụ gọi nhanh trong `SETUP.md` (section “Cách 0”)
- Cập nhật ví dụ trong `README.md` (Getting Started → Sử dụng)

### Khi thêm/sửa core agent

- Thêm/sửa `.claude/agents/<agent>/SKILL.md`
- Cập nhật bảng agents trong `CLAUDE.md` và `.claude/agents/README.md` (nếu thay đổi role/trigger)
- Nếu agent mới có “cách gọi đặc biệt” (alias mới) → cập nhật `GUIDELINES.md`

### Khi thêm/sửa skill

- Thêm/sửa `.claude/skills/<skill>/SKILL.md`
- Đảm bảo ít nhất 1 agent equip skill đó (agent SKILL.md)
- Nếu skill là “foundational” (vd security-hardening) → cân nhắc thêm vào reviewer/security

### Khi thay đổi semantics `.agent/` context

- Cập nhật `.claude/agents/agent-context-keeper/SKILL.md`
- Cập nhật `docs/team-setup-agent-context.md` (team rules: ignore/commit)
- Cập nhật `GUIDELINES.md` (mục semantics) nếu có thay đổi hành vi

### Khi đổi policy token / context-first

- Cập nhật `.claude/agents/agent-orchestrator/SKILL.md` (nguồn chi tiết)
- Đồng bộ tóm tắt trong `GUIDELINES.md` (mục Token & context policy)
- Cập nhật `CLAUDE.md` (Nguyên tắc) nếu thay đổi nguyên tắc toàn cục

