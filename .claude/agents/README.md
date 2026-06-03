# Agent Catalog

`agent-workspace` có **4 lớp agent**. Giữ các thuật ngữ này tách bạch trong docs, registry, handoff.
Xem chi tiết phân loại tại [`.agent/docs/agent-taxonomy.md`](../../.agent/docs/agent-taxonomy.md).

```
.claude/agents/
├── workflow/      12 control-plane agents (điều phối, gate, state machine)
├── coders/        built-in + generated service coders (viết code, scoped)
└── specialists/   19 specialist advisors (tư vấn trong pipeline, KHÔNG code)
```

| Lớp | Số lượng | Vai trò | Quyết định gate? | Viết app code? |
|-----|----------|---------|------------------|----------------|
| Workflow agents | 12 | Điều phối pipeline, approval gates, state transitions, verification, QC, memory | ✅ | ❌ |
| Built-in coders | 2 | `coder-infra`, `coder-database` — cross-cutting code | ❌ | ✅ (scoped) |
| Generated coders | n | Service-specific, do `agent-factory` sinh sau onboarding | ❌ | ✅ (scoped) |
| Specialist advisors | 19 | Chuyên gia domain, tư vấn có evidence | ❌ (chỉ recommend) | ❌ |

> **Nguyên tắc:** Mọi việc đi qua `coordinator` (single entrypoint). Specialist advisors **không** là entrypoint độc lập — workflow agent triệu hồi chúng trong pipeline.

---

## 1. Workflow agents → [`workflow/`](workflow/)

| Khi cần… | Dùng agent | Model |
|----------|-----------|-------|
| Route/điều phối mọi task, enforce gates | `coordinator` | fast_router |
| Scan project, tạo project brain | `onboarding` | deep_reasoning |
| Tạo service coder agents | `agent-factory` | coding_planner |
| Chuẩn hoá task thành spec + context_plan | `task-analysis` | deep_reasoning |
| Review kiến trúc/contract/rủi ro | `solution-architect` | deep_reasoning |
| Lập plan + assign coders + review code | `coder-leader` | coding_planner |
| Đánh giá Code Done (≥80% + critical checks) | `dev-verification` | verification |
| Tạo Dev→QC handoff | `qc-handoff` | fast_router |
| Chạy QC tests, stop on blocker | `qc-runner` | verification |
| Phân loại bug blocker/non-blocker | `bug-router` | deep_reasoning |
| Lưu learnings durable | `memory-update` | memory_light |
| Validate transitions/gates/artifacts | `workflow-policy` | deep_reasoning |

## 2. Coders → [`coders/`](coders/)

| Khi cần… | Dùng agent | Origin |
|----------|-----------|--------|
| Terraform/IaC, K8s, Docker, CI/CD | `coder-infra` | built-in |
| Schema, migrations, queries, indexes | `coder-database` | built-in |
| Code 1 service cụ thể | `coder-<service>` | generated (agent-factory) |

## 3. Specialist advisors → [`specialists/`](specialists/)

Xem bảng quick-selection đầy đủ tại [`specialists/README.md`](specialists/README.md). Tóm tắt theo category:

- **architecture/** — api-designer, database-architect, cloud-architect, event-architect, ui-ux-designer
- **quality-security/** — security-auditor, performance-engineer, accessibility-auditor, code-reviewer
- **product/** — discovery-analyst, business-analyst, product-strategist
- **data-ai/** — data-engineer, ml-ai-architect
- **ops-devex/** — sre-observability, technical-writer, migration-strategist
- **research-qa/** — tech-researcher, qa-strategist

---

## Đặt tên & vị trí file

```
Workflow agent:      .claude/agents/workflow/<name>.agent.md
Built-in coder:      .claude/agents/coders/<name>.agent.md
Generated coder:     .claude/agents/coders/coder-<service-slug>.agent.md
Specialist advisor:  .claude/agents/specialists/<category>/<name>.agent.md
```

Model routing cho mọi lớp: [`.runtime/context/model-routing.yaml`](../../.runtime/context/model-routing.yaml).
