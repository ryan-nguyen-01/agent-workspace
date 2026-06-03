# Changelog — agent-workspace

All notable changes to this project will be documented here.

Format: `## [version] — YYYY-MM-DD`

---

## [Unreleased]

### Added

- **`/access` tool-permission posture (R-011-14)** — Command thứ 17 + `scripts/access-mode.py` để bật `fullaccess` (chạy terminal + đọc/sửa file không bị hỏi permission từng lần) hoặc `guarded` (mặc định). Chỉ đổi `.claude/settings.json permissions.defaultMode` (bypassPermissions) + `workflow-state.yaml.access_mode` — **KHÔNG** đổi workflow approval gates (R-011) hay scope/secret/destructive hooks: cái gì cần hỏi vẫn hỏi, hook vẫn chặn. `/access` là Claude-specific (exclude khỏi Codex prompts như `/aw-init`). Áp dụng cho session mới hoặc qua harness permission UI.
- **Claude Code plugin wrapper** — Đóng gói Claude tool layer (agents + skills + commands + hooks) thành plugin cài qua `/plugin` mà **không trùng lặp** content: `.claude-plugin/plugin.json` trỏ path-override thẳng vào `.claude/`, hooks chạy từ `${CLAUDE_PLUGIN_ROOT}/scripts/hooks/`. Sinh bằng `scripts/build-plugin.py` (single source of truth: `.claude/` + `.claude/settings.json`), kèm `.claude-plugin/marketplace.json` (repo = marketplace). Drift được health-check bảo vệ (`check_plugin_wrapper`). Docs: [PLUGIN.md](PLUGIN.md). Giới hạn: plugin không ship được root `CLAUDE.md`/`.agent/`/`.runtime/`/adapter đa-tool — full workflow vẫn dùng repo workspace.
- **`/aw-init` full-flow scaffold** — Plugin chỉ ship được tool layer (agents/skills/commands/hooks), KHÔNG ship được `.agent/` (state machine + rules + templates), `.runtime/` (brain + state + artifacts), hay `CLAUDE.md` precedence — nên flow điều phối không chạy đủ ở project khác chỉ với plugin. `/aw-init` (command thứ 16) + `scripts/aw-init.py` scaffold đúng các file đó từ plugin root (`${CLAUDE_PLUGIN_ROOT}`) vào project hiện tại: copy `.agent/`, seed `.runtime/` từ templates, copy `CLAUDE.md`. An toàn: refuse self-scaffold, không ghi đè khi đã tồn tại (trừ `--force`), có `--dry-run`. Đã test scaffold vào project tạm: `.agent/workflow.md` + 18 rules + `.runtime/` tree + `CLAUDE.md` đầy đủ. Counts: commands 15 → 16.
- **Codex plugin (generated)** — Codex CLI (0.132+) CÓ plugin system riêng (`.codex-plugin/plugin.json` + `.agents/plugins/marketplace.json`, `codex plugin marketplace add` → `codex plugin add`). Toàn bộ marketplace gom dưới `.codex/marketplace/` (KHÔNG để `.agents/`/`plugins/` ở repo root — tránh nhầm với `.agent/` lõi). `scripts/build-codex-plugin.py` sinh manifest + marketplace và **copy** `.claude/skills/` (231) vào `.codex/marketplace/plugins/agent-workspace/skills/` vì Codex copy plugin vào cache và KHÔNG follow symlink/path-override (khác Claude). Bản copy được **gitignore** → repo không phình; single source vẫn là `.claude/skills/`. Đã test thật bằng `codex` binary: `(installed, enabled)`, 231 SKILL.md vào cache. `--check` bắt drift manifest + skills copy.
- **Codex custom prompts (generated)** — `scripts/build-codex-prompts.py` sinh `.codex/prompts/*.md` (15 lệnh) từ `.claude/commands/` để có `/coord`, `/analyze-task`, `/dev`… như slash command trong Codex TUI sau khi `cp .codex/prompts/*.md ~/.codex/prompts/`. Bổ trợ cho Codex plugin (prompts = command entrypoints, plugin = skills). Self-contained; single source = `.claude/commands/`, `--check` bắt drift. `aw-init` bị **exclude** khỏi Codex prompts (scaffold từ `${CLAUDE_PLUGIN_ROOT}` Claude-only; Codex plugin chỉ ship skills) → Codex prompts = 15, Claude commands = 16; generator có stale-cleanup tự xóa prompt bị loại.
- **Specialist advisor wiring** — Wire 19 specialist advisor vào các workflow agent thực sự triệu hồi chúng (task-analysis set `advisory_required[]`; solution-architect/coder-leader/dev-verification/qc-handoff/coordinator invoke + resolve `handoff.must_address`). Trước đó specialists được định nghĩa nhưng không agent nào gọi (nằm chết). Thêm guard `specialist-wiring-missing` vào health-check. Sửa 6 chỗ trỏ path generated coder phẳng (`coder-*.agent.md`) sang `coders/coder-*.agent.md` cho khớp agent-factory.
- **Specialist advisor layer (4th agent class)** — Thêm 19 specialist advisors tại `.claude/agents/specialists/<category>/` (architecture, quality-security, product, data-ai, ops-devex, research-qa). Đây là domain experts chạy in-pipeline: chỉ tư vấn bằng evidence (`.runtime/tasks/<task-id>/advisories/<id>.yaml`), không viết application code, không assign coder, không mark Code Done/QC Done, không phải user entrypoint. Contract ở `R-016`; routing ở `model-routing.yaml > agent_model_map.specialist_advisors`; catalog ở `.claude/agents/specialists/README.md`. Các advisor trùng mandate (code-reviewer, business-analyst, qa-strategist, security-auditor) **augment** chứ không thay thế workflow agent tương ứng.
- **Agent folder restructure** — Tổ chức `.claude/agents/` thành `workflow/` (12), `coders/` (built-in + generated), `specialists/` (19) thay vì phẳng. Thêm catalog `.claude/agents/README.md`. `agent-factory` giờ sinh service coder vào `.claude/agents/coders/`.
- **Deterministic hook guardrails cho Claude Code** — Thêm `scripts/hooks/{scope-guard,secret-guard,destructive-guard}.py` (pure Python, no deps) wired qua `.claude/settings.json` PreToolUse, mirror logic của `.cursor/hooks/*`. Biến R-000/R-006/R-013/R-011-07 thành hard block. Runtime controls qua env: `AW_HOOK_PROFILE=minimal|standard|strict`, `AW_DISABLED_HOOKS`. Contract ở `R-017`.
- **Skill discovery layer** — Thêm `scripts/build-skill-catalog.py` phân loại 231 skills thành ~12 domain, inject `category:` frontmatter (idempotent), sinh machine index `.runtime/context/skill-taxonomy.yaml` + human catalog `.agent/docs/skill-catalog.md`. Skills vẫn phẳng cho harness discovery.
- **Drift checks mở rộng** — `scripts/architecture-health-check.py` thêm `check_specialists` (count 19, category hợp lệ, advisor-only contract, routing parity), `check_claude_hooks` (3 hooks + scripts tồn tại), `check_skill_taxonomy` (catalog freshness). Đếm agents theo cấu trúc mới (workflow + specialists + built-in coders = 33, loại trừ generated coder). Counts cập nhật: agents 33, rules 18, templates 22.
- **Rules R-016 + R-017** — Thêm `16-specialist-advisory-rules.md` và `17-hook-enforcement-rules.md` (tổng 18 workflow rules).
- **Framework-template fast path** — Thêm rule rõ ràng cho `distribution_mode: framework-template` + `instance_status: not_applied`: `NEED_ONBOARDING`, service catalog rỗng, và seed brain values không block framework maintenance. Coordinator classify `target_scope` trước khi đọc rộng Project Brain/service catalog, set `requires_onboarding: false` cho docs/rules/templates/scripts/tool adapters, và dùng lightweight fast-track cho thay đổi nhỏ không đụng approval/security/state-machine/service scope.
- **Agent speed-path cleanup** — Đồng bộ coordinator/task-analysis/coder-leader/dev-verification/QC agent definitions để chỉ đọc project brain, registry, service catalog, test policy, và task artifacts khi phase thật sự cần. Framework maintenance trivial dùng lightweight evidence thay vì full task/dev/QC artifact chain.
- **Skill loading guard** — Thêm rule không scan/read toàn bộ `.claude/skills/**` ở runtime; agents phải chọn skill từ `skill-registry.yaml` trước rồi chỉ mở `SKILL.md` đã chọn.
- **`/workspace-mode` command** — Thêm command để chuyển `distribution_mode` giữa `framework-template` và `workspace` qua Coordinator. Command deny khi đang có `active_task_id`, chỉ cập nhật field mode/state trong `.runtime/context/workflow-state.yaml`, và không tự động sửa project brain/service catalog/services.
- **Agent-native workflow policy checker** — Nâng `workflow-policy` + `/policy-check snapshot` thành checker không phụ thuộc Python/Node/script để validate workspace hoặc artifact-only snapshot như `DATA/` không có `services/`. Checker bắt drift giữa `workflow-state.yaml` và Project Brain, `DEV_DONE` thiếu `dev-verification.yaml`, `QC_DONE/PASS` còn blocked/manual retest, artifact manifest lệch file thật, và agent-registry status conflict. Có report artifact template và safe repair path qua `/workspace-mode repair`.
- **Workspace Git detach helper** — Thêm `scripts/remove-workspace-git.sh` để xóa root `.git` của `agent-workspace` khi user chỉ muốn commit/push trong các repo dưới `services/`. Script có `--dry-run`, confirmation mặc định, và không đụng vào `services/<service-name>/.git`.
- **Context economy layer** — Thêm project/service archetypes, signature-first onboarding, `project_profile`, service `profile.context_hints`, `context_economy`, và task `context_plan` để framework áp dụng cho nhiều loại project nhưng vẫn giới hạn token/read scope.
- **Model routing + activity dashboard** — Thêm `.runtime/context/model-routing.yaml` để map agent → model profile (Claude Opus cho reasoning sâu, Sonnet cho coding; Codex GPT-5.5 cho reasoning sâu, Codex coding model cho coding), `.runtime/context/agent-activity.yaml` để `/status` hiển thị agent đang làm gì, elapsed/ETA, token budget/usage/cost khi biết, `scripts/status-dashboard.py` làm terminal mirror, và rule R-015 để cấm bịa token/cost.
- **Response UI contract** — Thêm `.runtime/context/response-ui.yaml` và `.agent/templates/response-ui.template.yaml` để cấu hình layout trả lời cho Claude/Codex/Cursor/Gemini/Copilot theo mode `compact`, `concise`, `dashboard`, `models`, `dev`, `review`, `policy`; terminal dashboard hỗ trợ `--mode compact|concise|dashboard|models|json` và `--write` để tạo `.runtime/status.md/.html`. R-015 mở rộng để phân biệt markdown/text response contract với native UI của từng client.
- **9.5+ hardening helpers** — Thêm `scripts/agent-activity.py` để adapter cập nhật telemetry start/heartbeat/block/complete và `scripts/architecture-health-check.py` để CI/local bắt drift deterministic ở counts, model routing, response UI, status artifacts, Cursor hooks, và cross-tool entrypoints. Helper này không thay thế `/policy-check` agent-native.
- **Scoped model overrides** — Thêm `model-routing.yaml.model_overrides` để switch model theo provider profile, agent, phase, hoặc emergency override mà không sửa agent files/provider defaults; health checker validate override contract.

