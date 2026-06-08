# R-019: Autonomous Delivery (Autopilot)

## Applies to

Coordinator, Coder Leader, Service Coders, Dev Verification, QC Runner, Bug Router, Workflow Policy.

## Purpose

Autopilot lets the coordinator run the full pipeline to a finished product
(`analysis → plan → dev → verify → QC → fix-loop → done`) without stopping at every soft gate,
while keeping the non-waivable safety stops. It is started with `/ship` (or `/coord` + an explicit
autonomous grant) and is a property of the active run, not a permanent project setting.

## Blueprint gate (direction approval — the one upfront human decision)

```text
R-019-0a: For idea-level or greenfield input, autopilot MUST NOT start building until the user
  approves a Product Blueprint. First run discovery + architecture proposal (discovery-analyst,
  product-strategist, solution-architect advisories feed it) and write
  .maestro/work/tasks/<task-id>/product-blueprint.yaml from
  .maestro/engine/templates/product-blueprint.template.yaml. It MUST cover:
    - problem, goal, target users
    - scope_target: MVP vs production (and what that means for this build)
    - architecture_style: monolith | modular-monolith | microservices — a clear recommendation with
      rationale and the main alternative
    - tech_stack: language, frontend/backend frameworks, database, key libraries — each with rationale
    - features → which become the acceptance criteria for this iteration
    - non-functional targets right-sized to scope_target
    - ui_ux design direction when the product has a UI (see R-019-0a-ui)
    - assumptions, risks/tradeoffs, out-of-scope (deployment is always out-of-scope here, R-019-00c)
    - open_questions that could change scope/behavior
R-019-0a-ui: If the product has any UI, the blueprint MUST include a UI/UX proposal the user approves
  BEFORE coding (ui-ux-designer produces it; accessibility-auditor advises). The deliverable is a
  viewable static HTML/CSS prototype the user opens in a browser, plus the supporting spec:
    - docs/experience/wireframes/index.html — links every screen (the entry the user opens to review)
    - docs/experience/wireframes/<screen>.html — one static page per key screen, real layout,
      showing relevant states (empty/loading/error/success)
    - docs/experience/wireframes/styles.css — the real design tokens (color/typography/spacing) and
      component styles the build will reuse
    - docs/experience/user-flows/<flow>.md — primary UX flows as Mermaid diagrams (entry → action → result)
    - docs/experience/ui-specifications/<screen>.md — component hierarchy, props/states, responsive +
      accessibility intent
  The prototype is a DESIGN artifact under docs/ (not application source under apps/services); it is
  static HTML/CSS only (no backend, no real data). Coding the real UI starts only after the user
  approves the prototype — never build screens first and reconcile the look at QC. The approved
  prototype + tokens are the visual contract the built UI must match.
R-019-0b: Present the blueprint to the user and get an EXPLICIT decision. Prefer a structured choice for
  the key forks (MVP vs production; monolith vs microservices; stack option; and for UI products the
  UI/UX direction). If the user requests changes, set status: changes_requested, revise, and re-present.
  Do not proceed on silence or guesses.
R-019-0c: Only when product-blueprint.yaml status: approved (with approved_by/approved_at recorded) does
  the to-DONE autonomous run begin. The approved blueprint is the build contract: task-analysis derives
  acceptance_criteria from it, and anything beyond it is scope expansion (hard-stop, R-019-05).
R-019-0d: If open_questions remain that affect scope, behavior, security, or cost, resolve them with the
  user during the blueprint gate — never assume them away to keep the run going.
```

## Autonomy grant

```text
R-019-01: Autopilot requires ONE explicit user grant per run, captured together with blueprint
  approval (R-019-0c). Record it once in
  .maestro/runtime/workflow-state.yaml.autopilot:
    enabled: true
    granted_by: "user"
    granted_at: "<iso8601>"
    task_id: "<task-id>"
    max_attempts_per_stage: <int, default 5>
    pre_authorized_gates: [R-011-01, R-011-06, R-011-10]
  The grant expires when the task reaches DONE, is cancelled, or the user revokes it.
R-019-02: While the grant is active, the pre-authorized soft gates change from "stop and ask" to
  "auto-approve and record". Each auto-approval still writes an approval record (R-011 "Approval
  record") with decided_by: "autopilot".
R-019-03: Autopilot does NOT widen tool/scope permissions by itself. Scope-guard, secret-guard, and
  destructive-guard hooks (R-017) still run and still block. Generated coders still write only inside
  their allowed_write_paths (R-006).
```

## Pre-authorized soft gates (auto-approve + record)

```text
R-019-04: Under an active grant, these gates auto-approve:
  R-011-01  create generated service coders
  R-011-06  create tests when needed
  R-011-10  proceed from governed Task Analysis to Coder Leader
  R-011-03  run onboarding when project knowledge is missing (autopilot runs it, does not skip it)
```

## Hard-stops (NEVER auto-approved, even under a grant)

```text
R-019-05: Autopilot MUST stop and ask the user for:
  R-011-07  destructive environment/database/deployment/data actions (rm -rf, DROP, prod deploy, force push)
  R-013     a real secret, credential, API key, or token is required to proceed
  external publish or irreversible action (production deploy, package publish, sending real data out)
  R-011-02 / R-011-09  expanding a coder's write scope or touching files outside approved scope
  R-011-08 / R-011-13  changing workflow policy, state-machine semantics, or workspace identity
  R-011-04 / R-011-05  skipping QC or downgrading a blocker bug (autopilot fixes blockers, never skips them)
  scope explosion: the work no longer matches the declared acceptance criteria
R-019-06: When a hard-stop is hit, write the blocker + the exact decision needed to
  workflow-state.yaml and the task folder, then return needs_user_approval. Do not guess credentials,
  do not fake a deploy, do not weaken a gate to keep going.
```

