# Changelog — agent-platform

All notable changes to this project will be documented here.

Format: `## [version] — YYYY-MM-DD`

---

## [1.5.2] — 2026-04-17

### Added

- **Workflow**: Task Analysis → User Approval Gate:
  - `R-004 task-analysis-rules` — Thêm R-004-08: User phải review và approve task-analysis.yaml trước khi chuyển Coder Leader
  - `R-011 approval-gates` — Thêm R-011-10: Approval gate từ Task Analysis sang Coder Leader
  - `R-012 artifact-contracts` — "Before coding" yêu cầu user approval
  - `skill-task-analysis/SKILL.md` — Thêm User Review Gate section (5-step approval flow)
- **Workflow**: QC Delivery Report cho User:
  - `R-008 qc-rules` — Thêm R-008-09: QC Runner phải viết qc-delivery-report.md sau QC_DONE
  - `R-012 artifact-contracts` — Thêm qc-delivery-report.md vào task folder + state artifacts
  - `skill-qc-runner/SKILL.md` — Thêm QC Delivery Report section + step 7 trong Flow
  - `qc-delivery-report.template.md` — Template mới (tóm tắt, kết quả, files, verify steps, đề xuất)
- **Example**: `TASK-example-full/qc-delivery-report.md` — Ví dụ delivery report cho JWT Auth task
- **Example**: `TASK-example-full/workflow-narrative.md` — Cập nhật: thêm User Approval Gate + QC Delivery Report + updated diagram

### Documentation

- **Docs sync**: Cập nhật 5 text docs và 4 SVG diagrams cho v1.5.2:
  - `workflow-reference.md` — Thêm User Approval Gate + QC Delivery Report vào flow
  - `architecture-guide.md` — Thêm approval gate + delivery report vào architecture flow
  - `visual-flow.md` — Cập nhật mermaid diagrams với 2 bước mới
  - `agent-catalog.md` — Cập nhật Task Analysis + QC Runner agent descriptions
  - `folder-guide.md` — Thêm qc-delivery-report.md vào task folder listing
  - `01-system-overview.svg` — Thêm User Approval gate (Phase 3) + QC Delivery Report (Phase 7)
  - `03-task-execution-flow.svg` — Thêm User Approval gate giữa Normalized và Coder Leader
  - `04-qc-bug-routing.svg` — Thêm QC Delivery Report giữa Task Done và Memory Update
  - `05-state-machine.svg` — Thêm annotation labels: "user approval" + "delivery report"

---

## [1.5.1] — 2026-04-17

### Added

- **Docs**: `README.md` — Ghi chú ngôn ngữ (Vietnamese) cho contributors quốc tế
- **Docs**: `SETUP.md` — FAQ & Troubleshooting section (6 topics: brain stale, onboard loop, skill conflict, coder scope, large project, CLAUDE.local)
- **Docs**: `customization-guide.md` — Step 4 "Cập nhật registries" trong quy trình thêm custom skill
- **Config**: `skill-registry.yaml` — `docs_reference` field + canonical source comment
- **Config**: `external-skills.md` — Section "Relationship to skill-registry.yaml"
- **Example**: `.claude/tasks/TASK-example-full/` — Ví dụ workflow đầy đủ JWT Authentication (10 artifacts):
  - `task-input.md` — Mô tả scenario multi-service JWT auth
  - `task-analysis.yaml` — 7 ACs, 3 services, 4 critical checks, risks, reuse analysis
  - `implementation-plan.yaml` — 8 steps, integration points, contracts
  - `service-assignments.yaml` — 3 coders scoped, 3-phase execution
  - `coder-handoff-database.yaml` — Handoff: 1 step, 2 files, UUID PK decision
  - `coder-handoff-api.yaml` — Handoff: 4 steps, 7 files, bcrypt/JWT decisions, 8 curl tests
  - `coder-handoff-frontend.yaml` — Handoff: 3 steps, 5 files, memory token strategy, 9 browser tests
  - `coder-results.yaml` — All done, files changed, reuse reports
  - `dev-verification.yaml` — Score 92%, critical checks pass
  - `qc-handoff.md` — Handoff doc với test commands
  - `qc-test-results.yaml` — 13 TCs, 0 blockers, verdict PASS
  - `memory-updates.yaml` — Learnings: conventions, anti-patterns, bug patterns
  - `workflow-narrative.md` — Mô tả luồng hoạt động đầy đủ 8 phases (bao gồm coder→leader handoff)
- **Template**: `coder-handoff.template.yaml` — Template cho coder-to-leader handoff artifact
- **Workflow**: Coder→Leader handoff obligation:
  - `skill-service-coder/SKILL.md` — Thêm Coder-to-Leader Handoff section (bắt buộc viết coder-handoff-<service>.yaml)
  - `skill-coder-leader/SKILL.md` — Thêm Collecting Coder Handoffs section (review + cross-check + consolidate)
  - `R-012 artifact-contracts` — Thêm `coder-handoff-<service>.yaml` vào required artifacts

---

## [1.5.0] — 2026-04-17

### Added

