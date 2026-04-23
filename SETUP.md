# Agent Platform — Hướng dẫn cài đặt

## Yêu cầu

- Claude (Sonnet/Opus) tích hợp trong IDE (VS Code, Cursor, Windsurf, hoặc Claude Desktop)
- Git (để clone repo)

---

## Cấu trúc Agent Platform

```
agent-platform/
├── CLAUDE.md                      ← Entry point (Claude đọc file này đầu tiên)
├── CLAUDE.local.md                ← Project-specific overrides (template)
├── GUIDELINES.md                  ← Cách dùng nhanh
├── SETUP.md                       ← File này
├── README.md                      ← Tổng quan dự án
└── .claude/
    ├── agents/                    ← 11 workflow agent definitions
    │   ├── coordinator.agent.md
    │   ├── onboarding.agent.md
    │   ├── agent-factory.agent.md
    │   ├── task-analysis.agent.md
    │   ├── coder-leader.agent.md
    │   ├── dev-verification.agent.md
    │   ├── qc-handoff.agent.md
    │   ├── qc-runner.agent.md
    │   ├── bug-router.agent.md
    │   ├── memory-update.agent.md
    │   └── workflow-policy.agent.md
    │
    ├── skills/                    ← 227 skill definitions
    │   ├── skill-project-brain/SKILL.md      (12 workflow skills)
    │   ├── skill-task-analysis/SKILL.md
    │   ├── react/SKILL.md                    (215 technical skills)
    │   ├── prisma/SKILL.md
    │   └── ...
    │
    ├── rules/                     ← 15 workflow rules
    │   ├── 00-core-rules.md
    │   ├── 01-project-brain-rules.md
    │   └── ... (00-14)
    │
    ├── templates/                 ← 13 artifact templates
    │   ├── task-analysis.template.yaml
    │   ├── dev-verification.template.yaml
    │   └── ...
    │
    ├── commands/                  ← 15 workflow commands
    │   ├── onboard.md
    │   ├── dev.md
    │   └── ...
    │
    ├── docs/                      ← Documentation + visual diagrams
    │   ├── visual-flow.md         ← All workflow diagrams (entry point)
    │   ├── folder-guide.md        ← Full .claude folder reference
    │   ├── deep-onboarding.md
    │   ├── skill-composition.md
    │   ├── external-skills.md
    │   └── diagrams/              ← 8 SVG workflow diagrams
    │
    └── context/                   ← Runtime (auto-generated per project)
        ├── project-brain.yaml
        ├── service-catalog.yaml
        └── ...
```

---

## Cài đặt

### Option A: Local (per project)

Cài agent-platform vào dự án cụ thể. Claude chỉ sử dụng khi mở project đó.

#### macOS / Linux

```bash
# 1. Clone agent-platform
git clone <repo-url> ~/Downloads/agent-platform

# 2. Copy vào project
cd <your-project>
cp -r ~/Downloads/agent-platform/.claude .
cp ~/Downloads/agent-platform/CLAUDE.md .
cp ~/Downloads/agent-platform/CLAUDE.local.md .

# 3. Verify
echo "Agents: $(ls .claude/agents/*.agent.md 2>/dev/null | wc -l | tr -d ' ')"
echo "Skills: $(ls -d .claude/skills/*/SKILL.md 2>/dev/null | wc -l | tr -d ' ')"
echo "Rules:  $(ls .claude/rules/*.md 2>/dev/null | wc -l | tr -d ' ')"
```

Expected output:

```
Agents: 11
Skills: 227
Rules:  16
```

#### Windows (PowerShell)

```powershell
# 1. Clone
git clone <repo-url> $HOME\Downloads\agent-platform

# 2. Copy vào project
cd <your-project>
Copy-Item -Recurse "$HOME\Downloads\agent-platform\.claude" .
Copy-Item "$HOME\Downloads\agent-platform\CLAUDE.md" .
Copy-Item "$HOME\Downloads\agent-platform\CLAUDE.local.md" .

# 3. Verify
Write-Host "Agents: $((Get-ChildItem .claude\agents\*.agent.md).Count)"
Write-Host "Skills: $((Get-ChildItem .claude\skills\*\SKILL.md).Count)"
Write-Host "Rules:  $((Get-ChildItem .claude\rules\*.md).Count)"
```

