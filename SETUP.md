# Setup Guide — agent-platform

> Bắt đầu nhanh + cách gọi alias + phân biệt `.claude/` vs `.agent/`: **[GUIDELINES.md](GUIDELINES.md)**

Hướng dẫn cài đặt hệ thống agent trên **macOS** và **Windows**, hỗ trợ 2 mode:
- **Local**: Chỉ áp dụng cho 1 project cụ thể
- **Global**: Áp dụng cho tất cả projects trên máy

---

## TL;DR (Clone → Copy)

Bạn chỉ cần:

1) **Clone** repo `agent-platform` về máy  
2) Chọn **1 trong 2 cách**:
- **Global**: copy `CLAUDE.md` + copy cả thư mục `.claude/` vào `~/.claude/` (macOS) hoặc `%USERPROFILE%\.claude\` (Windows)
- **Local (project scope)**: copy `CLAUDE.md` + copy cả thư mục `.claude/` vào root của project

> **Quan trọng**: `CLAUDE.md` là entry point. Không có file này, Claude có thể thấy agents nhưng không biết cách gọi.

## Team setup cho `.agent/`

Nếu làm theo team (repo shared), xem guide: `docs/team-setup-agent-context.md`.

---

## Yêu cầu

| Yêu cầu | Chi tiết |
|----------|---------|
| AI | [Claude](https://claude.ai) (Anthropic) |
| IDE | IDE có tích hợp Claude: [Cursor](https://cursor.sh), VS Code + Claude extension, Claude Code CLI, ... |
| OS | macOS 12+ / Windows 10+ |
| Disk | ~50MB cho toàn bộ agents + skills |

---

## `.claude/` là gì?

`.claude/` là **directory chuẩn của Claude** (Anthropic) để đọc agent definitions, skills, và project-specific instructions. Nó **không phải** là của Cursor hay bất kỳ IDE nào cụ thể.

Bất kỳ tool/IDE nào tích hợp Claude đều đọc `.claude/`:
- **Cursor** — tự động nhận `.claude/` khi mở project
- **VS Code + Claude extension** — tương tự
- **Claude Code (CLI)** — đọc từ working directory
- **Claude API** — có thể inject qua system prompt

---

## Hiểu cấu trúc trước khi setup

```
agent-platform/
├── CLAUDE.md                ← BẮT BUỘC: Entry point, routing logic (Claude đọc file này đầu tiên)
├── .claude/
│   ├── agents/              ← 20 agent definitions
│   │   ├── README.md        ← Handbook nội bộ
│   │   └── agent-*/SKILL.md
│   └── skills/              ← 106 skill definitions
│       └── skill-*/SKILL.md
├── README.md                ← Tổng quan project
└── SETUP.md                 ← File này
```

### File quan trọng nhất: `CLAUDE.md`

`CLAUDE.md` là file mà **Claude luôn đọc đầu tiên** khi bắt đầu session. Không có file này → Claude thấy agents nhưng **không biết cách gọi chúng**.

File này chứa:
- Danh sách agents và khi nào kích hoạt
- **Routing logic**: user nói gì → đọc SKILL.md nào
- Quy trình xử lý task (bootstrap → phân loại → đọc SKILL → thực thi)
- Nguyên tắc hoạt động

### Claude đọc files từ 2 vị trí:

| Scope | macOS | Windows |
|-------|-------|---------|
| **Global** (tất cả projects) | `~/.claude/` | `%USERPROFILE%\.claude\` |
| **Local** (1 project) | `<project>/.claude/` | `<project>\.claude\` |

> **Lưu ý**: Local luôn override Global khi trùng tên. Cả hai có thể dùng đồng thời.

---

## Option A: Setup Local (Per-Project / Scope)

Agents + skills chỉ hoạt động trong 1 project. Phù hợp khi mỗi project cần bộ agents khác nhau.

### macOS

```bash
# 1. Clone repo
git clone <repo-url> ~/Downloads/agent-platform

# 2. Vào project cần setup
cd ~/Documents/my-project

# 3. Copy các file cần thiết vào project (đúng 2 thứ)
cp ~/Downloads/agent-platform/CLAUDE.md .
cp -r ~/Downloads/agent-platform/.claude .

# 4. Verify
cat CLAUDE.md | head -1      # → "# Agent Platform — System Instructions"
ls .claude/agents/            # → 20 agent folders + README.md
ls .claude/skills/            # → 106 skill folders
```

### Windows (PowerShell)

```powershell
# 1. Clone repo
git clone <repo-url> $env:USERPROFILE\Downloads\agent-platform

