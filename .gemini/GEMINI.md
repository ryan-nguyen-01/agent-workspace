# Gemini Instructions — agent-workspace

Use this file when Gemini works in this repository.

## Repository Role

`agent-workspace` is a coordination workspace for AI-driven software engineering workflows. It is not application source code.

```text
inputs/              User-provided PRD/HLD/ADR/OpenAPI/glossary/runbooks
services/            Local clones of application repositories
.runtime/context/     Durable brain, service catalog, agent registry, workflow state
.runtime/tasks/       Per-task artifacts
.runtime/bugs/        Bug routing artifacts
```

## Required Reading

```text
AGENTS.md
CLAUDE.md
COMMAND.md
.agent/workflow.md
.runtime/context/workflow-state.yaml
```

## Coordination Policy

```text
Every request starts at /coord.
No coding before task-analysis.yaml.
No planning/coding before approved architecture-review.yaml when architecture_review.required is true.
No direct raw-user routing to coder-leader, qc-runner, generated coders, or built-in coders.
Generated coders must obey agent-registry.yaml allowed_write_paths and forbidden_paths.
```

## Task Policy

Task IDs use:

```text
TASK-YYYYMMDD-NNN-slug
```

All artifacts for a task live in:

```text
.runtime/tasks/<task_id>/
```

Use `task-updates.yaml` as the append-only update log.

Do not create a separate handoff folder; `qc-handoff.md` inside the task folder is the single Dev-to-QC handoff.

## Safety

Never write secrets, private keys, tokens, raw cookies, or long logs into `.runtime/` artifacts or tool adapter files.

If uncertain, mark the fact `unknown`, cite what evidence is missing, and ask the user through Coordinator or route to `/policy-check`.
