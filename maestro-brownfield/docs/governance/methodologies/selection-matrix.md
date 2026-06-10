# Methodology Selection Matrix

Use this when a task could fit more than one methodology.

## Primary Selection

| Signal | Prefer |
| --- | --- |
| Small and user can verify quickly | Risk-Based Workflow Routing `direct` |
| Needs a resumable task but little governance | Risk-Based Workflow Routing `assisted` |
| PRD/HLD/LLD/ADR drives implementation | Spec-Driven Development |
| Model behavior, RAG, evals, prompts, or agent behavior is central | Eval-Driven AI Development |
| Multi-team, compliance, production, or portfolio coordination | Enterprise Agent Governance |
| A production agent needs Mission, accountable owner, Behavior Contract, evals, or audit log | Enterprise Agent Governance |
| A new autonomous-agent product must be built before it can be operated | Spec-Driven Development first, then Enterprise Agent Governance |

## Combination Rules

- Eval-Driven AI Development can still use Spec-Driven Development artifacts when it is productized.
- Enterprise Agent Governance can wrap Spec-Driven Development when several teams or systems must coordinate.
- Enterprise Agent Governance requires explicit accountable ownership before autonomous production operation.
- Risk-Based Workflow Routing remains the routing layer even when a specialized methodology is selected.
- The selected methodology does not weaken approval gates, security rules, or verification evidence.

## Industry Alignment Rules

- Select `direct`, `assisted`, or `governed` before adding methodology overlays.
- Prefer overlays over hard switches when more than one pattern is true for the same task.
- Use `spec-driven-development` for spec-driven or document-led product delivery.
- Use `eval-driven-ai` for eval-driven model, RAG, prompt, tool, dataset, safety, or agent behavior work.
- Use `enterprise-agent-governance` for production autonomy, accountable ownership, audit, cost, compliance, or
  cross-team operating control.
- Treat checkpoints, continuation handoffs, and artifact indexes as the durable-execution layer for
  long-running work.
- Treat Dev Verification, QC, eval suites, and trace notes as evidence gates for completion claims.
- Treat unavailable environments or private data as user-owned or shared verification, not as missing
  work quality.
- Create a run when the task may pause/resume, involve multiple agents, need trace/eval evidence, or
  require human approval before continuing.

## Enterprise Agent Governance Readiness

Before selecting Enterprise Agent Governance for operation, confirm:

- A named primary and backup accountable owner exist.
- The first Mission is bounded, measurable, useful, and low risk.
- The Governance Policy or equivalent refusal policy is ratified.
- The agent has a Behavior Contract, Autonomy Policy, Eval Suite, and Audit Log plan.
- The substrate can provide identity, audit, tool scope, replay, and incident response.

## Coordinator Output

When methodology matters, the coordinator should record:

```yaml
methodology:
  selected: "risk-based-routing|spec-driven-development|enterprise-agent-governance|eval-driven-ai"
  overlays: []
  industry_patterns:
    - "durable-workflow"
    - "human-in-the-loop"
    - "eval-driven-ai"
  reason: ""
  execution_mode: "direct|assisted|governed"
  verification_owner: "agent|user|shared"
  required_artifacts: []
  accountable_owner_required: false
  production_agent_lifecycle: false
  run_required: false
```