# 2. Vào project cần setup
cd $env:USERPROFILE\Documents\my-project

# 3. Copy các file cần thiết vào project (đúng 2 thứ)
Copy-Item "$env:USERPROFILE\Downloads\agent-platform\CLAUDE.md" -Destination "."
Copy-Item -Recurse "$env:USERPROFILE\Downloads\agent-platform\.claude" -Destination ".claude"

# 4. Verify
Get-Content CLAUDE.md -TotalCount 1  # → "# Agent Platform — System Instructions"
Get-ChildItem .claude\agents\        # → 20 agent folders + README.md
Get-ChildItem .claude\skills\        # → 106 skill folders
```

### Windows (CMD)

```cmd
:: 1. Clone repo
git clone <repo-url> %USERPROFILE%\Downloads\agent-platform

:: 2. Vào project cần setup
cd %USERPROFILE%\Documents\my-project

:: 3. Copy các file cần thiết vào project (đúng 2 thứ)
copy "%USERPROFILE%\Downloads\agent-platform\CLAUDE.md" .
xcopy /E /I "%USERPROFILE%\Downloads\agent-platform\.claude" ".claude"

:: 4. Verify
dir CLAUDE.md
dir .claude\agents
dir .claude\skills
```

### Kết quả

```
my-project/
├── CLAUDE.md                ← Entry point (BẮT BUỘC)
├── .claude/
│   ├── agents/
│   │   ├── README.md
│   │   ├── agent-orchestrator/SKILL.md
│   │   ├── agent-sa/SKILL.md
│   │   └── ... (20 agents)
│   └── skills/
│       ├── skill-lang-typescript/SKILL.md
│       ├── skill-framework-nestjs/SKILL.md
│       └── ... (106 skills)
├── src/
├── package.json
└── ...
```

---

## Option B: Setup Global (All Projects)

Agents + skills hoạt động trên **tất cả** projects trên máy. Claude tự động nhận khi mở bất kỳ project nào.

> **Quan trọng**: Copy đúng 2 thứ vào global: `CLAUDE.md` + `.claude/` (thư mục).

### macOS

```bash
# 1. Clone repo
git clone <repo-url> ~/Downloads/agent-platform

# 2. Tạo thư mục global (nếu chưa có)
mkdir -p ~/.claude

# 3. Copy các file cần thiết vào global (đúng 2 thứ)
cp ~/Downloads/agent-platform/CLAUDE.md ~/.claude/
cp -r ~/Downloads/agent-platform/.claude/* ~/.claude/

# 4. Verify
cat ~/.claude/CLAUDE.md | head -1  # → "# Agent Platform — System Instructions"
ls ~/.claude/agents/               # → 20 agent folders + README.md
ls ~/.claude/skills/               # → 106 skill folders

# 5. Kiểm tra tổng
echo "Agents: $(ls -d ~/.claude/agents/agent-*/ | wc -l)"
echo "Skills: $(ls -d ~/.claude/skills/skill-*/ | wc -l)"
```

### Windows (PowerShell)

```powershell
# 1. Clone repo
git clone <repo-url> $env:USERPROFILE\Downloads\agent-platform

# 2. Tạo thư mục global (nếu chưa có)
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude"

# 3. Copy các file cần thiết vào global (đúng 2 thứ)
Copy-Item "$env:USERPROFILE\Downloads\agent-platform\CLAUDE.md" -Destination "$env:USERPROFILE\.claude\"
Copy-Item -Recurse "$env:USERPROFILE\Downloads\agent-platform\.claude\*" -Destination "$env:USERPROFILE\.claude\"

# 4. Verify
Get-Content "$env:USERPROFILE\.claude\CLAUDE.md" -TotalCount 1
Get-ChildItem "$env:USERPROFILE\.claude\agents"
Get-ChildItem "$env:USERPROFILE\.claude\skills"

# 5. Kiểm tra tổng
Write-Host "Agents: $((Get-ChildItem "$env:USERPROFILE\.claude\agents\agent-*" -Directory).Count)"
Write-Host "Skills: $((Get-ChildItem "$env:USERPROFILE\.claude\skills\skill-*" -Directory).Count)"
```

### Windows (CMD)

```cmd
:: 1. Clone repo
git clone <repo-url> %USERPROFILE%\Downloads\agent-platform

:: 2. Tạo thư mục global
mkdir "%USERPROFILE%\.claude" 2>nul

