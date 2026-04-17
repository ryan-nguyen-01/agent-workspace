# Skill Guide

![Skill composition](diagrams/08-skill-composition.svg)

This document explains how skills work, how they are organized, and how agents use them.

## What is a skill?

A skill is a **reusable capability** that an agent can load to gain domain-specific knowledge or procedures. Skills are not agents — they do not have independent state, permissions, or workflow ownership.

```text
Agent = role + responsibility + permissions + workflow state
Skill = knowledge + procedures + best practices for a domain
```

Key principle from R-014:

```text
One agent can use many skills.
One skill can be used by many agents.
Skills are selected by task context, not agent identity.
```

## Skill inventory

The system includes 227 skills in two categories:

### 12 workflow skills

These power the workflow agents and are prefixed with `skill-`:

| Skill                    | Used by                                | Purpose                                 |
| ------------------------ | -------------------------------------- | --------------------------------------- |
| skill-project-brain      | Coordinator, Onboarding, Memory Update | Manage project brain files              |
| skill-project-onboarding | Onboarding                             | Build initial project brain by scanning |
| skill-agent-factory      | Agent Factory                          | Generate service-specific coder agents  |
| skill-task-analysis      | Task Analysis                          | Convert tasks into normalized spec      |
| skill-coder-leader       | Coder Leader                           | Coordinate service coders               |
| skill-service-coder      | Generated Coders                       | Implement code within scoped boundaries |
| skill-dev-verification   | Dev Verification                       | Evaluate Code Done status               |
| skill-qc-handoff         | QC Handoff                             | Create Dev-to-QC handoff document       |
| skill-qc-runner          | QC Runner                              | Run QC and record test results          |
| skill-bug-routing        | Bug Router, QC Runner                  | Classify and route defects              |
| skill-memory-update      | Memory Update                          | Persist durable learnings               |
| skill-workflow-policy    | Workflow Policy                        | Validate transitions and gates          |

### 215 technical skills

These provide domain expertise across technology stacks:

| Category            | Example skills                                                                 |
| ------------------- | ------------------------------------------------------------------------------ |
| Frontend Frameworks | react, angular, vue, svelte, next-best-practices, astro                        |
| Backend Frameworks  | fastapi-python, nestjs-clean-typescript, java-spring-development, ruby-rails   |
| Databases & ORM     | postgresql-best-practices, prisma, drizzle-orm, supabase, redis-best-practices |
| Mobile              | flutter, building-native-ui, expo-\*, android-development                      |
| Cloud & DevOps      | aws-cloud-services, docker, cloudformation, lambda, azure-kubernetes           |
| Testing             | playwright-best-practices, python-testing, rspec                               |
| Go Language         | go-concurrency, go-testing, go-error-handling, golang-pro                      |
| CSS & Styling       | tailwindcss, scss-best-practices, styled-components-best-practices, shadcn     |
| Architecture        | api-design-principles, microservices, loom-event-driven                        |
| State Management    | redux-toolkit, zustand-state-management, react-query                           |
| Payment             | stripe-best-practices, payment-integration, paypal-integration                 |
| Knowledge Patches   | \*-knowledge-patch (latest framework/library updates)                          |

### External skills

Skills installed from `skills.sh` or third-party sources. See [external-skills.md](external-skills.md) for the full registry.

## How skills are loaded

Skills follow a **progressive loading** model — only load what the task needs:

### 1. Required skills

Always loaded for an agent's core responsibility. Defined in the agent contract.

```text
Coordinator always loads: skill-project-brain, skill-workflow-policy
QC Runner always loads: skill-qc-runner, skill-bug-routing
Generated Coder always loads: skill-service-coder
```

### 2. Optional skills

Loaded only when the task context requires them:

```text
Auth/password/token task → security skill
Database schema task → database/migration skill
Frontend UI task → accessibility skill
Payment task → security + audit skill
Performance issue → performance/observability skill
```

### 3. Contextual skills

Selected from project and service metadata. These match the project's actual stack:

```text
Project uses NestJS + Prisma + PostgreSQL
  → nestjs-clean-typescript, prisma, postgresql-best-practices

Project uses React + TailwindCSS
  → react, tailwindcss

Project uses FastAPI + SQLAlchemy
  → fastapi-python, postgresql-best-practices
```

## Skill composition for generated coders

A generated service coder combines skills from multiple categories:

```text
coder-payment-service might use:
  Workflow:    skill-service-coder
  Language:    typescript
  Framework:   nestjs-clean-typescript
  Database:    prisma, postgresql-best-practices
  API:         api-design-principles
  Security:    stripe-best-practices, payment-integration
  Testing:     playwright-best-practices
  Artifact:    skill-qc-handoff
```

### Skill declaration in agent contracts

Generated coders declare skills in their contract:

```yaml
skills:
  required_skills:
    - skill-service-coder
  optional_skills:
    - skill-dev-verification
    - skill-memory-update
  contextual_skills:
    language: [typescript]
    framework: [nestjs-clean-typescript]
    database: [prisma, postgresql-best-practices]
    api: [api-design-principles]
    testing: []
    security: []
    observability: []
```

See also: [skill-composition.md](skill-composition.md) for the full composition standard.

## Skill files

Every skill is a folder under `.claude/skills/` containing a `SKILL.md` file:

```text
.claude/skills/
├── skill-project-brain/SKILL.md        ← Workflow skill
├── react/SKILL.md                      ← Technical skill
├── postgresql-best-practices/SKILL.md  ← Technical skill
├── playwright-best-practices/SKILL.md  ← External skill
└── ...
```

### SKILL.md structure

Each skill file typically contains:

```text
Name and description
When to use this skill
Core principles and best practices
Code patterns and examples
Anti-patterns to avoid
Integration notes with other skills
```

## Knowledge patches

Skills with the `-knowledge-patch` suffix contain updates for frameworks and libraries that changed after the AI model's training cutoff:

```text
fastapi-knowledge-patch     → FastAPI 0.112-0.135.3 changes
prisma-knowledge-patch      → Prisma v7 ESM rewrite
django-knowledge-patch      → Django 6.0 composite PKs
tailwind-knowledge-patch    → Tailwind CSS v4.1 changes
```

Load the knowledge patch **before** working with the corresponding framework to avoid using outdated APIs.

## Conflict resolution

When two skills provide conflicting guidance:

```text
1. Workflow rules and service brain win over generic skill guidance
2. Project-specific conventions win over generic best practices
3. Security skills take priority for auth/payment/PII tasks
4. Knowledge patches override base skill guidance for version-specific APIs
```

## Related documents

- [skill-composition.md](skill-composition.md) — Full skill composition standard
- [external-skills.md](external-skills.md) — Installed external skills
- [agent-catalog.md](agent-catalog.md) — Agent descriptions and their skills
- [deep-onboarding.md](deep-onboarding.md) — How onboarding detects project stack for skill selection
