---
description: "agent-workspace /qc — Run QC from handoff and classify bugs."
argument-hint: "[request or args]"
---

You are running the agent-workspace `/qc` workflow command inside Codex.

Follow `.codex/AGENTS.md` (or `AGENTS.md`) routing and the framework rules. Route every
request through the coordinator model; do not bypass approval gates, security/secret rules,
or the task-analysis source-edit gate. If the agent-workspace framework files
(`.agent/`, `.runtime/`, `.claude/commands/qc.md`) are present, defer to them as the
authoritative contract — this prompt is a portable mirror.

User input for this command: $ARGUMENTS

---
## Command contract (mirrored from .claude/commands/qc.md)

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
7. Generate Postman collection only when qc-handoff.md records API endpoint changes.
8. Return QC_DONE only with zero open blockers.
```

Skip /qc for framework-maintenance fast-track unless the task explicitly changes QC policy, test behavior, or a runnable helper script with user-facing risk.

## Stop conditions

```text
Missing handoff
Blocking bug
Missing environment credentials required to continue
Security-sensitive issue
```
