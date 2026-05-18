# /handoff-qc

## Purpose

Create the mandatory Dev-to-QC handoff after DEV_DONE.

## Responsible agent

qc-handoff

## Required rules

```text
00-core-rules.md
07-dev-verification-rules.md
08-qc-rules.md
12-artifact-contracts.md
```

## Preconditions

```text
dev-verification.yaml result is DEV_DONE
```

## Workflow

```text
1. Read task-analysis.yaml.
2. Read implementation-plan.yaml.
3. Read coder-results.yaml.
4. Read dev-verification.yaml.
5. Write .runtime/tasks/<task-id>/qc-handoff.md.
6. Append task-updates.yaml with QC_READY transition.
7. Return QC_READY.
```

## Stop conditions

```text
Dev verification is not DEV_DONE
Known blocker exists
Missing evidence for QC
```
