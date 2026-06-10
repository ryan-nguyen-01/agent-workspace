# Anti-Patterns

Cac loi da lap lai qua feedback va bat buoc tranh.

## Template

```yaml
- id: AP-0001
  title: "Anti-pattern title"
  recurrence_key: "service|stack|symptom|root-cause"
  applies_to: [analysis, implementation, verification, qc, memory]
  avoid: "Hanh vi can tranh"
  replacement: "Hanh vi dung thay the"
  prevention_rule: "Rule ngan gon de agent phai ap dung"
  regression_check: "Check/test/manual step de xac minh khong lap lai"
  source_feedback: [FB-0001]
  source_bug: ".maestro/work/bugs/<severity>/<bug-id>.yaml"
  source_artifact: ".maestro/work/tasks/<task-id>/..."
  confidence: high|medium
  updated_at: 2026-04-23
```

## Entries

- id: AP-0001
  title: "Trộn prose user-facing với contract term thiếu chủ đích"
  recurrence_key: "docs|language|mixed-vi-en|missing-style-guardrail"
  applies_to: [analysis, implementation, verification, qc, memory]
  avoid: "Không viết heading, nhãn bảng, hoặc mô tả nửa tiếng Anh nửa tiếng Việt khi phần đó là prose dành cho user; cũng không dịch bừa các contract term mà AI/tool cần hiểu chính xác."
  replacement: "Dùng tiếng Việt cho phần giải thích user-facing; giữ tiếng Anh cho command, file path, agent id, model profile, workflow state, rule id, skill name, YAML key, tên tool, code symbol, và thuật ngữ AI/tooling đóng vai trò contract."
  prevention_rule: "Docs và final response phải rõ ranh giới: user-facing prose được chuẩn hóa, AI/tool-facing contract terms giữ tiếng Anh."
  regression_check: "Chạy review thủ công các heading và bảng trong README/COMMAND/SETUP trước khi release docs; xác nhận contract terms vẫn giữ nguyên."
  source_feedback: [FB-0002]
  source_bug: null
  source_artifact: "README.md"
  confidence: high
  updated_at: 2026-05-20
- id: AP-0002
  title: "Giọng văn AI-generated trong tài liệu user-facing"
  recurrence_key: "docs|voice|ai-generated-style|overclaim"
  applies_to: [analysis, implementation, verification, qc, memory]
  avoid: "Không viết docs user-facing như bài pitch: nhiều claim, nhiều buzzword, nhiều câu tổng quát nhưng ít hướng dẫn cụ thể."
  replacement: "Viết như maintainer: giải thích đủ dùng, chỉ rõ command/file liên quan, nói thẳng giới hạn và tradeoff."
  prevention_rule: "Mọi docs user-facing phải qua một lượt đọc lại để bỏ giọng quảng cáo hoặc AI-generated voice."
  regression_check: "Kiểm tra README/COMMAND/SETUP/QUICKSTART: intro, ví dụ, coverage và footer phải đọc như tài liệu vận hành, không như landing page."
  source_feedback: [FB-0003]
  source_bug: null
  source_artifact: "README.md"
  confidence: high
  updated_at: 2026-05-20
