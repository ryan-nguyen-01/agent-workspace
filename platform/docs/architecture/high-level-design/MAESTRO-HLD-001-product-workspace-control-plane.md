---
id: "MAESTRO-HLD-001"
title: "Product Workspace Control Plane"
status: approved
related_requirements: []
related_decisions:
  - "MAESTRO-ADR-001"
---

# Product Workspace Control Plane

## Context And Goals

`maestro` remains the stable workspace name. A greenfield product is configured inside it through
`.maestro/project.yaml`; the workspace root is not renamed and the product is not wrapped in a single service.

The layout must support product discovery, requirements, UX, architecture, delivery, operations, large work
decomposition, continuation across conversations, and future extraction into multiple repositories.

## System Boundaries

- `.claude/` is the Claude-native tool layer and stays at repository root.
- `.maestro/` is the product-development control plane.
- `docs/` stores official human-readable product artifacts.
- `apps/`, `services/`, `packages/`, `infra/`, and `tests/` are peer source roots.
- `inputs/` stores external source material that has not yet been distilled.

## Component Discovery

`.maestro/registry/components.yaml` is the machine-readable source of truth. Onboarding scans source roots only
when the registry is missing, stale, or explicitly refreshed.

Component names use product namespace plus business capability and component kind. Examples:

```text
nova-web-app
nova-identity-service
nova-order-worker
nova-public-api-gateway
nova-api-contracts
nova-design-system
```

## Work Model

Work uses `Initiative -> Epic -> Task -> Subtask`, with no nested subtasks. Large work must have a dependency
graph, progress record, and explicit verification ownership.

## Documentation And Traceability

Official artifacts live under `docs/` and are indexed from `.maestro/registry/artifacts.yaml`. Stable references
link PRD, features, user stories, flows, designs, decisions, work items, code components, test evidence,
releases, and runbooks.

## Memory And Conversation Continuation

Project memory stores durable facts. Task memory stores findings, resolved questions, checkpoints, and a
continuation handoff. Session memory is short-lived. A new conversation resumes from a continuation token
without replaying the full chat.

## Migration

The old `.agent/` and `.runtime/` roots are removed. Framework source moves to `.maestro/engine/`; state and
artifacts move to their owning `.maestro/` domains. All tool adapters, hooks, scripts, and documentation must use
the new paths before the migration is complete.
