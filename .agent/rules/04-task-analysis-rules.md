# R-004: Task Analysis Rules

## Applies to

Coordinator, Task Analysis, Coder Leader.

## Rules

```text
R-004-01: Every HLD, LLD, ticket, bug report, incident, or text task must be normalized before coding.
R-004-02: task-analysis.yaml must contain intent, summary, business goal, acceptance criteria, impacted services, context_plan for applied-service tasks, risks, blockers, critical checks, dev verification checklist, and QC focus.
R-004-03: Acceptance criteria must be explicit and testable.
R-004-04: Critical checks must be identified before development starts.
R-004-05: Cross-service impact must be identified before assigning coders.
R-004-06: If critical business or technical facts are missing, mark requires_user_clarification and stop.
R-004-07: Task Analysis must not modify application source code.
R-004-08: Task Analysis output must be presented to the user for review and approval before routing to Coder Leader.
R-004-09: Fast-track exception (workflow.md §6.2 + R-011-10b) — Task Analysis may skip the user approval gate only when ALL fast-track eligibility conditions hold and fast_track: true is recorded in task-analysis.yaml with fast_track_reason. Applied-service fast-track still requires task-analysis.yaml.context_plan, lightweight service-assignments.yaml, dev-verification, and (unless explicitly waived) qc-handoff.
R-004-10: Task Analysis must set architecture_review.required when the task changes cross-service flows, public APIs, event contracts, database/schema compatibility, shared packages, runtime topology, security-sensitive surfaces, or rollback/migration strategy.
R-004-11: When architecture_review.required is true, Task Analysis must include reason, triggers, and output_required in task-analysis.yaml.
R-004-12: Framework-maintenance fast-track exception — in framework-template/not_applied mode, trivial framework maintenance may skip full task-analysis.yaml, dev-verification.yaml, and qc-handoff.md when workflow.md §6.2 framework-maintenance eligibility holds. It must still record target_scope, changed_files, and verification evidence in the response or a lightweight task note.
R-004-13: R-004-12 is not allowed for approval gates, security/secret rules, workflow state machine changes, generated coder scope rules, destructive behavior, service contract changes, or any application source under services/<service-name>/.
R-004-14: Applied-service task-analysis.yaml must include context_plan before planning or coding.
R-004-15: context_plan must map acceptance criteria to required memory/source evidence, bounded budgets, excluded paths, confidence, and expansion triggers.
R-004-16: If Task Analysis cannot map acceptance criteria to impacted services or files with medium-or-higher confidence, mark requires_user_clarification or context_plan.unresolved_context and stop before Coder Leader.
R-004-17: Task Analysis must not load broad source context before checking Memory Index, Project Profile, Service Catalog, inputs-index, and relevant service brain summaries.
R-004-18: Security, schema, migration, data, infra, shared-code, and cross-service risks must be listed as context expansion triggers even when initial context is sufficient.
```

## Required artifacts

```text
.runtime/tasks/<task-id>/task-input.md
.runtime/tasks/<task-id>/task-analysis.yaml
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
R-004-D02: Task Analysis must identify relevant coding conventions and anti-patterns for impacted services.
R-004-D03: For implementation, bugfix, regression, or high-risk tasks, Task Analysis must consider `.runtime/context/feedback/patterns.md` and `feedback/anti-patterns.md` through the index and record relevant prevention items in `reuse_and_convention_analysis`.
R-004-D03: Task Analysis must include reuse_and_convention_analysis in task-analysis.yaml.
R-004-D04: If a new shared reusable asset appears necessary, Task Analysis must flag Coder Leader review before implementation.
R-004-D05: Do not invent reusable assets. Use Project Brain, Service Brain, common/generics.md, conventions.md, and architecture.md as evidence sources for applied-service work. For framework maintenance, use the relevant framework spec/rule/template/command files as evidence and do not load service brains unless the task directly touches service contracts.
