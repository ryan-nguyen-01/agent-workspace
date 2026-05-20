# /analyze-task

## Purpose

Normalize HLD, LLD, ticket, bug report, incident, or direct text into task-analysis.yaml.

For trivial framework maintenance in framework-template/not_applied mode, this command may produce lightweight evidence instead of a full task folder when workflow.md §6.2 and R-004-12 allow it.

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
1. Classify target_scope and task_size.
2. If target_scope=framework and lightweight fast-track is eligible:
   - do not create the full task folder
   - record target_scope, fast_track reason, changed_files, and verification evidence in the response or task note
   - stop before planning/dev/QC artifacts
3. For applied-service tasks, Coordinator assigns a unique task_id: TASK-YYYYMMDD-NNN-slug.
4. Create .runtime/tasks/<task_id>/.
5. Store original input as task-input.md.
6. Create task.yaml from task.template.yaml if missing.
7. Append task-updates.yaml with task creation/update event.
8. Identify source type and intent.
9. Define business goal and acceptance criteria.
10. Identify impacted services.
11. Build context_plan with bounded memory/source/skill budgets, required evidence, excluded paths, expansion triggers, unresolved context, and confidence.
12. Identify contract changes, risks, blockers, critical checks, dev verification checklist, and QC focus.
13. Capture assumptions and unknowns with confidence markers.
14. If critical ambiguity or low context confidence exists, mark requires_user_clarification or unresolved_context, add clarifying questions, and stop.
15. Write task-analysis.yaml in the same task folder.
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

For framework maintenance, use the directly relevant framework rule/template/command/script files as evidence. Do not open project brain, service catalog, agent registry, or service brains unless the task directly edits those contracts.

## Context plan

For applied-service tasks, Task Analysis must populate `context_plan` before Coder Leader runs. The context plan is the bounded context pack for the rest of the workflow:

- Memory/source files required for the task.
- Files explicitly excluded to reduce token use.
- Confidence and unresolved context.
- Expansion triggers for risks that justify reading more.
- Skill file budget for contextual skills.
