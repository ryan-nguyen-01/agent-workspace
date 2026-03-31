# Team setup guide — `.agent/` (runtime context)

Mục tiêu: để cả team dùng agent-platform mà **không tạo noise trong git**, đồng thời vẫn giữ được context local hữu ích.

---

## Nguyên tắc

- `.claude/` là **platform definitions** (agents/skills): có thể cài global hoặc commit local theo repo (tuỳ team).
- `.agent/` là **runtime context**, do onboarding/context-keeper tạo ra: thường **không nên commit** (trừ khi team muốn share snapshot có kiểm soát).

---

## Khuyến nghị mặc định (đa số teams)

### 1) Ignore `.agent/` trong git

Thêm vào `.gitignore` của project:

```
.agent/
```

### 2) Giữ lại template tối thiểu (tuỳ chọn)

Nếu muốn có structure rỗng để ai cũng biết hệ thống dùng gì, có thể commit:

```
.agent/.keep
.agent/context/.keep
.agent/context/feedback/.keep
```

---

## Khi nào nên commit `.agent/`

Chỉ nên commit nếu:
- repo không có docs, cần “context bootstrap” cho tất cả thành viên
- muốn dùng `.agent/context/*` như tài liệu sống (living docs)

Nếu commit, khuyến nghị:
- chỉ commit **read-only artifacts**: `summary.md`, `architecture.md`, `conventions.md`
- không commit progress/task-board (thay đổi liên tục)

Suggested policy:

```
commit_allowlist:
  - .agent/context/summary.md
  - .agent/context/architecture.md
  - .agent/context/conventions.md
  - .agent/context/existing-docs.md
denylist:
  - .agent/progress.md
  - .agent/task-board.md
  - .agent/dirty-flags.md
  - .agent/changelog.md
```

---

## Monorepo notes

Nếu monorepo (turborepo/nx/pnpm workspaces):
- Giữ `.agent/` ở root workspace
- Context per-app lưu trong `modules/` hoặc file naming theo app

---

## Workflow đề xuất cho team

1) Mỗi dev cài global `.claude/` (hoặc project local)  
2) Onboarding chạy 1 lần tạo `.agent/` local  
3) `.agent/` bị ignore → không ảnh hưởng PRs  
4) Khi cần share, trích xuất summary vào docs chính thức (`docs/architecture.md`)  
5) Khi codebase đổi nhiều: chủ động nhờ **agent-context-keeper** sync (hoặc mở task orchestrator) để `dirty-flags` được xử lý — **không** bắt buộc git hooks trong bản platform tối giản này.