### Option B: Global (tất cả projects)

Cài một lần, mọi project đều sử dụng.

#### macOS / Linux

```bash
# 1. Clone
git clone <repo-url> ~/Downloads/agent-platform

# 2. Setup global
mkdir -p ~/.claude
cp -r ~/Downloads/agent-platform/.claude/* ~/.claude/
cp ~/Downloads/agent-platform/CLAUDE.md ~/.claude/

# 3. Verify
echo "Agents: $(ls ~/.claude/agents/*.agent.md 2>/dev/null | wc -l | tr -d ' ')"
echo "Skills: $(ls -d ~/.claude/skills/*/SKILL.md 2>/dev/null | wc -l | tr -d ' ')"
echo "Rules:  $(ls ~/.claude/rules/*.md 2>/dev/null | wc -l | tr -d ' ')"
```

#### Windows (PowerShell)

```powershell
# 1. Clone
git clone <repo-url> $HOME\Downloads\agent-platform

# 2. Setup global
New-Item -ItemType Directory -Force "$HOME\.claude"
Copy-Item -Recurse "$HOME\Downloads\agent-platform\.claude\*" "$HOME\.claude\"
Copy-Item "$HOME\Downloads\agent-platform\CLAUDE.md" "$HOME\.claude\"

# 3. Verify
Write-Host "Agents: $((Get-ChildItem $HOME\.claude\agents\*.agent.md).Count)"
Write-Host "Skills: $((Get-ChildItem $HOME\.claude\skills\*\SKILL.md).Count)"
Write-Host "Rules:  $((Get-ChildItem $HOME\.claude\rules\*.md).Count)"
```

---

## Post-install Validation

Sau khi cài đặt, chạy script kiểm tra tính toàn vẹn:

```bash
bash scripts/validate-install.sh
# hoặc nếu cài ở thư mục khác:
bash scripts/validate-install.sh /path/to/project
```

Script kiểm tra: core files, directory structure, agent/skill/rule/template/command counts, context placeholders, settings, và docs. Output có màu (pass/fail/warn) và exit code 0 (OK) hoặc 1 (errors).

---

## Upgrade

### Option 1: Manual copy (đơn giản)

```bash
# 1. Pull version mới
cd ~/Downloads/agent-platform
git pull origin main

# 2. Backup custom files (nếu có)
cd <your-project>
cp -r .claude/agents/coder-*.agent.md /tmp/backup/     # generated coders
cp -r .claude/context/ /tmp/backup/context/             # runtime context
cp -r .claude/tasks/ /tmp/backup/tasks/                 # task history
cp -r .claude/bugs/ /tmp/backup/bugs/                   # bug history

# 3. Update framework files
cp -r ~/Downloads/agent-platform/.claude/agents/ .claude/agents/
cp -r ~/Downloads/agent-platform/.claude/skills/ .claude/skills/
cp -r ~/Downloads/agent-platform/.claude/rules/ .claude/rules/
cp -r ~/Downloads/agent-platform/.claude/templates/ .claude/templates/
cp -r ~/Downloads/agent-platform/.claude/commands/ .claude/commands/
cp -r ~/Downloads/agent-platform/.claude/docs/ .claude/docs/
cp ~/Downloads/agent-platform/.claude/settings.json .claude/
cp ~/Downloads/agent-platform/CLAUDE.md .
cp ~/Downloads/agent-platform/SETUP.md .
cp ~/Downloads/agent-platform/GUIDELINES.md .

# 4. Restore custom files
cp /tmp/backup/coder-*.agent.md .claude/agents/ 2>/dev/null || true
cp -r /tmp/backup/context/ .claude/
cp -r /tmp/backup/tasks/ .claude/
cp -r /tmp/backup/bugs/ .claude/

# 5. Validate
bash scripts/validate-install.sh
```

**Không ghi đè khi upgrade:**

