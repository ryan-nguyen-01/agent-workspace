# /bug

## Purpose

Create or route blocker/non-blocker defects.

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
2. Write the canonical bug artifact:
   - blocker: .maestro/work/bugs/blockers/<bug-id>.yaml
   - non-blocker: .maestro/work/bugs/non-blockers/<bug-id>.yaml
3. Update .maestro/work/tasks/<task-id>/bugs.yaml as the task-local bug index.
   The task index must reference bug_id, severity, status, canonical_path, and retest_scope.
   Do not store the only bug detail copy in the task folder.
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
