# /bug

## Purpose

Create or route blocker/non-blocker bug tasks.

## Responsible agent

bug-router

## Required rules

```text
00-core-rules.md
09-bug-routing-rules.md
11-approval-gates.md
12-artifact-contracts.md
13-security-secret-rules.md
```

## Workflow

```text
1. Classify defect as blocker or non-blocker.
2. Write blocker or non-blocker bug artifact.
3. Update .runtime/tasks/<task-id>/bugs.yaml.
4. For blocker, stop QC and route to Coder Leader.
5. For non-blocker, allow QC to continue and create parallel fix task if needed.
```

## Stop conditions

```text
Severity ambiguous and may block main flow
Missing reproduction steps
Missing expected or actual result
Sensitive evidence needs redaction
```
