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
1. Read task artifacts and changed decisions.
2. Identify durable facts worth storing.
3. Redact sensitive content.
4. Write memory-updates.yaml.
5. Update project-brain.yaml, service brain, test policy, or agent registry only where relevant.
6. Append changelog when workflow-level behavior changes.
```

## Stop conditions

```text
Proposed memory contains secrets
Fact is speculative without confidence
Source artifact is missing for a critical decision
```
