# Task: {{TASK_ID}}

> Task card theo state machine trong workflow.md.

## Metadata

- **ID:** {{TASK_ID}}  (format: `TASK-YYYYMMDD-<short-slug>`)
- **Title:** {{title}}
- **Type:** feature | bug-fix | refactor | chore
- **Service scope:** {{service-name}}
- **Owner agent:** {{agent-coder-project-service-tech}}
- **Created by:** agent-analyst
- **Created at:** {{timestamp}}
- **State:** todo

## Description

{{Task description từ user, giữ nguyên wording nếu có thể}}

## Acceptance Criteria

- [ ] **AC-1:** {{testable condition}}
- [ ] **AC-2:** {{testable condition}}
- [ ] **AC-3:** {{testable condition}}

Format AC: "khi X, thì Y" — testable + observable.

## Dependencies

- Depends on: {{TASK-...}} (nếu có)
- Blocks: {{TASK-...}} (nếu có)

## Risk notes

- {{risk 1}}
- {{risk 2}}

## Scope boundary

- **Files allowed:** `{{service-scope}}/**`
- **Files NOT allowed:** tất cả paths khác

---

## History

| Timestamp | Agent | Transition | Note |
|-----------|-------|------------|------|
| {{ts}} | agent-analyst | created (todo) | initial breakdown |
| {{ts}} | agent-coder-... | todo → dev-in-progress | start coding |
| {{ts}} | agent-coder-... | dev-in-progress → dev-done | unit tests pass |
| {{ts}} | agent-reviewer | - | review PASS |
| {{ts}} | agent-tester | - | integration PASS |
| {{ts}} | agent-handover | dev-done → qc-ready | handover v1 |
| {{ts}} | agent-qc-runner | qc-ready → qc-testing | start QC local |
| {{ts}} | agent-qc-runner | qc-testing → dev-fix-in-progress | BUG-B-... found |
| {{ts}} | agent-coder-... | dev-fix-in-progress → dev-done | fix done |
| {{ts}} | agent-handover | dev-done → qc-ready | handover v2 |
| {{ts}} | agent-qc-runner | qc-testing → qc-done | zero blocker |
| {{ts}} | agent-documenter | - | docs updated |
| {{ts}} | agent-context-keeper | qc-done → shipped | brain synced |

---

## Review report

_Populate bởi agent-reviewer._

(placeholder — see agents/_core/reviewer.agent.md for format)

---

## Test report

_Populate bởi agent-tester._

(placeholder — see agents/_core/tester.agent.md for format)

---

## Security report

_Populate bởi agent-security (nếu task có security concern)._

(placeholder)

---

## QC Test Report

_Populate bởi agent-qc-runner._

### Env: local
- Tested at: ...
- AC pass: X/Y
- Bugs found: ...

### Env: dev
...

### Env: sit
...

---

## Non-blocker bugs found

- BUG-N-... — {{title}} — severity: {{low/medium/cosmetic}}

---

## Handover docs

- v1: `handover/{{TASK_ID}}-handover.md` — {{date}}
- v2: `handover/{{TASK_ID}}-handover-v2.md` — {{date}} (after BUG-B-...)
