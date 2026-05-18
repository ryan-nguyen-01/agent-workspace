# Feedback Inbox

Noi tiep nhan feedback ve cac truong hop AI lam sai/lam thieu.

## Entry Template

```yaml
- id: FB-0001
  created_at: 2026-04-23
  task_id: TASK-unknown
  phase: analysis|implementation|verification|qc|memory
  area: backend|frontend|infra|docs|workflow
  issue_type: wrong-solution|missing-case|scope-violation|hallucination|quality-gap|other
  summary: "Mo ta ngan gon feedback"
  expected: "Mong doi dung la gi"
  actual: "AI da lam gi"
  impact: low|medium|high
  source_artifact: ".runtime/tasks/<task-id>/..."
  evidence: "file/line/command output"
  suggested_fix: "Cach tranh lap lai"
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
