# /status

## Purpose

Report current workspace mode, workflow state, brain freshness, generated coders, task status, model routing, response UI mode, and live agent activity.

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
1. Read .runtime/context/workflow-state.yaml.
2. Report distribution_mode and instance_status.
3. Read .runtime/context/index.yaml freshness.
4. Read .runtime/context/model-routing.yaml for agent model profiles when present.
5. Read .runtime/context/agent-activity.yaml for live activity/token/cost dashboard when present.
6. Read .runtime/context/response-ui.yaml for status layout mode when present.
7. Read .runtime/context/project-brain.yaml freshness only if needed.
8. Read .runtime/context/service-catalog.yaml summary only when relevant.
9. Read .runtime/context/agent-registry.yaml summary only when relevant.
10. If task id is provided, read task artifacts status.
11. When terminal artifacts are requested, render `.runtime/status.md` and `.runtime/status.html` from the same status data.
12. If the adapter supports shell hooks or phase callbacks, it may update telemetry through `python3 scripts/agent-activity.py`.
13. Report next recommended command.
```

## Output format

```yaml
workflow_state: "<state>"
distribution_mode: "framework-template|workspace"
instance_status: "not_applied|applied|onboarded"
project_brain: "fresh|stale|missing"
services_detected: 0
active_coder_agents: 0
task_state: null
model_routing:
  source: ".runtime/context/model-routing.yaml"
  active_profiles: []
response_ui:
  source: ".runtime/context/response-ui.yaml"
  mode: "dashboard|compact|concise|models|json"
  language: "vi|en|unknown"
status_artifacts:
  markdown: ".runtime/status.md"
  html: ".runtime/status.html"
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
      token_usage: "unknown|estimated|actual"
      cost_usd: "unknown"
next_command: "/onboard|/create-coders|/analyze-task|..."
```

## Display rules

```text
Show model profile and model id only when known from model-routing.yaml or the adapter.
Show actual token/cost only when the tool exposes reliable usage metrics.
When exact usage is unavailable, show estimated or unknown; never invent precise token/cost numbers.
For long-running work, show current_action, elapsed time, and ETA from agent-activity.yaml.
Use response-ui defaults.status_mode unless the user asks for compact, models, json, or another explicit format.
When writing status artifacts, derive them from the status data. Do not include secrets, raw prompts, credentials, private keys, raw cookies, or long logs.
Adapters may use `python3 scripts/agent-activity.py start|heartbeat|block|complete` to keep this dashboard current.
```