| File/Folder                       | Lý do                                        |
| --------------------------------- | -------------------------------------------- |
| `CLAUDE.local.md`                 | Project-specific overrides                   |
| `.claude/context/`                | Runtime data (project brain, service brains) |
| `.claude/tasks/`                  | Task history                                 |
| `.claude/bugs/`                   | Bug history                                  |
| `.claude/agents/coder-*.agent.md` | Generated service coders                     |
| `.claude/rules/15-*.md` trở lên   | Custom rules                                 |

### Option 2: Git subtree (tự động hơn)

Dùng git subtree để quản lý framework như dependency:

```bash
# ─── Lần đầu: thêm subtree ───
cd <your-project>
git remote add agent-platform <repo-url>
git subtree add --prefix=.claude agent-platform main --squash

# ─── Upgrade: pull version mới ───
git subtree pull --prefix=.claude agent-platform main --squash

# Resolve conflicts nếu có (thường là custom rules hoặc settings)
# Sau đó validate:
bash scripts/validate-install.sh
```

> **Lưu ý**: Với subtree, CLAUDE.md và các file root-level (SETUP.md, GUIDELINES.md) không được quản lý tự động. Copy chúng thủ công khi upgrade.

### Option 3: Git submodule

```bash
# ─── Lần đầu ───
cd <your-project>
git submodule add <repo-url> .agent-platform
ln -s .agent-platform/.claude .claude
cp .agent-platform/CLAUDE.md .

# ─── Upgrade ───
cd .agent-platform
git pull origin main
cd ..
git add .agent-platform
git commit -m "chore: upgrade agent-platform"
```

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

Agent-platform sử dụng **coordinator-driven workflow**. Bạn có thể giao tiếp bằng:

#### 1. Ngôn ngữ tự nhiên (khuyến nghị)

Claude tự động route qua coordinator đến đúng workflow agent:

```
"Phân tích dự án này"                      → coordinator → onboarding
"Thêm tính năng login bằng Google OAuth"   → coordinator → task-analysis → coder-leader → ...
"Kiểm tra code đã sẵn sàng chưa"          → coordinator → dev-verification
"Test tính năng vừa implement"             → coordinator → qc-runner
```

#### 2. Slash commands (direct)

Dùng commands để gọi trực tiếp workflow phase:

```
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
/policy-check               → Validate workflow policy
/coord                      → Coordinator direct
/status                     → Check workflow status
/resume-task                → Resume interrupted task
```

### Workflow tự động

Khi giao task, coordinator tự động chạy workflow đầy đủ:

```
1. coordinator        → Route task, check project brain
2. task-analysis      → Normalize → task-analysis.yaml
3. coder-leader       → Plan, assign service coders
4. [service coders]   → Implement (scoped per service)
5. dev-verification   → Check Code Done (≥80% + critical checks)
6. qc-handoff         → Handoff document
7. qc-runner          → Run QC tests
8. bug-router         → Route defects (nếu có)
9. memory-update      → Persist learnings
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
| Task folder      | `.claude/tasks/{task-id}/`          | `.claude/tasks/TASK-001/`            |
| Bug file         | `.claude/bugs/{type}/{bug-id}.yaml` | `.claude/bugs/blockers/BUG-001.yaml` |

---

## Troubleshooting

### Claude không nhận agent-platform

1. Kiểm tra file entry point:

```bash
# CLAUDE.md phải có ở root project hoặc ~/.claude/
ls CLAUDE.md
# hoặc
ls ~/.claude/CLAUDE.md
```

2. Kiểm tra cấu trúc:

```bash
# Verify tất cả resources
echo "Agents: $(ls .claude/agents/*.agent.md 2>/dev/null | wc -l | tr -d ' ')"
echo "Skills: $(ls -d .claude/skills/*/SKILL.md 2>/dev/null | wc -l | tr -d ' ')"
echo "Rules:  $(ls .claude/rules/*.md 2>/dev/null | wc -l | tr -d ' ')"
echo "Templates: $(ls .claude/templates/* 2>/dev/null | wc -l | tr -d ' ')"
echo "Commands: $(ls .claude/commands/*.md 2>/dev/null | wc -l | tr -d ' ')"
```

Expected:

```
Agents: 11
Skills: 227
Rules:  16
Templates: 13
Commands: 15
```

### Workflow không chạy đúng

1. Check project brain: `.claude/context/project-brain.yaml` phải tồn tại
2. Nếu chưa có → chạy `/onboard` hoặc gõ "Phân tích dự án này"
3. Check agent registry: `.claude/context/agent-registry.yaml` phải list active coders

### Lỗi "service coder không tồn tại"

Generated service coders được tạo per-project bởi agent-factory.
Chạy `/create-coders` để tạo coder agents cho project hiện tại.

---

## Cập nhật

```bash
# Pull bản mới
cd ~/Downloads/agent-platform
git pull

