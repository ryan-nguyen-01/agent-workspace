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
  source_bug: ".runtime/bugs/<severity>/<bug-id>.yaml"
  source_artifact: ".runtime/tasks/<task-id>/..."
  confidence: high|medium
  updated_at: 2026-04-23
```

## Entries
