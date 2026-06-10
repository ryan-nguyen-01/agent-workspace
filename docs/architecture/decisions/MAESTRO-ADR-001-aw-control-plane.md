---
id: "MAESTRO-ADR-001"
title: "Use .maestro as the single product-development control plane"
status: accepted
decided_at: "2026-06-06"
supersedes: null
---

# Use `.maestro` As The Single Control Plane

## Context

The previous layout split tool-neutral workflow source under `.agent/` and durable state under `.runtime/`.
It did not provide first-class locations for product documentation, design, decisions, work decomposition,
conversation continuation, or multi-root component discovery.

## Decision

Keep `.claude/` at repository root for native discovery. Consolidate tool-neutral product-development
control data under `.maestro/`, separated by ownership domain. Keep official user-facing documents under `docs/`
and source components in peer roots.

## Consequences

- There is one control-plane namespace and no `.agent`/`.runtime` collision.
- Scripts and adapters require a coordinated path migration.
- Runtime-only files remain distinguishable through `.maestro/runtime/` and `.maestro/memory/sessions/`.
- Products can grow from an embedded workspace into multiple repositories while stable component ids,
  design ids, decisions, and work history remain unchanged.
