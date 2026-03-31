---
name: skill-context-read
description: Đọc context từ .agent/ một cách chính xác và hiệu quả. Chỉ đọc đúng phần cần thiết, không đọc toàn bộ.
---

# Skill: Read Agent Context

## Mục đích
Đọc thông tin từ `.agent/` directory một cách có chọn lọc. **Không bao giờ đọc toàn bộ** — chỉ đọc đúng file cần thiết cho task hiện tại.

## Nguyên tắc
- Luôn đọc `summary.md` trước — đây là file nhỏ nhất, cung cấp overview
- Chỉ đọc thêm file khác nếu task thực sự cần
- Không đọc source code gốc — mọi thứ đã được compress vào `.agent/`
- Kiểm tra `dirty-flags.md` trước khi đọc — nếu dirty thì báo Orchestrator sync trước

## Thứ tự đọc theo loại task

### Task liên quan đến code mới
```
1. .agent/context/summary.md          (luôn đọc)
2. .agent/context/conventions.md      (cần biết naming, imports)
3. .agent/context/modules/<tên>.md    (chỉ module liên quan)
```

### Task liên quan đến architecture
```
1. .agent/context/summary.md
2. .agent/context/architecture.md
```

### Task liên quan đến test
```
1. .agent/context/conventions.md      (test framework, naming pattern)
2. .agent/context/modules/<tên>.md    (exports của module cần test)
```

### Task review code
```
1. .agent/context/conventions.md      (chỉ cần conventions)
```

### Task báo cáo tiến độ
```
1. .agent/progress.md                 (chỉ đọc file này)
```

## Cách đọc đúng

```
✅ Đúng: Đọc summary.md (300 tokens) + 1 module file (150 tokens) = ~450 tokens
❌ Sai:  Đọc toàn bộ .agent/ = ~2000 tokens không cần thiết
```

## Kiểm tra dirty flags trước khi đọc

```yaml
# Đọc .agent/dirty-flags.md
# Nếu section liên quan đến task của bạn nằm trong dirty list:
dirty:
  - section: modules/auth
    reason: auth.ts changed in last commit

# → Báo Orchestrator: "Context for auth module is stale, need sync"
# → Không làm việc với stale context
```

## Output sau khi đọc
Trả về structured summary của những gì đã đọc:
```yaml
context_loaded:
  files_read: [summary.md, conventions.md, modules/auth.md]
  total_tokens: ~450
  relevant_facts:
    - project: MyApp, stack: NestJS + React
    - auth module path: src/auth/
    - naming: camelCase, imports: absolute
```
