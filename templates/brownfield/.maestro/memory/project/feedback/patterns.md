# Confirmed Patterns

Cac pattern da duoc xac nhan qua feedback va nen duoc reuse.

## Template

```yaml
- id: P-0001
  title: "Pattern title"
  applies_to: [analysis, implementation, verification, qc, memory]
  rule: "Nguyen tac thuc thi ngan gon"
  guardrail_check: "Check/test/manual step de xac minh pattern da duoc ap dung"
  source_feedback: [FB-0001]
  source_bug: ".maestro/work/bugs/<severity>/<bug-id>.yaml"
  source_artifact: ".maestro/work/tasks/<task-id>/..."
  confidence: high|medium
  updated_at: 2026-04-23
```

## Entries

- id: P-0001
  title: "Chuẩn hóa prose cho user, giữ contract term cho AI/tool"
  applies_to: [analysis, implementation, verification, qc, memory]
  rule: "Khi người dùng dùng tiếng Việt hoặc tài liệu hướng tới team Việt Nam, viết phần giải thích user-facing bằng tiếng Việt nhất quán; giữ tiếng Anh cho command, file path, agent id, model profile, workflow state, rule id, skill name, YAML key, tên tool, code symbol, và thuật ngữ AI/tooling đóng vai trò contract."
  guardrail_check: "Trước khi hoàn tất docs/final response, rà heading, nhãn bảng, và đoạn mô tả để tránh trộn câu Việt-Anh không cần thiết; không dịch các contract term mà AI/tool cần đọc chính xác."
  source_feedback: [FB-0002]
  source_bug: null
  source_artifact: "README.md"
  confidence: high
  updated_at: 2026-05-20
- id: P-0002
  title: "Viết docs user-facing như maintainer"
  applies_to: [analysis, implementation, verification, qc, memory]
  rule: "Khi sửa README, COMMAND, SETUP, QUICKSTART hoặc final response dài, viết như maintainer đang hướng dẫn team dùng thật: câu ngắn, nói rõ hành động, tránh quảng cáo, tránh overclaim, giữ contract term khi nó giúp tool hiểu đúng."
  guardrail_check: "Trước khi hoàn tất docs, đọc lại intro, ví dụ, coverage và footer; nếu câu nào giống pitch marketing hoặc AI-generated voice thì viết lại thành ghi chú thực tế."
  source_feedback: [FB-0003]
  source_bug: null
  source_artifact: "README.md"
  confidence: high
  updated_at: 2026-05-20
