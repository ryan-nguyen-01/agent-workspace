# Context — Brain của Project

Thư mục này là **bộ não** của agent system. Fill bởi `agent-onboarding` lần đầu, update bởi `agent-context-keeper` sau mỗi task shipped.

## Files

| File | Owner | Purpose |
|------|-------|---------|
| `summary.md` | onboarding | Project overview: stack, type, services count |
| `architecture.md` | onboarding | Kiến trúc tổng thể, pattern, communication |
| `conventions.md` | onboarding + context-keeper | Coding style auto-detected từ code |
| `environments.md` | onboarding (user fill keys) | local/dev/sit config |
| `services/<service>.md` | onboarding + builder + context-keeper | Per-service brain: API, schema, deps |
| `common/generics.md` | onboarding + context-keeper | Common utils/helpers — tránh viết lại |

## Rules

1. **Không ghi secret** vào bất kỳ file nào ở đây
2. **Brain-first** — mọi agent đọc context trước khi scan code
3. **Delta sync** — context-keeper chỉ update phần thay đổi, không rebuild
4. **Mỗi file < 500 dòng** — tách nếu quá lớn

## Lifecycle

```
onboarding (lần đầu) → fill tất cả file
     ↓
builder → update services/*.md owner_agent
     ↓
tasks chạy → agents đọc context
     ↓
task shipped → context-keeper sync delta
     ↓
(repeat)
```

Rebuild toàn bộ context: chạy lại `agent-onboarding` (sẽ override).
