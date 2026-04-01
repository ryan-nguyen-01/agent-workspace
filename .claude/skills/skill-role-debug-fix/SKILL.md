---
name: skill-role-debug-fix
description: Skill chẩn đoán và fix errors — đọc error message, trace root cause, áp dụng fix đúng chỗ, verify lại. Dùng cho coder agent khi gặp runtime error, compile error, test failure.
---

# Skill: Debug & Fix Error

## Mục đích
Trang bị cho coder agent khả năng tự xử lý errors thay vì dừng lại và hỏi user. Áp dụng khi: compile error, runtime exception, test failure, type error, dependency conflict.

---

## Quy trình (4 bước bắt buộc)

### Bước 1 — READ THE ERROR (không đoán)

```
1. Đọc toàn bộ error message — không bỏ qua stack trace
2. Xác định:
   - Error type: compile | runtime | test | type | dependency
   - File + line number bị ảnh hưởng
   - Root cause message (thường ở dòng đầu hoặc "Caused by:")
3. KHÔNG fix ngay — hiểu xong mới fix
```

### Bước 2 — LOCATE ROOT CAUSE

```
Compile error:
  → Đọc file + dòng được chỉ ra
  → Kiểm tra: import missing? type mismatch? syntax sai?

Runtime exception:
  → Đọc stack trace từ dưới lên (innermost cause)
  → Xác định: null/undefined access? wrong type? network? DB?

Test failure:
  → Đọc: expected vs received
  → Xác định: logic sai? mock thiếu? data setup sai?

Type error (TypeScript):
  → Đọc: "Type X is not assignable to type Y"
  → Xác định: missing field? wrong interface? generics sai?

Dependency conflict:
  → Đọc: peer dependency warnings, version mismatch
  → Xác định package nào conflict
```

### Bước 3 — APPLY FIX

```
Nguyên tắc fix:
  ✅ Fix root cause — không fix symptom
  ✅ Fix tại đúng file/dòng — không patch ở nơi khác
  ✅ Giữ nguyên logic xung quanh — không refactor thêm
  ✅ Nếu fix cần thay đổi interface → update tất cả callers

Fix patterns theo error type:

  NULL/UNDEFINED:
    Bad:  user.name         → crash nếu user null
    Good: user?.name ?? ''  → safe access

  MISSING IMPORT:
    → Tìm đúng module export symbol đó
    → Thêm import — dùng absolute path theo convention của project

  TYPE MISMATCH:
    → Không dùng `as any` để ép kiểu
    → Sửa type definition hoặc transform data đúng kiểu

  ASYNC/AWAIT:
    Bad:  return fetchData()        → Promise chưa resolve
    Good: return await fetchData()  → đúng

  UNHANDLED PROMISE:
    Bad:  asyncFn().catch(console.log)  → error bị nuốt
    Good: try { await asyncFn() } catch(e) { throw new AppError(e) }

  CIRCULAR DEPENDENCY:
    → Tách interface ra file riêng
    → Import interface thay vì concrete class

  ENV/CONFIG MISSING:
    → Kiểm tra .env.example có key đó không
    → Thêm validation ở startup, không để crash ở runtime
```

### Bước 4 — VERIFY

```
Sau khi fix:
  1. Re-read lại đoạn code vừa fix — tự review
  2. Kiểm tra: fix này có tạo ra error mới không?
  3. Nếu có test liên quan → chạy lại test đó
  4. Nếu fix thay đổi interface → grep callers để đảm bảo tất cả đã update
```

---

## Retry Budget

```yaml
max_retries: 3

round_1:
  action: Fix theo root cause đã identify
  if_fail: Đọc lại error mới — error có thay đổi không?

round_2:
  action: Fix theo error mới sau round 1
  if_fail: Mở rộng scope — đọc thêm context xung quanh file

round_3:
  action: Fix với full context
  if_fail: ESCALATE → báo cáo cho orchestrator kèm:
    - Error message đầy đủ
    - Những gì đã thử
    - Hypothesis về root cause
    - File/line nghi ngờ
```

---

## Escalation Format

```yaml
escalation:
  error: |
    <full error message>
  tried:
    - "Round 1: Fixed null check tại user.service.ts:45 — error vẫn còn"
    - "Round 2: Thêm await tại order.controller.ts:23 — error mới xuất hiện"
    - "Round 3: Kiểm tra type interface — conflict giữa OrderDto và Order entity"
  hypothesis: "Circular type dependency giữa order.dto.ts và order.entity.ts"
  suspect_files:
    - src/orders/dto/order.dto.ts
    - src/orders/entities/order.entity.ts
  needs: "Human review để quyết định tách interface"
```

---

## KHÔNG làm

```
❌ Không dùng `as any`, `@ts-ignore`, `// eslint-disable` để bypass error
❌ Không thêm try-catch rỗng để nuốt error
❌ Không đổi test expectation để test pass (fix code, không fix test)
❌ Không downgrade package version mà không hiểu tại sao
❌ Không copy-paste fix từ stack trace mà không hiểu
❌ Không fix quá 3 lần — escalate sau round 3
```

---

## Nguyên tắc

- **Root cause first** — đọc error đầy đủ trước khi viết bất kỳ dòng code nào
- **Surgical fix** — chỉ thay đổi đúng chỗ cần thiết
- **No suppression** — không che giấu error, fix thật sự
- **Verify always** — luôn kiểm tra lại sau khi fix
- **Budget-aware** — 3 retries, sau đó escalate với đầy đủ context