:: 3. Copy các file cần thiết vào global (đúng 2 thứ)
copy "%USERPROFILE%\Downloads\agent-platform\CLAUDE.md" "%USERPROFILE%\.claude\"
xcopy /E /I "%USERPROFILE%\Downloads\agent-platform\.claude" "%USERPROFILE%\.claude"

:: 4. Verify
dir "%USERPROFILE%\.claude\CLAUDE.md"
dir "%USERPROFILE%\.claude\agents"
dir "%USERPROFILE%\.claude\skills"
```

### Kết quả (Global paths)

| OS | File | Path |
|----|------|------|
| macOS | CLAUDE.md | `~/.claude/CLAUDE.md` |
| macOS | agents | `~/.claude/agents/` |
| macOS | Skills | `~/.claude/skills/` |
| Windows | CLAUDE.md | `C:\Users\<username>\.claude\CLAUDE.md` |
| Windows | agents | `C:\Users\<username>\.claude\agents\` |
| Windows | Skills | `C:\Users\<username>\.claude\skills\` |

---

## Cách gọi agents

Agents được gọi thông qua **ngôn ngữ tự nhiên** — bạn mô tả task, Claude tự động chọn agent phù hợp dựa trên SKILL.md definitions.

### Cách 0: Gọi nhanh bằng alias (dễ nhớ nhất)

Format:

```
sa: <task>     (Solution Architect)
ba: <task>     (Business Analyst)
qa: <task>     (QA/QC)
pm: <task>     (Product/Project Manager)
sec: <task>    (Application Security)
sre: <task>    (SRE/Infra/Ops)
dev: <task>    (Orchestrator: build/ship/implement)
```

Ví dụ:

```
sa: thiết kế kiến trúc microservices cho dự án này
qa: viết test plan cho release v2.0
sec: threat model cho flow checkout
dev: implement API /orders + tests
```

### Cách 1: Gọi tự động (khuyến nghị)

Chỉ cần mô tả task, orchestrator tự route đến đúng agent:

```
"Thiết kế kiến trúc cho hệ thống e-commerce"
→ Claude tự kích hoạt agent-sa (vì task match với skill-arch-solution)

"Review code của PR này"
→ Claude tự kích hoạt agent-reviewer (vì task match với skill-role-code-review)

"Thêm tính năng đăng nhập Google OAuth"
→ Claude tự kích hoạt agent-analyst → breakdown → agent-coder-* → agent-reviewer
```

### Cách 2: Gọi agent cụ thể (explicit)

Nêu tên agent trực tiếp trong prompt:

```
"agent-sa: thiết kế kiến trúc microservices cho dự án này"
"agent-security: review bảo mật cho module payment"
"agent-perf: load test API /orders với 1000 concurrent users"
"agent-onboarding: scan project này và tạo context"
```

### Cách 3: Gọi theo vai trò

```
"Với vai trò Solution Architect, hãy thiết kế hệ thống notification"
"Đóng vai Security Engineer, review module auth"
"Là QA Lead, viết test plan cho release v2.0"
```

### Bảng quick reference — task → agent

| Bạn muốn làm gì | Gõ gì | Agent được kích hoạt |
|------------------|-------|---------------------|
| Phân tích ý tưởng | "Phân tích ý tưởng app X" | agent-discovery |
| Thiết kế kiến trúc | "Thiết kế kiến trúc cho..." | agent-sa |
| Viết user stories | "Viết user stories cho feature X" | agent-ba |
| Breakdown task | "Phân tích task này thành subtasks" | agent-analyst |
| Thiết kế UI | "Thiết kế giao diện cho trang Y" | agent-designer |
| Viết code | "Implement API endpoint /orders" | agent-coder-* |
| Review code | "Review code này" | agent-reviewer |
| Viết tests | "Viết unit tests cho OrderService" | agent-tester |
| Security audit | "Kiểm tra bảo mật module auth" | agent-security |
| Load test | "Test hiệu năng API" | agent-perf |
| Setup monitoring | "Setup monitoring cho production" | agent-sre |
| Tạo docs | "Cập nhật API docs" | agent-documenter |
| Scan project mới | "Phân tích dự án này" | agent-onboarding |

### Lưu ý quan trọng

```
@ trong Claude Code = reference FILES, không phải agents
  @src/main.ts     ← đúng (reference file)
  @agent-sa        ← sai (không tìm thấy file)

