# Agent Workspace Folder Guide

![Folder structure](diagrams/06-folder-structure.svg)

Tài liệu này giải thích các folder chính của `agent-workspace`: `.agent`, `.runtime`, `.claude`, `inputs`, và `services`.

## 1. Agent Workspace là gì?

`agent-workspace` là **workspace điều phối workflow agentic development**. Nó không phải source code ứng dụng. Source code ứng dụng được clone vào `services/<service-name>/`.

Workspace này tách 3 lớp:

```text
.agent/      Workflow source: workflow, rules, templates, docs
.runtime/    Runtime memory, task artifacts, bug records
.claude/     Claude adapter: agents, commands, skills, settings
```

Mục tiêu chính:

```text
Tránh mỗi hội thoại mới phải scan lại dự án từ đầu
Không tạo coder agent chung chung trước khi hiểu dự án
Bắt buộc task đi qua phân tích, planning, dev verification, QC, bug loop, memory update
Giới hạn coder agent theo service/module để tránh sửa sai phạm vi
Chuẩn hóa tài liệu bàn giao dev -> QC
```

## 2. Khi nào dùng agent-workspace?

Dùng workspace này khi bạn muốn làm việc theo quy trình agent end-to-end.

Ví dụ:

```text
Onboard một project mới
Phân tích cấu trúc project
Tạo Project Brain
Tạo coder agents theo service/module
Nhận task từ HLD, LLD, ticket, hoặc text
Chia task cho nhiều service coder
Kiểm tra Code Done
Tạo QC handoff
QC test và phân loại bug blocker/non-blocker
Resume task ở hội thoại mới
Cập nhật memory sau khi xong task
```

Các command thường dùng:

```text
/coord <request>       Entry chính, tự route workflow
/onboard               Scan project và tạo Project Brain
/create-coders         Tạo service coder agents sau user approval
/analyze-task <input>  Phân tích HLD/LLD/ticket/text
/plan-dev TASK-123     Tạo implementation plan
/dev TASK-123          Chạy dev flow
/verify-dev TASK-123   Kiểm tra Code Done
/handoff-qc TASK-123   Tạo tài liệu bàn giao QC
/qc TASK-123           Chạy QC flow
/bug TASK-123          Route bug blocker/non-blocker
/sync-memory TASK-123  Cập nhật Project Brain
/resume-task TASK-123  Tiếp tục task từ state hiện tại
/status                Xem trạng thái workflow/brain/agents
/policy-check          Kiểm tra gate/exception
```

## 3. Khi nào không nên dùng full workflow?

Không cần dùng full workflow cho việc quá nhỏ hoặc không thuộc workflow.

Ví dụ:

```text
Sửa một typo nhỏ mà không cần agent workflow
Hỏi giải thích một đoạn code đơn lẻ
Viết snippet tạm thời
Thử nghiệm local không cần lưu memory
Một task chưa muốn đi qua QC/handoff
```

Tuy nhiên, nếu task có thể ảnh hưởng project thật, nhiều service, auth, DB, API contract, QC, hoặc cần resume về sau, nên dùng workflow trong `agent-workspace`.

## 4. Nguyên tắc vận hành

`agent-workspace` được thiết kế theo mô hình:

```text
Workflow source -> Tool adapters -> Runtime context -> Task artifacts
```

Ý nghĩa từng lớp:

```text
.agent/workflow.md     State machine và SOP tổng thể
.agent/rules/          Luật bắt buộc, không được bỏ qua
.agent/templates/      Mẫu file artifact chuẩn
.agent/docs/           Tài liệu và sơ đồ
.claude/commands/      Entry point user gọi trong Claude Code
.claude/agents/        Vai trò và trách nhiệm của từng Claude agent
.claude/skills/        Hướng dẫn thao tác cụ thể cho agent
.runtime/context/      Project Brain, service control plane, workflow state
.runtime/tasks/        Artifact theo từng task
.runtime/bugs/         Bug blocker/non-blocker
```

Rule priority:

```text
.agent/workflow.md định nghĩa state machine
.agent/rules/ định nghĩa policy bắt buộc
.claude/commands/ định nghĩa cách user gọi workflow trong Claude Code
.claude/agents/ định nghĩa role behavior
.claude/skills/ định nghĩa cách làm chi tiết
```

Nếu có conflict, ưu tiên:

```text
.agent/workflow.md + .agent/rules/
.claude/commands/
.claude/agents/
.claude/skills/
.agent/templates/
```

