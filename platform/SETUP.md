# Maestro Setup Guide

## Documentation Entry Points

| Need | File |
| --- | --- |
| Fast workspace startup | [QUICKSTART.md](QUICKSTART.md) |
| Slash commands | [COMMAND.md](COMMAND.md) |
| Framework overview | [README.md](README.md) |
| Install, upgrade, and validation details | [SETUP.md](SETUP.md) |
| Entry point for AI agents | [AGENTS.md](AGENTS.md) |
| Entry point for Claude Code | [CLAUDE.md](CLAUDE.md) |
| Workflow source of truth | [.maestro/engine/workflow.md](.maestro/engine/workflow.md) |

## Requirements

- An AI coding tool that can read instruction files: Claude Code or Codex.
- Git.
- Python 3 for validation and local helper scripts.

## Workspace Shape

```text
maestro/
├── CLAUDE.md                      Claude Code entry point
├── AGENTS.md                      General AI-agent entry point
├── COMMAND.md                     Slash command index
├── GUIDELINES.md                  Fast usage guide
├── SETUP.md                       This file
├── README.md                      Framework overview
├── .maestro/                           Product-development control plane
├── .claude/                       Claude adapter: agents, skills, commands, hooks
├── .codex/                        Codex instructions and generated prompts
├── docs/                          Official product documentation
├── apps/                          Product applications
├── services/                      Deployable services
├── packages/                      Shared libraries and design systems
├── infra/                         Deployable infrastructure
├── tests/                         System, contract, performance, and E2E tests
└── inputs/                        User-provided reference documents
```

## 1. Clone The Workspace

```bash
git clone <repo-url> ~/Downloads/maestro
cd ~/Downloads/maestro
```

`maestro` is the product workspace root. New code is created directly under the relevant
component root. Existing code can be mounted or cloned into the proper root and registered in
`.maestro/registry/components.yaml`.

Do not copy `.claude/` into each component.

If you only want to commit and push inside individual service repositories and do not want the root
workspace to remain its own Git repository, detach the root `.git`:

```bash
scripts/remove-workspace-git.sh
```

Preview first:

```bash
scripts/remove-workspace-git.sh --dry-run
```

The script removes only the root `maestro/.git`. It does not touch
`services/<service-name>/.git`.

## 2. Verify Distribution Counts

```bash
echo "Agents: $(find .claude/agents -name '*.agent.md' 2>/dev/null | wc -l | tr -d ' ')"
echo "Skills: $(find .claude/skills -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')"
echo "Rules:  $(find .maestro/engine/rules -name '[0-9][0-9]-*.md' 2>/dev/null | wc -l | tr -d ' ')"
echo "Templates: $(find .maestro/engine/templates -maxdepth 1 -type f 2>/dev/null | wc -l | tr -d ' ')"
echo "Commands: $(find .claude/commands -maxdepth 1 -name '*.md' ! -name README.md 2>/dev/null | wc -l | tr -d ' ')"
```

Expected:

```text
Agents: 33
Skills: 231
Rules:  19
Templates: 46
Commands: 17
```

Strict validation:

```bash
python3 scripts/architecture-health-check.py --strict
```

## 3. Add User Inputs

Place project reference documents in `inputs/`:

```text
inputs/product/       PRDs, business specs, user stories
inputs/architecture/  HLDs, LLDs, ADRs, system diagrams
inputs/api/           OpenAPI/Swagger specs, contracts
inputs/domain/        Domain models, glossary, business rules
inputs/runbooks/      Operations playbooks, incident response
inputs/misc/          Uncategorized docs
```

Onboarding scans `inputs/` and cites it as user-provided knowledge.

## 4. Add Product Components

Create or mount source repositories into the right component roots:

```bash
git clone <auth-repo-url> services/nova-auth-service
git clone <web-repo-url> apps/nova-web-app
git clone <design-system-repo-url> packages/nova-design-system
```

`services/` is a normal product root. A service can be tracked in the monorepo or as an independent
repository, but it must be registered in `.maestro/registry/components.yaml` before agents rely on it.

During early framework maintenance, component roots may contain only README files. Register real components
before onboarding.

## 5. Onboard The Workspace

Open the root `maestro` folder in your AI coding tool and run:

```text
/coord
```

or:

```text
/onboard
```

Recommended flow:

```text
1. Clone maestro.
2. Put reference documents into inputs/.
3. Clone or create product components under apps/, services/, packages/, infra/, or tests/.
4. Run /coord or /onboard from the workspace root.
5. Review project knowledge, component registry, test policy, and coder candidates.
6. Approve /create-coders only for components that should receive generated coder agents.
7. Start implementation requests through /coord.
```

Built-in cross-cutting coders are available before component-specific coder generation:

- `coder-infra`: Terraform/IaC, Kubernetes, Docker, CI/CD.
- `coder-database`: schemas, migrations, queries, indexes.

They are marked `origin: "built-in"` in `.maestro/registry/agents.yaml` and do not mean the workspace has
already been onboarded.

## 6. Per-Tool Setup

Maestro ships entry points for multiple AI coding tools. Each tool has its own discovery rules.

### Claude Code

No extra setup is required. Claude Code discovers:

- `.claude/agents/**/*.agent.md`: 12 workflow agents, 3 built-in coders, and 19 specialist advisors.
- `.claude/skills/*/SKILL.md`: 231 skills.
- `.claude/commands/*.md`: 20 slash commands.
- `CLAUDE.md`: root system instructions.

### Codex CLI

`.codex/AGENTS.md` is read automatically.

