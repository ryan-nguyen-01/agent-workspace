# R-005: Coder Leader Rules

## Applies to

Coder Leader, Coordinator, generated service coders.

## Rules

```text
R-005-01: Coder Leader owns all multi-service implementation coordination.
R-005-02: Service coders must not coordinate cross-service changes directly.
R-005-03: In the standard applied-service pipeline, Coder Leader must create implementation-plan.yaml before assigning coders.
R-005-04: In the standard applied-service pipeline, Coder Leader must create service-assignments.yaml before coder work starts.
R-005-04b: In applied-service fast-track, Coder Leader may skip implementation-plan.yaml but must still create a lightweight service-assignments.yaml before coder work starts.
R-005-05: Coder Leader must select coders from agent-registry.yaml.
R-005-06: Coder Leader must reject tasks when no active coder exists for an impacted service.
R-005-07: Coder Leader must protect API, event, schema, and shared package contracts.
R-005-08: Coder Leader must not claim Code Done; Dev Verification owns that decision.
R-005-09: Coder Leader must complete code quality and architecture review before sending work to Dev Verification.
R-005-10: If quality review fails, Coder Leader must return NEEDS_FIX to assigned coders and record findings in coder-results.yaml.
R-005-11: If task-analysis.yaml has architecture_review.required: true, Coder Leader must not create implementation-plan.yaml until architecture-review.yaml exists and its decision is approved.
R-005-12: Coder Leader must copy applicable constraints_for_coder_leader from architecture-review.yaml into implementation-plan.yaml and service-assignments.yaml.
R-005-13: Framework-maintenance fast-track skips Coder Leader unless the task changes workflow rules, command contracts, generated coder templates, service scope contracts, or other high-risk framework behavior.
R-005-14: Coder Leader must read and follow task-analysis.yaml.context_plan before opening source files or assigning coders.
R-005-15: Coder Leader may expand beyond the context_plan budget only when a recorded expansion trigger fires; it must record the trigger and files opened in implementation-plan.yaml or coder-results.yaml.
R-005-16: Coder Leader must reject planning when context_plan.confidence is low or unresolved_context contains service boundary, contract ownership, or test policy gaps.
R-005-17: Service assignments must include only the source/memory context each coder needs, not the whole project brain or all service brains.
R-005-18: Service assignments must include relevant feedback patterns, known error anti-patterns, and regression checks when task-analysis identifies them.
R-005-19: Coder Leader must route `coding_error_feedback` from coder-results or dev-verification to Memory Update before closing the task.
```

## Required artifacts

```text
.runtime/tasks/<task-id>/implementation-plan.yaml   (standard pipeline)
.runtime/tasks/<task-id>/service-assignments.yaml   (standard pipeline or lightweight applied-service fast-track)
.runtime/tasks/<task-id>/coder-results.yaml         (standard pipeline or applied-service fast-track)
.runtime/tasks/<task-id>/architecture-review.yaml   (when task-analysis.yaml requires it)
```

## Violation handling

Stop implementation and route to Coordinator for missing coder creation, scope approval, or task clarification.

## Boundary with Dev Verification (clarifies R-005-09 / R-007-11)

Coder Leader and Dev Verification have distinct, non-overlapping concerns. When in doubt, use this matrix.

```text
COVERAGE                                   | OWNER                | EVIDENCE LOCATION
-------------------------------------------|----------------------|-------------------------
Architecture / layer boundary violation    | coder-leader         | coder-results.yaml.findings
Dependency direction wrong                 | coder-leader         | coder-results.yaml.findings
Duplicate helper / reuse missed            | coder-leader         | coder-results.yaml.findings
Naming / readability / API ergonomics      | coder-leader         | coder-results.yaml.findings
Contract drift (api/event/schema/shared)   | coder-leader         | coder-results.yaml.contract_review
Cross-service coordination correctness     | coder-leader         | coder-results.yaml.cross_service
Code smell / refactoring opportunity       | coder-leader         | coder-results.yaml.findings
-------------------------------------------|----------------------|-------------------------
Required artifacts exist                   | dev-verification     | dev-verification.yaml.artifact_check
Allowed_write_paths respected              | dev-verification     | dev-verification.yaml.scope_check
Critical_checks pass/fail (functional)     | dev-verification     | dev-verification.yaml.critical_checks
Test policy compliance                     | dev-verification     | dev-verification.yaml.test_evidence
Tests actually executed and pass           | dev-verification     | dev-verification.yaml.test_evidence
Manual verification recorded               | dev-verification     | dev-verification.yaml.manual_evidence
Score >= 80% computation                   | dev-verification     | dev-verification.yaml.score_breakdown
Secrets/PII not leaked into artifacts      | dev-verification     | dev-verification.yaml.security_scan
```

### Worked examples

```text
1. "PaymentController imports OrderRepository directly, bypassing OrdersService."
   → Architecture/dependency direction → coder-leader rejects, returns NEEDS_FIX in coder-results.yaml.findings.

2. "Coder created src/utils/formatDate.ts but src/lib/date.ts already exports the same function."
   → Reuse violation → coder-leader rejects with reference to existing asset.

3. "Coder modified files outside allowed_write_paths."
   → Scope violation → dev-verification DEV_BLOCKED (overrides any score).

4. "Acceptance criterion AC-3 has no test and policy says unit_tests_required: true."
   → Test-policy compliance → dev-verification DEV_BLOCKED (R-007-05).

5. "Two coders both wrote nearly-identical retry helpers."
   → Reuse / duplication → coder-leader (R-005-09); not a verification concern.

6. "Tests pass locally but verification artifact missing test_evidence section."
   → Artifact contract → dev-verification NEEDS_FIX, route back to coder-leader to fill evidence.

7. "Implementation deviates from implementation-plan.yaml.sequence."
   → Plan adherence is coder-leader concern (was the deviation justified?). Verification only flags it if it caused scope or test gaps.
```

### Order of operations

```text
1. Coder Leader review runs FIRST (R-005-09).
2. If Leader returns NEEDS_FIX → coders fix → Leader re-reviews. Do not forward to Dev Verification yet.
3. Once Leader passes → Dev Verification runs (R-007).
4. Dev Verification is a binary gate (Code Done / not). It does not re-do Leader's qualitative review.
5. If Dev Verification finds an architecture issue Leader missed: returns NEEDS_FIX and explicitly notes "missed by leader review" so the gap is auditable.
```
