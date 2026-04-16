# Workflow — SOP BẮT BUỘC

**File này là nguồn chân lý duy nhất về quy trình. Mọi agent PHẢI đọc đầu tiên trước khi thực hiện task.**

---

## 0. Required reading order (mọi agent)

Khi được kích hoạt, agent đọc theo thứ tự:

1. `.agent/workflow.md` (file này) — SOP chung
2. `.agent/agents/_core/<tên-agent>.agent.md` — định nghĩa của chính mình
3. `.agent/context/summary.md` — project overview
4. `.agent/context/conventions.md` — coding style
5. Context liên quan đến scope:
   - Coder: `.agent/context/services/<service>.md` + `.agent/context/common/generics.md`
   - Reviewer/Tester: service file + conventions
   - QC: `.agent/context/environments.md` + handover doc
6. Task file: `.agent/tasks/<task-id>.md`

Nếu thiếu file bắt buộc → gọi `agent-onboarding` để rebuild, không tự đoán.

---

## 1. Roles & responsibilities

| Agent | Scope | Output |
|-------|-------|--------|
| **orchestrator** | Điều phối toàn bộ pipeline | Task assignment + state tracking |
| **onboarding** | Scan project lần đầu | `.agent/context/` đầy đủ |
| **builder** | Detect stack → tạo agent-coder per service | `.agent/agents/generated/*.agent.md` |
| **analyst** | Breakdown task → subtasks có AC rõ ràng | `.agent/tasks/<id>.md` |
| **agent-coder-\<service\>** | Code + unit test TRONG scope service | Code changes + unit tests |
| **reviewer** | Review code quality, conventions | Review report |
| **tester** | Integration + E2E tests | Test files + results |
| **handover** | Tổng hợp dev output → handover doc | `.agent/handover/<id>-handover.md` |
| **qc-runner** | Test multi-env, phân loại bug | Test report + bugs files |
| **documenter** | Update docs/README/changelog | Doc diffs |
| **context-keeper** | Sync brain sau mỗi task | Updated `context/services/*` + `generics.md` |
| **security** | Audit security (parallel với reviewer) | Security report |
| **migrator** | Refactor/upgrade lớn | Migration plan + execution |

---

## 2. Scope isolation (QUAN TRỌNG)

`agent-coder-<project>-<service>-<tech>` được sinh bởi builder với ràng buộc:

- **Working directory** khai báo rõ trong agent definition (ví dụ `services/payment/`)
- **Không đọc/ghi ngoài scope** — nếu task đụng service khác → báo orchestrator để spawn coder của service đó
- **Shared code** (common/generics): chỉ đọc; muốn thêm util mới → yêu cầu orchestrator phê duyệt qua task riêng

Vi phạm scope → reviewer MUST reject.

---

## 3. Task state machine

```
       todo
         │ (analyst breakdown xong)
         ▼
   dev-in-progress
         │ (coder done + unit test pass)
         ▼
      dev-done
         │ (reviewer + tester pass)
         ▼
    qc-ready ◄───────────────────┐
         │ (handover doc tạo xong)│
         ▼                        │
   qc-testing                     │
         │                        │
    ┌────┴────────────┐           │
    ▼                 ▼           │
blocker bug      non-blocker bug  │
    │                 │           │
    ▼                 ▼           │
STOP QC       tiếp tục QC         │
    │         + bugs/non-blockers/│
    ▼                             │
dev-fix-in-progress               │
    │                             │
    ▼                             │
handover lại ─────────────────────┘
                  
khi no bugs:
    qc-testing → qc-done
                    │
                    ▼
                shipped
         (docs + brain synced)
```

Mỗi transition ghi vào `tasks/<id>.md` section `## History` với timestamp + agent.

---

## 4. Dev workflow (chi tiết)

### 4.1 — Coder nhận task

```
Input: tasks/<id>.md với state=todo

Steps:
1. Đọc required files (section 0)
2. Kiểm tra scope: task có thuộc service mình phụ trách không?
   → Không → báo orchestrator, REJECT
3. Set state = dev-in-progress
4. Đọc services/<service>.md để biết API/schema/deps hiện tại
5. Đọc common/generics.md để tái dùng utils có sẵn (KHÔNG viết lại)
6. Implement theo conventions.md
7. Viết unit tests (colocated) — xem Definition of Done section 5
8. Self-verify:
   - Lint pass
   - Unit tests pass  
   - Không sửa file ngoài scope (run: git diff --name-only, confirm paths)
9. Update services/<service>.md nếu có thay đổi API/schema (để brain fresh)
10. Set state = dev-done
11. Trigger reviewer + tester song song
```

### 4.2 — Reviewer + Tester parallel

```
Reviewer:
  - Check conventions compliance
  - Check scope isolation (không sửa ngoài service)
  - Check không viết lại util đã có trong generics
  - Output: review-report.md trong task file

Tester:
  - Viết integration tests (cross-boundary)
  - Chạy E2E cho happy path
  - Output: tests + coverage diff

Cả hai PASS → chuyển sang handover
Một trong hai FAIL → loop back dev-in-progress với feedback
```

### 4.3 — Handover agent