### Removed

- **`/workspace-mode` command** — Gỡ bỏ command switch/repair `distribution_mode` vì không cần thiết. `distribution_mode`/`instance_status` vẫn là field core (mọi adapter đọc) nhưng giờ chỉ được set khi onboarding hoặc qua edit `workflow-state.yaml` có user approval (R-011-13 reframed). Bỏ rule R-011-14 (chỉ về `/workspace-mode repair`), bỏ workflow.md §2.2 command-based switch (thay bằng note), và mọi reference trong command lists/docs/adapters (CLAUDE/AGENTS/COMMAND/README/SETUP/GUIDELINES/codex/gemini/copilot/cursor/workflow-reference). Command count: 16 → 15.
- **Stale-count fix kèm theo** — Sửa các snippet verify trong SETUP.md dùng glob phẳng `.claude/agents/*.agent.md` (trả 0 sau restructure) sang `find` đệ quy, và cập nhật expected counts (Agents 33, Rules 18, Templates 22, Commands 15).

### Fixed

- **Seed runtime semantics** — Sửa seed `project-brain.yaml` và `service-catalog.yaml` để mô tả đúng `services/` là workspace clone source application; control plane nằm trong `.runtime/context`.
- **Cursor runtime gates** — `check-task-analysis.sh` giờ chặn source edits khi thiếu architecture approval, thiếu standard plan artifacts, hoặc file nằm ngoài active coder write scope; `block-destructive.sh` chặn rộng hơn các lệnh destructive tương đối như `rm -rf services`, `rm -rf .git`, `git reset --hard`, và `git clean -fd`.
- **Policy reference drift** — Đồng bộ `.agent/workflow.md` và workflow reference với `/workspace-mode`, artifact snapshot policy checks, và R-011-10b..14.
- **Context-read stability** — Bổ sung rule để block planning/coding khi context confidence thấp, thiếu service/test/contract ownership, hoặc agent cần vượt context budget mà chưa ghi trigger/evidence.
- **P1/P2/P3 review fixes** — Cursor source-edit gate chuyển sang fail-closed, mở rộng nhận diện source layout phổ biến, bắt `context_plan` cho mọi applied-service task kể cả fast-track, yêu cầu lightweight `service-assignments.yaml` cho applied-service fast-track, đồng bộ `approval_gates` với R-011, chuẩn hóa archetype `docs-and-templates`, bỏ full-root service reads khỏi service-brain template, và sửa count docs.
- **Status/template drift fixes** — `/status` terminal mirror giờ hiển thị `project_brain` freshness và response UI selected mode đúng command contract; `model-routing.template.yaml` seed đủ 12 workflow agents + 2 built-in coders; docs nói rõ `services/` có thể rỗng/không cần scaffold files trong framework-template mode; health-check bắt drift giữa status contract, renderer, model-routing template, và services workspace policy.
- **Bug artifact contract** — Làm rõ `.runtime/tasks/<task-id>/bugs.yaml` chỉ là task-local index; canonical bug detail bắt buộc nằm ở `.runtime/bugs/blockers/<bug-id>.yaml` hoặc `.runtime/bugs/non-blockers/<bug-id>.yaml`. `/bug`, Bug Router, rules, templates, và health-check giờ bắt case task index có bug nhưng thiếu canonical artifact.
- **Coding error feedback loop** — Bổ sung root-cause/prevention loop để agent không lặp lỗi coding: bug/dev-verification/coder result phải ghi `root_cause`, `prevention_rule`, `regression_check`, `recurrence_key`; Memory Update promote lỗi bền vững sang `feedback/anti-patterns.md` hoặc fix pattern sang `feedback/patterns.md`; Task Analysis/Coder Leader đưa feedback liên quan vào context pack; health-check bắt drift contract này.
- **Styled status HTML** — `scripts/status-dashboard.py --write` giờ render `.runtime/status.html` theo dạng GitHub README card với tab bar, hero banner, metric cards, workflow/model/response sections, và raw status audit block; health-check bắt drift nếu HTML artifact không còn style marker.

