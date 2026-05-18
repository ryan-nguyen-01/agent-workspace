---
name: skill-memory-update
description: Persist durable project, service, task, agent, and QC learnings after meaningful workflow events.
---

# Skill: Memory Update

Use after task completion, bug discovery, decisions, or scope changes.

Always read and refresh `.runtime/context/index.yaml` so future agents can select relevant memory without rereading the whole brain.

## Store

```text
architecture decisions
service/API/schema changes
test policy changes
bug root cause patterns
QC blocker rules
generated coder scope updates
user-approved workflow exceptions
actionable user feedback from .runtime/context/feedback/inbox.md
promoted reusable learnings into feedback/patterns.md and feedback/anti-patterns.md
```

## Do not store

```text
secrets
raw tokens
passwords
long logs
temporary noise
low-confidence guesses without confidence marker
```

## Reuse and convention memory updates

After a task, update project memory when implementation or QC reveals reusable knowledge:

- New reusable asset introduced.
- Existing reusable asset changed.
- Reuse rule added or corrected.
- Coding convention discovered or changed.
- Business/technical flow clarified.
- Anti-pattern identified from bug or review.

Update only durable knowledge. Do not store speculative patterns without confidence.

## Feedback intake loop

When user/team reports AI mistakes or omissions:

1. Capture raw feedback in `.runtime/context/feedback/inbox.md`.
2. During `/sync-memory`, triage feedback:
   - recurring mistakes -> `feedback/anti-patterns.md`
   - validated fixes/best practices -> `feedback/patterns.md`
3. Record `source_artifact` and `confidence` in memory updates.
4. Mark processed inbox entries as `promoted` or `closed`.
5. Refresh `.runtime/context/index.yaml` or record why it did not change.
