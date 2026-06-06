# Customization Guide — agent-workspace

How to extend `agent-workspace` following the current model: the user clones this repo, clones application repositories into `services/`, puts reference docs in `inputs/`, then runs onboarding from this workspace.

## Principles

```text
Do not copy .claude/ into service repos.
Do not create a root memory/ or state/.
Do not use scripts to run the main workflow.
Do not route raw user input straight into a sub-agent.
The coordinator is the single entrypoint.
```

The current runtime lives in:

```text
.runtime/context/   Project brain, service catalog, agent registry, test policy, workflow state, model/status/response UI
.runtime/status.md  Generated status artifact
.runtime/status.html Generated browser status dashboard
.runtime/tasks/     Task artifacts
.runtime/bugs/      Bug artifacts
inputs/            User-provided PRD/HLD/ADR/OpenAPI/glossary/runbooks
services/          Gitignored local clones of application repositories
```

## When to customize

Customize when the workspace needs additional truly-durable policy or knowledge:

```text
Add a generated service coder after onboarding
Add a built-in/cross-cutting coder with a clear permission contract
Add a specialized skill
Add a team policy rule
Add a new artifact template
Update docs so agents understand the workflow correctly
```

Do not customize just to route faster. Routing must still go through the Coordinator.

## Adding a Service Coder

Service coders should be created through the workflow:

```text
1. Clone the service into services/<service-name>/
2. Run /onboard
3. Review the service catalog and coder candidates
4. Approve /create-coders
5. Agent Factory creates .claude/agents/coders/coder-<service>.agent.md
6. Agent Factory updates .runtime/context/agent-registry.yaml
```

Do not create a service coder by hand without a service catalog and allowed/forbidden paths.

## Adding a Cross-Cutting Coder

Use when the scope is not within a single service, e.g. infra or database.

Checklist:

```text
1. Create .claude/agents/coders/coder-<scope>.agent.md
2. Add the contract to .runtime/context/agent-registry.yaml
3. Define allowed_read_paths, allowed_write_paths, forbidden_paths
4. Add escalation rules and test_policy
5. Update AGENTS.md, CLAUDE.md, README.md if it is a built-in shipped coder
6. Update CHANGELOG.md
```

Current built-ins:

```text
coder-infra      Terraform/IaC, Kubernetes, Docker, CI/CD
coder-database   schema, migrations, queries, indexes
```

## Adding a Workflow Agent

A workflow agent is a control-plane agent, not a coder. Add one only when there is a new phase/gate in the workflow.

Checklist:

```text
1. Create .claude/agents/workflow/<role>.agent.md
2. Update .agent/workflow.md
3. Update .runtime/context/workflow-state.yaml if there is a new state
4. Update .agent/templates/workflow-state.template.yaml
5. Add an artifact template if the agent has a new output
6. Update the related rules
7. Update CLAUDE.md, AGENTS.md, README.md, docs/agent-catalog.md, docs/agent-taxonomy.md
8. Update diagrams and CHANGELOG.md
```

Current workflow agents: 12. Built-in coders do not count as workflow agents.

## Adding a Skill

A skill is a capability, not an agent identity.

Checklist:

```text
1. Create .claude/skills/<skill-name>/SKILL.md
2. Run /skills refresh-registry
3. Update .runtime/context/skill-registry.yaml if metadata/risk is needed
4. Update skills-lock.json if the skill is lock-managed
5. Update .agent/docs/external-skills.md if it is an external skill
6. Update CHANGELOG.md if behavior or risk changes
```

For an existing skill, use:

```text
/skills status
/skills audit
/skills update <skill-name>
/skills refresh-registry
```

## Adding a Rule

A custom rule should use the prefix `19+` since built-in rules are `00-18`.

Checklist:

```text
1. Create .agent/rules/19-<name>.md
2. Specify Applies to, Rules, Violation handling
3. Update the CLAUDE.md rules list if the rule is default framework policy
4. Update CHANGELOG.md
```

Do not add a rule if it is only a temporary preference for one task. A temporary preference belongs in the task artifact.

## Adding a Template

A template is for an artifact with a stable schema.

Checklist:

```text
1. Create .agent/templates/<artifact>.template.yaml or .md
2. Update .agent/rules/12-artifact-contracts.md
3. Update the agent/command that will produce that artifact
4. Update docs if the artifact belongs to the main workflow
```

## Custom Routing

Do not use a local override config as the routing source of truth.

Standard routing:

```text
Raw user input -> /coord -> coordinator -> the right workflow phase
```

To change the default routing, edit the corresponding policy files:

```text
.agent/workflow.md
.claude/agents/workflow/coordinator.agent.md
.agent/rules/11-approval-gates.md
.runtime/context/workflow-state.yaml
```

Then update the docs and CHANGELOG.

## Override Workflow Settings

Default framework settings live in:

```text
.claude/settings.json
```

Only edit when you want to change the framework's default shipped behavior. For the runtime policy of an onboarded workspace, prefer writing to `.runtime/context/` through the appropriate workflow.

High-risk changes need a clear rule/approval:

```text
code_done_threshold
qc_handoff_required
blocker_stops_qc
coder_creation_requires_approval
memory_updates_enabled
```

## Integration Checklist

```text
□ Clone agent-workspace
□ Clone service repositories into services/<service-name>/
□ Put PRD/HLD/ADR/specs in inputs/
□ Run /coord or /onboard
□ Review project brain, service catalog, test policy, coder candidates
□ Approve /create-coders for the right services
□ Start a task via /coord
```

## Upgrade Framework

When `agent-workspace` has a new version:

```text
1. Pull the new version in the agent-workspace repo
2. Resolve conflicts carefully in .runtime/context, .runtime/tasks, .runtime/bugs
3. Do not overwrite generated coder agents if the workspace is already onboarded
4. See CHANGELOG.md for breaking changes
5. Run /status to check state
```
