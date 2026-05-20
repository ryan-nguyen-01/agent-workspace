# R-000: Core Rules

## Applies to

All agents and commands.

## Rules

```text
R-000-01: Read .agent/workflow.md before acting.
R-000-02: Check Project Brain before project-specific work.
R-000-03: Coordinator routes and gates; Coordinator does not implement application code.
R-000-04: No generic static coder may implement project work.
R-000-05: Generated service coders may exist only after onboarding and user approval.
R-000-06: No application coding under services/<service-name>/ starts before task-analysis.yaml exists.
R-000-07: In the standard pipeline, no QC starts before qc-handoff.md exists.
R-000-08: No state transition may skip required artifacts.
R-000-09: Stop immediately on blocker bugs.
R-000-10: Record durable decisions in memory updates.
R-000-11: If confidence is low or facts are missing, do not guess; ask for clarification.
R-000-12: Never fabricate APIs, file facts, command outputs, or evidence. Mark unknown explicitly.
R-000-13: Critical claims must include evidence (file, command, or artifact) before completion.
R-000-14: If uncertainty affects correctness, security, or scope, stop and route via Coordinator.
R-000-15: In framework-template/not_applied mode, classify target_scope before Project Brain checks.
R-000-16: Framework maintenance on this repository does not require onboarding, service catalog, generated coders, or service brain freshness unless it touches services/<service-name>/ or applied-project artifacts.
```

## Stop conditions

```text
Missing Project Brain for applied-service work
Missing required artifact
Missing required user approval
Detected blocker bug
Scope violation required to proceed
Critical uncertainty without clarification
```

## Violation handling

Stop current work, report the violated rule id, and route to Coordinator or Workflow Policy.