```
Input: task done + reviewer/tester pass

Steps:
1. Đọc tasks/<id>.md + git diff của task
2. Tổng hợp theo template handover.template.md
3. Ghi vào handover/<task-id>-handover.md gồm:
   - Changes (file list + summary)
   - API Diff (endpoints mới/thay đổi, schema changes)
   - Test Evidence (test files, coverage, how to run)
   - Env & Keys (env vars cần thêm, key placeholders)
   - How to verify (step-by-step cho QC)
   - Known limitations (edge cases chưa handle, tech debt)
   - Scope of retest (dùng khi fix blocker: "chỉ retest phần X" vs "full regression")
4. Set state = qc-ready
5. Notify qc-runner
```

---

## 5. Definition of Done

Task DONE khi tất cả pass:

### 5.1 — Dev-done checklist

- [ ] Tất cả AC trong task implement đủ
- [ ] Lint pass, compile pass
- [ ] Unit tests cover happy path + edge + error (nếu project có test framework)
- [ ] Không sửa file ngoài service scope
- [ ] `services/<service>.md` updated (nếu có API/schema change)
- [ ] Reviewer approve
- [ ] Tester integration/E2E pass

### 5.2 — QC-done checklist

- [ ] Test trên local pass
- [ ] Test trên dev env pass (nếu có)
- [ ] Test trên sit env pass (nếu có)
- [ ] Zero blocker bug
- [ ] Non-blocker bug đã có ticket, được team accept

### 5.3 — Shipped checklist

- [ ] Docs updated (API docs, README nếu cần)
- [ ] CHANGELOG.md entry
- [ ] Brain synced: `services/<service>.md` + `generics.md` mới nhất
- [ ] Task file archived

---

## 6. Multi-env testing protocol

qc-runner theo thứ tự:

```
1. local      → luôn chạy trước
2. dev        → chỉ chạy nếu local pass
3. sit        → chỉ chạy nếu dev pass
4. (pre-prod) → optional, user trigger riêng
```

**Key handling:**

- Đọc `context/environments.md` để biết env nào cần key gì
- Key THẬT không bao giờ ghi vào `.agent/` — chỉ placeholder
- Key thật user để ở `.env.local`, `.env.dev`, `.env.sit` (gitignored)
- Thiếu key khi chạy env X → qc-runner HỎI user:
  > "Cần `STRIPE_KEY_SIT` để test payment trên env SIT. Bạn cung cấp key hoặc skip env này?"
- User có thể chọn: `[provide]` / `[skip env]` / `[abort]`

**Domain config:**

- Mỗi env có `base_url` riêng trong environments.md
- qc-runner inject base_url vào test config, không hardcode

---

## 7. Bug classification

### 7.1 — BLOCKER (chặn QC)

Bug được phân loại blocker nếu THỎA 1 trong:

- Happy path của feature FAIL
- Crash app / 500 error trên core endpoint
- Data corruption / data loss
- Security vulnerability (auth bypass, SQL injection, XSS...)
- Blocker downstream cho test khác (VD: login fail → không test được gì sau đó)

**Hành động:**

1. qc-runner tạo `bugs/blockers/<bug-id>.md` theo `templates/bug.template.md`
2. **DỪNG QC test ngay** — không test tiếp cả env hiện tại
3. Update task state → `dev-fix-in-progress`
4. Assign về `agent-coder-<service>` tương ứng
5. Coder fix → handover lại (handover doc mới ghi rõ "scope of retest")
6. qc-runner resume với retest scope theo handover

### 7.2 — NON-BLOCKER (test song song)

Bug non-blocker:

- UI glitch không ảnh hưởng function
- Log sai format
- Edge case hiếm (user report < 1%)
- Performance chậm nhưng chưa vượt SLA
- Cosmetic / copywriting

**Hành động:**

1. Tạo `bugs/non-blockers/<bug-id>.md`
2. **Tiếp tục QC test** các AC còn lại
3. Ghi vào task file section `## Non-blocker bugs found`
4. Sau khi QC done feature chính → team quyết định fix trong sprint hoặc backlog

### 7.3 — Definition of QC-done

QC-done khi:

- Tất cả AC trong handover PASS
- Zero blocker bug open
- Non-blocker bugs đã được ghi nhận (không yêu cầu fix để QC-done)

---

## 8. Brain sync (context-keeper)

Sau mỗi task transition `qc-done → shipped`, context-keeper:

1. Delta-scan service folder vừa thay đổi
2. Update `context/services/<service>.md`:
   - API endpoints mới
   - Schema changes
   - Dependencies mới
3. Update `context/common/generics.md` nếu có util common mới
4. Update `context/conventions.md` nếu detect pattern mới (>2 lần dùng)
5. Ghi vào `changelog.md`

Brain luôn là **nguồn tham khảo đầu tiên** — không ai scan repo lại khi context fresh.

---

## 9. Quy tắc tuyệt đối

1. **Không agent nào bypass workflow.md này** — nếu cần thay đổi quy trình, sửa file này trước
2. **Không sửa file ngoài scope** — vi phạm → revert
3. **Không viết lại util đã có trong generics** — tái dùng
4. **Không đánh dấu task done khi AC còn lại** — honest reporting
5. **Không ghi secret vào `.agent/`** — chỉ placeholder, key thật ở `.env.*`
6. **Không skip handover** — dev done KHÔNG phải task done
7. **Không test env khác khi local chưa pass** — tiết kiệm thời gian + tránh noise

---

## 10. Escalation

Khi agent gặp vấn đề không thể tự giải quyết → ghi vào `progress.md` section `## Blockers` + notify orchestrator. Orchestrator quyết định:

- Re-assign agent khác
- Hỏi user
- Split task nhỏ hơn
- Abort task (ghi lý do)