## 5. Cấu trúc folder tổng quan

```text
.agent/
  workflow.md
  rules/
  templates/
  docs/

.runtime/
  context/
  tasks/
  bugs/

.claude/
  agents/
  commands/
  skills/
  settings.json
```

## 6. File cấp root

### `CLAUDE.md`

File hướng dẫn chính cho Claude/agent khi vào project.

Dùng để biết:

```text
Workflow mặc định
Bootstrap sequence
Alias/command cơ bản
Approval gates
Rule priority
Visual flow reference
```

Khi nào đọc:

```text
Khi agent bắt đầu làm việc trong project
Khi cần hiểu cách `agent-workspace` điều phối tổng thể
Khi cần biết entrypoint nào nên dùng
```

### `README.md`

Tài liệu dành cho người dùng/dev lead.

Dùng để biết:

```text
Kiến trúc tổng thể của `agent-workspace`
Cách chạy lần đầu
Luồng task tiêu chuẩn
Code Done rule
QC rule
Rules và commands hiện có
```

Khi nào đọc:

```text
Khi onboarding người mới vào workflow
Khi cần giới thiệu các folder chính của workspace
Khi cần xem command path chuẩn
```

### `workflow.md`

Nguồn chân lý cho state machine và SOP end-to-end.

Dùng để biết:

```text
Các state hợp lệ
Agent nào chịu trách nhiệm state nào
Luồng onboarding
Luồng tạo coder agents
Luồng task intake
Luồng dev
Luồng QC
Luồng bug
Luồng memory update
```

Khi nào đọc:

```text
Mọi agent phải đọc trước khi hành động
Khi cần validate một state transition
Khi cần biết task đang ở bước nào
```

### `.runtime/context/workflow-state.yaml`

Theo dõi trạng thái workflow hiện tại. Đây là file state chính của workspace.

Dùng để biết:

```text
State hiện tại
Task active
Next required action
```

Khi nào đọc:

```text
Khi muốn biết hệ thống đang ở đâu
Khi resume task hoặc resume workflow
```

### `changelog.md`

Ghi lại thay đổi quan trọng của workflow `agent-workspace`.

Dùng để biết:

```text
Kiến trúc đã thay đổi gì
Rules/commands/agents được cập nhật khi nào
Workflow policy thay đổi ra sao
```

Khi nào đọc:

```text
Khi audit thay đổi workflow
Khi cần hiểu vì sao cấu trúc hiện tại tồn tại
```

## 7. `agents/`

Folder này chứa định nghĩa các agent lõi và về sau sẽ chứa generated service coder agents.

```text
.claude/agents/
  coordinator.agent.md
  onboarding.agent.md
  agent-factory.agent.md
  task-analysis.agent.md
  coder-leader.agent.md
  dev-verification.agent.md
  qc-handoff.agent.md
  qc-runner.agent.md
  bug-router.agent.md
  memory-update.agent.md
  workflow-policy.agent.md
  coder-<service>.agent.md       generated later
```

### Khi nào dùng?

Dùng khi cần biết agent nào làm gì.

Ví dụ:

```text
Coordinator route task nhưng không code
Onboarding scan project nhưng không tạo coder
Agent Factory tạo coder sau approval
Task Analysis chuẩn hóa HLD/LLD/text
Coder Leader chia việc cho nhiều service coder
Service Coder chỉ sửa đúng scope
Dev Verification quyết định Code Done
QC Runner test và phân loại bug
Bug Router route blocker/non-blocker
Memory Update cập nhật Project Brain
Workflow Policy validate gate/transition
```

### Agent lõi

| Agent              | Vai trò                                                       |
| ------------------ | ------------------------------------------------------------- |
| `coordinator`      | Điều phối workflow, check brain, route command, hỏi approval  |
| `onboarding`       | Scan project, tạo Project Brain, Service Catalog, Test Policy |
| `agent-factory`    | Sinh coder agents theo service sau approval                   |
| `task-analysis`    | Phân tích HLD/LLD/ticket/text thành task spec                 |
| `coder-leader`     | Lead multi-service implementation                             |
| `dev-verification` | Kiểm tra Code Done, score >= 80%, critical pass               |
| `qc-handoff`       | Tạo tài liệu bàn giao dev -> QC                               |
| `qc-runner`        | Chạy QC, tạo test results, phát hiện bug                      |
| `bug-router`       | Phân loại blocker/non-blocker, route về dev                   |
| `memory-update`    | Cập nhật durable memory                                       |
| `workflow-policy`  | Validate state transition và approval gates                   |

