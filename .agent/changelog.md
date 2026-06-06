# `.claude` Changelog

## Framework-template maintenance fast path

Added explicit framework-template behavior so the reusable distribution can be maintained without running project onboarding:

- `framework-template` + `not_applied` treats `NEED_ONBOARDING`, empty service catalogs, and seed brain values as expected.
- Coordinator classifies `target_scope` before broad brain/service reads.
- Framework maintenance sets `requires_onboarding: false` unless application source under `services/<service-name>/` is involved.
- Trivial framework maintenance can use lightweight fast-track evidence instead of full task artifacts.
- `/workspace-mode` switches `distribution_mode` between `framework-template` and `workspace` through Coordinator-owned workflow-state updates.
- `/workspace-mode repair` and `/policy-check snapshot` now use the `workflow-policy` agent checklist for migration/snapshot validation.
- Workflow Policy validates artifact-only snapshots without requiring `services/` or Python/Node/script dependencies, catches Code Done/QC Done gate bypasses, and offers dry-run-first mode repair.
- Coordinator, Task Analysis, Coder Leader, Dev Verification, QC Handoff, and QC Runner now use conditional reads so framework maintenance does not load project brain, registry, service catalog, test policy, or task artifacts unnecessarily.
- Runtime skill loading now starts from `skill-registry.yaml` and must not scan/read all of `.claude/skills/**`.
- Cross-tool entrypoints were aligned for Codex, Cursor, Gemini, and GitHub Copilot.
- Seed runtime files now describe `services/` as the application-source workspace and `.runtime/context` as the service control plane.
- Cursor hooks now enforce architecture approval, standard plan artifacts, active coder write scope, and broader destructive-command blocking before source edits or shell execution.
- Workflow references now include `/workspace-mode`, artifact snapshot policy checks, and approval gates R-011-10b through R-011-14.
- Context economy layer added: project/service archetypes, signature-first onboarding, project_profile, service profile.context_hints, context_economy, and task context_plan.
- Planning/coding now blocks when context confidence is low or service/test/contract ownership is unresolved.
- Cursor source-edit gating now fails closed, covers common universal source roots, requires context_plan for all applied-service edits including fast-track, and requires lightweight service-assignments.yaml for applied-service fast-track.
- Runtime/template approval_gates now include the full R-011 approval surface, service-brain no longer encourages full service-root reads, and docs counts were synced.
- Model routing and observability added: model-routing.yaml maps agents to stable model profiles, agent-activity.yaml backs `/status`, `scripts/status-dashboard.py` provides a terminal mirror, and R-015 governs model fallback plus token/cost/ETA reporting.
- Response UI contract added: response-ui.yaml defines compact/concise/dashboard/models/dev/review/policy markdown layouts for Claude, Codex, Cursor, Gemini, and Copilot, while documenting that native client chrome remains tool-owned.
- Status artifacts added: `python3 scripts/status-dashboard.py --mode dashboard --write` generates `.runtime/status.md` and `.runtime/status.html` from workflow state, model routing, agent activity, and response UI.
- 9.5+ hardening helpers added: `scripts/agent-activity.py` updates adapter telemetry and `scripts/architecture-health-check.py --strict` catches deterministic drift without replacing agent-native `/policy-check`.
- Scoped model overrides added: `model-routing.yaml.model_overrides` supports safe model switching without editing agent files or removing stable profiles.
- `/status` terminal mirror now reports Project Brain freshness and selected response UI mode, model-routing template ships the complete runtime seed agent map, docs treat `services/` as an optional empty local clone workspace, and architecture health checks catch these drift classes.
- Bug routing contract clarified: task-level `bugs.yaml` is an index only, canonical bug details must live under `.runtime/bugs/blockers/` or `.runtime/bugs/non-blockers/`, and health checks now detect missing canonical bug artifacts referenced by task indexes.
- Coding error feedback loop added: confirmed implementation errors carry root cause, prevention rule, regression check, and recurrence key; Memory Update promotes durable lessons into feedback patterns/anti-patterns; future Task Analysis and Coder Leader context packs include relevant prevention items.
- Status HTML now renders as a GitHub README-style card with tabs, hero banner, metric cards, and raw status audit text; health checks verify the generated HTML style marker.

## Dynamic agent architecture installed

Replaced static agent and technology skill set with a project-aware workflow:

```text
Coordinator
Onboarding
Agent Factory
Task Analysis
Coder Leader
Generated Service Coders
Dev Verification
QC Handoff
QC Runner
Bug Router
Memory Update
Workflow Policy
```

Project brain now starts in `NEED_ONBOARDING` state.

## Skill registry hardening

Implemented review fixes without running project onboarding:

```text
settings.json and settings.local.json are now valid JSON objects.
workflow.md duplicate skill-composition section removed.
rules/README.md rule 14 formatting fixed.
.runtime/context/skill-registry.yaml added as machine-readable skill selection source of truth.
Agent Factory and /create-coders now use skill-registry.yaml before external-skills.md.
High-risk and failed external skills are represented as explicit registry gates.
```

## Deep onboarding and reuse enforcement

Added deeper onboarding support without scanning the real project:

- project-brain.yaml now has deep_project_intelligence placeholder sections.
- project-brain and service-brain templates now include reusable assets, coding flow, business flows, reuse rules, anti-patterns, evidence, and confidence fields.
- task-analysis template now includes reuse_and_convention_analysis.
- dev-verification template now includes reuse_and_convention_check.
- memory-update template now includes reuse_and_convention_memory_updates.
- Onboarding, Task Analysis, Coder Leader, Service Coder, Dev Verification, and Memory Update instructions now enforce reuse-before-create behavior.
- Added docs/deep-onboarding.md as the human-readable standard.
[session-end] 2026-05-18T06:27:46Z
[session-end] 2026-05-18T06:39:46Z
[session-end] 2026-05-18T06:47:21Z
[session-end] 2026-05-18T06:49:16Z
[session-end] 2026-05-18T07:06:43Z
[session-end] 2026-05-18T07:15:32Z
[session-end] 2026-05-18T07:25:14Z
[session-end] 2026-06-02T04:18:49Z
[session-end] 2026-06-02T04:41:22Z
[session-end] 2026-06-02T06:20:22Z
[session-end] 2026-06-02T08:25:09Z
[session-end] 2026-06-03T01:17:40Z
[session-end] 2026-06-03T01:27:03Z
[session-end] 2026-06-06T09:04:26Z
