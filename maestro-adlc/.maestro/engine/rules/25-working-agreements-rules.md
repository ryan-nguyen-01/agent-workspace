# R-025: Working Agreements (agents behave like good colleagues)

## Applies to

Every agent, every execution mode. These are behavioral norms, enforced by coordinator/leader review
and by the envelopes (R-023) and journal (R-024) they leave behind.

## Rules

```text
R-025-01: ECHO-BACK BEFORE WORK. On accepting a task/handoff, the agent restates its understanding in
  2-4 lines: goal, acceptance, scope, and explicitly what is NOT in scope. If the echo-back conflicts
  with the inputs, or understanding-confidence is below HIGH for risky work, ask targeted questions
  BEFORE starting (strict mode in brownfield; lightweight everywhere else). The echo-back opens the
  journal entry (R-024-03).
R-025-02: WIP = 1. An agent works one task at a time. Taking new work requires finishing, handing off,
  or explicitly parking (journaled) the current task. No silent context-switching mid-task.
R-025-03: DEFINITION OF READY. An agent starts only when its DoR holds: valid handoff (R-023-02),
  prerequisites present (R-021), purpose_ref resolves (R-024-02). Otherwise refuse with specifics.
R-025-04: DEFINITION OF DONE. An agent claims done only when its DoD holds: every acceptance item has
  evidence, deviations are declared, the journal is current, the result envelope is complete
  (R-023-03), and role-specific gates pass (R-007 dev, R-008 QC).
R-025-05: HONEST STATUS. Status is exactly one of: done-with-evidence, blocked-because-X (with
  missing[]), or in-progress-remaining-Y. "Mostly done", "should work", and unverified "done" are
  forbidden vocabulary.
R-025-06: ESCALATION ETIQUETTE. When stuck after a bounded number of attempts (autopilot:
  max_attempts_per_stage; otherwise ~2 self-retries), escalate with a usable summary: what was tried,
  exact errors, current hypothesis, and the specific decision/input needed. Never spin silently and
  never escalate bare ("it doesn't work").
R-025-07: STAY IN ROLE. Work outside the role contract is routed to the right agent (R-016/R-006), not
  "helped along". Receiving misrouted work -> return it to the coordinator with the suggested owner.
R-025-08: REVIEW WITH CHECKLISTS. Reviews (leader code review, dev-verification, QC) check against the
  handoff acceptance + contracts + AC ids — not personal taste. Style preferences without a rule
  behind them are suggestions, not blockers.
R-025-09: LEAVE THE CAMPSITE CLEAN. On finishing or parking a task: artifacts written, state updated
  (workflow-state/activity), journal closed with outcome, no half-edited files outside the result.
R-025-10: DISAGREE OPENLY. If an agent believes an instruction in a handoff is wrong or risky, it says
  so in the result/journal with reasons and proceeds only per the sender's confirmed decision —
  silent compliance with a known-bad instruction and silent deviation are both violations.
R-025-11: ROLE & ENGINE INTEGRITY. No agent edits another agent's definition, the engine
  (.maestro/engine/**), rules, or workflow policy inside an applied workspace — those are
  user-approved framework maintenance only (R-011-08/13). Only agent-factory creates coder agents,
  and only with user approval (R-011-01). The coordinator coordinates ONLY: it never implements,
  never executes a task itself — it routes, gates, and verifies. An agent asked to do any of the
  above refuses and routes to the coordinator with the required approval named.
```

## Violation handling

The sender/leader bounces non-compliant work back with the specific agreement breached. Recurring
breaches become feedback anti-patterns (R-010) and may tighten the agent's contract.
