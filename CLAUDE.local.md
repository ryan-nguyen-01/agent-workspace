# CLAUDE.local.md — Project-Specific Overrides

#

# File này dành cho **project khách** — ghi đè hoặc bổ sung cấu hình

# riêng cho project cụ thể mà không sửa CLAUDE.md gốc.

#

# CLAUDE.md chứa workflow routing + agent definitions (đừng sửa).

# File này chứa local overrides cho project hiện tại.

#

# Cách dùng:

# 1. Copy file này vào root project khách cùng CLAUDE.md

# 2. Uncomment và chỉnh sửa các section bên dưới

# 3. Claude sẽ đọc cả CLAUDE.md + CLAUDE.local.md

---

## Project Info

<!-- Uncomment và điền thông tin project khách -->
<!--
project:
  name: "my-project"
  type: "monorepo | single-service | library"
  primary_language: "TypeScript | Python | Go | Java | ..."
  framework: "NestJS | FastAPI | Spring Boot | Next.js | ..."
  database: "PostgreSQL | MongoDB | MySQL | ..."
-->

---

## Custom Workflow Overrides

<!-- Uncomment để ghi đè workflow defaults -->
<!--
### Skip QC (cho prototype / spike)
qc_required: false

### Custom Code Done threshold
code_done_threshold: 0.70

### Disable memory updates
memory_updates: false
-->

---

## Additional Instructions

<!-- Thêm instructions riêng cho project -->
<!--
- Luôn dùng pnpm thay npm
- Test coverage tối thiểu 80%
- Commit message format: conventional commits
- Branch naming: feature/TASK-xxx-description
-->

---

## Custom Routing

<!-- Thêm routing rules riêng nếu project có agent/skill đặc biệt -->
<!--
routing_overrides:
  - match: ["payment", "thanh toán"]
    agent: coder-payment
    note: "Route payment tasks to dedicated coder"
-->

---

## Environment Notes

<!-- Ghi chú môi trường dev -->
<!--
- Dev server: http://localhost:3000
- Database: PostgreSQL on localhost:5432
- Redis: localhost:6379
- API docs: http://localhost:3000/api/docs
-->
