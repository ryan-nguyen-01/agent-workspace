# /dev

## Purpose

Run implementation flow through Coder Leader and generated service coders.

This command is for applied-service implementation. Standard tasks require implementation-plan.yaml; applied-service fast-track requires only lightweight service-assignments.yaml. Framework-maintenance fast-track skips /dev and records changed files plus verification evidence directly.

## Responsible agent

coder-leader

## Required rules

```text
00-core-rules.md
05-coder-leader-rules.md
06-service-coder-rules.md
07-dev-verification-rules.md
11-approval-gates.md
12-artifact-contracts.md
14-skill-composition-rules.md
```

## Preconditions

```text
task-analysis.yaml exists
implementation-plan.yaml exists unless applied-service fast_track: true
service-assignments.yaml exists
active generated coder agents exist
```

## Workflow

```text
1. Coder Leader dispatches assignments to service coders.
2. Service coders implement only inside allowed_write_paths.
3. Service coders follow test policy.
4. Service coders document manual verification when tests are not required.
5. Service coders return coder-results.yaml.
6. Route to /verify-dev.
```

## Stop conditions

```text
Scope violation required
Test policy conflict
Missing active coder
Critical ambiguity
Cross-service change needs unassigned coder
```
