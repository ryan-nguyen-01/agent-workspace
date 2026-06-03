# Customization Guide — agent-workspace

Hướng dẫn mở rộng `agent-workspace` theo đúng mô hình hiện tại: user clone repo này, clone application repositories vào `services/`, đặt reference docs vào `inputs/`, rồi chạy onboarding từ workspace này.

## Nguyên tắc

```text
Không copy .claude/ sang service repos.
Không tạo root memory/ hoặc state/.
Không dùng scripts để vận hành workflow chính.
Không route raw user input thẳng vào sub-agent.
Coordinator là entrypoint duy nhất.
```

Runtime hiện tại nằm trong:

```text
.runtime/context/   Project brain, service catalog, agent registry, test policy, workflow state, model/status/response UI
.runtime/status.md  Generated status artifact
.runtime/status.html Generated browser status dashboard
.runtime/tasks/     Task artifacts
.runtime/bugs/      Bug artifacts
inputs/            User-provided PRD/HLD/ADR/OpenAPI/glossary/runbooks
services/          Gitignored local clones of application repositories
```

## Khi Nào Nên Customize

Customize khi workspace cần thêm policy hoặc knowledge thật sự bền vững:

```text
Thêm generated service coder sau onboarding
Thêm built-in/cross-cutting coder có permission contract rõ
Thêm skill chuyên môn
Thêm rule policy cho team
Thêm artifact template mới
Cập nhật docs để agents hiểu đúng workflow
```

Không customize chỉ để route nhanh hơn. Routing vẫn phải đi qua Coordinator.

## Thêm Service Coder

Service coders nên được tạo qua workflow:

```text
1. Clone service vào services/<service-name>/
2. Chạy /onboard
3. Review service catalog và coder candidates
4. Approve /create-coders
5. Agent Factory tạo .claude/agents/coders/coder-<service>.agent.md
6. Agent Factory cập nhật .runtime/context/agent-registry.yaml
```

Không tạo service coder bằng tay nếu chưa có service catalog và allowed/forbidden paths.

## Thêm Cross-Cutting Coder

Dùng khi scope không thuộc một service duy nhất, ví dụ infra hoặc database.

Checklist:

```text
1. Tạo .claude/agents/coders/coder-<scope>.agent.md
2. Thêm contract vào .runtime/context/agent-registry.yaml
3. Định nghĩa allowed_read_paths, allowed_write_paths, forbidden_paths
4. Thêm escalation rules và test_policy
5. Cập nhật AGENTS.md, CLAUDE.md, README.md nếu là built-in shipped coder
6. Cập nhật CHANGELOG.md
```

Built-in hiện có:

```text
coder-infra      Terraform/IaC, Kubernetes, Docker, CI/CD
coder-database   schema, migrations, queries, indexes
```

## Thêm Workflow Agent

Workflow agent là control-plane agent, không phải coder. Chỉ thêm khi có một phase/gate mới trong workflow.

Checklist:

```text
1. Tạo .claude/agents/<role>.agent.md
2. Cập nhật .agent/workflow.md
3. Cập nhật .runtime/context/workflow-state.yaml nếu có state mới
4. Cập nhật .agent/templates/workflow-state.template.yaml
5. Thêm artifact template nếu agent có output mới
6. Cập nhật rules liên quan
7. Cập nhật CLAUDE.md, AGENTS.md, README.md, docs/agent-catalog.md, docs/agent-taxonomy.md
8. Cập nhật diagrams và CHANGELOG.md
```

Workflow agents hiện có: 12. Built-in coders không được tính là workflow agents.

## Thêm Skill

Skill là capability, không phải agent identity.

Checklist:

```text
1. Tạo .claude/skills/<skill-name>/SKILL.md
2. Chạy /skills refresh-registry
3. Cập nhật .runtime/context/skill-registry.yaml nếu cần metadata/risk
4. Cập nhật skills-lock.json nếu skill được quản lý trong lock
5. Cập nhật .agent/docs/external-skills.md nếu là external skill
6. Cập nhật CHANGELOG.md nếu behavior hoặc risk thay đổi
```

Với skill đã tồn tại, dùng:

```text
/skills status
/skills audit
/skills update <skill-name>
/skills refresh-registry
```

## Thêm Rule

Custom rule nên dùng prefix `16+` vì built-in rules là `00-15`.

Checklist:

```text
1. Tạo .agent/rules/16-<name>.md
2. Ghi rõ Applies to, Rules, Violation handling
3. Cập nhật CLAUDE.md rules list nếu rule là default framework policy
4. Cập nhật CHANGELOG.md
```

Không thêm rule nếu chỉ là preference tạm thời cho một task. Preference tạm thời nên nằm trong task artifact.

## Thêm Template

Template dùng cho artifact có schema ổn định.

Checklist:

```text
1. Tạo .agent/templates/<artifact>.template.yaml hoặc .md
2. Cập nhật .agent/rules/12-artifact-contracts.md
3. Cập nhật agent/command sẽ tạo artifact đó
4. Cập nhật docs nếu artifact thuộc workflow chính
```

## Custom Routing

Không dùng local override config làm routing source of truth.

Routing chuẩn:

```text
Raw user input -> /coord -> coordinator -> đúng workflow phase
```

Muốn thay đổi routing mặc định thì sửa các file policy tương ứng:

```text
.agent/workflow.md
.claude/agents/workflow/coordinator.agent.md
.agent/rules/11-approval-gates.md
.runtime/context/workflow-state.yaml
```

Sau đó cập nhật docs và CHANGELOG.

## Override Workflow Settings

Default framework settings nằm ở:

```text
.claude/settings.json
```

Chỉ sửa khi muốn đổi default shipped behavior của framework. Với policy runtime của workspace đã onboard, ưu tiên ghi vào `.runtime/context/` qua workflow phù hợp.

Các thay đổi có rủi ro cao cần rule/approval rõ:

```text
code_done_threshold
qc_handoff_required
blocker_stops_qc
coder_creation_requires_approval
memory_updates_enabled
```

## Checklist Tích Hợp

```text
□ Clone agent-workspace
□ Clone service repositories vào services/<service-name>/
□ Đặt PRD/HLD/ADR/specs vào inputs/
□ Chạy /coord hoặc /onboard
□ Review project brain, service catalog, test policy, coder candidates
□ Approve /create-coders cho services phù hợp
□ Bắt đầu task qua /coord
```

## Upgrade Framework

Khi `agent-workspace` có version mới:

```text
1. Pull version mới trong repo agent-workspace
2. Resolve conflicts cẩn thận trong .runtime/context, .runtime/tasks, .runtime/bugs
3. Không ghi đè generated coder agents nếu workspace đã onboard
4. Xem CHANGELOG.md cho breaking changes
5. Chạy /status để kiểm tra state
```
