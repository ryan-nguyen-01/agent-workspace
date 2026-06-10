# R-004: Task Analysis Rules

## Applies to

Coordinator, Task Analysis, Coder Leader.

## Rules

```text
R-004-01: Every request must be classified. Full normalization before coding is required in governed
mode; assisted mode may use a bounded task manifest; direct mode may omit persistent task artifacts.
R-004-02: task-analysis.yaml must contain intent, summary, business goal, acceptance criteria, impacted components, context_plan for product-component tasks, risks, blockers, critical checks, dev verification checklist, and QC focus.
R-004-03: Acceptance criteria must be explicit and testable.
R-004-04: Critical checks must be identified before development starts.
R-004-05: Cross-service impact must be identified before assigning coders.
R-004-06: If critical business or technical facts are missing, mark requires_user_clarification and stop.
R-004-07: Task Analysis must not modify application source code.
R-004-08: Governed Task Analysis output must be presented for review before routing to Coder Leader
when the applicable approval policy requires it.
R-004-09: Fast-track exception (workflow.md §6.2 + R-011-10b) — Task Analysis may skip the user approval gate only when ALL fast-track eligibility conditions hold and fast_track: true is recorded in task-analysis.yaml with fast_track_reason. product-component fast-track still requires task-analysis.yaml.context_plan, lightweight service-assignments.yaml, dev-verification, and (unless explicitly waived) qc-handoff.
R-004-10: Task Analysis must set architecture_review.required when the task changes cross-component flows, public APIs, event contracts, database/schema compatibility, shared packages, runtime topology, security-sensitive surfaces, or rollback/migration strategy.
R-004-11: When architecture_review.required is true, Task Analysis must include reason, triggers, and output_required in task-analysis.yaml.
R-004-12: Framework-maintenance fast-track exception — trivial framework maintenance may skip full task-analysis.yaml, dev-verification.yaml, and qc-handoff.md when workflow.md §6.2 framework-maintenance eligibility holds. It must still record target_scope, changed_files, and verification evidence in the response or a lightweight task note.
R-004-13: R-004-12 is not allowed for approval gates, security/secret rules, workflow state machine
changes, generated coder scope rules, destructive behavior, or governed product-component work.
R-004-14: product-component task-analysis.yaml must include context_plan before planning or coding.
R-004-15: context_plan must map acceptance criteria to required memory/source evidence, bounded budgets, excluded paths, confidence, and expansion triggers.
R-004-16: If Task Analysis cannot map acceptance criteria to impacted components or files with medium-or-higher confidence, mark requires_user_clarification or context_plan.unresolved_context and stop before Coder Leader.
R-004-17: Task Analysis must not load broad source context before checking Memory Index, Project Profile, Component Registry, inputs-index, and relevant component knowledge summaries.
R-004-18: Security, schema, migration, data, infra, shared-code, and cross-service risks must be listed as context expansion triggers even when initial context is sufficient.
R-004-19: Task Analysis must assign execution_mode=direct|assisted|governed, verification_owner=agent|user|shared, run_required, methodology.selected, methodology.overlays, and methodology.industry_patterns.
R-004-20: A task must be decomposed before implementation when it spans multiple sessions, has independent acceptance criteria, combines design and implementation, affects multiple components, contains parallel workstreams, requires migration/rollout, or invokes multiple specialists.
R-004-21: Work decomposition is limited to Initiative -> Epic -> Task -> Subtask. A subtask that still needs decomposition becomes a task; nested subtasks are forbidden.
R-004-22: Task Analysis must reference relevant PRD, feature, user story, user flow, HLD, LLD, ADR, design, and component ids when they exist.
R-004-23: Missing agent access to an environment or protected data is not permission to invent verification. Record verification_owner=user|shared, the unavailable evidence, and explicit user checks.
R-004-24: direct mode may omit persistent task artifacts for low-risk work. assisted mode requires task/progress/verification records when work crosses a conversation. governed mode requires the full artifact pipeline.
R-004-25: Risk-Based Workflow Routing is the default router. Use Spec-Driven Development, Eval-Driven AI Development, and Enterprise Agent Governance as overlays when the task requires traceability, eval-driven AI, or governed autonomous operation instead of forcing a single hard methodology switch.
R-004-26: Task Analysis must set run_required=true when work may pause/resume, involve multiple agents,
need trace/eval evidence, wait on human approval, or have multiple execution attempts.
```

## Required artifacts by mode

```text
direct: none required
assisted: .maestro/work/tasks/<task-id>/task.yaml, progress.yaml, verification.yaml
governed: .maestro/work/tasks/<task-id>/task-input.md and task-analysis.yaml, followed by the full pipeline
```

For R-004-12 framework-maintenance fast-track, lightweight evidence may replace these artifacts:

```text
target_scope: framework
fast_track: true
changed_files[]
verification command or reason no command applies
```

## Violation handling

Reject development routing and send the task back to Task Analysis.

## Reuse and convention analysis rules

R-004-D01: Task Analysis must identify relevant reusable assets before implementation planning.
R-004-D02: Task Analysis must identify relevant coding conventions and anti-patterns for impacted components.
R-004-D03: For implementation, bugfix, regression, or high-risk tasks, Task Analysis must consider `.maestro/memory/project/feedback/patterns.md` and `feedback/anti-patterns.md` through the index and record relevant prevention items in `reuse_and_convention_analysis`.
R-004-D03: Task Analysis must include reuse_and_convention_analysis in task-analysis.yaml.
R-004-D04: If a new shared reusable asset appears necessary, Task Analysis must flag Coder Leader review before implementation.
R-004-D05: Do not invent reusable assets. Use Project Brain, Component Knowledge, common/generics.md, conventions.md, and architecture.md as evidence sources for product-component work. For framework maintenance, use the relevant framework spec/rule/template/command files as evidence and do not load component knowledge files unless the task directly touches component contracts.