Để gọi agent → dùng ngôn ngữ tự nhiên, không dùng @
```

---

## Verify sau khi setup

Mở IDE (Cursor/VS Code/Claude Code), gõ bất kỳ task nào và kiểm tra:

### Quick test

```
Gõ: "Hãy phân tích dự án này và cho tôi biết cấu trúc"

Expected:
- agent-onboarding kích hoạt (scan project)
- agent-builder detect stack
- .agent/ directory được tạo
```

### Kiểm tra agents nhận đúng skills

```
Gõ: "Hãy liệt kê tất cả agents và skills hiện có"

Expected: 20 agents + 106 skills
```

### Kiểm tra đường dẫn

| OS | Verify command |
|----|---------------|
| macOS (local) | `ls .claude/agents/ \| wc -l` → 21 (20 folders + README) |
| macOS (global) | `ls ~/.claude/agents/ \| wc -l` → 21 |
| Windows (local) | `(Get-ChildItem .claude\agents).Count` |
| Windows (global) | `(Get-ChildItem $env:USERPROFILE\.claude\agents).Count` |

---

## Optional (nâng cao) — Update scripts

### Update (khi repo `agent-platform` có thay đổi)

Nếu bạn pull code mới và muốn update nhanh:

- **macOS (Global)**: copy `CLAUDE.md` + copy `.claude/*` vào `~/.claude/`
- **Windows (Global)**: copy `CLAUDE.md` + copy `.claude\\*` vào `%USERPROFILE%\\.claude\\`
- **Local**: copy tương tự vào root project

Nếu muốn tự động hoá, dùng scripts dưới đây.

### Script tự động (macOS)

```bash
#!/bin/bash
# update-agents.sh — Chạy khi pull code mới từ agent-platform repo

SOURCE="$HOME/Downloads/agent-platform/.claude"
MODE="${1:-local}"  # local hoặc global

if [ "$MODE" = "global" ]; then
  TARGET="$HOME/.claude"
else
  TARGET=".claude"
fi

echo "Updating $MODE agents..."
mkdir -p "$TARGET"
cp -r "$SOURCE/agents/" "$TARGET/agents/"
cp -r "$SOURCE/skills/" "$TARGET/skills/"

AGENTS=$(ls -d "$TARGET/agents/agent-"*/ 2>/dev/null | wc -l | tr -d ' ')
SKILLS=$(ls -d "$TARGET/skills/skill-"*/ 2>/dev/null | wc -l | tr -d ' ')
echo "Done: $AGENTS agents, $SKILLS skills → $TARGET"
```

```bash
# Sử dụng
chmod +x update-agents.sh
./update-agents.sh local     # update project hiện tại
./update-agents.sh global    # update global
```

### Script tự động (Windows PowerShell)

```powershell
# update-agents.ps1

param(
    [ValidateSet("local", "global")]
    [string]$Mode = "local"
)

$Source = "$env:USERPROFILE\Downloads\agent-platform\.claude"

if ($Mode -eq "global") {
    $Target = "$env:USERPROFILE\.claude"
} else {
    $Target = ".claude"
}

Write-Host "Updating $Mode agents..."
New-Item -ItemType Directory -Force -Path $Target | Out-Null
Copy-Item -Recurse -Force "$Source\agents\*" "$Target\agents\"
Copy-Item -Recurse -Force "$Source\skills\*" "$Target\skills\"

$Agents = (Get-ChildItem "$Target\agents\agent-*" -Directory -ErrorAction SilentlyContinue).Count
$Skills = (Get-ChildItem "$Target\skills\skill-*" -Directory -ErrorAction SilentlyContinue).Count
Write-Host "Done: $Agents agents, $Skills skills -> $Target"
```

```powershell
# Sử dụng
.\update-agents.ps1 -Mode local     # update project hiện tại
.\update-agents.ps1 -Mode global    # update global
```

---

## Gỡ cài đặt (Uninstall)

### Local

```bash
# macOS
rm -rf .claude/agents .claude/skills

# Windows (PowerShell)
Remove-Item -Recurse -Force .claude\agents, .claude\skills
```

### Global

```bash
# macOS
rm -rf ~/.claude/agents ~/.claude/skills

