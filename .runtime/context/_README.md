# `.runtime/context`

This directory is the durable context and runtime memory for `.claude` agents.

Agents read `index.yaml` first, then open only the memory files relevant to the current task. This prevents each new conversation from rereading the whole brain.

## Required files

```text
index.yaml               Small routing index for selective reads
project-brain.yaml       Project-level memory, policies, freshness
service-catalog.yaml     Service inventory and source-code paths
agent-registry.yaml      Generated service coders and approved scopes
test-policy.yaml         Per-service test and manual verification policy
skill-registry.yaml      Stack-to-skill selection registry
model-routing.yaml       Agent-to-model profile routing policy
agent-activity.yaml      Status dashboard, activity, ETA, token/cost telemetry
response-ui.yaml         Response layout modes for chat/status/report outputs
workflow-state.yaml      Current workflow state
summary.md               Human-readable short project memory
architecture.md          Durable architecture and flow notes
conventions.md           Durable coding conventions
common/generics.md       Reusable asset index
feedback/                Patterns and anti-patterns
services/<service>.yaml  Per-service brain and service-specific memory
```

Generated status artifacts live outside this directory at `.runtime/status.md` and `.runtime/status.html`. Regenerate them with `python3 scripts/status-dashboard.py --mode dashboard --write`; do not treat them as source of truth.

Activity telemetry can be updated by adapters with `python3 scripts/agent-activity.py`. Optional deterministic drift reports are generated at `.runtime/architecture-health-report.json` and `.runtime/architecture-health-report.md` by `python3 scripts/architecture-health-check.py --strict --write-report`. These helpers do not replace the agent-native `/policy-check`.

Model switches live in `model-routing.yaml.model_overrides`. Do not switch models by editing agent files or removing stable profile names.

Application source code does not live here. It lives in local clones under `services/<service-name>` or another path recorded in `service-catalog.yaml`. The root `services/` workspace may be empty in framework-template mode and does not require placeholder files.

Do not store secrets, passwords, raw tokens, or long logs here.
