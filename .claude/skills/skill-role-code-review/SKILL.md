---
name: skill-role-code-review
description: Review code diff theo conventions của project, kiểm tra correctness, security và code quality. Chỉ đọc diff không đọc full file.
---

# Skill: Code Review

## Mục đích
Review code được viết bởi CoderAgent, đảm bảo đúng conventions, không có lỗi logic, không có security issues. Chỉ nhận **diff** — không đọc full file.

## Nguyên tắc
- Review diff, không review full file
- Chỉ flag issues thực sự — không nitpick style không quan trọng
- Severity rõ ràng: critical phải fix, minor chỉ suggest
- Output structured YAML để Orchestrator xử lý tự động

## Checklist Review

### 1. Convention Compliance
```
✅ Naming đúng pattern (camelCase / snake_case / PascalCase)?
✅ Import style đúng (absolute / relative)?
✅ File naming đúng pattern?
✅ Function/method naming mô tả đúng behavior?
✅ Không có magic strings/numbers (phải là constants)?
```

### 2. Correctness
```
✅ Function làm đúng những gì task description yêu cầu?
✅ Return type đúng?
✅ Null/undefined được handle?
✅ Edge cases được xử lý (đúng những gì được mention trong task)?
✅ Async/await đúng pattern?
✅ Error handling ở đúng chỗ?
```

### 3. Security (critical)
```
❗ Không có hardcoded secrets, API keys, passwords?
❗ Input từ user được validate trước khi xử lý?
❗ Không có SQL injection patterns (string concat vào query)?
❗ Không có command injection (exec với user input)?
❗ Sensitive data không bị log ra?
❗ Authorization check có mặt nếu endpoint cần auth?
```

### 4. Performance
```
⚡ Không có N+1 query rõ ràng?
⚡ Không có blocking operations trong async context?
⚡ Không có unnecessary re-computation trong loop?
```

### 5. Code Quality
```
🔍 Function quá dài (> 50 lines)? → suggest extract
🔍 Quá nhiều parameters (> 4)? → suggest object param
🔍 Duplicate code với logic có sẵn? → suggest reuse
🔍 Có dead code không?
```

## Severity Definitions

```yaml
severity:
  critical:
    description: Security issue hoặc sẽ break production
    action: BLOCK — phải fix trước khi merge
    examples:
      - Hardcoded credentials
      - SQL injection vulnerability
      - Missing auth check trên protected endpoint
      - Null pointer sẽ crash runtime

  major:
    description: Logic error hoặc convention violation đáng kể
    action: MUST FIX — không block nhưng cần fix ngay
    examples:
      - Wrong return type
      - Missing error handling ở boundary
      - Naming hoàn toàn không theo convention
      - Async function không await

  minor:
    description: Style issue hoặc cải thiện nhỏ
    action: SUGGEST — có thể fix sau hoặc ignore
    examples:
      - Comment không rõ nghĩa
      - Magic number nên đặt tên
      - Function hơi dài nhưng vẫn readable
```

## Output Format

### Khi pass
```yaml
status: pass
issues: []
approved_at: <timestamp>
```

### Khi fail
```yaml
status: fail
issues:
  - line: 23
    type: security
    severity: critical
    description: "Hardcoded JWT secret in code"
    suggestion: "Move to environment variable: process.env.JWT_SECRET"

  - line: 45
    type: correctness
    severity: major
    description: "Missing null check before accessing user.email"
    suggestion: "Add null check: if (!user) throw new NotFoundException()"

  - line: 67
    type: convention
    severity: minor
    description: "Variable 'usr' should be 'user' per naming conventions"
    suggestion: "Rename to 'user'"

blocking_issues: 1
must_fix_issues: 1
suggestion_only: 1
```

## Feedback Loop

```
ReviewerAgent → fail → Orchestrator → CoderAgent (với issues list)
                                    ↓
                        CoderAgent fix → new diff
                                    ↓
                        ReviewerAgent review lại (chỉ xem changed lines)
                                    ↓
                        Tối đa 2 vòng — nếu vẫn fail → escalate user
```

## Những gì KHÔNG review

```
❌ Không comment về approach/architecture (không phải scope của reviewer)
❌ Không suggest refactor code ngoài phạm vi diff
❌ Không yêu cầu thêm test (đó là task của TesterAgent)
❌ Không rewrite code — chỉ flag issues
```
