---
description: "maestro /dev — Run implementation flow through Coder Leader and generated service coders."
argument-hint: "[request or args]"
---

You are running the maestro `/dev` workflow command inside Codex.

Follow `.codex/AGENTS.md` (or `AGENTS.md`) routing and the framework rules. Route every
request through the coordinator model; do not bypass approval gates, security/secret rules,
or the task-analysis source-edit gate. If the maestro framework files
(`.maestro/engine/`, `.maestro/registry/`, `.maestro/knowledge/`, `.maestro/work/`, `.maestro/runtime/`, `.claude/commands/dev.md`) are present, defer to them as the
authoritative contract — this prompt is a portable mirror.

User input for this command: $ARGUMENTS

---
## Command contract (mirrored from .claude/commands/dev.md)

# /dev

## Purpose

Run implementation flow through Coder Leader and generated service coders.

This command is for product-component implementation. Standard tasks require implementation-plan.yaml; product-component fast-track requires only lightweight service-assignments.yaml. Framework-maintenance fast-track skips /dev and records changed files plus verification evidence directly.

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
implementation-plan.yaml exists unless product-component fast_track: true
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
