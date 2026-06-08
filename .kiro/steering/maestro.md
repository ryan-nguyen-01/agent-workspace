---
inclusion: always
---

# Kiro Steering — Maestro

Steering for Kiro working in this repository. Kiro auto-includes `.kiro/steering/*.md`; this file points
Kiro at the Maestro control plane and workflow.

## Repository Role

`maestro` is a product-development workspace with a multi-agent control plane.

```text
.maestro/             Control plane, knowledge, work, memory, history, local runtime
docs/                 Official product and engineering documentation
apps|services|packages|infra|tests/  Product implementation
inputs/               External references awaiting curation
```

## Framework Maintenance Scope

Treat this repository as the `maestro` product-development control plane. `NEED_ONBOARDING`, an empty
component registry, and seed project knowledge are expected for framework-only maintenance.

For framework tasks that edit docs, workflow rules, templates, commands, tool adapters, workflow agents,
or helper scripts:

```yaml
target_scope: framework
requires_onboarding: false
methodology:
  selected: risk-based-routing
  overlays: []
run_required: false
```

Require onboarding only when assisted/governed product work depends on missing component facts.

## Required Reading

```text
AGENTS.md
CLAUDE.md
COMMAND.md
.maestro/INSTRUCTIONS.md
.maestro/engine/workflow.md
.maestro/runtime/workflow-state.yaml
```

## Kiro specs ↔ Maestro

Kiro specs (requirements/design/tasks) map onto Maestro's existing artifacts — do not create a parallel
source of truth:

```text
requirements -> docs/requirements (BA Documentation Standard) + product-blueprint.yaml (blueprint gate)
design       -> docs/architecture (HLD/LLD/ADR), docs/experience (UI/UX prototype), code-layout.md
tasks        -> .maestro/work/tasks/<task-id>/ (task-analysis, plan, progress, verification)
```

## Coordination Policy

```text
Every request starts at /coord for classification; /ship for autonomous build-to-done; /overview for a
full project briefing; /git for the Git-flow workflow.
Classify target_scope before broad brain/service reads.
Select direct, assisted, governed, or autonomous; add Spec-Driven Development, Eval-Driven AI Development,
or Enterprise Agent Governance overlays when traceability, eval-driven AI, or governed autonomy applies.
No raw-user routing to coder-leader, qc-runner, generated coders, or built-in coders.
Generated coders obey agents.yaml allowed_write_paths and forbidden_paths.
Specialist advisors (.claude/agents/specialists/) are advisor-only (R-016): they write only their advisory
artifact, never application code, never assign coders or mark gates.
Use `.maestro/config/model-routing.yaml` for model profiles and `.maestro/runtime/agent-activity.yaml`
for `/status` activity/ETA reporting; switch models via model_overrides, not by editing agent files.
Use `.maestro/config/response-ui.yaml` for markdown/text response structure.
Use `python3 scripts/status-dashboard.py --mode <compact|concise|dashboard|models|json|overview>` as a
terminal status mirror. Optional: `python3 scripts/architecture-health-check.py --strict` drift check.
If Kiro agent hooks are configured, mirror the deterministic guards in scripts/hooks/ (scope/secret/
destructive); otherwise enforce the execution mode and approval gates manually.
```

## Safety

```text
Never write secrets, private keys, tokens, raw cookies, or long logs into .maestro/, product docs, or
tool adapter files.
Require explicit user approval for destructive or outward-facing actions (deploy, push/PR, prod data).
If uncertain, mark the fact unknown, cite the missing evidence, and ask the user through Coordinator.
Do not fabricate exact elapsed time or ETA; write unknown or clearly marked estimates.
```

## Key files (Kiro file references)

#[[file:.maestro/INSTRUCTIONS.md]]
#[[file:.maestro/engine/workflow.md]]
#[[file:.maestro/methodology.yaml]]
#[[file:COMMAND.md]]
