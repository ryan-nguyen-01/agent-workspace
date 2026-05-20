# R-001: Project Brain Rules

## Applies to

Coordinator, Onboarding, Agent Factory, Task Analysis, Coder Leader, Memory Update, Workflow Policy.

## Rules

```text
R-001-01: .runtime/context/index.yaml is the first memory routing source.
R-001-02: .runtime/context/project-brain.yaml is the first durable project brain source after the index.
R-001-03: Do not rescan the full repository when Memory Index and Project Brain are fresh enough for the task.
R-001-04: If Memory Index or Project Brain is missing, empty, or stale for applied-service work, route to Onboarding or /sync-memory --refresh-index.
R-001-05: Prefer partial rescan when stale areas are known.
R-001-06: Service-specific facts belong in .runtime/context/services/<service>.yaml.
R-001-07: Generated coder facts belong in .runtime/context/agent-registry.yaml.
R-001-08: Test policy belongs in .runtime/context/test-policy.yaml.
R-001-09: Service source paths and coding ownership belong in .runtime/context/service-catalog.yaml.
R-001-10: Inferred facts must carry confidence or be marked unknown.
R-001-11: Drift detection — Coordinator must inspect project-brain.yaml freshness fields at session startup. Result must appear in the state banner.
R-001-12: After /onboard or /sync-memory --refresh-index, the responsible agent must set project-brain.yaml.freshness.last_indexed_at to today's date and last_drift_check_result to "fresh".
R-001-13: If freshness.tracked_paths is empty, default to ["services", "src", "packages", "apps"] until onboarding writes the real set.
R-001-14: When drift check reports stale and Coordinator would route into IN_DEV, block until user runs /sync-memory --refresh-index or explicitly accepts the stale brain (record acceptance in workflow-state.yaml.stale_brain_accepted_for_task).
R-001-15: Framework-template exception — when workflow-state.yaml has distribution_mode=framework-template and instance_status=not_applied, missing/stale Project Brain must not block framework maintenance tasks.
R-001-16: The exception in R-001-15 does not apply to application source work under services/<service-name>/; applied-service work still requires Project Brain, service catalog, and scoped coder contracts.
R-001-17: For framework maintenance, read only the entrypoints and directly relevant framework files unless the requested change explicitly concerns memory, service catalog, registry, or test policy contracts.
R-001-18: Project Brain must include project_profile with archetypes, source_layout, critical_manifests, boundary_strategy, onboarding_scan_profile, evidence, and confidence.
R-001-19: Memory Index must expose context_economy defaults so agents can choose bounded reads without opening all memory files.
R-001-20: Agents must use signature-first reads before broad source reads: tree shape, manifests, service-catalog paths, API/schema/test/CI config, and indexed inputs.
R-001-21: Agents must skip generated/vendor/heavy roots by default unless explicitly referenced by task evidence.
R-001-22: For applied-service work, Task Analysis must create task-analysis.yaml.context_plan before Coder Leader or service coders open broad source context.
R-001-23: If context_plan.confidence is low, or required service/test/contract evidence is missing, block progression into IN_DEV until context is refreshed or user explicitly accepts the risk.
R-001-24: Context expansion beyond the budget must be recorded with trigger, files opened, and evidence gained in the relevant task artifact.
```

## Required artifacts for applied-service memory

```text
.runtime/context/project-brain.yaml
.runtime/context/index.yaml
.runtime/context/service-catalog.yaml
.runtime/context/test-policy.yaml
.runtime/context/agent-registry.yaml
```

## Violation handling

If memory is stale or insufficient for applied-service work, stop normal routing and run `/onboard` or partial onboarding. For framework maintenance in framework-template/not_applied mode, continue with targeted file reads and record the assumption in the response or task note.
