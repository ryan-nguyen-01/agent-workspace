# Enterprise Agent Governance Artifacts

This directory stores official artifacts for production or enterprise autonomous agents.

Use these artifacts when an agent is not merely helping developers, but operating as part of a
business workflow with an Agent Mission, accountable owner, tool access, eval gates, and audit
obligations.

## Artifact Roots

```text
policies/              Governance policies, hard refusals, and owner obligations.
missions/              Per-agent mission, success criteria, non-goals, termination, owner.
behavior-contracts/    Typed I/O, refusal, escalation, forbidden tools, tone, SLA.
autonomy-policies/     Granted autonomy level, blast radius, cost cap, approval boundaries.
agent-definitions/     Persona, skills, tools, knowledge, memory bounds, guards, model routing.
eval-suites/           Golden, adversarial, regression, and drift eval definitions.
audit-logs/            Append-only version, eval, deployment, incident, and drift records.
interaction-protocols/ Agent-human, agent-agent, and agent-system protocol specs.
```

The methodology playbook is
[docs/governance/methodologies/enterprise-agent-governance.md](../methodologies/enterprise-agent-governance.md).

Templates live in `.maestro/engine/templates/` with descriptive `agent-*.template.*` names. The canonical
routing source is `.maestro/registry/artifacts.yaml`.
