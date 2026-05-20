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
R-014-11: Total skills loaded per agent execution must not exceed the skill budget (see Selection algorithm).
R-014-12: Contextual skill selection must be deterministic from inputs in the order defined by Selection algorithm.
R-014-13: A skill is eligible only if its name appears in .runtime/context/skill-registry.yaml or .claude/skills/<name>/SKILL.md exists.
R-014-14: If two candidate skills have overlapping scope (e.g. two ORMs), select the one referenced by service-brain or project-brain; never load both.
R-014-15: Skill updates must go through /skills. Do not mutate installed skills, skills-lock.json, or skill-registry risk metadata from onboarding, coder generation, or implementation commands.
R-014-16: A newly updated skill must not be attached to generated coders automatically; Agent Factory must re-evaluate it through skill-registry.yaml and approval gates.
R-014-17: Runtime agents must not scan or read all of .claude/skills/**. Use .runtime/context/skill-registry.yaml first, select a minimal candidate set, then read only the selected skill's SKILL.md and directly referenced files.
R-014-18: Framework maintenance tasks must not load technical skills unless the task explicitly edits skill metadata, skill files, or stack-selection behavior.
R-014-19: Skill selection must consider project_profile.archetypes and service profile.archetypes before falling back to generic project language/framework metadata.
R-014-20: task-analysis.yaml.context_plan.budget.max_skill_files is the hard contextual skill budget unless Coordinator records an approved exception or a high-risk trigger requires expansion.
R-014-21: Agents must record dropped candidate skills when a budget cut occurs so missing context can be audited later.
```

## Selection algorithm (contextual_skills)

When an agent needs to pick contextual skills from the 219 technical skills, apply this deterministic algorithm:

```text
Step 1. Build candidate set from .runtime/context/skill-registry.yaml without opening .claude/skills/**.
        Inputs (priority order, dedup by skill name):
          a. service profile archetypes (backend-api, frontend-web, mobile-app, etc.)
          b. project_profile archetypes
          c. service-brain stack    (language, framework, db, queue, api, frontend)
          d. project-brain stack    (primary_languages, frameworks)
          e. task-analysis tags     (security|perf|a11y|data|migration|ui|ops)
          f. impacted_services      (intersect their service-brain stacks)

Step 2. Drop ineligible candidates:
          - skill not in skill-registry and no .claude/skills/<name>/SKILL.md
          - skill in service-brain forbidden_skills (if defined)
          - skill conflicts with a higher-priority candidate (R-014-14)

Step 3. Rank remaining candidates:
          1) service-stack match
          2) task-intent match (security skills for auth task, etc.)
          3) project-stack match
          4) risk-area match (from task-analysis.risks)

Step 4. Apply skill budget (R-014-11 and context_plan when present):
          - workflow agents: max 3 contextual skills
          - generated service coders: max 5 contextual skills
          - task-analysis.yaml.context_plan.budget.max_skill_files overrides the default when present
          - if budget exceeded, drop lowest-ranked candidates and record dropped[] in task artifact

Step 5. Read only selected skills, then record selection in task-analysis.yaml or coder-results.yaml:
          skills_used:
            required: [...]
            optional: [...]
            contextual: [...]
            dropped: [{name, reason}]   # when budget cut anything
            reason: "<one line per chosen skill>"
```

## Worked example

```yaml
# Inputs
task_intent: feature
impacted_services: [api-orders]
service_brain.api-orders.stack: {language: typescript, framework: nestjs, db: postgres, orm: prisma}
task_analysis.risks: [auth-bypass, slow-query]

# Output (budget = 5 for service coder)
skills_used:
  required: [skill-service-coder]
  contextual:
    - {name: typescript-advanced-types, reason: service stack match}
    - {name: nestjs-clean-typescript,   reason: framework match}
    - {name: prisma,                    reason: orm match}
    - {name: postgresql-best-practices, reason: db + slow-query risk}
    - {name: api-design-principles,     reason: auth-bypass risk on api}
  dropped:
    - {name: typeorm, reason: conflicts with prisma (R-014-14)}
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
