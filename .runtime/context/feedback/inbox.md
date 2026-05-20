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
  source_artifact: ".runtime/tasks/<task-id>/..."
  canonical_bug: ".runtime/bugs/<severity>/<bug-id>.yaml"
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
