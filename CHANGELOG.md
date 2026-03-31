# Changelog — agent-platform

All notable changes to this project will be documented here.

Format: `## [version] — YYYY-MM-DD`

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
- `skill-role-update-agent-brief` — quy ước `.agent/context/handoffs/active.yaml` cho handoff giữa các agent (orchestrator + analyst + inject-context)

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
- Agent definitions: orchestrator, onboarding, builder, sa, ba, pm, analyst, designer, coder-*, reviewer, tester, security, documenter, migrator, qa, perf, sre, data, context-keeper, reporter
- Skill library: 106 skills across languages, frameworks, databases, auth, testing, UI, DevOps, architecture, observability, tooling
- CLAUDE.md routing system (Vietnamese)
- SETUP.md with macOS and Windows installation guides
- Feedback loop system (.agent/context/feedback/)
- Blueprints system (7 blueprints in skill-role-blueprints)
- Context system (.agent/ with delta sync)
- Generated agents via agent-builder (naming convention + skill budget)
