# Agent Workspace — Hướng dẫn cài đặt

## Documentation entry points

| Need | File |
| --- | --- |
| Khởi tạo workspace nhanh | [QUICKSTART.md](QUICKSTART.md) |
| Slash commands | [COMMAND.md](COMMAND.md) |
| Tổng quan framework | [README.md](README.md) |
| Cài đặt/upgrade/validation chi tiết | [SETUP.md](SETUP.md) |
| Entry point cho AI agents | [AGENTS.md](AGENTS.md) |
| Entry point cho Claude Code | [CLAUDE.md](CLAUDE.md) |
| Workflow source of truth | [.agent/workflow.md](.agent/workflow.md) |

## Yêu cầu

- Một AI coding tool có thể đọc instruction files: Claude Code, Codex, Cursor, Gemini, GitHub Copilot, Aider, Continue, Cody, hoặc tương đương
- Git (để clone repo)

---

## Cấu trúc Agent Workspace

```text
agent-workspace/
├── CLAUDE.md                      ← Entry point (Claude đọc file này đầu tiên)
├── AGENTS.md                      ← Entry point chung cho AI coding agents
├── COMMAND.md                     ← Slash command index
├── GUIDELINES.md                  ← Cách dùng nhanh
├── SETUP.md                       ← File này
├── README.md                      ← Tổng quan dự án
├── .codex/                        ← Codex instructions
├── .cursor/                       ← Cursor rules
├── .gemini/                       ← Gemini instructions
├── .agent/                        ← Tool-neutral workflow source
│   ├── workflow.md
│   ├── rules/                     ← 19 workflow rules
│   ├── templates/                 ← 22 artifact templates
│   └── docs/                      ← Documentation + visual diagrams
├── .runtime/                      ← Runtime memory and workflow artifacts
│   ├── context/                   ← Project brain + service contracts + workflow state + model/status/response UI telemetry
│   ├── tasks/                     ← Task artifacts
│   └── bugs/                      ← Bug reports
├── .claude/                       ← Claude adapter
│   ├── agents/                    ← 12 workflow agents + built-in/generated coders
│   │   ├── coordinator.agent.md
│   │   ├── onboarding.agent.md
│   │   ├── agent-factory.agent.md
│   │   ├── task-analysis.agent.md
│   │   ├── solution-architect.agent.md
│   │   ├── coder-leader.agent.md
│   │   ├── dev-verification.agent.md
│   │   ├── qc-handoff.agent.md
│   │   ├── qc-runner.agent.md
│   │   ├── bug-router.agent.md
│   │   ├── memory-update.agent.md
│   │   └── workflow-policy.agent.md
│   │
│   ├── skills/                    ← 231 skill definitions
│   │   ├── skill-project-brain/SKILL.md      (12 workflow skills)
│   │   ├── skill-task-analysis/SKILL.md
│   │   ├── react/SKILL.md                    (219 technical skills)
│   │   ├── prisma/SKILL.md
│   │   └── ...
│   │
│   ├── commands/                  ← 17 workflow commands
│   │   ├── onboard.md
│   │   ├── dev.md
│   │   └── ...
│   └── settings.json
├── inputs/                        ← User-provided reference docs (PRD, HLD, ADR, OpenAPI…)
│   ├── product/                   PRD, business specs, user stories
│   ├── architecture/              HLD, LLD, ADRs, system diagrams
│   ├── api/                       OpenAPI/Swagger specs, contracts
│   ├── domain/                    Domain models, glossary, business rules
│   ├── runbooks/                  Ops playbooks, incident response
│   └── misc/                      Uncategorized
└── services/                      ← Ignored workspace for cloned application repos
```

---

## Cài Đặt Workspace

`agent-workspace` là workspace điều phối. User clone repo này về, sau đó clone các application/service repositories vào `services/`. Không copy `.claude/` sang từng service repo, không cài global vào `~/.claude/`, và không dùng subtree/submodule để nhúng framework vào project khác.

### 1. Clone agent-workspace

```bash
git clone <repo-url> ~/Downloads/agent-workspace
cd ~/Downloads/agent-workspace
```

Nếu user chỉ muốn commit/push trong từng service repo và không muốn workspace
điều phối này còn là Git repo riêng, có thể detach root `.git`:

```bash
scripts/remove-workspace-git.sh
```

Script này chỉ xóa `.git` ở root `agent-workspace`, không đụng vào
`services/<service-name>/.git`. Có thể kiểm tra trước bằng:

```bash
scripts/remove-workspace-git.sh --dry-run
```

Expected distribution shape:

```bash
echo "Agents: $(find .claude/agents -name '*.agent.md' 2>/dev/null | wc -l | tr -d ' ')"
echo "Skills: $(ls -d .claude/skills/*/SKILL.md 2>/dev/null | wc -l | tr -d ' ')"
echo "Rules:  $(find .agent/rules -name '[0-9][0-9]-*.md' 2>/dev/null | wc -l | tr -d ' ')"
```

```text
Agents: 33
Skills: 231
Rules:  18
```

### 2. Add user inputs

Đặt tài liệu tham chiếu của dự án vào `inputs/`:

```text
inputs/product/       PRD, business specs, user stories
inputs/architecture/  HLD, LLD, ADRs, system diagrams
inputs/api/           OpenAPI/Swagger specs, contracts
inputs/domain/        Domain models, glossary, business rules
inputs/runbooks/      Ops playbooks, incident response
inputs/misc/          Uncategorized docs
```

### 3. Clone services

Clone hoặc đặt source repositories vào `services/<service-name>/`:

```bash
git clone <api-repo-url> services/api
git clone <web-repo-url> services/web
git clone <worker-repo-url> services/worker
```

`services/` được gitignored trong repo `agent-workspace`, nên source code của app không bị commit vào framework.
Trong framework-template mode, `services/` có thể rỗng và không cần file scaffold bên trong; clone service repo thật vào đây khi áp dụng workspace.

### 4. Onboard workspace

Mở chính repo `agent-workspace` trong IDE/Claude Code rồi chạy:

```text
/coord
```

hoặc:

```text
/onboard
```

Recommended flow:

```text
1. Clone agent-workspace.
2. Put reference docs into inputs/.
3. Clone application repositories into services/.
4. Run /coord or /onboard from agent-workspace.
5. Review project brain, service catalog, test policy, and coder candidates.
6. Approve /create-coders only for services that should receive generated service coders.
7. Start implementation requests through /coord.
```

Built-in cross-cutting coders are available before service-specific coder generation:

- `coder-infra`: Terraform/IaC, Kubernetes, Docker, CI/CD.
- `coder-database`: schema, migrations, queries, indexes.

They are marked `origin: "built-in"` in `.runtime/context/agent-registry.yaml` and do not mean the workspace has already been onboarded.

### 5. Per-tool setup (optional)

Agent Workspace ship sẵn entrypoints cho 5 AI tools. Mỗi tool có convention riêng — phần này nói rõ những step **tool-specific** cần làm thủ công.

#### Claude Code

Không cần setup thêm. Claude Code tự discover:

- `.claude/agents/**/*.agent.md` — 12 workflow agents + 2 built-in coders + 19 specialist advisors qua Agent tool
- `.claude/skills/*/SKILL.md` — 231 skills qua Skill tool
- `.claude/commands/*.md` — 17 slash commands (`/coord`, `/onboard`, …)
- `CLAUDE.md` ở root — system instructions

#### Codex CLI

`.codex/AGENTS.md` được Codex đọc tự động.

Tuy nhiên **`.codex/config.toml` (project-level) BỊ IGNORE mặc định** vì Codex yêu cầu user phải trust project trước khi load config. Để kích hoạt:

```toml
# Thêm vào ~/.codex/config.toml của bạn:
[projects."/absolute/path/to/agent-workspace"]
trust_level = "trusted"
```

Hoặc đơn giản hơn: chạy `codex` lần đầu trong workspace và accept trust prompt khi Codex hỏi. Sau đó các lần sau Codex sẽ load `.codex/config.toml` (sandbox mode, project doc fallback, approval policy).

Nếu không trust, Codex vẫn dùng `.codex/AGENTS.md` (luôn đọc) nhưng bỏ qua `.codex/config.toml`. Workflow vẫn chạy được, chỉ mất phần sandbox/approval tinh chỉnh.

