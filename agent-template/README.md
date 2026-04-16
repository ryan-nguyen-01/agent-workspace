# Agent Template — Agentic Dev + Testing Workflow

Bộ template **self-contained** để clone về bất kỳ project nào và chạy workflow multi-agent: scan → build agents → dev per service → review/test → handover → QC test multi-env → bug loop → done.

---

## Cách dùng (clone về project mới)

```bash
# 1. Copy folder này vào project đích và đổi tên thành .agent
cp -r agent-template/ /path/to/your-project/.agent

# 2. Copy CLAUDE.md template vào root project đích
cp agent-template/CLAUDE.md.template /path/to/your-project/CLAUDE.md

# 3. Vào project đích, mở Claude và gõ:
#    "onboard project" → agent-onboarding sẽ scan và build brain
#    "build agents"    → agent-builder tạo agent-coder cho từng service
#    "dev: <task>"     → orchestrator phân công
```

Template không tạo `.claude/` — user tự di chuyển thủ công nếu muốn agent hoạt động global.

---

## Cấu trúc

```
.agent/
├── README.md                     ← Chính file này
├── workflow.md                   ← SOP BẮT BUỘC mọi agent đọc đầu tiên
├── CLAUDE.md.template            ← Template CLAUDE.md cho project root
├── agents/
│   ├── _core/                    ← 12 agent cố định
│   │   ├── orchestrator.agent.md
│   │   ├── onboarding.agent.md
│   │   ├── builder.agent.md
│   │   ├── analyst.agent.md
│   │   ├── context-keeper.agent.md
│   │   ├── reviewer.agent.md
│   │   ├── tester.agent.md
│   │   ├── handover.agent.md     ← NEW: tạo handover doc khi dev done
│   │   ├── qc-runner.agent.md    ← NEW: QC test multi-env, phân loại bug
│   │   ├── documenter.agent.md
│   │   ├── security.agent.md
│   │   └── migrator.agent.md
│   └── generated/                ← Builder ghi agent-coder-<service> vào đây
├── templates/
│   ├── agent-coder.template.md   ← Template cho generated coder
│   ├── handover.template.md      ← Dev → QC handover doc
│   ├── service.template.md       ← Per-service brain
│   ├── task.template.md          ← Task state file
│   ├── bug.template.md           ← Bug tracking
│   └── environment.template.md   ← Multi-env config
├── context/                      ← Brain: fill bởi onboarding
│   ├── summary.md                ← Project overview
│   ├── architecture.md           ← System architecture
│   ├── conventions.md            ← Auto-detected coding style
│   ├── environments.md           ← local/dev/sit config
│   ├── services/                 ← Per-service brain
│   │   └── <service>.md
│   └── common/
│       └── generics.md           ← Common utils/helpers (tránh viết lại)
├── handover/                     ← Handover docs dev→QC
│   └── <task-id>-handover.md
├── bugs/
│   ├── blockers/                 ← Bug dừng QC test
│   └── non-blockers/             ← Bug test song song
├── tasks/                        ← Task state machine
│   └── <task-id>.md
├── progress.md                   ← Tracking pipeline hiện tại
└── changelog.md                  ← Log quan trọng
```

---

## Workflow tổng quan

```
user giao task
  ↓
orchestrator đọc .agent/workflow.md + context
  ↓
analyst breakdown → tasks/<id>.md (state: todo)
  ↓
agent-coder-<service> chỉ làm trong scope service đó
  state: dev-in-progress → dev-done (sau khi unit test pass)
  ↓
reviewer + tester chạy song song
  ↓
handover agent tạo handover/<id>-handover.md
  state: qc-ready
  ↓
qc-runner test theo env (local → dev → sit)
  hỏi user key nếu thiếu
  ↓
phát hiện bug?
  ├─ BLOCKER → dừng test, tạo bugs/blockers/<id>.md
  │            state: dev-fix-in-progress
  │            dev fix → handover lại → qc retest
  │
  └─ NON-BLOCKER → tạo bugs/non-blockers/<id>.md, test tiếp
                    fix trong sprint, không chặn flow
  ↓
no bugs → state: qc-done
  ↓
documenter cập nhật docs
context-keeper sync brain
```

Chi tiết trong [workflow.md](workflow.md).

---

## Nguyên tắc cốt lõi

1. **Brain-first** — mọi agent phải đọc `workflow.md` + context liên quan trước khi action
2. **Scope isolation** — agent-coder-<service> CHỈ sửa file trong service của nó
3. **Handover mandatory** — dev done ≠ task done; phải có handover doc thì QC mới nhận
4. **Bug classification** — mỗi bug phải phân loại blocker/non-blocker rõ ràng
5. **Brain sync** — sau mỗi task done, context-keeper update services/<service>.md + generics.md

---

## Trạng thái task (state machine)

| State | Ý nghĩa | Agent phụ trách |
|-------|---------|-----------------|
| `todo` | Chưa bắt đầu | analyst |
| `dev-in-progress` | Đang code | coder-<service> |
| `dev-done` | Code xong, unit test pass | coder + reviewer + tester |
| `qc-ready` | Có handover doc | handover |
| `qc-testing` | QC đang test | qc-runner |
| `dev-fix-in-progress` | Fix blocker bug | coder-<service> |
| `qc-done` | Hết bug | qc-runner |
| `shipped` | Docs updated, brain synced | documenter + context-keeper |

---

## Môi trường testing

Khai báo trong `context/environments.md`:

```yaml
envs:
  local:
    base_url: http://localhost:3000
    db: postgres://localhost:5432/app_local
    keys: <gitignored .env.local>
  dev:
    base_url: https://dev.yourapp.com
    keys: <gitignored .env.dev>
  sit:
    base_url: https://sit.yourapp.com
    keys: <gitignored .env.sit>
```

qc-runner sẽ hỏi user nếu key thiếu (được phép hỏi — nằm trong exception của rule autonomy).
