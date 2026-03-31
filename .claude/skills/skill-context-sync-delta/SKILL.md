---
name: skill-context-sync-delta
description: Đồng bộ context trong .agent/ khi có thay đổi, chỉ cập nhật phần bị ảnh hưởng thay vì rebuild toàn bộ.
---

# Skill: Sync Context Delta

## Mục đích
Khi code hoặc docs thay đổi, chỉ cập nhật **đúng phần bị ảnh hưởng** trong `.agent/`. Không rebuild toàn bộ context — quá tốn token và chậm.

## Nguyên tắc
- Delta only: chỉ xử lý những gì thay đổi
- Map file thay đổi → section context bị ảnh hưởng
- Cập nhật dirty-flags trước, clear sau khi sync xong
- Ghi changelog sau mỗi sync

## Trigger Events

| Event | Hành động |
|-------|-----------|
| `git commit` | Scan files trong commit, sync sections liên quan |
| `git pull / merge` | Diff với lần pull trước, sync toàn bộ phần thay đổi |
| File save (*.md, *.txt) | Sync section docs liên quan |
| Task completed | Update task-board.md + progress.md |
| New file/folder | Tạo module file mới nếu là module mới |
| File deleted | Xóa module file tương ứng |

## Mapping: File thay đổi → Context section

```yaml
mappings:
  - pattern: "src/<module>/**"
    affects: ".agent/context/modules/<module>.md"

  - pattern: "README.md"
    affects: ".agent/context/summary.md"

  - pattern: "docs/**"
    affects: ".agent/context/summary.md"

  - pattern: "package.json | pyproject.toml | pom.xml"
    affects: ".agent/context/summary.md"  # key_commands, stack

  - pattern: ".env.example"
    affects: ".agent/context/modules/*.md"  # env_vars sections

  - pattern: "src/**/*.test.* | tests/**"
    affects: ".agent/context/conventions.md"  # test patterns

  - pattern: "tsconfig.json | .eslintrc | prettier.config.*"
    affects: ".agent/context/conventions.md"
```

## Quy trình sync

### Bước 1 — Mark dirty (trước khi bắt đầu)
```yaml
# Ghi vào .agent/dirty-flags.md
dirty:
  - section: modules/auth
    reason: src/auth/auth.service.ts changed
    since: <timestamp>
last_sync: <previous_timestamp>
```
Điều này báo hiệu cho tất cả agents: "context đang được cập nhật, chờ."

### Bước 2 — Phân loại thay đổi
```
Với mỗi file thay đổi:
1. Tra cứu mapping ở trên
2. Xác định section context bị ảnh hưởng
3. Xác định loại thay đổi: exports thêm/bớt? purpose đổi? deps mới?
```

### Bước 3 — Tính delta
```
Đọc git diff (chỉ changed lines, không phải full file)
So sánh với context hiện tại
Xác định: field nào sai? field nào thiếu? field nào cần xóa?
```

### Bước 4 — Apply patch
```
Chỉ update fields bị ảnh hưởng
Giữ nguyên phần còn lại của file context
Cập nhật last_updated timestamp
```

### Bước 5 — Clear dirty flags
```yaml
# .agent/dirty-flags.md sau sync
dirty: []
last_sync: <current_timestamp>
```

### Bước 6 — Append changelog
```markdown
## <timestamp>
- Trigger: git_commit | file_save | git_pull
- Files changed: [src/auth/auth.service.ts]
- Context updated: [modules/auth.md → exports section]
- Delta size: ~50 tokens
```

## Quy tắc quyết định patch vs rewrite

| Tình huống | Quyết định |
|------------|------------|
| < 30% nội dung module thay đổi | Patch: chỉ sửa fields đó |
| > 70% nội dung module thay đổi | Rewrite module file |
| Module bị xóa | Xóa module file khỏi .agent/context/modules/ |
| Module mới xuất hiện | Tạo module file mới (scan module đó) |
| Rename module | Rename file + update architecture.md |

## Token budget
```
Mỗi lần sync:
- Input (git diff): ~200–500 tokens
- Processing: ~100 tokens
- Output (patch): ~50–200 tokens
- Tổng: ~350–800 tokens

So với rebuild toàn bộ: ~8,000–10,000 tokens
Tiết kiệm: ~90%
```
