---
name: skill-role-breakdown-tasks
description: Phân tích yêu cầu của user và breakdown thành subtasks atomic, mỗi task giao đúng 1 agent, có dependency rõ ràng.
---

# Skill: Breakdown Tasks

## Mục đích
Chuyển đổi yêu cầu của user thành danh sách subtasks có thể thực thi được, mỗi task được giao cho đúng agent, có thứ tự thực hiện rõ ràng.

## Nguyên tắc
- 1 subtask = 1 agent = 1 action = 1 output cụ thể
- Không tạo subtask mơ hồ — phải đủ rõ để agent thực hiện không cần hỏi
- Identify dependencies chính xác để chạy song song tối đa
- Không tạo thừa subtasks — đơn giản hóa khi có thể

## Phân loại độ phức tạp

### Simple (1-2 subtasks)
```
Dấu hiệu:
- Chỉ ảnh hưởng 1 file hoặc 1 function
- Yêu cầu rõ ràng, không có ambiguity
- Không cần review hoặc test riêng

Ví dụ: "Thêm field email vào UserDto"
→ T-001: CoderAgent → add email field to UserDto
```

### Medium (3-6 subtasks)
```
Dấu hiệu:
- Ảnh hưởng 2-3 files
- Cần cả code + test
- Cần review

Ví dụ: "Thêm endpoint GET /users/:id"
→ T-001: CoderAgent → create endpoint handler
→ T-002: CoderAgent → create service method
→ T-003: TesterAgent → write unit tests (depends: T-001, T-002)
→ T-004: ReviewerAgent → review code (depends: T-001, T-002)
```

### Complex (7+ subtasks)
```
Dấu hiệu:
- Ảnh hưởng nhiều modules
- Cần architectural decision
- Có nhiều edge cases

→ Hỏi user để clarify scope trước khi breakdown
```

## Format subtask chuẩn

```yaml
subtask:
  id: T-<số 3 chữ số>
  title: <Imperative verb + object>    # "Add login endpoint"
  agent: <full-agent-name>             # agent-coder-api-nestjs (TÊN ĐẦY ĐỦ)
  module: <module_name>                # auth
  scope: <working directory>           # src/auth/
  file_target: <file_path>             # src/auth/auth.controller.ts
  description: <cụ thể những gì cần làm, đủ để agent hiểu>
  input_requires: [<T-xxx.output>]     # dependencies
  output_produces: <format output>     # "NestJS endpoint code"
  depends_on: [<T-xxx>]
  can_run_parallel_with: [<T-xxx>]
```

**Quy tắc đặt tên agent trong subtask:**
```
✅ Đúng: agent-coder-api-nestjs       (tên đầy đủ theo convention)
✅ Đúng: agent-coder-web-react        (scope + tech rõ ràng)
✅ Đúng: agent-devops-pipeline-gha    (devops agent cụ thể)
✅ Đúng: agent-tester                 (core agent, tên cố định)

❌ Sai: agent-coder-be                (không có scope cụ thể)
❌ Sai: coder                         (thiếu prefix agent-)
❌ Sai: nestjs-agent                  (sai thứ tự naming)
```

## Ví dụ breakdown thực tế

### Yêu cầu: "Xây dựng tính năng đăng nhập bằng email/password"

```yaml
task_analysis:
  type: feature
  complexity: medium
  affected_modules: [auth, user]

subtasks:
  - id: T-001
    title: Create LoginDto with email and password validation
    agent: agent-coder-api-nestjs      # ← tên đầy đủ
    module: auth
    scope: src/auth/
    file_target: src/auth/dto/login.dto.ts
    description: "Create DTO class with email (IsEmail) and password (MinLength 8) decorators"
    depends_on: []
    output_produces: LoginDto class

  - id: T-002
    title: Create validateUser method in AuthService
    agent: agent-coder-api-nestjs      # ← cùng agent vì cùng scope
    module: auth
    scope: src/auth/
    file_target: src/auth/auth.service.ts
    description: "Add validateUser(email, password) that checks against UserRepository, returns user or null"
    depends_on: []
    output_produces: validateUser method

  - id: T-003
    title: Create POST /auth/login endpoint
    agent: agent-coder-api-nestjs      # ← cùng agent
    module: auth
    scope: src/auth/
    file_target: src/auth/auth.controller.ts
    description: "Add login endpoint that accepts LoginDto, calls validateUser, returns JWT token"
    depends_on: [T-001, T-002]
    output_produces: login endpoint

  - id: T-004
    title: Write unit tests for AuthService.validateUser
    agent: agent-tester                 # ← core agent, tên cố định
    module: auth
    scope: src/auth/
    file_target: src/auth/auth.service.spec.ts
    description: "Test cases: valid credentials, wrong password, user not found"
    depends_on: [T-002]
    output_produces: test file

  - id: T-005
    title: Review auth implementation
    agent: agent-reviewer               # ← core agent, tên cố định
    module: auth
    description: "Review T-001, T-002, T-003 code for security issues and convention compliance"
    depends_on: [T-003]
    output_produces: review result

execution_plan:
  parallel_groups:
    - group: 1
      tasks: [T-001, T-002]    # Independent, chạy song song
    - group: 2
      tasks: [T-003]           # Cần T-001 và T-002 xong trước
    - group: 3
      tasks: [T-004, T-005]    # T-004 và T-005 chạy song song
  critical_path: [T-002, T-003, T-005]
```

## Quy tắc đặt tên subtask

```
✅ Đúng: "Create validateUser method in AuthService"
✅ Đúng: "Add email field to UserDto"
✅ Đúng: "Write unit tests for UserService.findById"

❌ Sai: "Implement auth"  (quá chung)
❌ Sai: "Fix the stuff"   (không rõ)
❌ Sai: "Auth and user"   (2 việc trong 1 task)
```

## Khi nào cần hỏi user trước khi breakdown

```
1. Yêu cầu mâu thuẫn với architecture hiện tại
2. Scope quá lớn (> 10 files, > 3 modules)
3. Có 2+ cách implement, tradeoffs khác nhau đáng kể
4. Yêu cầu không rõ (thiếu thông tin về behavior mong muốn)
```
