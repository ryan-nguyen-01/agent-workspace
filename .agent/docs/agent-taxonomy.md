# Agent Taxonomy

`agent-workspace` has three different agent classes. Keep these terms separate in docs, registries, and handoffs.

## 1. Workflow Agents

Workflow agents are the 12 fixed control-plane agents that run the process.

Examples:

- `coordinator`
- `onboarding`
- `agent-factory`
- `task-analysis`
- `solution-architect`
- `coder-leader`
- `dev-verification`
- `qc-handoff`
- `qc-runner`
- `bug-router`
- `memory-update`
- `workflow-policy`

Rules:

- They define routing, gates, state transitions, verification, QC, and memory.
- They are not service-specific implementation agents.
- They must not be replaced by generated coders.
- They are counted as `12 workflow agents`.

## 2. Built-in Cross-cutting Coders

Built-in cross-cutting coders are shipped with the framework because their scope often spans services.

Current built-ins:

- `coder-infra`: Terraform/IaC, Kubernetes, Docker, CI/CD.
- `coder-database`: schema, migrations, queries, indexes.

Rules:

- They have `origin: "built-in"` in `.runtime/context/agent-registry.yaml`.
- They are not generated from workspace onboarding.
- They do not prove that the workspace has been onboarded.
- Coder Leader may assign them only when task scope matches their permission contract.
- They still obey `allowed_write_paths`, `forbidden_paths`, approval gates, handoff, and dev verification.

## 3. Generated Service Coders

Generated service coders are created by `agent-factory` after workspace onboarding and user approval.

Examples:

- `coder-api`
- `coder-web`
- `coder-shared`
- `coder-payments`

Rules:

- They have `origin: "generated"` or an equivalent generated-coder registry entry.
- They are service-specific and must reference the target service in `service_id`.
- They write only inside approved `allowed_write_paths`.
- They must not touch `forbidden_paths`.
- Scope expansion requires user approval.

## Counting Rule

Use these counts separately:

```text
Workflow agents: 12
Built-in cross-cutting coders: 2
Generated service coders: unlimited, per onboarded workspace
Agent definition files: workflow agents + built-ins + generated coders
```

Do not say "14 workflow agents" when the repository has 14 `.agent.md` files. The correct wording is: `12 workflow agents + 2 built-in cross-cutting coders`.
