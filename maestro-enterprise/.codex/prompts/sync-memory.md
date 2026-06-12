---
description: "maestro /sync-memory — Persist durable project, component, agent, bug, and workflow knowledge."
argument-hint: "[request or args]"
---

You are running the maestro `/sync-memory` workflow command inside Codex.

Follow `.codex/AGENTS.md` (or `AGENTS.md`) routing and the framework rules. Route every
request through the coordinator model; do not bypass approval gates, security/secret rules,
or the task-analysis source-edit gate. If the maestro framework files
(`.maestro/engine/`, `.maestro/registry/`, `.maestro/knowledge/`, `.maestro/work/`, `.maestro/runtime/`, `.claude/commands/sync-memory.md`) are present, defer to them as the
authoritative contract — this prompt is a portable mirror.

User input for this command: $ARGUMENTS

---
## Command contract (mirrored from .claude/commands/sync-memory.md)

# /sync-memory

## Purpose

Persist durable project, component, agent, bug, and workflow knowledge.

## Responsible agent

memory-update

## Required rules

```text
00-core-rules.md
01-project-brain-rules.md
10-memory-rules.md
12-artifact-contracts.md
13-security-secret-rules.md
```

## Workflow

```text
1. Read .maestro/knowledge/index.yaml first.
2. Choose refresh mode:
   - --scan: rescan the requested component/repo scope.
   - --files: read only explicitly provided files/paths.
3. Read only task artifacts and memory files relevant to the changed paths/components.
4. Identify durable facts worth storing, including context misses or source layout changes.
5. For coding errors, extract root_cause, prevention_rule, regression_check, and recurrence_key from bugs/dev-verification/coder-results.
6. Redact sensitive content.
7. Write memory-updates.yaml when a task is involved.
8. Update project.yaml, component knowledge, test policy, component registry, agent registry, or feedback patterns/anti-patterns only where relevant.
9. Refresh project_profile/context_economy/index routing rows when source layout or context hints changed.
10. Refresh .maestro/knowledge/index.yaml so future sessions can skip full memory rereads.
11. Append changelog when workflow-level behavior changes.
```

## Usage

```text
/sync-memory --scan --components <component-ids>
  Rescan the requested component/repo scope and update memory from current source evidence.

/sync-memory --scan --inputs
  Rescan inputs/ recursively. Re-builds .maestro/registry/inputs.yaml and re-extracts
  facts from changed files into project.yaml / component knowledge files. Does NOT touch component source.

/sync-memory --files <paths> [--components <component-ids>]
  Read only the specified files or folders and update the matching memory section.
  --components is OPTIONAL when all paths are under inputs/ (refresh resolves automatically
  to inputs.yaml + project.yaml.inputs.last_scanned_at).
  --components is REQUIRED when paths touch source code under registered component roots.

/sync-memory --refresh-index
  Use after manual memory edits. Rebuilds .maestro/knowledge/index.yaml without rescanning source code.

/sync-memory <task-id>
  Use after a completed workflow task to persist durable learnings from task artifacts.
```

### Picking the right mode after adding inputs

```text
Scenario                                     | Recommended command
---------------------------------------------|------------------------------------------------
Added 1-3 specific files to inputs/          | /sync-memory --files inputs/api/orders.yaml ...
Added many files / new subdir in inputs/     | /sync-memory --scan --inputs
Replaced PRD or product pivot                | /sync-memory --scan --inputs
Source code structure also changed           | /onboard --refresh <component> (heavier)
Stack/services/test-policy all changed       | /onboard                       (full rescan)
```

If source structure, stack, component boundary, or test policy changed, prefer `/sync-memory --scan --components <component>` or `/onboard --refresh <component>`. For small updates, prefer `/sync-memory --files <paths>` to avoid token-heavy scans.

## Stop conditions

```text
Proposed memory contains secrets
Fact is speculative without confidence
Source artifact is missing for a critical decision
Change affects component boundaries but no component id/path is provided
Neither --scan nor --files is provided for a source refresh request
--files paths span both inputs/ and registered component roots without --components specified
```
