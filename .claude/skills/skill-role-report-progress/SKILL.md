---
name: skill-role-report-progress
description: Theo dõi và báo cáo tiến độ của tất cả agents đang chạy cho user. Chỉ đọc progress.md, output ngắn gọn và scannable.
---

# Skill: Report Progress

## Mục đích
Báo user biết đang chuyện gì xảy ra: agent nào đang làm gì, tiến độ đến đâu, có blocker không. Chỉ đọc `.agent/progress.md` — không đọc source code hay docs.

## Nguyên tắc
- Ngắn gọn: user không cần đọc essay
- Scannable: dùng icons, không phải paragraphs
- Chính xác: không đoán mò — chỉ report những gì có trong progress.md
- Escalate ngay khi có blocker — không chờ

## Icons chuẩn
```
🚀  Starting / Spawning
⚙️  In progress / Running
✅  Completed
⏳  Waiting for dependency
🚨  Blocked — cần user action
❌  Failed
📊  Summary
```

## Report Templates

### Khi task bắt đầu
```
🚀 [agent-coder-nestjs] Bắt đầu: Create login endpoint
```

### Khi đang chạy (parallel agents)
```
Đang chạy:
  ⚙️  agent-coder-nestjs    → Create LoginDto         [60%]
  ⚙️  agent-coder-nestjs    → Create validateUser()   [40%]
  ⏳  agent-tester-jest     → Write tests             [chờ coder xong]
```

### Khi 1 task hoàn thành
```
✅ [agent-coder-nestjs] Xong: Create LoginDto (src/auth/dto/login.dto.ts)
```

### Khi có blocker — báo ngay
```
🚨 BLOCKER — [agent-coder-nestjs] không thể tiếp tục

Lý do: Dependency 'bcrypt' chưa được install
Cần làm: Chạy `npm install bcrypt` rồi retry

Task bị chặn: T-002 (Create validateUser)
Chờ từ: 14:32:05
```

### Khi review fail
```
🔄 REVIEW FAILED — [agent-reviewer] phát hiện issues

Critical (phải fix):
  • Line 23: Hardcoded JWT secret → Move to .env

Major (nên fix):
  • Line 45: Missing null check on user object

→ Đã gửi lại cho agent-coder-nestjs để fix
```

### Summary khi tất cả hoàn thành
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Hoàn thành: Tính năng đăng nhập
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tasks: 5/5 ✅
Files thay đổi:
  • src/auth/dto/login.dto.ts
  • src/auth/auth.service.ts
  • src/auth/auth.controller.ts
  • src/auth/auth.service.spec.ts
Agents đã dùng: agent-coder-nestjs, agent-tester-jest, agent-reviewer
Review: Pass ✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Quy trình đọc progress.md

```yaml
# Đọc .agent/progress.md
active_agents:
  - id: agent-001
    type: agent-coder-nestjs
    task: "Create LoginDto"
    status: running
    progress_pct: 60
    started_at: 14:30:00

completed_tasks:
  - task: "Analyze requirements"
    agent: agent-analyst
    completed_at: 14:29:45

blockers:
  - agent: agent-coder-nestjs
    reason: "Missing bcrypt package"
    since: 14:32:05
```

### Logic quyết định loại report
```
IF blockers not empty → báo BLOCKER ngay (ưu tiên cao nhất)
ELSE IF all tasks done → báo SUMMARY
ELSE IF multiple agents running → báo PARALLEL VIEW
ELSE → báo task vừa hoàn thành hoặc bắt đầu
```

## Tần suất báo cáo

```
Báo ngay:              Blocker, task completed, task failed
Báo mỗi milestone:    Task bắt đầu, review result
Không báo liên tục:   Progress percentage (chỉ hiện khi có parallel agents)
```

## Ghi vào progress.md sau khi report

```yaml
# Append
reports_sent:
  - type: blocker | progress | completion | summary
    timestamp: <now>
    content: <1 line tóm tắt>
```
