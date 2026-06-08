---
description: "maestro /status — Report current workflow state, execution mode, verification owner, brain freshness, generated coders, task status, mo..."
argument-hint: "[request or args]"
---

You are running the maestro `/status` workflow command inside Codex.

Follow `.codex/AGENTS.md` (or `AGENTS.md`) routing and the framework rules. Route every
request through the coordinator model; do not bypass approval gates, security/secret rules,
or the task-analysis source-edit gate. If the maestro framework files
(`.maestro/engine/`, `.maestro/registry/`, `.maestro/knowledge/`, `.maestro/work/`, `.maestro/runtime/`, `.claude/commands/status.md`) are present, defer to them as the
authoritative contract — this prompt is a portable mirror.

User input for this command: $ARGUMENTS

---
## Command contract (mirrored from .claude/commands/status.md)

# /status

## Purpose

Report current workflow state, execution mode, verification owner, brain freshness, generated coders, task status, model routing, response UI mode, and live agent activity.

## Responsible agent

coordinator

## Required rules

```text
00-core-rules.md
01-project-brain-rules.md
12-artifact-contracts.md
15-model-routing-observability-rules.md
```

## Workflow

```text
1. Read .maestro/runtime/workflow-state.yaml.
2. Report execution_mode and verification_owner.
3. Read .maestro/knowledge/index.yaml freshness.
4. Read .maestro/config/model-routing.yaml for agent model profiles when present.
5. Read .maestro/runtime/agent-activity.yaml for live activity dashboard when present.
6. Read .maestro/config/response-ui.yaml for status layout mode when present.
7. Read .maestro/knowledge/project.yaml freshness only if needed.
8. Read .maestro/registry/components.yaml summary only when relevant.
9. Read .maestro/registry/agents.yaml summary only when relevant.
10. If task id is provided, read task artifacts status.
11. When terminal artifacts are requested, render `.maestro/runtime/reports/status.md` and `.maestro/runtime/reports/status.html` from the same status data.
12. If the adapter supports shell hooks or phase callbacks, it may update telemetry through `python3 scripts/agent-activity.py`.
13. Report next recommended command.
```

## Output format

```yaml
workflow_state: "<state>"
execution_mode: "direct|assisted|governed|unknown"
verification_owner: "agent|user|shared|unknown"
project_brain: "fresh|stale|missing"
services_detected: 0
active_coder_agents: 0
task_state: null
model_routing:
  source: ".maestro/config/model-routing.yaml"
  active_profiles: []
response_ui:
  source: ".maestro/config/response-ui.yaml"
  mode: "dashboard|compact|concise|models|json"
  language: "vi|en|unknown"
status_artifacts:
  markdown: ".maestro/runtime/reports/status.md"
  html: ".maestro/runtime/reports/status.html"
  generated: true|false
agent_activity:
  status: "idle|running|blocked|unknown"
  running_agents: 0
  current:
    - agent_id: ""
      phase: ""
      status: ""
      model_profile: ""
      model_id: "unknown"
      current_action: ""
      elapsed_seconds: "unknown"
      eta_seconds: "unknown"
next_command: "/onboard|/create-coders|/analyze-task|..."
```

## Display rules

```text
Show model profile and model id only when known from model-routing.yaml or the adapter.
For long-running work, show current_action, elapsed time, and ETA from agent-activity.yaml.
Use response-ui defaults.status_mode unless the user asks for compact, models, json, or another explicit format.
When writing status artifacts, derive them from the status data. Do not include secrets, raw prompts, credentials, private keys, raw cookies, or long logs.
Adapters may use `python3 scripts/agent-activity.py start|heartbeat|block|complete` to keep this dashboard current.
```