# Windows (PowerShell)
Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\agents", "$env:USERPROFILE\.claude\skills"
```

> **Lưu ý**: Không xóa `.agent/` trong project — đó là context data, không phải agent definitions.

---

## Troubleshooting

### Agents không được nhận diện

| Nguyên nhân | Giải pháp |
|-------------|-----------|
| Sai path | Kiểm tra `.claude/agents/agent-*/SKILL.md` (phải có SKILL.md bên trong folder) |
| File rỗng | Mỗi SKILL.md phải có nội dung (>10 dòng) |
| Tên folder sai | Agent folder phải bắt đầu bằng `agent-`, skill bắt đầu bằng `skill-` |
| Cache cũ | Restart IDE (Cursor: Cmd+Shift+P → Reload Window) |

### Skills không load được

```bash
# Kiểm tra cấu trúc đúng
# ĐÚNG:
.claude/skills/skill-lang-typescript/SKILL.md

# SAI:
.claude/skills/skill-lang-typescript.md        # thiếu folder
.claude/skills/lang-typescript/SKILL.md         # thiếu prefix skill-
.claude/skills/skill-lang-typescript/skill.md   # SKILL.md phải viết HOA
```

### Local và Global conflict

```
Triệu chứng: Agent hoạt động khác kỳ vọng

Giải pháp:
1. Kiểm tra cả 2 nơi có cùng agent không
2. Local luôn ưu tiên — xóa local nếu muốn dùng global
3. Hoặc xóa global nếu chỉ muốn dùng local
```

### Kiểm tra nhanh trên macOS

```bash
echo "=== LOCAL ==="
[ -d ".claude/agents" ] && echo "Local agents: $(ls -d .claude/agents/agent-*/ 2>/dev/null | wc -l | tr -d ' ')" || echo "No local agents"
[ -d ".claude/skills" ] && echo "Local skills: $(ls -d .claude/skills/skill-*/ 2>/dev/null | wc -l | tr -d ' ')" || echo "No local skills"

echo "=== GLOBAL ==="
[ -d "$HOME/.claude/agents" ] && echo "Global agents: $(ls -d ~/.claude/agents/agent-*/ 2>/dev/null | wc -l | tr -d ' ')" || echo "No global agents"
[ -d "$HOME/.claude/skills" ] && echo "Global skills: $(ls -d ~/.claude/skills/skill-*/ 2>/dev/null | wc -l | tr -d ' ')" || echo "No global skills"
```

### Kiểm tra nhanh trên Windows

```powershell
Write-Host "=== LOCAL ==="
if (Test-Path ".claude\agents") {
    Write-Host "Local agents: $((Get-ChildItem .claude\agents\agent-* -Directory -ErrorAction SilentlyContinue).Count)"
} else { Write-Host "No local agents" }

if (Test-Path ".claude\skills") {
    Write-Host "Local skills: $((Get-ChildItem .claude\skills\skill-* -Directory -ErrorAction SilentlyContinue).Count)"
} else { Write-Host "No local skills" }

Write-Host "=== GLOBAL ==="
if (Test-Path "$env:USERPROFILE\.claude\agents") {
    Write-Host "Global agents: $((Get-ChildItem $env:USERPROFILE\.claude\agents\agent-* -Directory -ErrorAction SilentlyContinue).Count)"
} else { Write-Host "No global agents" }

