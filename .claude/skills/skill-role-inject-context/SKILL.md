---
name: skill-role-inject-context
description: Trích xuất đúng phần context cần thiết từ .agent/ và đóng gói thành input package cho từng agent. Tối thiểu token, tối đa chính xác.
---

# Skill: Inject Context To Agent

## Mục đích
Orchestrator dùng skill này để chuẩn bị input cho mỗi agent worker. Nguyên tắc: **inject minimum context để agent làm đúng việc — không hơn, không kém.**

## Nguyên tắc
- Mỗi agent chỉ nhận context liên quan đến task của nó
- Context package tối đa 500 tokens per agent
- Structured YAML — không phải prose
- Include đủ để agent không cần hỏi lại

## Context Package theo loại agent

### Package cho CoderAgent
```
[ROLE]
Bạn là <stack> developer. Viết code production-ready, follow conventions.

[CONTEXT]
project: <name> | stack: <stack>
module: <module_name>
path: <file_path>
conventions:
  naming: <pattern>
  imports: <absolute|relative>
  style: <notes>
existing_exports: [<list>]
dependencies_available: [<packages đã install>]

[TASK]
<mô tả cụ thể: function name, inputs, outputs, behavior>

[OUTPUT FORMAT]
Code only. Include imports. No explanation.
```

### Package cho ReviewerAgent
```
[ROLE]
Bạn là code reviewer. Check correctness và convention compliance.

[CONTEXT]
conventions:
  naming: <pattern>
  imports: <style>
  style: <rules>
task_was: <mô tả task vừa được code>

[TASK]
Review diff này:
<diff — chỉ changed lines>

[OUTPUT FORMAT]
status: pass | fail
issues:
  - line: <n>
    type: convention | correctness | safety
    severity: critical | major | minor
    description: <what is wrong>
```

### Package cho TesterAgent
```
[ROLE]
Bạn là <framework> test writer.

[CONTEXT]
test_framework: <jest|pytest|junit>
test_file_pattern: <pattern>
mock_library: <jest.mock|unittest.mock|Mockito>
conventions:
  test_naming: <pattern>
function_under_test:
  name: <name>
  signature: <inputs → output>
  purpose: <1 sentence>
  edge_cases: [<case1>, <case2>]
  module_path: <path>

[TASK]
Viết tests cho <function_name>

[OUTPUT FORMAT]
Test file content only.
```

### Package cho DocumenterAgent
```
[ROLE]
Bạn là documentation writer. Chỉ update phần thay đổi.

[CONTEXT]
doc_format: <markdown|jsdoc|docstring>
existing_section: <nội dung section hiện tại>
module: <module_name>

[TASK]
Cập nhật docs cho thay đổi này:
<diff của code vừa thay đổi>

[OUTPUT FORMAT]
Updated section only. No full file rewrite.
```

### Package cho AnalystAgent
```
[ROLE]
Bạn là task analyst. Breakdown request thành subtasks.

[CONTEXT]
project_type: <type>
stack: [<tech>]
modules_available: [<module names>]
available_agent_variants: [<list từ available-agents.md>]

[TASK]
Breakdown: <user request>

[OUTPUT FORMAT]
YAML subtask list with dependencies.
```

## Quy trình inject

```
1. Đọc task từ Orchestrator
2. Xác định agent type cần spawn
3. Load context template cho agent type đó (ở trên)
4. Điền thông tin từ .agent/:
   - summary.md → project, stack
   - conventions.md → naming, imports
   - modules/<tên>.md → exports, dependencies
5. Trim bất kỳ field nào không liên quan đến task
6. Kiểm tra tổng theo budget orchestrator (400 / 500 / 600 tokens)
   - Nếu vượt → cắt thêm, ưu tiên [TASK] + conventions/module facts
7. Thêm [TASK] và [OUTPUT FORMAT]
8. Gửi cho agent
```

## Rules quan trọng

```
❌ Không inject toàn bộ architecture.md vào CoderAgent
❌ Không inject toàn bộ modules list vào ReviewerAgent
❌ Không inject summary.md vào ReporterAgent (chỉ cần progress.md)

✅ CoderAgent chỉ nhận conventions + 1 module file
✅ ReviewerAgent chỉ nhận conventions + diff
✅ ReporterAgent chỉ nhận progress.md
```

## Token budget tracking

```yaml
context_package_log:
  agent: CoderAgent
  context_tokens: 320
  task_tokens: 80
  total_injected: 400
  budget_remaining: 100
```