### Generated coder agents

Generated coder agents chưa có ngay từ đầu.

Chúng chỉ được tạo sau:

```text
/onboard
-> phát hiện services/modules
-> user approve
-> /create-coders
```

Ví dụ sau này có thể có:

```text
coder-auth-service.agent.md
coder-payment-service.agent.md
coder-admin-web.agent.md
coder-notification-worker.agent.md
```

Mỗi coder agent phải có:

```text
allowed_read_paths
allowed_write_paths
forbidden_paths
test_policy
critical_checks
handoff obligations
escalation rules
```

## 8. `commands/`

Folder này chứa các lệnh user-facing.

```text
.claude/commands/
  coord.md
  onboard.md
  create-coders.md
  status.md
  analyze-task.md
  plan-dev.md
  dev.md
  verify-dev.md
  handoff-qc.md
  qc.md
  bug.md
  sync-memory.md
  skills.md
  resume-task.md
  policy-check.md
```

### Khi nào dùng?

Dùng khi bạn muốn gọi workflow bằng entrypoint rõ ràng.

Ví dụ:

```text
/coord thêm chức năng reset password
/onboard
/create-coders
/qc TASK-123
/skills status
/status
```

### Vì sao cần commands?

Commands giúp:

```text
User không cần nhớ agent nào cần gọi
Agent biết rules nào phải đọc
Workflow không bị nhảy bước
Artifact nào cần tạo được định nghĩa rõ
Stop condition rõ ràng
Output format nhất quán
```

### Command path chuẩn

```text
/coord
-> /onboard
-> /create-coders
-> /analyze-task
-> /plan-dev
-> /dev
-> /verify-dev
-> /handoff-qc
-> /qc
-> /bug nếu có defect
-> /sync-memory
```

## 9. `rules/`

Folder này chứa policy bắt buộc.

```text
.agent/rules/
  00-core-rules.md
  01-project-brain-rules.md
  02-onboarding-rules.md
  03-agent-factory-rules.md
  04-task-analysis-rules.md
  05-coder-leader-rules.md
  06-service-coder-rules.md
  07-dev-verification-rules.md
  08-qc-rules.md
  09-bug-routing-rules.md
  10-memory-rules.md
  11-approval-gates.md
  12-artifact-contracts.md
  13-security-secret-rules.md
```

### Khi nào dùng?

Dùng khi cần kiểm tra agent có được phép làm gì không.

Ví dụ:

```text
Có được tạo coder agents chưa?
Có được code chưa?
Có được tạo unit test không?
Có được chuyển sang QC không?
QC có được tiếp tục khi gặp bug không?
Có được lưu thông tin này vào memory không?
Có cần hỏi user approval không?
```

### Một số rule quan trọng

```text
Không có Project Brain thì không code
Không có onboarding thì không tạo coder
Không có task-analysis.yaml thì không dev
Không có qc-handoff.md thì không QC
Service coder chỉ sửa trong allowed_write_paths
Unit test chỉ tạo khi service policy yêu cầu
Nếu confidence thấp hoặc thiếu facts: hỏi user, không đoán, không fabricate evidence
Code Done cần >= 80% và critical checks pass 100%
QC gặp blocker thì dừng ngay
Không lưu secret/token/password/log dài vào `.runtime` artifacts hoặc tool adapter files
```

## 10. `skills/`

Folder này chứa hướng dẫn thao tác cụ thể cho agent.

```text
.claude/skills/
  skill-project-brain/
  skill-project-onboarding/
  skill-agent-factory/
  skill-task-analysis/
  skill-coder-leader/
  skill-service-coder/
  skill-dev-verification/
  skill-qc-handoff/
  skill-qc-runner/
  skill-bug-routing/
  skill-memory-update/
  skill-workflow-policy/
```

### Khi nào dùng?

Dùng khi một agent cần biết **cách làm** một capability.

Ví dụ:

```text
Onboarding agent dùng skill-project-onboarding
Agent Factory dùng skill-agent-factory
Task Analysis dùng skill-task-analysis
Coder Leader dùng skill-coder-leader
QC Runner dùng skill-qc-runner
Memory Update dùng skill-memory-update
```

### Khác gì với `agents/`?

```text
agents/ = ai là người chịu trách nhiệm
skills/ = làm việc đó theo phương pháp nào
rules/  = luật nào không được vi phạm
```

## 11. `templates/`