Project-level `.codex/config.toml` may be ignored until Codex trusts the project. To activate it, add
the project to your user config:

```toml
[projects."/absolute/path/to/maestro"]
trust_level = "trusted"
```

You can also run `codex` once in the workspace and accept the trust prompt. After trust is granted,
Codex loads `.codex/config.toml`.

Without trust, Codex still reads `.codex/AGENTS.md`, but it skips project-level sandbox and approval
configuration. The workflow still works, but the tuned sandbox/approval posture is unavailable.

Codex sandboxing is a support layer, not the source of truth for component write scope. The source of
truth is `.maestro/runtime/workflow-state.yaml.active_task_id` plus
`.maestro/registry/agents.yaml.allowed_write_paths`.

Optional Codex plugin and slash commands:

```bash
python3 scripts/build-codex-plugin.py
codex plugin marketplace add "$(pwd)/.codex/marketplace"
codex plugin add maestro@maestro
codex plugin list --marketplace maestro

mkdir -p ~/.codex/prompts
cp .codex/prompts/*.md ~/.codex/prompts/
```

Notes:

- Run `python3 scripts/build-codex-plugin.py` after each clone, pull, or skill edit. The copied skills
  are gitignored.
- The Codex plugin ships skills only. The full workflow still needs `.maestro/`, routing, and workspace
  documents.

### Gemini Code Assist

`.gemini/GEMINI.md` is read automatically. No additional setup is required.

## Upgrade

Upgrade the framework by pulling the latest version in the root workspace:

```bash
cd ~/Downloads/maestro
git pull origin main
```

If the workspace has been onboarded and contains generated coders or task history, review these paths
carefully when resolving conflicts:

| Path | Why It Matters |
| --- | --- |
| `.maestro/knowledge/` | Durable project and component knowledge |
| `.maestro/work/tasks/` | Task history |
| `.maestro/work/bugs/` | Bug history |
| `.claude/agents/coders/coder-*.agent.md` | Generated service coders |
| `.maestro/engine/rules/15-*.md` and above | Advanced/custom workflow rules |
| `inputs/` | User-provided reference documents |

Check version:

```bash
cat .claude/settings.json | grep version
head -5 CHANGELOG.md
```

## Usage

Maestro uses a coordinator-driven workflow. You can interact through natural language:

```text
"Analyze this project"                    -> coordinator -> onboarding
"Add Google OAuth login"                  -> coordinator -> task-analysis -> coder-leader -> ...
"Check if the code is ready"              -> coordinator -> dev-verification
"Test the feature that was just built"    -> coordinator -> qc-runner
```

Or call commands directly:

```text
/onboard                    -> Scan project and create project knowledge
/analyze-task               -> Normalize task into a spec
/create-coders              -> Create service coder agents
/plan-dev                   -> Create implementation plan
/dev                        -> Implement code
/verify-dev                 -> Check Code Done
/handoff-qc                 -> Create QC handoff
/qc                         -> Run QC tests
/bug                        -> Route bug report
/sync-memory                -> Update memory
/skills                     -> Maintain installed skills
/policy-check               -> Validate workflow policy
/coord                      -> Call coordinator directly
/status                     -> Show workflow and activity dashboard
/resume-task                -> Resume interrupted task
```

Terminal mirrors for tools without project slash commands:

```bash
python3 scripts/status-dashboard.py --mode <compact|concise|dashboard|models|json>
python3 scripts/status-dashboard.py --mode dashboard --write
python3 scripts/agent-activity.py start --agent-id <agent> --phase <phase> --current-action <summary>
python3 scripts/architecture-health-check.py --strict --write-report
```

## Troubleshooting

### Claude Code Does Not See Maestro

Check the root entry point:

```bash
ls CLAUDE.md
```

Check distribution counts:

```bash
python3 scripts/architecture-health-check.py --strict
```

### Workflow Does Not Route Correctly

1. Check `.maestro/knowledge/index.yaml`.
2. Check `.maestro/knowledge/project.yaml`.
3. If either is missing or stale, run `/onboard`.
4. Check `.maestro/registry/agents.yaml` for active coders and write scope.

### Service Coder Does Not Exist

Generated service coders are created per project by Agent Factory. Run `/create-coders` after onboarding
and approve only the coders the project needs.

### Counts Do Not Match

Common causes:

```text
1. Pull or merge was incomplete.
2. .claude/ or .maestro/ had unresolved conflicts.
3. Skill, template, rule, or command counts changed but docs or health-check constants were not updated.
```

Run:

```bash
python3 scripts/architecture-health-check.py --strict
```

### CLAUDE.md Is Not Read

```bash
pwd
ls CLAUDE.md
```

Make sure the IDE opened the folder, not a single file.

### Onboarding Runs Every Time

Check project knowledge:

```bash
cat .maestro/knowledge/project.yaml | head -5
cat .maestro/knowledge/index.yaml | head -5
```

If files are empty or corrupt, run `/sync-memory --refresh-index`. If service structure changed, run
`/onboard --refresh <service>`.

### Windows Line Endings

```powershell
git config --global core.autocrlf input
```

Recommended `.gitattributes`:

```text
*.md text eol=lf
*.yaml text eol=lf
```

## Setup Checklist

- [ ] Clone the `maestro` repository.
- [ ] Put reference documents into `inputs/`.
- [ ] Clone or create product components under `apps/`, `services/`, `packages/`, `infra/`, or `tests/`.
- [ ] Run `python3 scripts/architecture-health-check.py --strict`.
- [ ] Open the root `maestro` folder in the AI coding tool.
- [ ] Test with `"Analyze this project"` or `/onboard`.
