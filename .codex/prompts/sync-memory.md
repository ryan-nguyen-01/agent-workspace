---
description: "agent-workspace /sync-memory — Persist durable project, service, agent, bug, and workflow knowledge."
argument-hint: "[request or args]"
---

You are running the agent-workspace `/sync-memory` workflow command inside Codex.

Follow `.codex/AGENTS.md` (or `AGENTS.md`) routing and the framework rules. Route every
request through the coordinator model; do not bypass approval gates, security/secret rules,
or the task-analysis source-edit gate. If the agent-workspace framework files
(`.agent/`, `.runtime/`, `.claude/commands/sync-memory.md`) are present, defer to them as the
authoritative contract — this prompt is a portable mirror.

User input for this command: $ARGUMENTS

---
## Command contract (mirrored from .claude/commands/sync-memory.md)

# /sync-memory

## Purpose

Persist durable project, service, agent, bug, and workflow knowledge.

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
1. Read .runtime/context/index.yaml first.
2. Choose refresh mode:
   - --scan: rescan the requested service/repo scope.
   - --files: read only explicitly provided files/paths.
3. Read only task artifacts and memory files relevant to the changed paths/services.
4. Identify durable facts worth storing, including context misses or source layout changes.
5. For coding errors, extract root_cause, prevention_rule, regression_check, and recurrence_key from bugs/dev-verification/coder-results.
6. Redact sensitive content.
7. Write memory-updates.yaml when a task is involved.
8. Update project-brain.yaml, service brain, test policy, service catalog, agent registry, or feedback patterns/anti-patterns only where relevant.
9. Refresh project_profile/context_economy/index routing rows when source layout or context hints changed.
10. Refresh .runtime/context/index.yaml so future sessions can skip full memory rereads.
11. Append changelog when workflow-level behavior changes.
```

## Usage

```text
/sync-memory --scan --services <service-ids>
  Rescan the requested service/repo scope and update memory from current source evidence.

/sync-memory --scan --inputs
  Rescan inputs/ recursively. Re-builds .runtime/context/inputs-index.yaml and re-extracts
  facts from changed files into project-brain.yaml / service brains. Does NOT touch services/.

/sync-memory --files <paths> [--services <service-ids>]
  Read only the specified files or folders and update the matching memory section.
  --services is OPTIONAL when all paths are under inputs/ (refresh resolves automatically
  to inputs-index.yaml + project-brain.inputs.last_scanned_at).
  --services is REQUIRED when paths touch source code under services/<repo>/.

/sync-memory --refresh-index
  Use after manual memory edits. Rebuilds .runtime/context/index.yaml without rescanning source code.

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
Source code structure also changed           | /onboard --refresh <service>   (heavier)
Stack/services/test-policy all changed       | /onboard                       (full rescan)
```

If source structure, stack, service boundary, or test policy changed, prefer `/sync-memory --scan --services <service>` or `/onboard --refresh <service>`. For small updates, prefer `/sync-memory --files <paths>` to avoid token-heavy scans.

## Stop conditions

```text
Proposed memory contains secrets
Fact is speculative without confidence
Source artifact is missing for a critical decision
Change affects service boundaries but no service id/path is provided
Neither --scan nor --files is provided for a source refresh request
--files paths span both inputs/ and services/<repo>/ without --services specified
```
