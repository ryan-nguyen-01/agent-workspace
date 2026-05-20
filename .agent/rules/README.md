# Rules Index

Rules are mandatory policy files. Agents and commands must follow these rules before acting.

## Rule loading principle

```text
Read only the rule files required by the active command or agent.
If a rule conflicts with an agent file, the rule wins.
If a rule conflicts with workflow.md, workflow.md defines the state machine and this folder defines the enforcement details.
```

## Rule files

```text
00-core-rules.md                 Global invariants
01-project-brain-rules.md        Project Brain and freshness
02-onboarding-rules.md           Onboarding boundaries
03-agent-factory-rules.md        Generated coder creation
04-task-analysis-rules.md        Task normalization
05-coder-leader-rules.md         Multi-service coordination
06-service-coder-rules.md        Generated coder behavior
07-dev-verification-rules.md     Code Done gate
08-qc-rules.md                   QC execution
09-bug-routing-rules.md          Blocking and non-blocking bugs
10-memory-rules.md               Durable memory updates
11-approval-gates.md             User approval requirements
12-artifact-contracts.md         Required artifacts and schemas
13-security-secret-rules.md      Secrets, PII, auth-sensitive work
14-skill-composition-rules.md    Skill composition and multi-skill agents
15-model-routing-observability-rules.md  Model profiles, activity dashboard, response UI, token/cost reporting
```
