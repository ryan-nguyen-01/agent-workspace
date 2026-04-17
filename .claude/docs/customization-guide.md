# Customization Guide — agent-platform

Hướng dẫn mở rộng framework cho project khách.

---

## Mục lục

1. [Tổng quan](#tổng-quan)
2. [Thêm Custom Agent](#thêm-custom-agent)
3. [Thêm Custom Skill](#thêm-custom-skill)
4. [Thêm Custom Rule](#thêm-custom-rule)
5. [Custom Routing](#custom-routing)
6. [Override Workflow Settings](#override-workflow-settings)
7. [Thêm Custom Command](#thêm-custom-command)
8. [Checklist tích hợp](#checklist-tích-hợp)

---

## Tổng quan

agent-platform là framework kit — bạn cài vào project khách và mở rộng theo nhu cầu:

```
.claude/                    ← Framework (không sửa trực tiếp)
├── agents/                 ← 11 workflow agents (built-in)
├── skills/                 ← 227 skills (built-in)
├── rules/                  ← 15 rules (built-in)
├── commands/               ← 15 commands (built-in)
└── context/                ← Runtime context (auto-generated)

CLAUDE.local.md             ← Project overrides (bạn sửa file này)
```

**Nguyên tắc**: Thêm file mới thay vì sửa file framework gốc. Điều này giúp upgrade framework dễ dàng.

---

## Thêm Custom Agent

### Khi nào cần?

- Project cần agent chuyên biệt cho domain cụ thể (payment, notification, ML pipeline...)
- Muốn agent có scope hẹp hơn built-in agents

### Cách làm

1. **Tạo agent file** tại `.claude/agents/`:

```bash
# Naming: <tên-agent>.agent.md
touch .claude/agents/coder-payment.agent.md
```

2. **Viết agent definition** theo template:

```markdown
# Agent: coder-payment

## Vai trò

Viết code cho payment service (Stripe integration, webhook handling).

## Skills

- skill-service-coder (workflow)
- stripe-best-practices (technical)
- payment-integration (technical)

## Allowed paths

- allowed_read_paths: ["src/payment/", "src/shared/", ".claude/context/"]
- allowed_write_paths: ["src/payment/"]
- forbidden_paths: ["src/auth/", "src/database/migrations/"]

## Test policy

- unit_tests_required: true
- test_framework: jest
- coverage_target: 80%

## Escalation

- Cross-service changes → route to coder-leader
- Auth/security changes → require critical check
```

3. **Đăng ký trong `CLAUDE.local.md`**:

```yaml
routing_overrides:
  - match: ["payment", "thanh toán", "stripe"]
    agent: coder-payment
    note: "Route payment tasks to dedicated coder"
```

4. **Cập nhật agent-registry** (sau khi chạy `/create-coders` hoặc thủ công):

```yaml
# .claude/context/agent-registry.yaml
agents:
  - id: coder-payment
    file: .claude/agents/coder-payment.agent.md
    status: active
    service: payment
```

---

## Thêm Custom Skill

### Khi nào cần?

- Agent cần kiến thức chuyên sâu về thư viện/framework project dùng
- Muốn chuẩn hóa cách viết code cho domain cụ thể

### Cách làm

1. **Tạo skill folder**:

```bash
mkdir -p .claude/skills/skill-my-custom-lib
```

2. **Viết `SKILL.md`**:

````markdown
# Skill: my-custom-lib

## Mô tả

Hướng dẫn sử dụng thư viện XYZ trong project.

## Khi nào dùng

- Khi cần implement feature liên quan đến XYZ
- Khi viết code trong `src/xyz/`

## Patterns

### Pattern 1: Basic usage

\```typescript
import { XYZ } from 'xyz-lib';
const client = new XYZ({ apiKey: process.env.XYZ_KEY });
\```

### Pattern 2: Error handling

\```typescript
try {
await client.doSomething();
} catch (e) {
if (e instanceof XYZError) {
// handle specific error
}
throw e;
}
\```

## Anti-patterns

- ❌ Không khởi tạo client trong mỗi request
- ❌ Không hardcode API key
- ✅ Dùng singleton pattern cho client
- ✅ Luôn handle XYZError riêng
````

3. **Reference trong agent**:

```markdown
# Trong agent definition

## Skills

- skill-my-custom-lib
```

4. **Cập nhật registries** (nếu skill là external hoặc cần runtime selection):

```yaml
# .claude/context/skill-registry.yaml — machine config (Agent Factory reads this)
skills:
  my-custom-lib:
    installed: true
    source: local
    category: custom
    risk: low

# .claude/docs/external-skills.md — human docs (install history, security notes)
```

> Xem thêm: [external-skills.md](external-skills.md) giải thích quan hệ giữa hai files.

---

## Thêm Custom Rule

### Khi nào cần?

- Enforce convention cho toàn project (naming, folder structure...)
- Thêm security policy riêng
- Quy định riêng về test/QC cho project

### Cách làm

1. **Tạo rule file** với prefix số thứ tự tiếp theo:

```bash
# Built-in rules: 00-14
# Custom rules: 15+
touch .claude/rules/15-project-specific.md
```

2. **Viết rule theo format chuẩn**:

````markdown
# R-015: Project Specific Rules

## Applies to

All agents.

## Rules

\```text
R-015-01: All API responses must use camelCase field names.
R-015-02: Database queries must use parameterized statements.
R-015-03: Every public API endpoint must have rate limiting.
\```

## Violation handling

Stop and report to Coordinator.
````

---

## Custom Routing

Thêm routing rules vào `CLAUDE.local.md`:

```yaml
routing_overrides:
  # Route payment tasks
  - match: ["payment", "thanh toán", "stripe", "invoice"]
    agent: coder-payment
    note: "Dedicated payment coder"

  # Route ML tasks
  - match: ["ML", "model", "training", "prediction"]
    agent: coder-ml
    note: "ML pipeline coder"

  # Override built-in routing
  - match: ["deploy"]
    agent: my-custom-deployer
    note: "Use custom deployer instead of SRE"
```

---

## Override Workflow Settings

Trong `CLAUDE.local.md`, uncomment và chỉnh:

```yaml
# Giảm threshold cho prototype/spike
code_done_threshold: 0.70

# Skip QC cho nội bộ
qc_required: false

# Tắt memory updates
memory_updates: false
```

Hoặc sửa `.claude/settings.json`:

```json
{
  "workflow": {
    "code_done_threshold": 0.7,
    "qc_handoff_required": false
  }
}
```

---

## Thêm Custom Command

### Cách làm

1. **Tạo command file**:

```bash
touch .claude/commands/my-command.md
```

2. **Viết command definition**:

```markdown
# /my-command

## Mô tả

Chạy custom workflow cho project.

## Steps

1. Đọc context từ .claude/context/
2. Thực hiện action X
3. Output kết quả

## Sử dụng

User gõ: `/my-command <arguments>`
```

---

## Checklist tích hợp

Khi apply framework vào project khách:

```
□ Copy .claude/ vào project root
□ Copy CLAUDE.md, CLAUDE.local.md, SETUP.md, GUIDELINES.md
□ Chỉnh CLAUDE.local.md (project info, overrides)
□ Chạy /onboard để scan project
□ Review agent candidates → approve
□ Chạy /create-coders cho approved services
□ (Optional) Thêm custom agents, skills, rules
□ Chạy scripts/validate-install.sh kiểm tra
□ Commit .claude/ vào git
```

---

## Upgrade framework

Khi agent-platform có version mới:

1. **Backup** custom files: agents, skills, rules bạn thêm
2. **Update** `.claude/` từ agent-platform mới
3. **Restore** custom files
4. **Chạy** `scripts/validate-install.sh` kiểm tra
5. **Xem** CHANGELOG.md cho breaking changes

> **Tip**: Dùng git subtree hoặc git submodule để quản lý upgrade tự động. Xem chi tiết trong SETUP.md.
