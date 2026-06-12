# A2A Contract Layer (Agent-to-Agent)

Every agent-to-agent handoff in Maestro uses **one standardized envelope** instead of implicit file
conventions. The schemas here are versioned contracts: agents validate an envelope BEFORE accepting
work (like a person rejecting an incomplete brief), and a result is invalid without evidence.

Contract rules: `.maestro/engine/rules/23-agent-collaboration-rules.md` (R-023).

## Files

| File | Purpose |
|------|---------|
| `handoff.schema.yaml` | The envelope every delegation carries: intent, purpose_ref, inputs, expected output, acceptance, confidence |
| `result.schema.yaml` | The symmetric reply: status, evidence, deviations, next handoff |
| (advisory) | Specialist advisories already follow `templates/advisory.template.yaml` — same evidence discipline |

## How it works

```text
1. SENDER fills the handoff envelope (template: engine/templates/handoff.template.yaml) and stores it
   in the task folder: .maestro/work/tasks/<task-id>/handoffs/<seq>-<from>-to-<to>.yaml
2. RECEIVER validates before working (R-023-02): intent present? purpose_ref resolves? every required
   input (per R-021 matrix for its role) attached and authoritative? acceptance testable?
   -> any failure: REFUSE with blocked: invalid_handoff + what is missing. Never guess the gaps.
3. RECEIVER works, keeping the task journal (R-024), then returns a result envelope:
   done requires evidence[]; deviations from the handoff must be listed explicitly.
4. SENDER verifies the result against acceptance before passing downstream.
```

## Versioning

```text
- Each schema carries schema_version. Breaking changes bump the version; both sides must speak the
  same version or the receiver refuses with schema_mismatch.
- Schemas change only via framework maintenance (R-011-08 applies to semantic changes).
```
