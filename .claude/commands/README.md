# Commands Index

Canonical root index: [../../COMMAND.md](../../COMMAND.md)

Commands are user-facing entrypoints. They describe which agent owns the action, which rules apply, which artifacts are required, and when to stop.

## Commands

```text
/coord          Main coordinator entrypoint
/onboard        Build or refresh Project Brain
/create-coders  Generate scoped service coder agents after approval
/status         Report workflow, brain, task, model routing, response UI, and agent activity dashboard
/analyze-task   Normalize HLD/LLD/ticket/text into task-analysis.yaml
/plan-dev       Build implementation plan and service assignments
/dev            Run implementation through Coder Leader and service coders
/verify-dev     Evaluate Code Done
/handoff-qc     Create QC handoff after DEV_DONE
/qc             Run QC and classify bugs
/bug            Create or route blocker/non-blocker bug
/sync-memory    Persist durable memory updates
/skills         Maintain installed skills and skill registry metadata
/resume-task    Continue a task from its current state
/aw-init        Scaffold .agent/+.runtime/+CLAUDE.md into another project (post-plugin-install)
/policy-check   Validate transition, gate, exception, or artifact snapshot
```