## Local-only scope

```text
R-019-00b: Autopilot runs entirely in the LOCAL development environment. It installs dependencies,
  builds, runs the test suite, and smoke-runs the app locally (dev server / local process / local DB
  or fixtures). The deliverable is a product the user verifies on their own machine first.
R-019-00c: Autopilot MUST NOT provision infrastructure or deploy. No cloud/staging/production deploy,
  no remote DB/migration against shared environments, no DNS/secrets/CI changes against real targets.
  Environment provisioning and deployment are a SEPARATE phase that runs only after the user confirms
  the local result and explicitly requests it. Any such action is a hard-stop (R-019-05).
R-019-00d: Autopilot generates standard local data via coder-data (seeds/fixtures/synthetic datasets
  conforming to schema + business rules; no real PII/secrets) so the app runs locally and real-user QC
  has realistic test data. Data is loaded locally only (never into shared/remote stores).
```

## Self-heal loop (build → run → test → fix)

```text
R-019-07: After each implementation step, autopilot runs the real verification for the stack LOCALLY:
  build/compile, lint when configured, the test suite, and a local smoke run of the app when runnable.
  Evidence (command + exit code + key output) is recorded per the artifact contracts.
R-019-08: On failure, autopilot captures the error, routes it back through the normal flow
  (dev-verification finding → coder-leader/service coder, or qc bug → bug-router → dev), applies a
  fix, and re-runs verification. This reuses the existing DEV_VERIFYING/FIXING/QC_RETESTING states;
  it does not create new states.
R-019-09: The loop is bounded by max_attempts_per_stage (default 5). If a stage still fails after the
  limit, autopilot stops and escalates to the user with: the failing stage, the attempts tried, the
  latest error evidence, and the most likely cause. It must not loop forever or declare done on red.
R-019-10: Autopilot must not fabricate green. A "done" claim requires real passing evidence
  (Four Karpathy principle 4). Disabling, deleting, or skipping a failing test to pass counts as
  fabrication and is forbidden.
```

## Real-user QC (autopilot acts as a thorough tester)

```text
R-019-QC1: Under autopilot, QC plays a real end user and tests hard, not a token smoke pass. QC Runner
  (using qa-strategist for strategy and accessibility-auditor where there is UI) produces a FULL test
  plan from the approved blueprint's features/acceptance criteria, covering every relevant dimension:
    - Functional: each feature's happy path + alternate paths.
    - UI: rendering, states (empty/loading/error/success), forms/validation, navigation, responsive,
      and fidelity to the approved prototype/design tokens (docs/experience/wireframes).
    - API: each endpoint — success, validation errors, auth/authz, status codes, schema/contract,
      pagination/edge inputs (Postman collection when endpoints exist).
    - UX: real user flows end-to-end, clarity, error messaging, basic accessibility (keyboard, labels,
      contrast) when there is a UI.
    - Edge/negative: boundaries, empty/large/malformed input, error and failure paths.
    - Regression: previously passing behavior still works after fixes.
R-019-QC2: Write every test case and its result to qc-test-results.yaml with status
  (pass|fail|blocked) and evidence. Each failure becomes a logged bug under
  .maestro/work/bugs/ and is indexed in the task bugs.yaml.
R-019-QC3: QC is DONE only when EVERY test case passes AND every logged QC bug is fixed — zero open
  bugs of ANY severity (blocker AND non-blocker). Run the loop qc -> bug-router -> dev fix ->
  re-QC (re-test the bug scope + regression) until the QC bug log is empty. This is stricter than the
  standard pipeline (R-008-06 zero blockers); autopilot clears non-blockers too before DONE.
R-019-QC4: QC must not weaken itself to pass: no deleting/skipping test cases, no downgrading a real
  bug to "won't fix" to reach zero — that is fabrication (R-019-10). Bounded by max_attempts_per_stage;
  if a bug cannot be fixed within the limit, stop and escalate to the user with the failing cases.
```

## Definition of done (complete product)

```text
R-019-11: Autopilot may transition to DONE only when ALL hold (verified LOCALLY):
  - build/compile succeeds locally with no errors
  - the configured test suite passes locally (per component test-policy)
  - the app boots / smoke-runs locally without crashing when it is runnable
  - every acceptance criterion (from the approved blueprint) is satisfied with evidence
  - the full real-user QC suite passes — every test case green across UI/API/UX/edge (R-019-QC1..3)
  - ZERO open QC bugs of any severity: dev has fixed every bug in the QC log (R-019-QC3), not just blockers
  - dev-verification score and critical checks pass (R-007)
  DONE means "locally complete and user-verifiable", not "deployed". Provisioning/deploy comes after.
R-019-12: On DONE, autopilot delivers a handover: what was built, changed files, the exact LOCAL run
  commands (install/build/run/test + env vars to set), test/verification evidence, known limitations,
  and suggested next steps. The user verifies locally first. Provisioning/deployment is offered as the
  explicit NEXT phase and only runs when the user confirms the local result and requests it.
```

## Observability

```text
R-019-13: Throughout the run, keep .maestro/runtime/agent-activity.yaml and workflow-state.yaml
  current (current stage, attempt count, last error, next action) so /status shows real progress and
  the run is resumable after an interruption (R-015, /resume-task).
```
