# Risk-Based Workflow Routing

Risk-Based Workflow Routing is the default router. It does not replace Spec-Driven Development,
Eval-Driven AI Development, or Enterprise Agent Governance; it chooses how much process a task needs.

Legacy alias: `adaptive`.

## Use When

- The project contains both quick user-verified work and large governed delivery.
- The agent cannot access some environments or data, so verification may be user-owned or shared.
- The team wants speed by default, with automatic escalation for risk.

## Flow Selection

| Situation | Mode | Required posture |
| --- | --- | --- |
| Small, reversible, low-risk change | `direct` | Implement quickly, disclose unverified checks. |
| Work may span conversations | `assisted` | Create `task.yaml`, `progress.yaml`, and `verification.yaml`. |
| Security, data, production, public contract, or cross-component work | `governed` | Use the full state machine and approval gates. |

## Agent Rules

- Start with classification, not broad scanning.
- Choose the smallest mode that can preserve correctness.
- Escalate automatically; do not downgrade automatically.
- Record verification owner as `agent`, `user`, or `shared`.
- If the conversation grows long, write a checkpoint and continuation handoff.

## Required References

- `.maestro/methodology.yaml`
- `.maestro/work/index.yaml`
- `.maestro/engine/workflow.md`
- `.maestro/engine/rules/11-approval-gates.md`
