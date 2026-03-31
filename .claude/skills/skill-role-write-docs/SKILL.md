---
name: skill-role-write-docs
description: Cập nhật tài liệu sau mỗi thay đổi code. Chỉ update section liên quan, match đúng format hiện có, ngắn gọn và chính xác.
---

# Skill: Write Documentation

## Mục đích
Tự động cập nhật tài liệu sau khi code thay đổi. Không viết lại toàn bộ docs — chỉ update **đúng section bị ảnh hưởng** theo đúng format đang dùng.

## Nguyên tắc
- Match format docs hiện có chính xác
- Ngắn gọn: docs cho developer, không phải tutorial cho người mới
- Update cả `.agent/context/modules/` lẫn docs chính thức
- Không viết những gì rõ ràng từ code (tên function đã nói lên tất cả)

## Phát hiện format docs hiện có

### Kiểm tra trước khi viết
```
1. Tìm docs hiện có: docs/ | README.md | *.md files
2. Xác định format đang dùng:
   - Markdown với headings → dùng Markdown
   - JSDoc/TSDoc comments → dùng JSDoc
   - Python docstrings → dùng docstring
   - OpenAPI/Swagger → dùng YAML schema
3. Đọc 1 section mẫu → match exactly style đó
```

## Templates theo format

### Markdown API Documentation
```markdown
### `functionName(param: Type, param2: Type): ReturnType`

Mô tả ngắn gọn trong 1 câu.

**Parameters:**
- `param` — mô tả
- `param2` — mô tả

**Returns:** mô tả return value

**Throws:** `ErrorType` — khi nào throw

**Example:**
```ts
const result = functionName(input, options)
```
```

### JSDoc / TSDoc
```typescript
/**
 * Mô tả ngắn gọn trong 1 câu.
 *
 * @param param - mô tả
 * @param param2 - mô tả
 * @returns mô tả return value
 * @throws {ErrorType} khi nào throw
 */
```

### Python Docstring (Google style)
```python
def function_name(param: Type) -> ReturnType:
    """Mô tả ngắn gọn trong 1 câu.

    Args:
        param: Mô tả param.

    Returns:
        Mô tả return value.

    Raises:
        ErrorType: Khi nào raise.
    """
```

### OpenAPI/Swagger Endpoint
```yaml
/path:
  post:
    summary: Mô tả ngắn gọn
    tags: [module-name]
    security:
      - bearerAuth: []
    requestBody:
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/RequestDto'
    responses:
      200:
        description: Success
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ResponseDto'
      400:
        description: Validation error
      401:
        description: Unauthorized
```

## Quy trình update

### Khi function mới được thêm
```
1. Tìm section docs cho module đó
2. Thêm entry mới theo đúng format
3. Giữ thứ tự alphabetical hoặc theo nhóm (match style hiện có)
```

### Khi function bị sửa signature
```
1. Tìm entry hiện có trong docs
2. Cập nhật params, return type
3. Cập nhật description nếu behavior thay đổi
```

### Khi function bị xóa
```
1. Tìm và xóa entry khỏi docs
2. Kiểm tra có reference đến function đó ở docs khác không
```

### Khi endpoint REST thay đổi
```
1. Cập nhật Swagger/OpenAPI spec
2. Cập nhật README API section nếu có
```

## Update .agent/context/modules/

Sau khi update docs chính thức, luôn update module context:

```yaml
# Patch vào .agent/context/modules/<name>.md
exports:
  - name: <function_name>     # thêm mới
    type: function
    description: <1 sentence>

# Hoặc xóa entry nếu function bị remove
```

## Những gì KHÔNG viết vào docs

```
❌ Implementation details (how it works internally)
❌ TODO comments trong public docs
❌ History ("this was changed because...")
❌ Ví dụ quá dài (> 10 lines)
❌ Giải thích những gì đã rõ từ type signature
```

## Output format

```yaml
doc_update:
  - file: docs/api/auth.md
    action: add
    section: "AuthService"
    content: <nội dung mới>

  - file: src/auth/auth.service.ts
    action: update
    type: jsdoc
    function: validateUser
    content: <updated jsdoc>

agent_context_update:
  file: .agent/context/modules/auth.md
  patch:
    exports:
      - name: validateUser
        type: function
        description: "Validate user credentials, return user or null"
```