- **Docs**: `architecture-guide.md` — Kiến trúc tổng quan hệ thống (agents, skills, rules, context)
- **Docs**: `workflow-reference.md` — Tham chiếu nhanh workflow phases và state machine
- **Docs**: `agent-catalog.md` — Danh mục 11 workflow agents với vai trò và triggers
- **Docs**: `skill-guide.md` — Hướng dẫn skill system (12 workflow + 215 technical skills)
- **Docs**: `customization-guide.md` — Hướng dẫn mở rộng framework (thêm agents, skills, rules)
- **Script**: `validate-install.sh` — Script kiểm tra tính toàn vẹn framework sau cài đặt
- **Template**: `.claude/tasks/TASK-example/` — Demo task end-to-end cho workflow reference
- **Config**: `.claude/settings.json` — Default framework configuration

### Changed

- `CLAUDE.local.md` — Chuyển từ copy nguyên CLAUDE.md sang template override cho project khách
- `SETUP.md` — Bổ sung section upgrade, git subtree, post-install validation
- `CHANGELOG.md` — Cập nhật v1.5.0

### Fixed

- SVG diagrams: sửa viewBox, font consistency, dark theme (#111827)
- Cross-references giữa docs, README, và diagrams đồng bộ 100%

---

## [1.4.0] — 2026-03-31

### Removed (tối giản repo)

- Không còn ship trong tree: `hooks/`, `.githooks/`, thư mục `blueprints/` ở root, skill `skill-role-update-agent-brief` (handoffs).

### Changed

- Tài liệu và SKILL: `SETUP.md`, `GUIDELINES.md`, `README.md`, `docs/team-setup-agent-context.md`, `CLAUDE.md`, `agent-orchestrator`, `agent-analyst`, `agent-context-keeper`, `agent-onboarding`, `skill-role-inject-context`, `skill-role-blueprints`, `.claude/agents/README.md` — đồng bộ mô tả với bản **không hooks / không handoff file / blueprint chỉ inline trong skill**.

> Các mục dưới đây trong changelog là lịch sử; một số tính năng đã gỡ khỏi repo theo hướng tối giản 1.4.0.

---

## [1.3.1] — 2026-03-31

### Added

- `skill-role-update-agent-brief` — quy ước `.claude/context/handoffs/active.yaml` cho handoff giữa các agent (orchestrator + analyst + inject-context)

### Changed

- `agent-orchestrator`, `agent-analyst`, `agent-context-keeper`: equip / tham chiếu skill mới
- `skill-role-inject-context`: merge handoff vào bước inject
- `GUIDELINES.md`: mô tả thư mục `handoffs/`

---

## [1.3.0] — 2026-03-31

### Added

- `GUIDELINES.md`: “Token & context policy (context-first)”
- `agent-context-keeper`: Phase 0 — xử lý `dirty-flags` chỉ có `pending_trigger` từ git hooks → map file → delta sync → clear

### Changed

- `agent-orchestrator`: context-first read order, progressive escalation (pass 1–3), inject budget chuẩn hoá 400/500/600 tokens; Bước 1 đồng bộ với policy dirty/hook
- `CLAUDE.md`: bổ sung nguyên tắc context-first, progressive disclosure, dirty-flags → context-keeper

---

## [1.2.0] — 2026-03-31

### Added

- `blueprints/` directory with 7 concrete blueprint files:
  - BLUEPRINT-001 CRUD Module
  - BLUEPRINT-002 Authentication Flow
  - BLUEPRINT-003 File Upload
  - BLUEPRINT-004 Payment Integration
  - BLUEPRINT-005 Real-time Features
  - BLUEPRINT-006 Search & Filter
  - BLUEPRINT-007 Caching Strategy

### Changed

- `skill-role-blueprints`: documented blueprint files as source of truth (repo `blueprints/`)

---

## [1.1.0] — 2026-03-31

### Added

- `hooks/` directory with `post-commit`, `post-merge`, and `install-hooks.sh` scripts
- English keyword routing in `CLAUDE.md` for all 15 routing rules
- Decision rules for `agent-pm` (sprint re-planning, release delays, escalation triggers)
- Decision rules for `agent-data` (OLTP vs OLAP, pipeline design, incident response)
- Validation checklist for `agent-context-keeper` (structural, content, performance checks)

### Changed

- `agent-sa`: Restructured skills into Core + API + Conditional Architecture tiers (was flat list of 28)
- `agent-builder`: Removed duplicate Skills Catalog section (was 120 redundant lines)
- `agent-reporter`: Clarified execution model (not a background daemon)
- `agent-context-keeper`: Clarified execution model (hook-triggered, not autonomous)

### Fixed

- `agent-pm` lacked decision rules for when to re-plan, delay, or escalate
- `agent-data` lacked decision rules for pipeline design choices and incidents
- `agent-builder` SKILL.md was >800 lines with duplicate content

---

## [1.0.0] — 2026-02-01

### Added

- Initial release: 20 core agents, 106 skills
- Agent definitions: orchestrator, onboarding, builder, sa, ba, pm, analyst, designer, coder-\*, reviewer, tester, security, documenter, migrator, qa, perf, sre, data, context-keeper, reporter
- Skill library: 106 skills across languages, frameworks, databases, auth, testing, UI, DevOps, architecture, observability, tooling
- CLAUDE.md routing system (Vietnamese)
- SETUP.md with macOS and Windows installation guides
- Feedback loop system (.claude/context/feedback/)
- Blueprints system (7 blueprints in skill-role-blueprints)
- Context system (.claude/context/ with delta sync)
- Generated agents via agent-builder (naming convention + skill budget)