Folder này chứa mẫu artifact chuẩn.

```text
.agent/templates/
  agent-coder.template.md
  agent-registry.template.yaml
  architecture-review.template.yaml
  bug.template.yaml
  dev-verification.template.yaml
  environment.template.yaml
  memory-update.template.yaml
  project-brain.template.yaml
  qc-handoff.template.md
  qc-test-result.template.yaml
  service-brain.template.yaml
  task-analysis.template.yaml
  task-update.template.yaml
  task.template.yaml
  workflow-state.template.yaml
```

### Khi nào dùng?

Dùng khi agent cần tạo file artifact mới.

Ví dụ:

```text
Agent Factory tạo coder agent từ agent-coder.template.md
Onboarding tạo service brain từ service-brain.template.yaml
Task Analysis tạo task-analysis.yaml từ task-analysis.template.yaml
Dev Verification tạo dev-verification.yaml
QC Runner tạo qc-test-results.yaml
Bug Router tạo bug yaml
Memory Update tạo memory-updates.yaml
```

### Vì sao cần templates?

Templates giúp:

```text
Artifact nhất quán giữa các task
QC dễ đọc handoff
Agent mới có thể resume task từ file
Workflow Policy dễ validate thiếu file nào
```

## 12. `.runtime/context/`

`.runtime/context/` là runtime context của workspace:

```text
Project brain: kiến thức bền vững
Service control plane: service path, coder scope, test policy
Workflow state: task đang ở bước nào
```

Không tạo root `memory/` hoặc root `state/`. Source of truth hiện tại nằm dưới `.runtime/context/`.

```text
.runtime/context/
  index.yaml
  project-brain.yaml
  summary.md
  architecture.md
  conventions.md
  environments.md
  common/generics.md
  feedback/inbox.md
  feedback/patterns.md
  feedback/anti-patterns.md
  services/<service>.yaml
  service-catalog.yaml
  agent-registry.yaml
  test-policy.yaml
  skill-registry.yaml
  workflow-state.yaml
```

### Khi nào dùng?

Dùng khi agent cần nhớ thông tin dự án mà không scan lại từ đầu.

Ví dụ:

```text
Project này dùng stack gì?
Có những service nào?
Service nào có coder agent?
Service nào yêu cầu unit test?
API/schema/event nào đang tồn tại?
Task này đụng service nào?
Có pattern/common util nào nên reuse?
```

### File quan trọng

| File                      | Vai trò                                                                                 |
| ------------------------- | --------------------------------------------------------------------------------------- |
| `.runtime/context/index.yaml`       | Index đọc trước để tránh mở toàn bộ memory                                               |
| `.runtime/context/project-brain.yaml` | Memory tổng thể của project                                                           |
| `.runtime/context/service-catalog.yaml`   | Danh sách service/module, source path, coding boundary                                  |
| `.runtime/context/agent-registry.yaml` | Danh sách coder agents và scope                                                   |
| `.runtime/context/test-policy.yaml` | Quy định unit/manual test theo service                                                |
| `.runtime/context/workflow-state.yaml` | State hiện tại của workflow                                                           |
| `.runtime/context/skill-registry.yaml` | Registry máy đọc được cho skill selection, risk gate, approval, installed/failed skills |
| `feedback/inbox.md`       | Nơi nhận feedback thô khi AI làm sai/làm thiếu                                           |
| `feedback/patterns.md`    | Pattern đã xác nhận qua feedback để reuse                                                 |
| `feedback/anti-patterns.md` | Lỗi lặp lại cần tránh từ feedback                                                        |
| `services/<service>.yaml` | Memory chi tiết từng service                                                            |
| `common/generics.md`      | Pattern/util dùng chung để tránh viết lại                                               |

### Trạng thái ban đầu

Sau khi setup, state thường ở trạng thái:

```text
NEED_ONBOARDING
```

Nghĩa là cần chạy:

```text
/onboard
```

để fill thông tin thật của project.

## 13. `docs/`

Folder tài liệu giải thích và visual.

```text
.agent/docs/
  folder-guide.md
  visual-flow.md
  deep-onboarding.md
  skill-composition.md
  external-skills.md
  diagrams/
    01-system-overview.svg
    02-bootstrap-flow.svg
    03-task-execution-flow.svg
    04-qc-bug-routing.svg
    05-state-machine.svg
    06-folder-structure.svg
    07-deep-onboarding.svg
    08-skill-composition.svg
    09-principle-flow.svg
```

### Khi nào dùng?

