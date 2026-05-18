# Quickstart

Use this when setting up `agent-workspace` as the coordination workspace for one or more service repositories.

## Read This First

| Need | Read |
|---|---|
| Start a workspace quickly | `QUICKSTART.md` |
| Slash commands | `COMMAND.md` |
| Understand the framework | `README.md` |
| Install/upgrade details | `SETUP.md` |
| AI-agent entrypoint | `AGENTS.md` |
| Claude Code entrypoint | `CLAUDE.md` |
| Workflow source of truth | `.agent/workflow.md` |

## 1. Clone Workspace

```bash
git clone <repo-url> ~/Downloads/agent-workspace
cd ~/Downloads/agent-workspace
```

## 2. Add Project Inputs

Put reference docs under `inputs/`:

```text
inputs/product/       PRD, user stories
inputs/architecture/  HLD, LLD, ADRs
inputs/api/           OpenAPI, Swagger, contracts
inputs/domain/        Glossary, business rules
inputs/runbooks/      Ops playbooks
```

## 3. Clone Services

Clone or place application repositories under `services/`:

```bash
git clone <api-repo-url> services/api
git clone <web-repo-url> services/web
git clone <worker-repo-url> services/worker
```

## 4. Onboard

Open `agent-workspace` in your AI coding environment and start through Coordinator:

```text
/coord
```

or:

```text
/onboard
```

Review the generated project brain, service catalog, test policy, and coder candidates.

## 5. Approve Coders

Approve only the service coders you want generated:

```text
/create-coders
```

Built-in coders are already available:

- `coder-infra` for Terraform/IaC, Kubernetes, Docker, CI/CD.
- `coder-database` for schema, migrations, queries, indexes.

## 6. Run Work

Start all implementation requests through Coordinator:

```text
/coord Implement <task>
```

Expected flow:

```text
coordinator
→ task-analysis
→ coder-leader
→ scoped coder(s)
→ dev-verification
→ qc-handoff
→ qc-runner
→ memory-update
```
