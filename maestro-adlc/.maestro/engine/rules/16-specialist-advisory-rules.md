# R-016: Specialist Advisory Rules

## Applies to

All 19 specialist advisors under `.claude/agents/specialists/<category>/`, and every workflow agent that may invoke them (Coordinator, Task Analysis, Solution Architect, Coder Leader, Dev Verification, QC Handoff, Memory Update).

## Core principle

```text
A specialist advisor is a domain expert that produces evidence-based recommendations.
It is NOT a control-plane agent and NOT a coder.
Advisors advise; workflow agents decide; coders implement.
```

Specialist advisors are the 4th agent class (see `.maestro/engine/docs/agent-taxonomy.md`): they sit beside
the 12 workflow agents and the coders, but never replace either.

## Rules

```text
R-016-01: A specialist advisor must never write application/source code, run migrations, or edit infra.
R-016-02: An advisor writes exactly one artifact: .maestro/work/tasks/<task-id>/advisories/<id>.yaml (its own advisory).
R-016-03: An advisor must never assign coders, mark Code Done / QC Done, or approve gates. Only workflow agents do that.
R-016-04: An advisor is not a user entrypoint. It is invoked in-pipeline by a workflow agent; never routed to from raw user input.
R-016-05: Every specialist file must carry frontmatter: name, description, tools, model, category. category ∈ {architecture, quality-security, product, data-ai, ops-devex, research-qa}.
R-016-06: The description must end with the advisor-only clause so both humans and routers see the boundary.
R-016-07: An advisor's model is governed by model-routing.yaml > agent_model_map.specialist_advisors; do not hardcode a model that diverges from that map.
R-016-08: Advisories do NOT introduce new workflow states. They run as sub-steps inside existing states (ANALYZED, ARCHITECTURE_REVIEWING, DEV_VERIFYING, QC).
R-016-09: task-analysis.yaml MAY declare advisory_required: [<specialist-id>, ...]. The downstream workflow agent must invoke each and resolve handoff.must_address before proceeding.
R-016-10: An advisory must follow the Karpathy anti-guessing rules: state confidence, list assumptions, cite evidence (file/line/contract), never fabricate.
R-016-11: Advisors that overlap a workflow agent's mandate must AUGMENT, not replace it. Specifically:
          - code-reviewer augments Coder Leader's R-005-09 review; it does not gate Code Done.
          - business-analyst augments Task Analysis; only task-analysis.yaml is authoritative.
          - qa-strategist advises test strategy; qc-runner executes and qc-handoff owns the handoff doc.
          - security-auditor may propose critical checks; dev-verification still owns the Code Done gate.
R-016-12: An advisory is advisory by default. A workflow agent may accept, defer, or reject a recommendation, but must record the disposition (handoff.must_address vs. acknowledged) in its own artifact.
R-016-13: Advisors obey the same security/secret rules (R-013) and never emit secrets into advisories.
R-016-14: Advisor tool access is read + own-artifact-write only (Read, Grep, Glob, Write). They must not gain Bash/Edit on app code.
R-016-15: Adding or removing a specialist requires updating: the file under specialists/<category>/, model-routing.yaml specialist_advisors, the catalog (.claude/agents/specialists/README.md), and EXPECTED_SPECIALIST_COUNT in scripts/architecture-health-check.py.
```

## Advisory artifact contract

```yaml
# .maestro/work/tasks/<task-id>/advisories/<specialist-id>.yaml
specialist: <id>
category: <category>
task_id: <task-id>
confidence: high | medium | low
summary: "<one-line recommendation>"
findings:
  - area: "<domain area>"
    severity: blocker | high | medium | low | info
    evidence: "<file:line / contract / measurement>"
    recommendation: "<actionable change>"
assumptions: ["<assumption + why>"]
handoff:
  to: <downstream workflow agent or coder>
  must_address: ["<items the downstream MUST resolve>"]
  acknowledged: ["<advice noted but not mandatory>"]
```

## Invocation flow

```text
1. A workflow agent detects a domain risk OR reads advisory_required from task-analysis.yaml.
2. It invokes the specialist (subagent) with the task context.
3. The specialist writes advisories/<id>.yaml and returns its summary.
4. The workflow agent reads handoff.must_address, decides disposition, records it, and continues the state.
```

## Violation handling

If a specialist attempts to write outside its advisory artifact or assert a gate decision, the hook
layer (R-017) and the invoking workflow agent must reject it. Re-issue the request scoped to advice only.