Dùng khi cần hiểu hệ thống bằng tài liệu hoặc sơ đồ.

Ví dụ:

```text
Người mới muốn hiểu agent-workspace
Dev lead muốn review workflow
QC muốn hiểu bug loop
Agent designer muốn chỉnh architecture
```

### File quan trọng

| File                   | Vai trò                                          |
| ---------------------- | ------------------------------------------------ |
| `folder-guide.md`      | Tài liệu này                                     |
| `visual-flow.md`       | Trang xem toàn bộ sơ đồ workflow                 |
| `deep-onboarding.md`   | Tiêu chuẩn deep onboarding                       |
| `skill-composition.md` | Tiêu chuẩn skill composition                     |
| `external-skills.md`   | Registry các external skills đã cài              |
| `diagrams/*.svg`       | Hình tĩnh để Markdown preview hiển thị trực tiếp |

## 14. `.runtime/tasks/`

Folder lưu artifact theo từng task.

```text
.runtime/tasks/
  TASK-20260518-001-login/
    task-input.md
    task.yaml
    task-updates.yaml
    task-analysis.yaml
    architecture-review.yaml
    implementation-plan.yaml
    service-assignments.yaml
    coder-results.yaml
    dev-verification.yaml
    qc-handoff.md
    qc-test-results.yaml
    qc-delivery-report.md
    bugs.yaml
    memory-updates.yaml
```

### Khi nào dùng?

Dùng khi có một task cụ thể cần đi qua workflow.

Ví dụ:

```text
Thêm feature
Fix bug
Refactor có scope rõ
Thay đổi API
Task lấy từ HLD/LLD/ticket
```

### Vì sao quan trọng?

Task folder giúp:

```text
Resume task ở hội thoại mới
Biết task đang ở state nào
Biết ai đã làm gì
QC có handoff rõ
Bug có reproduction rõ
Memory update có source artifact
```

QC handoff canonical nằm tại `.runtime/tasks/<task_id>/qc-handoff.md`. Không mirror sang folder riêng.

## 15. `.runtime/bugs/`

Folder lưu bug do QC hoặc workflow phát hiện.

```text
.runtime/bugs/
  blockers/
    BUG-123.yaml
  non-blockers/
    BUG-456.yaml
```

### Khi nào dùng?

Dùng khi QC phát hiện bug.

### Blocker bug

Blocker là bug khiến QC không thể tiếp tục luồng chính.

Ví dụ:

```text
Happy path fail
App crash
Core API 500 toàn bộ
Auth/permission bị sai
Data corruption
Không tạo được test data nền
Bug chặn các case QC tiếp theo
```

Hành động:

```text
Dừng QC ngay
Tạo .runtime/bugs/blockers/<bug-id>.yaml
Route về Coder Leader
Dev fix
Verify lại
QC retest
```

### Non-blocker bug

Non-blocker là bug không chặn QC tiếp tục.

Ví dụ:

```text
UI copy sai
Layout nhỏ
Warning không ảnh hưởng flow
Edge case phụ
```

Hành động:

```text
Tạo .runtime/bugs/non-blockers/<bug-id>.yaml
QC tiếp tục các case không bị ảnh hưởng
Dev có thể fix song song
```

## 17. Luồng sử dụng thực tế

### Lần đầu setup project

```text
/coord
-> Project Brain Check
-> NEED_ONBOARDING
-> /onboard
-> Agent Candidate Report
-> User approve
-> /create-coders
-> AGENTS_READY
```

### Làm một task mới

```text
/coord <task text hoặc HLD/LLD>
-> /analyze-task
-> /plan-dev
-> /dev
-> /verify-dev
-> /handoff-qc
-> /qc
-> /sync-memory
```

### Gặp blocker bug trong QC

```text
/qc TASK-123
-> blocking bug found
-> /bug
-> create .runtime/bugs/blockers/BUG-xxx.yaml
-> stop QC
-> route to Coder Leader
-> /dev fix
-> /verify-dev
-> /handoff-qc
-> /qc retest
```

### Gặp non-blocker bug trong QC

```text
/qc TASK-123
-> non-blocking bug found
-> /bug
-> create .runtime/bugs/non-blockers/BUG-xxx.yaml
-> QC continues
-> dev fixes in parallel if needed
```

### Resume task ở hội thoại mới

```text
/resume-task TASK-123
-> read task artifacts
-> detect current state
-> suggest next command
```

## 18. Ai nên đọc file nào?

### Dev lead / user

