# Feedback Inbox

Noi tiep nhan feedback ve cac truong hop AI lam sai/lam thieu.

## Entry Template

```yaml
- id: FB-0001
  created_at: 2026-04-23
  task_id: TASK-unknown
  phase: analysis|implementation|verification|qc|memory
  area: backend|frontend|infra|docs|workflow
  issue_type: wrong-solution|missing-case|scope-violation|hallucination|quality-gap|coding-error|regression|verification-miss|other
  summary: "Mo ta ngan gon feedback"
  expected: "Mong doi dung la gi"
  actual: "AI da lam gi"
  impact: low|medium|high
  source_artifact: ".maestro/work/tasks/<task-id>/..."
  canonical_bug: ".maestro/work/bugs/<severity>/<bug-id>.yaml"
  evidence: "file/line/command output"
  root_cause: "Vi sao loi xay ra"
  suggested_fix: "Cach tranh lap lai"
  prevention_rule: "Rule ngan gon de agent phai ap dung lan sau"
  regression_check: "Check/test/manual step de xac minh loi khong lap lai"
  recurrence_key: "service|stack|symptom|root-cause"
  status: queued|promoted|closed
```

## Entries

- id: FB-0001
  created_at: 2026-04-23
  task_id: TASK-unknown
  phase: implementation
  area: workflow
  issue_type: missing-case
  summary: "Placeholder entry - replace with real feedback"
  expected: ""
  actual: ""
  impact: low
  source_artifact: "unknown"
  evidence: "unknown"
  suggested_fix: ""
  status: queued
- id: FB-0002
  created_at: 2026-05-20
  task_id: TASK-unknown
  phase: memory
  area: docs
  issue_type: quality-gap
  summary: "Tài liệu và phản hồi đang trộn tiếng Anh với tiếng Việt khiến người đọc khó hiểu."
  expected: "Phần prose dành cho user dùng một ngôn ngữ chính nhất quán; giữ tiếng Anh cho command, file path, agent id, model profile, workflow state, rule id, skill name, YAML key, tên tool, và thuật ngữ AI/tooling đóng vai trò contract."
  actual: "README có nhiều heading, nhãn bảng, và mô tả trộn tiếng Anh/tiếng Việt."
  impact: medium
  source_artifact: "README.md"
  evidence: "User feedback on 2026-05-20; README headings and tables before language normalization."
  root_cause: "Chưa có guardrail rõ ràng để phân biệt prose cho user với contract term dành cho AI/tool."
  suggested_fix: "Chuẩn hóa phần prose user-facing sang tiếng Việt làm ngôn ngữ chính, nhưng giữ nguyên contract term tiếng Anh."
  prevention_rule: "Khi viết tài liệu hoặc final response, chuẩn hóa prose cho user; không dịch command, file path, agent id, workflow state, YAML key, hoặc thuật ngữ AI/tooling là contract."
  regression_check: "Review heading/table labels của README và response-ui global_rules trước khi release docs; xác nhận contract terms vẫn giữ tiếng Anh."
  recurrence_key: "docs|language|mixed-vi-en|missing-style-guardrail"
  status: promoted
- id: FB-0003
  created_at: 2026-05-20
  task_id: TASK-unknown
  phase: memory
  area: docs
  issue_type: quality-gap
  summary: "Tài liệu user-facing vẫn có cảm giác AI viết: nhiều claim, nhiều buzzword, ít giống ghi chú maintainer."
  expected: "Tài liệu nên đọc như một maintainer giải thích cho team: thực tế, ngắn gọn, nói rõ dùng khi nào, giữ contract term khi cần."
  actual: "README có các đoạn giới thiệu và ví dụ mang giọng marketing hoặc AI-generated voice."
  impact: medium
  source_artifact: "README.md"
  evidence: "User feedback on 2026-05-20 requesting human-maintainer style."
  root_cause: "Response/docs guardrail mới chỉ xử lý ngôn ngữ, chưa xử lý voice và overclaim trong prose user-facing."
  suggested_fix: "Viết lại phần prose user-facing bằng giọng maintainer, tránh quảng cáo, tránh claim quá rộng, tránh câu khuôn mẫu."
  prevention_rule: "Docs user-facing phải dùng giọng maintainer: cụ thể, vừa đủ, ít buzzword; contract term giữ nguyên nhưng không dùng để làm câu văn nặng tính quảng cáo."
  regression_check: "Review README trước khi release: intro, problem/solution, flow ví dụ, coverage, footer không được có giọng marketing hoặc AI-generated voice."
  recurrence_key: "docs|voice|ai-generated-style|overclaim"
  status: promoted
