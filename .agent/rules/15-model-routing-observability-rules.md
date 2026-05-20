# R-015: Model Routing and Observability Rules

## Applies to

Coordinator, all workflow agents, built-in coders, generated service coders, status/reporting commands, and tool entrypoints.

## Rules

```text
R-015-01: `.runtime/context/model-routing.yaml` is the source of truth for agent-to-model-profile routing.
R-015-02: Agents must route by stable model_profile names (`fast_router`, `deep_reasoning`, `coding`, `coding_planner`, `verification`, `memory_light`) instead of scattering provider-specific model IDs across agent files.
R-015-03: Provider model IDs are defaults/aliases only. If a tool account does not support the configured model, use the best available equivalent and record the fallback in `.runtime/context/agent-activity.yaml`.
R-015-04: Deep reasoning work uses the `deep_reasoning` profile. This includes task-analysis, solution-architect, workflow-policy, blocker bug routing, architecture/security/data/contract ambiguity, and high-risk scope decisions.
R-015-05: Coding work uses the `coding` or `coding_planner` profile. This includes coder-leader planning, generated service coders, `coder-infra`, `coder-database`, implementation, refactors, tests, and code review.
R-015-06: Default provider mapping: Claude deep reasoning -> Opus, Claude coding -> Sonnet; Codex deep reasoning -> GPT-5.5, Codex coding -> Codex coding model (`gpt-5.3-codex` by default). These are configurable in `model-routing.yaml`.
R-015-07: `/status` must surface agent activity from `.runtime/context/agent-activity.yaml`: agent id, phase, status, current action, model profile/model id when known, elapsed time, ETA, token budget, token usage, and cost when known.
R-015-08: Do not fabricate exact token usage, cost, elapsed time, or ETA. If the tool does not expose reliable usage metrics, write `unknown` or clearly mark estimates as `source: estimated`.
R-015-09: Activity records must not include secrets, raw prompts, raw cookies, private keys, credentials, or long logs.
R-015-10: Long-running phases should update `agent-activity.yaml` when the current action changes, when the phase blocks, and when the phase completes.
R-015-11: Coordinator is responsible for initializing activity records at phase start and closing them at phase end. A delegated agent may update its own heartbeat when the adapter supports it.
R-015-12: Model escalation is allowed when a configured trigger fires (for example architecture conflict, security risk, state dispute, destructive operation, or cross-service contract ambiguity). Record the escalation reason.
R-015-13: `.runtime/context/response-ui.yaml` is the source of truth for text response layout modes across Claude, Codex, Cursor, Gemini, and GitHub Copilot.
R-015-14: Tool entrypoints must reference response-ui when they define answer format, status layout, or completion/report structure.
R-015-15: User-requested output format overrides response-ui for the current response unless it would hide required evidence, safety warnings, policy decisions, or unknown/estimated token-cost labels.
R-015-16: Response UI modes may change presentation order and verbosity, but must not change workflow gates, approval requirements, model routing, write scopes, or evidence requirements.
R-015-17: Native chat UI chrome is client-owned. The framework controls markdown/text structure and terminal/dashboard artifacts, not Claude/Copilot/Cursor native panel layout.
R-015-18: Copilot/Gemini support for response-ui is best-effort; do not claim hard UI enforcement where the tool exposes no hook or plugin surface.
R-015-19: Generated status artifacts (`.runtime/status.md`, `.runtime/status.html`) must be derived from model-routing, agent-activity, response-ui, and workflow state. They must not include secrets, raw prompts, raw cookies, credentials, private keys, or long logs.
R-015-20: Tool adapters may use `scripts/agent-activity.py` to update activity telemetry at phase start, heartbeat, block, and completion. Values written by this helper are still governed by R-015-08 and R-015-09.
R-015-21: `scripts/architecture-health-check.py` is an optional deterministic drift checker for CI/local maintenance. It does not replace the agent-native `/policy-check` contract and must not become a required runtime dependency for workflow-policy.
R-015-22: Model switching must use `.runtime/context/model-routing.yaml.model_overrides` or a recorded adapter fallback. Do not edit agent files or remove stable model profiles to switch models. Overrides must keep provider/profile contracts valid, include a reason when policy requires it, and be visible in agent activity/status when used.
```

## Required artifacts

```text
.runtime/context/model-routing.yaml
.runtime/context/agent-activity.yaml
.runtime/context/response-ui.yaml
.agent/templates/model-routing.template.yaml
.agent/templates/agent-activity.template.yaml
.agent/templates/response-ui.template.yaml
```

## Generated status artifacts

```text
.runtime/status.md
.runtime/status.html
```

## Optional deterministic helpers

```text
scripts/agent-activity.py
scripts/architecture-health-check.py
```

## Violation handling

If the selected model profile is missing or activity telemetry is stale, continue only when the task is low risk. For high-risk applied-service work, route to Coordinator or Workflow Policy before continuing.
