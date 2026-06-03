# Specialist Advisors

19 chuyên gia domain hoạt động ở chế độ **advisor trong pipeline**: được workflow agent triệu hồi,
sản xuất artifact tư vấn có evidence tại `.runtime/tasks/<task-id>/advisories/<id>.yaml`, **không**
viết application code, **không** assign coder, **không** mark Code Done/QC Done.

Hợp đồng & giới hạn: [`.agent/rules/16-specialist-advisory-rules.md`](../../../.agent/rules/16-specialist-advisory-rules.md).
Template: [`.agent/templates/agent-specialist.template.md`](../../../.agent/templates/agent-specialist.template.md).

## Quick-selection

| Khi cần tư vấn về… | Specialist | Category | Model | Triệu hồi bởi |
|--------------------|-----------|----------|-------|---------------|
| Thiết kế REST/GraphQL API, versioning, contract | `api-designer` | architecture | sonnet | task-analysis, solution-architect |
| Schema, migration, chọn SQL/NoSQL, indexing | `database-architect` | architecture | opus | task-analysis, solution-architect |
| Topology cloud, IAM, networking, DR, WAF | `cloud-architect` | architecture | opus | solution-architect |
| Event contract, messaging, saga, ordering | `event-architect` | architecture | opus | solution-architect |
| Wireframe, component, design tokens, layout | `ui-ux-designer` | architecture | sonnet | task-analysis, coder-leader |
| OWASP, authn/authz, secrets, injection, threat model | `security-auditor` | quality-security | opus | dev-verification, coder-leader |
| Latency, N+1, caching, bundle size, load test | `performance-engineer` | quality-security | opus | dev-verification, coder-leader |
| WCAG, ARIA, keyboard nav, contrast | `accessibility-auditor` | quality-security | sonnet | dev-verification, coder-leader |
| Deep code review (augments coder-leader) | `code-reviewer` | quality-security | opus | coder-leader, dev-verification |
| Phân tích vấn đề, thị trường, MVP, validate ý tưởng | `discovery-analyst` | product | opus | coordinator (pre-pipeline) |
| User stories, acceptance criteria (augments task-analysis) | `business-analyst` | product | sonnet | coordinator, task-analysis |
| Roadmap, prioritization, release scoping | `product-strategist` | product | opus | coordinator |
| Data pipeline, ETL, streaming, analytics schema | `data-engineer` | data-ai | sonnet | task-analysis, solution-architect |
| Kiến trúc AI/LLM, RAG, eval, model selection | `ml-ai-architect` | data-ai | opus | solution-architect, task-analysis |
| Monitoring, SLO, tracing, incident runbook | `sre-observability` | ops-devex | sonnet | dev-verification, coder-leader |
| Docs, API docs, README, changelog, ADR | `technical-writer` | ops-devex | haiku | memory-update, coder-leader |
| Migration/upgrade/refactor planning, tech-debt | `migration-strategist` | ops-devex | opus | task-analysis, coder-leader |
| Đánh giá công nghệ, so sánh thư viện, spike | `tech-researcher` | research-qa | opus | task-analysis, solution-architect |
| Test strategy, test-case design, coverage (advises qc) | `qa-strategist` | research-qa | sonnet | task-analysis, qc-handoff |

## Cách kích hoạt

1. `task-analysis` gắn cờ trong `task-analysis.yaml`:
   ```yaml
   advisory_required: [security-auditor, api-designer]
   ```
2. Hoặc workflow agent (coordinator/solution-architect/coder-leader/dev-verification/qc-handoff) phát hiện rủi ro thuộc domain và triệu hồi.
3. Specialist ghi advisory → workflow agent downstream đọc và xử lý `handoff.must_address`.

Advisory **không tạo state machine mới** — chạy như sub-step trong các state hiện có (ANALYZED, ARCHITECTURE_REVIEWING, DEV_VERIFYING, QC). Xem [`.agent/workflow.md`](../../../.agent/workflow.md).
