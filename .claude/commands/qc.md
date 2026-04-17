# /qc

## Purpose

Run QC from handoff and classify bugs.

## Responsible agent

qc-runner

## Required rules

```text
00-core-rules.md
08-qc-rules.md
09-bug-routing-rules.md
12-artifact-contracts.md
13-security-secret-rules.md
```

## Preconditions

```text
qc-handoff.md exists
Task state is QC_READY, QC_TESTING, or QC_RETESTING
```

## Workflow

```text
1. Read qc-handoff.md.
2. Create or record QC test cases.
3. Execute or document tests by environment.
4. On blocker, stop immediately and route to /bug.
5. On non-blocker, create bug and continue unaffected cases.
6. Write qc-test-results.yaml.
7. Return QC_DONE only with zero open blockers.
```

## Stop conditions

```text
Missing handoff
Blocking bug
Missing environment credentials required to continue
Security-sensitive issue
```