Lưu ý: Codex sandbox là lớp hỗ trợ, không phải hard gate theo từng service. Source of truth cho write scope vẫn là `.runtime/context/workflow-state.yaml.active_task_id` và `.runtime/context/agent-registry.yaml.allowed_write_paths`.

Verify project-level config schema tại [`developers.openai.com/codex/config-reference`](https://developers.openai.com/codex/config-reference).

**Codex plugin (231 skills) + slash commands — tùy chọn.** Codex CLI 0.132+ có plugin system riêng.
Cài skill layer của framework dưới dạng Codex plugin:

```bash
# 1. Sinh plugin (BẮT BUỘC chạy trước — bản copy skills bị gitignore, không có sẵn sau git clone/pull)
python3 scripts/build-codex-plugin.py
# 2. Add marketplace của repo + cài plugin
codex plugin marketplace add "$(pwd)/.codex/marketplace"
codex plugin add agent-workspace@agent-workspace
# 3. Verify → (installed, enabled), 231 skills vào cache
codex plugin list --marketplace agent-workspace
```

Lấy 15 workflow command thành Codex `/` slash command (custom prompts):

```bash
mkdir -p ~/.codex/prompts && cp .codex/prompts/*.md ~/.codex/prompts/
```

Lưu ý:

- Chạy lại `python3 scripts/build-codex-plugin.py` sau mỗi lần `git clone`/`git pull` (skills copy bị gitignore) và sau khi sửa skills.
- `/aw-init` và `/access` là Claude-specific nên KHÔNG có trong Codex prompts.
- Codex plugin chỉ ship skills; full workflow (`.agent/`, `.runtime/`, routing) vẫn cần làm việc trong repo này. Chi tiết: [`.codex/AGENTS.md`](.codex/AGENTS.md).

#### Cursor

Cursor tự discover:

- `.cursor/rules/*.mdc` — 4 glob-targeted rule files (auto-apply theo file type bạn đang edit)
- `.cursor/hooks.json` — lifecycle hooks (gating edits + shell commands)

Hooks scripts dùng `bash` + `grep`/`sed` (BSD/GNU portable), không yêu cầu `jq`. Nếu hệ thống có `jq`, scripts dùng `jq` cho JSON parsing robust hơn — không có cũng OK.

Hooks chỉ chạy trong **Cursor IDE**. Claude Code / Codex / Gemini KHÔNG respect `.cursor/hooks.json` — workflow gates ở các tool khác đến từ AGENTS.md / CLAUDE.md / `.codex/AGENTS.md` / `.gemini/GEMINI.md`.

Schema verify tại [`cursor.com/docs/agent/hooks`](https://cursor.com/docs/agent/hooks).

#### Gemini Code Assist

`.gemini/GEMINI.md` được Gemini đọc tự động. Không config thêm.

#### GitHub Copilot

`.github/copilot-instructions.md` được Copilot Chat đọc tự động. Không config thêm.

## Upgrade

Upgrade framework bằng cách pull version mới trong chính workspace `agent-workspace`.

```bash
cd ~/Downloads/agent-workspace
git pull origin main
```

Nếu workspace đã onboard và có generated coders/task history, kiểm tra các folder runtime này khi resolve conflict:

| File/Folder                       | Lý do                                              |
| --------------------------------- | -------------------------------------------------- |
| `.runtime/context/`                | Brain, service contracts, workflow state, feedback |
| `.runtime/tasks/`                  | Task history                                       |
| `.runtime/bugs/`                   | Bug history                                        |
| `.claude/agents/coders/coder-*.agent.md` | Generated service coders                    |
| `.agent/rules/15-*.md` trở lên   | Custom rules                                       |
| `inputs/`                         | User-provided reference docs (PRD/HLD/ADR/specs)   |

### Kiểm tra version

```bash
# Xem version hiện tại
cat .claude/settings.json | grep version
# hoặc
head -5 CHANGELOG.md
```

---

## Sử dụng

### Cách gọi workflow

Agent Workspace sử dụng **coordinator-driven workflow**. Bạn có thể giao tiếp bằng:

#### 1. Ngôn ngữ tự nhiên (khuyến nghị)

Claude tự động route qua coordinator đến đúng workflow agent:

```text
"Phân tích dự án này"                      → coordinator → onboarding
"Thêm tính năng login bằng Google OAuth"   → coordinator → task-analysis → coder-leader → ...
"Kiểm tra code đã sẵn sàng chưa"          → coordinator → dev-verification
"Test tính năng vừa implement"             → coordinator → qc-runner
```

#### 2. Slash commands (direct)

Dùng commands để gọi trực tiếp workflow phase:

```bash
/onboard                    → Scan project, tạo project brain
/analyze-task               → Normalize task thành spec
/create-coders              → Tạo service coder agents
/plan-dev                   → Lên plan implementation
/dev                        → Implement code
/verify-dev                 → Check Code Done
/handoff-qc                 → Tạo QC handoff document
/qc                         → Run QC tests
/bug                        → Route bug report
/sync-memory                → Update memory
/skills                     → Maintain installed skills
/policy-check               → Validate workflow policy
/coord                      → Coordinator direct
/status                     → Check workflow status + agent activity dashboard
python3 scripts/status-dashboard.py --mode <compact|concise|dashboard|models|json>
python3 scripts/status-dashboard.py --mode dashboard --write
python3 scripts/agent-activity.py start --agent-id <agent> --phase <phase> --current-action <summary>
python3 scripts/architecture-health-check.py --strict --write-report
                            → Terminal dashboard mirror for tools without project slash commands
/resume-task                → Resume interrupted task
```

### Workflow tự động

Khi giao task, coordinator tự động chạy workflow đầy đủ:

```text
1. coordinator        → Route task, check project brain
2. task-analysis      → Normalize → task-analysis.yaml
3. solution-architect → Review architecture khi task yêu cầu
4. coder-leader       → Plan, assign service coders
5. [service coders]   → Implement (scoped per service)
6. dev-verification   → Check Code Done (≥80% + critical checks)
7. qc-handoff         → Handoff document
8. qc-runner          → Run QC tests
9. bug-router         → Route defects (nếu có)
10. memory-update     → Persist learnings
```

---

## Quick Reference

| Tôi muốn...                    | Command / cách gọi |
| ------------------------------ | ------------------ |
| Scan project mới               | `/onboard`         |
| Phân tích task trước khi code  | `/analyze-task`    |
| Tạo coder agents cho project   | `/create-coders`   |
| Implement feature              | `/dev`             |
| Kiểm tra code đã sẵn sàng chưa | `/verify-dev`      |
| Chạy QC tests                  | `/qc`              |
| Báo bug                        | `/bug`             |
| Quản lý/update skills          | `/skills`          |
| Xem trạng thái workflow        | `/status`          |
| Tiếp tục task bị gián đoạn     | `/resume-task`     |

---

## Naming Conventions

| Resource         | Format                              | Ví dụ                                |
| ---------------- | ----------------------------------- | ------------------------------------ |
| Agent definition | `{role}.agent.md`                   | `coordinator.agent.md`               |
| Skill folder     | `{skill-name}/SKILL.md`             | `react/SKILL.md`                     |
| Workflow skill   | `skill-{name}/SKILL.md`             | `skill-task-analysis/SKILL.md`       |
| Rule             | `{nn}-{name}.md`                    | `00-core-rules.md`                   |
| Template         | `{name}.template.{ext}`             | `task-analysis.template.yaml`        |
| Command          | `{name}.md`                         | `dev.md`                             |
| Generated coder  | `coder-{service}.agent.md`          | `coder-api.agent.md`                 |
| Task folder      | `.runtime/tasks/{task_id}/`          | `.runtime/tasks/TASK-20260518-001-login/` |
| Bug file         | `.runtime/bugs/{type}/{bug-id}.yaml` | `.runtime/bugs/blockers/BUG-001.yaml` |

---

## Troubleshooting

### Claude không nhận agent-workspace

1. Kiểm tra file entry point:

```bash
# CLAUDE.md phải có ở root workspace agent-workspace
ls CLAUDE.md
```

2. Kiểm tra cấu trúc:

```bash
# Verify tất cả resources
echo "Agents: $(find .claude/agents -name '*.agent.md' 2>/dev/null | wc -l | tr -d ' ')"
echo "Skills: $(ls -d .claude/skills/*/SKILL.md 2>/dev/null | wc -l | tr -d ' ')"
echo "Rules:  $(find .agent/rules -name '[0-9][0-9]-*.md' 2>/dev/null | wc -l | tr -d ' ')"
echo "Templates: $(ls .agent/templates/* 2>/dev/null | wc -l | tr -d ' ')"
echo "Commands: $(ls .claude/commands/*.md 2>/dev/null | wc -l | tr -d ' ')"
```

Expected:

```text
Agents: 33
Skills: 231
Rules:  18
Templates: 22
Commands: 15
```

### Workflow không chạy đúng

1. Check memory index: `.runtime/context/index.yaml` phải tồn tại
2. Check project brain: `.runtime/context/project-brain.yaml` phải tồn tại
3. Nếu chưa có → chạy `/onboard` hoặc gõ "Phân tích dự án này"
4. Check agent registry: `.runtime/context/agent-registry.yaml` phải list active coders

### Lỗi "service coder không tồn tại"

Generated service coders được tạo per-project bởi agent-factory.
Chạy `/create-coders` để tạo coder agents cho project hiện tại.

---

## Cập nhật

```bash
cd ~/Downloads/agent-workspace
git pull
```

### Verify sau khi cập nhật

```bash
echo "=== Verification ==="
echo "Agents: $(find .claude/agents -name '*.agent.md' 2>/dev/null | wc -l | tr -d ' ')"
echo "Skills: $(ls -d .claude/skills/*/SKILL.md 2>/dev/null | wc -l | tr -d ' ')"
echo "Rules:  $(find .agent/rules -name '[0-9][0-9]-*.md' 2>/dev/null | wc -l | tr -d ' ')"
echo "Templates: $(ls .agent/templates/* 2>/dev/null | wc -l | tr -d ' ')"
echo "Commands: $(ls .claude/commands/*.md 2>/dev/null | wc -l | tr -d ' ')"
```

---

## FAQ & Troubleshooting

### Git conflict khi upgrade

```bash
git status
# Resolve conflicts carefully. Do not overwrite runtime context/task history blindly.
git add .
git commit -m "chore: resolve agent-workspace upgrade conflicts"
```

### Permission denied

```bash
# macOS / Linux: .claude/ folder bị read-only
chmod -R u+w .claude/

# Hoặc nếu dùng sudo để clone:
sudo chown -R $(whoami) .claude/
```

### Skills / agents count không đúng expected

Nguyên nhân phổ biến:

```text
1. Pull/merge chưa đầy đủ.
2. .claude/ bị xóa hoặc conflict chưa resolve.
3. Skill/template/rule count thay đổi nhưng docs/config chưa cập nhật.
```

### CLAUDE.md không được Claude đọc

```bash
# Kiểm tra IDE đang mở đúng folder agent-workspace:
pwd
ls CLAUDE.md

# Nếu dùng VS Code, đảm bảo open folder (không phải open file)
```

### Onboarding chạy lại mỗi lần mở project

Project brain đã tồn tại nhưng coordinator vẫn trigger onboarding:

```bash
# Kiểm tra project brain
cat .runtime/context/project-brain.yaml | head -5

# Kiểm tra memory index
cat .runtime/context/index.yaml | head -5

# Nếu file rỗng hoặc corrupt → refresh:
# Gõ: /sync-memory --refresh-index
# Nếu service structure thay đổi → /onboard --refresh <service>

```

### Windows: Line ending issues

```powershell
# Git tự convert CRLF → gây lỗi khi Claude parse YAML
# Fix: configure git trước khi clone
git config --global core.autocrlf input

# Hoặc thêm .gitattributes vào project:
# *.md text eol=lf
# *.yaml text eol=lf
```

---

## Checklist cài đặt

- [ ] Clone agent-workspace repo
- [ ] Đặt reference docs vào `inputs/`
- [ ] Clone service repositories vào `services/<service-name>/`
- [ ] Verify: 12 workflow agents + 2 built-in coders + 19 specialist advisors, 231 skills, 19 workflow rules, 22 templates, 17 commands
- [ ] Mở repo `agent-workspace` trong IDE có Claude
- [ ] Test: gõ "Phân tích dự án này" hoặc `/onboard`
