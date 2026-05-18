# R-001: Project Brain Rules

## Applies to

Coordinator, Onboarding, Agent Factory, Task Analysis, Coder Leader, Memory Update, Workflow Policy.

## Rules

```text
R-001-01: .runtime/context/index.yaml is the first memory routing source.
R-001-02: .runtime/context/project-brain.yaml is the first durable project brain source after the index.
R-001-03: Do not rescan the full repository when Memory Index and Project Brain are fresh enough for the task.
R-001-04: If Memory Index or Project Brain is missing, empty, or stale, route to Onboarding or /sync-memory --refresh-index.
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
```

## Required artifacts

```text
.runtime/context/project-brain.yaml
.runtime/context/index.yaml
.runtime/context/service-catalog.yaml
.runtime/context/test-policy.yaml
.runtime/context/agent-registry.yaml
```

## Violation handling

If memory is stale or insufficient, stop normal routing and run `/onboard` or partial onboarding.