---

## [1.7.0] — 2026-05-18

### Added

- **`inputs/` folder convention** — Folder root-level cho user-provided reference docs (PRD, HLD, ADR, OpenAPI specs, domain glossary, runbooks). Có 6 subdirs phân loại (`product/`, `architecture/`, `api/`, `domain/`, `runbooks/`, `misc/`) và `inputs/README.md` hướng dẫn dùng. Onboarding agent giờ scan 2 nguồn: `inputs/` (user knowledge) + `services/<repo>/` (source code). Mỗi memory entry trích từ `inputs/` cite `source: inputs/<path>` để audit.
- **Incremental refresh cho inputs/** — Thêm `/onboard --refresh inputs` và `/sync-memory --scan --inputs`. `/sync-memory --files inputs/...` không còn yêu cầu `--services`. Diff strategy: skip files khi `mtime <= indexed_mtime` + content hash match → tránh re-scan lãng phí. Khi inputs file bị xóa, onboarding tự remove memory entries cite path đó. R-002-13..15 + bảng "picking the right command" trong `/onboard` và `/sync-memory` docs.
- **Onboarding scan inputs/** — R-002-09..12: bắt buộc scan inputs/, viết `.runtime/context/inputs-index.yaml` (path, category, summary, mtime, confidence), conflict resolution rule (code wins technical, inputs/ wins intent), read-only ở inputs/.
- **`.runtime/context/inputs-index.yaml`** — Index mới do onboarding sinh ra. Agents đọc index này trước khi mở file inputs/.
- **`project-brain.inputs` + `project-brain.conflicts`** — Schema mới: tracking root inputs/, last_scanned_at, file_count, và list conflicts giữa inputs/ và source code.
- **AGENTS.md** — File entrypoint cho AI coding agents không phải Claude (Codex, Cursor, Aider…), tóm tắt 12 workflow agents, slash commands, folder semantics, conflict rule, và link sang `.agent/workflow.md`.
- **Solution Architect workflow agent** — Thêm `solution-architect.agent.md` làm architecture review gate tùy chọn sau task-analysis và trước coder-leader cho cross-service/API/data/event/security/infra risk. Thêm `ARCHITECTURE_REVIEWING` state, `architecture-review.template.yaml`, và `task-analysis.yaml.architecture_review`.
- **Cross-cutting coders** — Thêm `coder-infra` (Terraform/IaC, Kubernetes, Docker, CI/CD scope) và `coder-database` (schema/migrations, queries, indexes scope), kèm registration trong `.runtime/context/agent-registry.yaml`.
- **Distribution readiness** — Thêm template-mode metadata trong project brain/workflow state, `agent-taxonomy.md`, schema checks trong agent-facing contracts, và chuẩn hóa workspace semantics.
- **Operational hardening** — Thêm `QUICKSTART.md`, task artifact contract hardening, và R-006 rules enforce built-in coder usage.
- **Template contract sync** — Đồng bộ templates với runtime contract: distribution metadata, built-in coder registry seed, required workflow skills, `fast_track_acknowledged`, và QC `verdict`.
- **Schema hardening** — Enforce `fast_track_acknowledged` và QC `verdict`, validate active built-in coder skill references, sync built-in coder template scopes với runtime registry, bump `project-brain.template.yaml` lên version 2, và sửa R-006 applies-to wording.
- **Docs entrypoint + skill hardening** — Chuẩn hóa documentation entrypoint trong README/SETUP/QUICKSTART và validate `skill-registry.yaml` references against installed skills/unavailable list.
- **Workspace-first setup** — Chuẩn hóa lại setup theo mô hình clone `agent-workspace` làm workspace điều phối, clone service repos vào `services/`, không copy `.claude/` sang từng project.
- **Skill maintenance command** — Thêm `/skills` để status/audit/update/refresh-registry cho installed skills, `skills-lock.json`, và `skill-registry.yaml` với approval gate riêng.
- **COMMAND.md** — Thêm root command index làm entrypoint canonical cho 16 slash commands, trỏ xuống `.claude/commands/*.md` cho contract chi tiết.
- **Drift detection**: Coordinator đọc `project-brain.yaml.freshness` ở session startup; banner state thêm `Brain: fresh|stale|missing`.
- **Fast-track lane** (workflow.md §6.2): pipeline rút gọn cho 7 loại task nhỏ (typo, comment, format, rename-local, docs-only, dependency-version-bump, config-value-tweak). Bỏ qua user-approval gate R-011-10 và `implementation-plan.yaml` / `service-assignments.yaml`. Vẫn giữ scope, secrets, dev-verification, và (mặc định) QC.
- **Skill selection algorithm** (R-014): 5-bước deterministic từ service-brain → project-brain → task-tags → impacted-services. Skill budget: 3 (workflow agent) / 5 (service coder). Có worked example chọn 5 skills từ 215 ứng viên.
- **Boundary matrix Coder-Leader vs Dev-Verification**: 16-row ownership table + 7 worked examples + order-of-operations. Phân biệt rõ "qualitative review" (Leader) vs "binary gate" (Verification).
- **Task update template** — Thêm `task-update.template.yaml` để chuẩn hóa append-only update log trong `.runtime/tasks/<task_id>/task-updates.yaml`.
- **QC handoff template rename** — Chuẩn hóa template Dev→QC thành `qc-handoff.template.md`; artifact canonical là `.runtime/tasks/<task_id>/qc-handoff.md`.
- **Tool-specific AI entrypoints** — Thêm `.codex/AGENTS.md`, `.cursor/rules/agent-workspace.mdc`, và `.gemini/GEMINI.md` để Codex, Cursor, Gemini cùng tuân thủ `/coord`, task ID, task folder, scoped coders, và anti-guessing policy.
- **`.agent/` folder cho framework spec tool-agnostic** — Move `rules/`, `templates/`, `docs/`, `workflow.md`, `README.md`, `changelog.md` từ `.claude/` ra `.agent/`. Lý do: `.claude/` là convention Claude Code, đặt cả framework spec ở đó làm Codex/Cursor/Aider phải đọc path Claude-specific. Sau reorg: `.agent/` chứa spec đọc bởi mọi AI tool, `.claude/` chỉ giữ Claude Code runtime (`agents/`, `skills/`, `commands/`, `context/`, `tasks/`, `bugs/`, `settings.json`). Bulk-replace 35 file references, không có symlink/shim (clean break). `agents/`, `skills/`, `commands/` vẫn ở `.claude/` để Claude Code auto-discovery tiếp tục hoạt động (`/coord`, Agent tool, skill loading).
- **Tool-native value-add (Codex config + Cursor hooks + rules split)** — Lấy cảm hứng từ project lớn trên GitHub:
  - `.codex/config.toml` — Codex CLI project-level config, schema **verified** against `https://developers.openai.com/codex/config-reference`. Sử dụng real keys: `project_doc_fallback_filenames`, `project_root_markers`, `project_doc_max_bytes`, `sandbox_mode = "workspace-write"`, `[sandbox_workspace_write]` với `writable_roots = [".runtime", "inputs"]` + `network_access = false`, `approval_policy = "on-request"`, `[history]`, `web_search = "disabled"`, commented `[mcp_servers.*]` template. Model field để comment cho user tự fill. Project-level config chỉ load khi project được trust trong `~/.codex/config.toml`.
  - `.cursor/hooks.json` + `.cursor/hooks/*.sh` (4 hooks + 1 shared `_lib.sh`), schema **verified** against `https://cursor.com/docs/agent/hooks`. Cấu trúc đúng: `{version: 1, hooks: {<event>: [{command, type, timeout, failClosed}]}}`. Real event names: `preToolUse` (2 hooks: check-task-analysis + warn-engine-edit), `beforeShellExecution` (block-destructive với `failClosed: true`), `afterFileEdit` (flag-drift). Hook scripts đọc JSON từ **stdin** (không dùng env vars như `$CURSOR_FILE` — đó là fabrication trước đó), parse qua `_lib.sh` helper: ưu tiên `jq` (robust nested + escaped JSON), fallback grep+sed nếu không có jq. `init_stdin` được gọi 1 lần ở top-level mỗi script để cache `_HOOK_STDIN` qua subshells (fix bug stdin-drained-on-first-read). Exit code 2 = block (verified), exit 0 = allow, exit codes khác = fail-open. Sed dùng `[[:space:]]` thay `\s` cho BSD/GNU compat. Smoke-tested 10/10 cases pass (cả jq-present và jq-absent paths).
- **SETUP.md per-tool setup section** — Thêm `### 5. Per-tool setup (optional)` document cụ thể từng AI tool: Claude Code (auto-discover, no setup), Codex CLI (cảnh báo `.codex/config.toml` bị ignore mặc định, cần `[projects."<abs-path>"] trust_level = "trusted"` trong `~/.codex/config.toml` để activate), Cursor (rules + hooks, `jq` optional), Gemini, Copilot.
- **AGENTS.md per-tool enforcement boundary table** — Bảng so sánh 5 tools với cột `Auto-discovers`, `Lifecycle hooks`, `Enforcement path`. Khẳng định rõ Cursor là tool DUY NHẤT có lifecycle hooks; các tool khác enforce qua AGENTS.md / CLAUDE.md / `.codex/AGENTS.md` / `.gemini/GEMINI.md`.
  - Split `.cursor/rules/` thành 4 file glob-targeted: `agent-workspace.mdc` (alwaysApply core), `agent-workspace-source.mdc` (globs: services/**, src/**, …), `agent-workspace-runtime.mdc` (globs: .runtime/**), `agent-workspace-spec.mdc` (globs: .agent/**, .claude/agents/**, …). Cursor chỉ load đúng rule cho đúng file type, giảm token cost.
  - Không mirror `.claude/agents/` vào `.codex/agents/` hay `.claude/skills/` vào `.cursor/skills/` — giữ DRY (14 agents × 4 tools = 56 file sync nightmare; 231 skills × 4 = 924 file). Tool khác đọc qua entrypoint `.codex/AGENTS.md`, `.cursor/rules/`, `.gemini/GEMINI.md` trỏ về `.agent/` và `.runtime/`.
- **`.runtime/` folder cho runtime data tool-agnostic** — Move `context/`, `tasks/`, `bugs/` từ `.claude/` ra `.runtime/`. Đây là dữ liệu runtime (project-brain, workflow-state, service-catalog, agent-registry, task artifacts, bug reports) — không phải Claude convention. Sau reorg: `.runtime/` đọc bởi mọi AI tool (Claude/Codex/Cursor/Gemini), `.claude/` chỉ còn `agents/`, `skills/`, `commands/`, `settings.json` (Claude conventions thật sự). Bulk-replace 53 file references. Update tool entrypoints (`.codex/AGENTS.md`, `.cursor/rules/agent-workspace.mdc`, `.gemini/GEMINI.md`, `.github/copilot-instructions.md`) trỏ path mới. Xóa `.claude/progress.md` stale (duplicate `workflow-state.yaml`). Layout cuối: `.agent/` (spec) + `.runtime/` (runtime) + `.claude/` (Claude engine) + `.codex/`/`.cursor/`/`.gemini/`/`.github/` (tool entrypoints) + `inputs/` + `services/`.

### Changed

- **CLAUDE.md (project)**: thêm section "Precedence: project CLAUDE.md ghi đè global CLAUDE.md" — map legacy agent names (agent-orchestrator, business-analyst…) về 12 workflow agents thực tế. `solution-architect` giờ là workflow agent hợp lệ nhưng vẫn phải được route qua Coordinator sau Task Analysis. Disable aliases `sa:/ba:/qa:/pm:/sec:/sre:/dev:` trong scope project.
- **Policy gates tightened from real DATA evidence**: `DEV_DONE` giờ bắt buộc có `dev-verification.yaml` verdict/result `DEV_DONE`; coder/coder-leader không được tự set Code Done. `QC_DONE/PASS` không hợp lệ nếu còn blocked/pending/not_run/failed test case hoặc notes vẫn yêu cầu manual/retest evidence. `/policy-check` và `/workspace-mode repair` được nối với checker mới.
- **Rules mới**:
  - `R-001-11..14` — Drift detection bookkeeping cho Coordinator/Onboarding/Memory-Update.
  - `R-004-09..11` — Fast-track exception và architecture-review trigger fields cho task-analysis.
  - `R-005-11..12` — Coder Leader phải đọc `architecture-review.yaml` khi task-analysis yêu cầu và copy constraints vào plan/assignments.
  - `R-011-10b` — Exception R-011-10 cho fast-track.
  - `R-011-11` — User có thể disable fast-track bằng `test-policy.fast_track_enabled: false`.
  - `R-014-11..14` — Skill budget, deterministic selection, eligibility check, conflict resolution.
- **Templates**: thêm `fast_track`, `fast_track_reason`, và `architecture_review` vào `task-analysis.template.yaml`; thêm `architecture-review.template.yaml`; thêm `last_indexed_at`, `stale_after_days`, `tracked_paths`, `last_drift_check_at`, `last_drift_check_result` vào `freshness:` block của `project-brain.template.yaml`.
- **Task ID contract**: chuẩn hóa task folder theo `TASK-YYYYMMDD-NNN-slug`; Coordinator cấp ID trước Task Analysis, tạo `task.yaml`, và append `task-updates.yaml` cho mỗi state/artifact update.
- **Coder output contract**: bỏ per-service `coder-handoff-<service>.yaml`; Coder Leader gom output của service coders vào `coder-results.yaml.coder_outputs[]`.
- **Coordinator startup**: thêm Step 6 (drift check) và "Drift handling rules" — block routing vào IN_DEV khi brain stale trừ khi user accept.
- **Counts**: sync count thực tế trong README/SETUP/GUIDELINES/CLAUDE — **12 workflow agents**, 231 skills (12 workflow + 219 technical), 20 templates, 16 workflow rules, 16 commands.

### Removed

- **Placeholder folders ở root**: xóa `memory/` (rỗng) và `state/` (chỉ có README), vốn là vết tích migration v1.6.0 chưa hoàn tất. Source of truth duy nhất giờ là `.runtime/context/` (project-brain, workflow-state, service-catalog, agent-registry, test-policy, services/, feedback/). `services/` ở root vẫn giữ — là workspace gitignored để user clone application repos vào.
- **Duplicate handover layer**: xóa folder handoff riêng; Dev→QC handoff chỉ còn một artifact canonical trong `.runtime/tasks/<task_id>/qc-handoff.md`.
- **Runtime example tasks**: xóa các sample folders dưới `.runtime/tasks/` để runtime task folder không bị lẫn với task thật.
- **Old handoff templates**: xóa `handover.template.md` và `coder-handoff.template.yaml`.

### Fixed

- Doc drift count trong `README.md`, `SETUP.md`, `GUIDELINES.md`, `CLAUDE.md`: chuẩn hóa về 231 skills, 20 templates, 16 workflow rules, và 16 slash commands.
- **Folder semantics**: sửa `.agent/workflow.md §1.1` không còn liệt kê `memory/` và `state/` như folder root. `SETUP.md` backup/restore script và bảng "không ghi đè khi upgrade" trỏ về `.runtime/context/`. `project-brain.yaml.memory` schema đổi `root: "memory"` → `root: ".runtime/context"`, bỏ `state_root`, thêm `state_file` trỏ thẳng `.runtime/context/workflow-state.yaml`.

---

## [1.6.0] — 2026-05-17

### Changed

- **Runtime structure**: tách `.runtime/context/` thành 3 vùng rõ nghĩa:
  - `memory/` — agent brain, project/service memory, feedback, reusable knowledge
  - `services/` — service coding control plane, source paths, coder scopes, test policy, skill registry
  - `state/` — workflow state và approval gates
  - `tasks/`, `bugs/`, `handover/` — project artifacts cùng cấp `.claude`, không nằm trong agent engine
- **Memory read policy**: thêm `memory/index.yaml` để agent đọc index trước, sau đó chỉ mở memory liên quan đến task/service.
- **Commands**: mở rộng `/onboard` và `/sync-memory` với flow `/onboard --refresh <service>` và `/sync-memory --refresh-index`.
- **Docs and contracts**: cập nhật agents, rules, templates, skills, setup docs, folder guide, and validator script theo cấu trúc memory/services/state.

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
- **Example**: `tasks/TASK-example-full/` — Ví dụ workflow đầy đủ JWT Authentication (10 artifacts):
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
- **Docs**: `agent-catalog.md` — Danh mục workflow agents với vai trò và triggers
- **Docs**: `skill-guide.md` — Hướng dẫn skill system (12 workflow + 219 technical skills)
- **Docs**: `customization-guide.md` — Hướng dẫn mở rộng framework (thêm agents, skills, rules)
- **Template**: `tasks/TASK-example/` — Demo task end-to-end cho workflow reference
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

- `skill-role-update-agent-brief` — quy ước `memory/handoffs/active.yaml` cho handoff giữa các agent (orchestrator + analyst + inject-context)

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
- Feedback loop system (memory/feedback/)
- Blueprints system (7 blueprints in skill-role-blueprints)
- Context system (memory/ with delta sync)
- Generated agents via agent-builder (naming convention + skill budget)