# Copy lại vào project (local)
cd <your-project>
cp -r ~/Downloads/agent-platform/.claude .
cp ~/Downloads/agent-platform/CLAUDE.md .

# Hoặc cập nhật global
cp -r ~/Downloads/agent-platform/.claude/* ~/.claude/
cp ~/Downloads/agent-platform/CLAUDE.md ~/.claude/
```

### Verify sau khi cập nhật

```bash
echo "=== Verification ==="
echo "Agents: $(ls .claude/agents/*.agent.md 2>/dev/null | wc -l | tr -d ' ')"
echo "Skills: $(ls -d .claude/skills/*/SKILL.md 2>/dev/null | wc -l | tr -d ' ')"
echo "Rules:  $(ls .claude/rules/*.md 2>/dev/null | wc -l | tr -d ' ')"
echo "Templates: $(ls .claude/templates/* 2>/dev/null | wc -l | tr -d ' ')"
echo "Commands: $(ls .claude/commands/*.md 2>/dev/null | wc -l | tr -d ' ')"
```

---

## FAQ & Troubleshooting

### Git subtree conflict khi upgrade

```bash
# Lỗi thường gặp:
# "refusing to merge unrelated histories" hoặc conflict ở custom rules

# Cách xử lý:
git subtree pull --prefix=.claude agent-platform main --squash

# Nếu conflict:
git status                         # xem files conflict
git checkout --theirs .claude/skills/   # giữ version mới cho skills
git checkout --ours .claude/rules/15-*  # giữ custom rules của bạn
git add .
git commit -m "chore: resolve subtree upgrade conflicts"
```

### Permission denied khi copy files

```bash
# macOS / Linux: .claude/ folder bị read-only
chmod -R u+w .claude/

# Hoặc nếu dùng sudo để clone:
sudo chown -R $(whoami) .claude/
```

### Skills / agents count không đúng expected

```bash
# Chạy validation script để xem chi tiết
bash scripts/validate-install.sh

# Nguyên nhân phổ biến:
# 1. Copy thiếu files (dùng cp -r, không phải cp)
# 2. .gitignore exclude .claude/ → thêm !.claude/ vào .gitignore
# 3. Git subtree chưa pull hết → chạy lại subtree pull
```

### CLAUDE.md không được Claude đọc

```bash
# Kiểm tra file tồn tại ở đúng vị trí:
# - Local install: CLAUDE.md ở root project
# - Global install: ~/.claude/CLAUDE.md

# Kiểm tra IDE đang mở đúng folder:
pwd
ls CLAUDE.md

# Nếu dùng VS Code, đảm bảo open folder (không phải open file)
```

### Onboarding chạy lại mỗi lần mở project

Project brain đã tồn tại nhưng coordinator vẫn trigger onboarding:

```bash
# Kiểm tra project brain
cat .claude/context/project-brain.yaml | head -5

# Nếu file rỗng hoặc corrupt → chạy lại onboarding:
# Gõ: /onboard

# Nếu file tồn tại và valid → kiểm tra CLAUDE.md có bị sửa đổi
diff CLAUDE.md ~/Downloads/agent-platform/CLAUDE.md
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

- [ ] Clone agent-platform repo
- [ ] Copy `.claude/` folder vào project (hoặc `~/.claude/`)
- [ ] Copy `CLAUDE.md` vào project root (hoặc `~/.claude/`)
- [ ] Verify: 11 agents, 227 skills, 16 rules, 15 templates, 15 commands
- [ ] Mở project trong IDE có Claude
- [ ] Test: gõ "Phân tích dự án này" hoặc `/onboard`
