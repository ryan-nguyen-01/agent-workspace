---
name: skill-memory-update
description: Persist durable project, service, task, agent, and QC learnings after meaningful workflow events.
---

# Skill: Memory Update

Use after task completion, bug discovery, decisions, or scope changes.

## Store

```text
architecture decisions
service/API/schema changes
test policy changes
bug root cause patterns
QC blocker rules
generated coder scope updates
user-approved workflow exceptions
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
