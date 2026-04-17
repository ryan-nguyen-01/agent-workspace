# R-014: Skill Composition Rules

## Applies to

All agents, Agent Factory, Coder Leader, Task Analysis, Workflow Policy.

## Core principle

```text
A skill is a reusable capability, not a one-to-one agent identity.
One agent may use many skills.
One skill may be used by many agents.
Skills are selected by task context, service stack, risk area, artifact need, and workflow state.
```

## Rules

```text
R-014-01: Do not design agents as if each agent has exactly one skill.
R-014-02: Every agent may declare required_skills, optional_skills, and contextual_skills.
R-014-03: Required skills are always loaded for that agent's primary command.
R-014-04: Optional skills are loaded only when the task needs that capability.
R-014-05: Contextual skills are selected from project/service/task metadata.
R-014-06: Generated service coders must inherit workflow skills and service-specific technical skills.
R-014-07: Skill selection must be recorded in task artifacts when it affects implementation or verification.
R-014-08: If two skills conflict, workflow rules and service brain win.
R-014-09: Skills must not override allowed_write_paths or approval gates.
R-014-10: Prefer minimal skill loading: load enough skills to do the job, not every possible skill.
```

## Skill categories

```text
workflow_skills: project-brain, task-analysis, coder-leader, service-coder, dev-verification, qc, memory-update
technical_skills: language, framework, database, queue, API style, frontend stack, DevOps tooling
quality_skills: testing, security, performance, accessibility, observability
artifact_skills: handoff, bug-routing, documentation, migration notes
```

## Required artifact fields

When a task uses meaningful skills, record them in:

```yaml
skills_used:
  required: []
  optional: []
  contextual: []
  reason: []
```

## Violation handling

If an agent lacks a required capability for the task, stop and ask Coder Leader or Coordinator to add the needed skill or route to another agent.
