# Document Precedence (tier model)

Adapted from a Spec-Driven Development tier model. Goal: **exactly one official source per decision**, and a
deterministic winner when two documents disagree. Lower tiers never override higher tiers.

> When two documents conflict, the **higher tier wins**. Do not "patch" the lower tier to mask the
> conflict — fix the higher-tier source (or raise it to the user), then let lower tiers re-derive.

## Tiers

```text
T0  Invariant authority — the framework contract. Conflicts here go to the user.
    - CLAUDE.md                      (precedence: project CLAUDE.md overrides global)
    - .maestro/engine/workflow.md             (state machine, gates, wave/stage flow)
    - .maestro/engine/rules/**                (R-000..R-018 constraints)
    - .maestro/engine/docs/agent-taxonomy.md  (agent class definitions)

T1  Project SSOT — durable project truth, one per workspace.
    - .maestro/knowledge/project.yaml
    - .maestro/config/model-routing.yaml
    - .maestro/config/response-ui.yaml
    - .maestro/runtime/workflow-state.yaml   (current state/mode; transient but authoritative for "now")

T2  Service / contract level — per service or cross-service interface.
    - .maestro/registry/components.yaml
    - .maestro/registry/agents.yaml   (coder scopes, signed — see R-006/R-018)
    - .maestro/knowledge/test-policy.yaml
    - .maestro/registry/skills.yaml
    - .maestro/knowledge/components/<component-id>.yaml  (component knowledge files)

T3  Task / runtime level — per task, regenerated each pipeline.
    - .maestro/work/tasks/<task-id>/task-analysis.yaml
    - .maestro/work/tasks/<task-id>/*.yaml  (implementation-plan, service-assignments, dev-verification, …)
    - .maestro/work/tasks/<task-id>/advisories/<id>.yaml  (specialist advisories)
```

## Rules of precedence

```text
1. Conflict resolution: higher tier wins. T3 must never silently contradict T1/T2.
2. One official source: every decision has exactly one authoritative location (the highest tier that
   owns it). Other docs reference it; they do not restate-and-diverge.
3. Upward correction: if a lower tier reveals the higher tier is wrong, surface it (raise to user /
   record in CHANGELOG as a decision) and fix the higher-tier source — do not fork the truth.
4. Generated docs are never authoritative: anything produced by scripts/build-*.py mirrors a source;
   the source (its tier) wins. Manual edits to generated files are drift (see R-018 + generator --check).
5. Specialist advisories (T3) recommend; the owning workflow agent decides (R-016). An advisory never
   overrides a T0–T2 contract.
```

## See also

- `R-018` (`.maestro/engine/rules/18-doc-precedence-rules.md`) — the enforceable form of this model.
- Spec-Driven Development document dependency maps — the source pattern this adapts.
