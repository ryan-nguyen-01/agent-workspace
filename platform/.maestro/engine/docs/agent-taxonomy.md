# Agent Taxonomy

`maestro` has four different agent classes. Keep these terms separate in docs, registries, and handoffs.

```text
.claude/agents/
├── workflow/      class 1 — 12 control-plane agents
├── coders/        class 2 (built-in) + class 3 (generated)
└── specialists/   class 4 — 19 specialist advisors, grouped by category
```

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
- They are not component-specific implementation agents.
- They must not be replaced by generated coders.
- They are counted as `12 workflow agents`.

## 2. Built-in Cross-cutting Coders

Built-in cross-cutting coders are shipped with the framework because their scope often spans services.

Current built-ins:

- `coder-infra`: Terraform/IaC, Kubernetes, Docker, CI/CD.
- `coder-database`: schema, migrations, queries, indexes.

Rules:

- They have `origin: "built-in"` in `.maestro/registry/agents.yaml`.
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
- They are component-specific and must reference the target component in the agent registry.
- They write only inside approved `allowed_write_paths`.
- They must not touch `forbidden_paths`.
- Scope expansion requires user approval.

## 4. Specialist Advisors

Specialist advisors are domain experts that produce evidence-based recommendations **inside the
pipeline**. They are the newest agent class and live under `.claude/agents/specialists/<category>/`.

Categories and members (19 total):

- `architecture/` — api-designer, database-architect, cloud-architect, event-architect, ui-ux-designer
- `quality-security/` — security-auditor, performance-engineer, accessibility-auditor, code-reviewer
- `product/` — discovery-analyst, business-analyst, product-strategist
- `data-ai/` — data-engineer, ml-ai-architect
- `ops-devex/` — sre-observability, technical-writer, migration-strategist
- `research-qa/` — tech-researcher, qa-strategist

Rules (full set in `.maestro/engine/rules/16-specialist-advisory-rules.md`):

- They **advise**; they never write application code, assign coders, mark Code Done/QC Done, or approve gates.
- They are **not** user entrypoints — a workflow agent invokes them in-pipeline.
- Each writes exactly one artifact: `.maestro/work/tasks/<task-id>/advisories/<id>.yaml`.
- Their model comes from `model-routing.yaml > agent_model_map.specialist_advisors`.
- They run as sub-steps inside existing workflow states; they introduce no new state.
- Where they overlap a workflow agent (code-reviewer, business-analyst, qa-strategist, security-auditor) they **augment**, never replace it.
- Tool access is read + own-artifact-write only (`Read, Grep, Glob, Write`).

## Counting Rule

Use these counts separately:

```text
Workflow agents: 12
Built-in cross-cutting coders: 2
Specialist advisors: 19
Generated service coders: unlimited, per onboarded workspace
Framework-owned agent definition files: 12 + 2 + 19 = 33
```

Do not collapse the classes. The correct distribution wording is:
`12 workflow agents + 3 built-in cross-cutting coders + 20 specialist advisors` (35 framework-owned),
plus any generated service coders in an applied workspace.
