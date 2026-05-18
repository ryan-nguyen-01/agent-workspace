# /analyze-task

## Purpose

Normalize HLD, LLD, ticket, bug report, incident, or direct text into task-analysis.yaml.

## Responsible agent

task-analysis

## Required rules

```text
00-core-rules.md
04-task-analysis-rules.md
12-artifact-contracts.md
13-security-secret-rules.md
```

## Workflow

```text
1. Coordinator assigns a unique task_id: TASK-YYYYMMDD-NNN-slug.
2. Create .runtime/tasks/<task_id>/.
3. Store original input as task-input.md.
4. Create task.yaml from task.template.yaml if missing.
5. Append task-updates.yaml with task creation/update event.
6. Identify source type and intent.
7. Define business goal and acceptance criteria.
8. Identify impacted services.
9. Identify contract changes, risks, blockers, critical checks, dev verification checklist, and QC focus.
10. Capture assumptions and unknowns with confidence markers.
11. If critical ambiguity exists, mark requires_user_clarification, add clarifying questions, and stop.
12. Write task-analysis.yaml in the same task folder.
```

## Stop conditions

```text
Critical requirement is unclear
Impacted service cannot be inferred
Security-sensitive requirement lacks enough detail
```

## Reuse and convention analysis

Task Analysis must populate reuse_and_convention_analysis in task-analysis.yaml:

- Relevant project flows from .runtime/context/project-brain.yaml and .runtime/context/architecture.md.
- Relevant service flows from .runtime/context/services/<service>.yaml.
- Reusable assets that service coders should use.
- Coding conventions that affect the implementation.
- Anti-patterns to avoid.
- Whether a new reusable asset appears necessary and why.

If the task clearly needs a new cross-service reusable asset, mark Coder Leader review required before implementation.
