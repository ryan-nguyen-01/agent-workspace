---
name: skill-context-write
description: Ghi và cập nhật context vào .agent/ theo đúng format. Chỉ ghi những gì thay đổi, không overwrite toàn bộ file.
---

# Skill: Write Agent Context

## Mục đích
Ghi thông tin vào `.agent/` directory theo đúng format YAML. Luôn dùng **patch update** — chỉ sửa phần thay đổi, không rewrite toàn bộ file.

## Nguyên tắc
- Patch first: chỉ update section thay đổi, giữ nguyên phần còn lại
- Format YAML nhất quán — không dùng prose
- Luôn ghi timestamp vào `last_updated`
- Luôn append vào `changelog.md` sau mỗi lần ghi
- Không ghi thông tin nhạy cảm (secrets, passwords, API keys)

## Cấu trúc file chuẩn

### summary.md
```yaml
project:
  name: <string>
  type: frontend | backend | fullstack | monorepo
  stack: [<tech1>, <tech2>]
  purpose: <1 sentence mô tả mục đích>
  entry_points: [<file_path>]
  key_commands:
    dev: <command>
    build: <command>
    test: <command>
    lint: <command>
last_updated: <ISO timestamp>
```

### architecture.md
```yaml
modules:
  - name: <module_name>
    path: <relative_path>
    purpose: <1 sentence>
    depends_on: [<module_name>]
    type: controller | service | repository | util | config | middleware
last_updated: <ISO timestamp>
```

### conventions.md
```yaml
naming:
  files: camelCase | PascalCase | kebab-case | snake_case
  variables: camelCase | snake_case
  functions: camelCase | snake_case
  classes: PascalCase
  constants: UPPER_SNAKE_CASE
imports:
  style: absolute | relative
  alias: "@/*" → "src/*"
tests:
  pattern: "*.test.ts" | "*_test.py" | "*Test.java"
  framework: jest | vitest | pytest | junit | go-test
  coverage_min: <number>%
git:
  branch_pattern: feature/<name> | fix/<name> | chore/<name>
  commit_format: <type>(<scope>): <description>
last_updated: <ISO timestamp>
```

### modules/<name>.md
```yaml
module: <name>
path: <relative_path>
purpose: <1 sentence>
exports:
  - name: <function|class|type>
    type: function | class | interface | enum | constant
    description: <1 sentence>
dependencies:
  internal: [<module_name>]
  external: [<package_name>]
env_vars: [<VAR_NAME>]
last_updated: <ISO timestamp>
```

## Quy trình ghi

### Khi tạo file mới
```
1. Tạo file với đúng YAML schema ở trên
2. Điền đầy đủ các trường bắt buộc
3. Ghi timestamp vào last_updated
4. Append vào .agent/changelog.md
```

### Khi cập nhật file hiện có
```
1. Đọc file hiện tại
2. Chỉ sửa field bị thay đổi
3. Cập nhật last_updated
4. Append vào .agent/changelog.md
```

## Ghi changelog
Sau mỗi lần write, append vào `.agent/changelog.md`:
```markdown
## <ISO timestamp>
- Action: create | update | patch
- File: <file_path>
- Changed: <brief description of what changed>
- Reason: <why this changed>
```

## Lỗi thường gặp
```
❌ Sai: Rewrite toàn bộ summary.md chỉ vì 1 field thay đổi
✅ Đúng: Chỉ update field đó, giữ nguyên phần còn lại

❌ Sai: Dùng prose "The auth module handles authentication using JWT"
✅ Đúng: purpose: "Handle JWT authentication and session management"

❌ Sai: Không ghi timestamp
✅ Đúng: Luôn ghi last_updated sau mỗi lần write
```