if (Test-Path "$env:USERPROFILE\.claude\skills") {
    Write-Host "Global skills: $((Get-ChildItem $env:USERPROFILE\.claude\skills\skill-* -Directory -ErrorAction SilentlyContinue).Count)"
} else { Write-Host "No global skills" }
```

---

## Local vs Global (khi nào dùng cái nào?)

| Tiêu chí | Local | Global |
|----------|-------|--------|
| Phạm vi | 1 project | Tất cả projects |
| Path | `<project>/.claude/` | `~/.claude/` |
| Git tracked | Có (commit cùng project) | Không |
| Team sharing | Cả team dùng chung | Chỉ máy cá nhân |
| Custom per project | Dễ override | Cần local override |
| Update | Mỗi project update riêng | 1 lần cho tất cả |

### Khuyến nghị

| Tình huống | Nên dùng |
|-----------|---------|
| Làm 1 project, team dùng chung agents | **Local** (commit vào git) |
| Làm nhiều projects solo | **Global** |
| Team project + cần custom | **Hybrid** (Global base + Local override) |
| Thử nghiệm agents mới | **Local** (không ảnh hưởng projects khác) |

---

## Optional (nâng cao) — Hybrid (override per project)

Nếu bạn muốn override từng project trên nền global (hybrid) hoặc muốn script update tự động, dùng các mục dưới đây. Không cần cho setup cơ bản.

### Hybrid (Global + Local Override)

```
Priority:
1) Local  (<project>/.claude/)  — cao nhất
2) Global (~/.claude/)          — fallback
```

Ví dụ thêm agent riêng cho 1 project:

```bash
cd <your-project>
mkdir -p .claude/agents/agent-coder-ecom-api-nestjs
cat > .claude/agents/agent-coder-ecom-api-nestjs/SKILL.md << 'EOF'
# Agent: agent-coder-ecom-api-nestjs
(custom definition cho project này)
EOF
```

### Update (khi repo agent-platform có thay đổi)

- **Nguyên tắc**: update global thì copy `~/.claude/` (CLAUDE.md + `.claude/*`), update local thì copy vào project.

### Quick Reference

```bash
# macOS — Setup local (2 lệnh)
cp /path/to/agent-platform/CLAUDE.md . && cp -r /path/to/agent-platform/.claude .

# macOS — Setup global (3 lệnh)
cp /path/to/agent-platform/CLAUDE.md ~/.claude/ && \
cp -r /path/to/agent-platform/.claude/* ~/.claude/

# Windows PowerShell — Setup local
Copy-Item "C:\path\to\agent-platform\CLAUDE.md" .; Copy-Item -Recurse "C:\path\to\agent-platform\.claude" ".claude"

# Windows PowerShell — Setup global
Copy-Item "C:\path\to\agent-platform\CLAUDE.md" "$env:USERPROFILE\.claude\"; Copy-Item -Recurse "C:\path\to\agent-platform\.claude\*" "$env:USERPROFILE\.claude\"
```

## Selective Install (nâng cao)

Không cần copy toàn bộ 20 agents + 109 skills. Có thể chỉ copy những gì dùng.

### Skills bắt buộc (không bỏ)

```
skill-context-read      skill-context-write
skill-role-blueprints   skill-role-code-review
skill-role-breakdown-tasks
```

### Stack templates

**Next.js fullstack**
```bash
SKILLS="skill-lang-typescript skill-framework-nextjs skill-api-trpc \
  skill-database-postgresql skill-database-prisma skill-auth-jwt \
  skill-ui-tailwind skill-ui-shadcn skill-testing-jest skill-testing-playwright \
  skill-tooling-git skill-tooling-packagemanager skill-tooling-linting \
  skill-context-read skill-context-write skill-role-blueprints \
  skill-role-code-review skill-role-breakdown-tasks skill-security-hardening"
for s in $SKILLS; do cp -r /path/to/agent-platform/.claude/skills/$s .claude/skills/; done
```

**NestJS + React**
```bash
SKILLS="skill-lang-typescript skill-framework-nestjs skill-framework-react \
  skill-database-postgresql skill-database-prisma skill-auth-jwt skill-api-rest \
  skill-ui-tailwind skill-testing-jest skill-tooling-git skill-tooling-packagemanager \
  skill-context-read skill-context-write skill-role-blueprints \
  skill-role-code-review skill-role-breakdown-tasks skill-security-hardening"
for s in $SKILLS; do cp -r /path/to/agent-platform/.claude/skills/$s .claude/skills/; done
```

**Python FastAPI**
```bash
SKILLS="skill-lang-python skill-framework-fastapi skill-database-postgresql \
  skill-database-sqlalchemy skill-database-migration skill-auth-jwt skill-api-rest \
  skill-testing-pytest skill-tooling-git skill-tooling-packagemanager \
  skill-context-read skill-context-write skill-role-blueprints \
  skill-role-code-review skill-role-breakdown-tasks skill-security-hardening"
for s in $SKILLS; do cp -r /path/to/agent-platform/.claude/skills/$s .claude/skills/; done
```

### Agents tối thiểu theo team size

| Team size | Agents cần thiết |
|-----------|-----------------|
| Solo dev | orchestrator, onboarding, builder, reviewer, tester, security |
| Small team | + ba, designer, qa, documenter, reporter |
| Full team | Copy toàn bộ (khuyến nghị) |

---

## Checklist

```
[ ] CLAUDE.md exists (global: ~/.claude/CLAUDE.md hoặc local: ./CLAUDE.md)
[ ] .claude/agents/ có ít nhất 6 folders agent-* (hoặc 20 nếu full install)
[ ] .claude/skills/ có ít nhất 19 folders skill-* bắt buộc (hoặc 109 nếu full install)
[ ] Mỗi agent folder có SKILL.md bên trong
[ ] Mỗi skill folder có SKILL.md bên trong
```
