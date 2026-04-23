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
1. Store original input as task-input.md.
2. Create task.yaml if missing.
3. Identify source type and intent.
4. Define business goal and acceptance criteria.
5. Identify impacted services.
6. Identify contract changes, risks, blockers, critical checks, dev verification checklist, and QC focus.
7. Capture assumptions and unknowns with confidence markers.
8. If critical ambiguity exists, mark requires_user_clarification, add clarifying questions, and stop.
9. Write task-analysis.yaml.
```

## Stop conditions

```text
Critical requirement is unclear
Impacted service cannot be inferred
Security-sensitive requirement lacks enough detail
```

## Reuse and convention analysis

Task Analysis must populate reuse_and_convention_analysis in task-analysis.yaml:

- Relevant project flows from project-brain.yaml and architecture.md.
- Relevant service flows from services/<service>.yaml.
- Reusable assets that service coders should use.
- Coding conventions that affect the implementation.
- Anti-patterns to avoid.
- Whether a new reusable asset appears necessary and why.

If the task clearly needs a new cross-service reusable asset, mark Coder Leader review required before implementation.