```text
.claude/README.md
.agent/docs/folder-guide.md
.agent/docs/visual-flow.md
.claude/commands/README.md
```

### Coordinator agent

```text
.agent/workflow.md
.agent/rules/00-core-rules.md
.agent/rules/01-project-brain-rules.md
.agent/rules/11-approval-gates.md
.agent/rules/12-artifact-contracts.md
.claude/commands/coord.md
```

### Onboarding agent

```text
.agent/workflow.md
.claude/commands/onboard.md
.agent/rules/02-onboarding-rules.md
.agent/templates/project-brain.template.yaml
.agent/templates/service-brain.template.yaml
```

### Agent Factory

```text
.claude/commands/create-coders.md
.agent/rules/03-agent-factory-rules.md
.agent/templates/agent-coder.template.md
.runtime/context/service-catalog.yaml
.runtime/context/test-policy.yaml
```

### Service coder agent

```text
.agent/rules/06-service-coder-rules.md
.runtime/context/services/<service>.yaml
.runtime/tasks/<task-id>/service-assignments.yaml
```

### QC agent

```text
.claude/commands/qc.md
.agent/rules/08-qc-rules.md
.agent/rules/09-bug-routing-rules.md
.runtime/tasks/<task-id>/qc-handoff.md
```

## 19. Cách maintain folder này

Khi thêm rule mới:

```text
Thêm file hoặc section trong .agent/rules/
Update .agent/rules/README.md
Update commands liên quan
Update agent Rule bindings nếu cần
```

Khi thêm command mới:

```text
Thêm .claude/commands/<command>.md
Khai báo responsible agent
Khai báo required rules
Khai báo required artifacts
Update .claude/commands/README.md
Update README.md nếu command user-facing quan trọng
```

Khi thêm artifact mới:

```text
Thêm template trong .agent/templates/
Update .agent/rules/12-artifact-contracts.md
Update .agent/workflow.md nếu artifact ảnh hưởng state machine
Update .agent/docs/visual-flow.md nếu thay đổi luồng
```

Khi thay đổi workflow:

```text
Update .agent/workflow.md trước
Update rules liên quan
Update commands liên quan
Update agents liên quan
Update docs/visual-flow.md và diagrams nếu cần
Update changelog.md
```

## 20. Checklist nhanh

Trước khi code:

```text
Project Brain fresh chưa?
Task đã có task-analysis.yaml chưa?
Impacted services có active coder agents chưa?
Coder scopes đúng chưa?
Test policy rõ chưa?
```

Trước khi chuyển QC:

```text
Dev verification score >= 80% chưa?
Critical checks pass 100% chưa?
Không có blocker chưa?
QC handoff đã tạo chưa?
```

Khi QC gặp bug:

```text
Bug có blocker không?
Nếu blocker: dừng QC ngay
Nếu non-blocker: tạo bug task và tiếp tục QC
Bug có reproduction, expected, actual chưa?
```

Khi kết thúc task:

```text
QC_DONE chưa?
Memory update cần ghi gì?
Service brain có thay đổi không?
Bug pattern có cần lưu không?
```

## 21. Skill composition standard

Skills are capabilities, not agent identities.

```text
One agent can use many skills.
One skill can be reused by many agents.
Generated service coders should combine workflow skills, technical skills, quality skills, and artifact skills.
```

Read [skill-composition.md](skill-composition.md) for the full standard.

## 22. Deep onboarding

Deep onboarding là lớp scan sâu để agent hiểu project-specific reusable assets, coding flow, business flow, conventions và anti-patterns trước khi sinh coder agents.

Dùng khi:

- Project có nhiều helper/shared module dễ bị viết trùng.
- Cần coder agent tuân thủ style/code flow hiện có.
- Task chạm business flow phức tạp như auth, payment, notification, order, worker, event-driven, sync data.
- Cần QC và Dev Verification biết flow nào là critical.

File liên quan:

- docs/deep-onboarding.md
- .runtime/context/common/generics.md
- .runtime/context/conventions.md
- .runtime/context/architecture.md
- .runtime/context/project-brain.yaml deep_project_intelligence
- .runtime/context/services/<service>.yaml service_deep_intelligence

Nguyên tắc chính:

- Onboarding phải ghi path, purpose, when_to_reuse, evidence và confidence.
- Không paste source code dài vào memory.
- Service coder phải check reusable assets trước khi tạo helper mới.
- Dev Verification phải kiểm tra duplicate helper risk và convention compliance.
