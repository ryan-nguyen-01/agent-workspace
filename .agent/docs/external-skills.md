# External Skills from skills.sh

This document tracks skills installed from `skills.sh` for the Project-Aware Dynamic Agent System.

> See also: [skill-composition.md](skill-composition.md) — how skills are selected and attached to agents

## Relationship to skill-registry.yaml

```
external-skills.md (this file)           ← Human docs: what was installed, from where, security notes
.runtime/context/skill-registry.yaml      ← Machine config: selection policy, risk levels, auto-attach rules
```

- **Canonical source for skill selection at runtime** is `skill-registry.yaml`. Agent Factory and Coder Leader read that file to decide which skills to attach.
- **This file** (`external-skills.md`) is documentation: install history, sources, agent-to-skill mapping, and security audit notes. Update it when installing new skills.
- When adding or updating a skill: use `/skills` and update `skill-registry.yaml`, `skills-lock.json`, this file, and `CHANGELOG.md` when behavior or risk changes.

## Installation policy

```text
Target agent: claude-code
Install location: .claude/skills/
Telemetry: disabled with DISABLE_TELEMETRY=1
Install mode: project-local, copied
```

These skills are third-party instructions and may include scripts or references. Review before use because skills run with full agent permissions.

## Installed core skills

| Skill                            | Source                                         | Primary use in this system                            | Use when                                                    |
| -------------------------------- | ---------------------------------------------- | ----------------------------------------------------- | ----------------------------------------------------------- |
| `find-skills`                    | `vercel-labs/skills`                           | Discover more skills from skills.sh                   | Onboarding finds stack gaps or user asks for new capability |
| `writing-plans`                  | `obra/superpowers`                             | Write implementation plans                            | Task Analysis or Coder Leader needs a structured plan       |
| `executing-plans`                | `obra/superpowers`                             | Execute written plans with checkpoints                | Coder Leader executes a sequential implementation plan      |
| `subagent-driven-development`    | `obra/superpowers`                             | Dispatch task-focused subagents with review loops     | Multi-service or parallelizable task needs isolated workers |
| `dispatching-parallel-agents`    | `obra/superpowers`                             | Parallelize independent agent work                    | Coder Leader has independent service assignments            |
| `systematic-debugging`           | `obra/superpowers`                             | Root-cause-first debugging                            | Bugfix, blocker bug, production issue, flaky behavior       |
| `test-driven-development`        | `obra/superpowers`                             | TDD when tests are required                           | Only when service test policy allows/requires test files    |
| `verification-before-completion` | `obra/superpowers`                             | Avoid claiming done without verification              | Dev Verification and Coder Leader before Code Done          |
| `requesting-code-review`         | `obra/superpowers`                             | Request focused review                                | Before DEV_DONE or after complex implementation             |
| `receiving-code-review`          | `obra/superpowers`                             | Process review feedback correctly                     | After review returns findings                               |
| `finishing-a-development-branch` | `obra/superpowers`                             | Finish dev branch with checks                         | End of a dev cycle if branch workflow is used               |
| `using-git-worktrees`            | `obra/superpowers`                             | Isolated workspaces                                   | Only when user/project wants worktree-based isolation       |
| `webapp-testing`                 | `anthropics/skills`                            | Local web application testing with Playwright scripts | QC Runner or manual verification for web apps               |
| `playwright-best-practices`      | `currents-dev/playwright-best-practices-skill` | Playwright test design/debugging                      | QC/testing when Playwright is project-approved              |
| `api-design-principles`          | `wshobson/agents`                              | API contract and design guidance                      | Task touches REST/GraphQL/gRPC/API design                   |

## Security notes from installer

```text
find-skills: Gen Safe, Socket 0 alerts, Snyk Med Risk
obra/superpowers skills: Gen Safe, Socket 0 alerts, Snyk Low Risk
webapp-testing: Gen Safe, Socket 0 alerts, Snyk Low Risk
playwright-best-practices: Gen Safe, Socket 0 alerts, Snyk Low Risk
api-design-principles: Gen Safe, Socket 0 alerts, Snyk Low Risk
```

Because `find-skills` reported Snyk Med Risk, agents should use it for discovery only and should not execute bundled scripts from it without review.

## Mapping to `.claude` agents

### Coordinator

```yaml
required_skills:
  - find-skills
contextual_skills:
  planning:
    - writing-plans
  policy:
    - verification-before-completion
```

### Onboarding Agent

```yaml
contextual_skills:
  discovery:
    - find-skills
  planning:
    - writing-plans
```

### Agent Factory

```yaml
contextual_skills:
  discovery:
    - find-skills
  planning:
    - writing-plans
```

### Task Analysis Agent

```yaml
contextual_skills:
  planning:
    - writing-plans
  api:
    - api-design-principles
```

### Coder Leader

```yaml
contextual_skills:
  planning:
    - writing-plans
    - executing-plans
  orchestration:
    - subagent-driven-development
    - dispatching-parallel-agents
  verification:
    - verification-before-completion
  review:
    - requesting-code-review
    - receiving-code-review
```

### Generated Service Coder

```yaml
contextual_skills:
  debugging:
    - systematic-debugging
  testing_when_policy_allows:
    - test-driven-development
  verification:
    - verification-before-completion
  api:
    - api-design-principles
```

### Dev Verification Agent

```yaml
required_skills:
  - verification-before-completion
contextual_skills:
  debugging:
    - systematic-debugging
  review:
    - receiving-code-review
```

### QC Runner

```yaml
contextual_skills:
  web_testing:
    - webapp-testing
  playwright_when_policy_allows:
    - playwright-best-practices
  debugging:
    - systematic-debugging
```

### Bug Router

```yaml
contextual_skills:
  debugging:
    - systematic-debugging
  review:
    - receiving-code-review
```

### Memory Update Agent

```yaml
contextual_skills:
  verification:
    - verification-before-completion
```

## Skills intentionally deferred until onboarding

Do not install stack-specific skills until Project Brain identifies the actual stack.

Examples to decide later:

```text
React / Next.js / Vue / Angular skills
NestJS / FastAPI / Spring / Rails skills
Postgres / Prisma / TypeORM / MongoDB skills
Docker / Kubernetes / GitHub Actions skills
Cloud-provider skills
Auth-provider skills
```

Use `/onboard` first, then use `find-skills` or `npx skills find <query>` to select stack-specific skills.

---

# Stack Skill Pack - installed on 2026-04-17

Purpose: these skills are pre-installed so Agent Factory can attach the right stack skills when generating service coder agents. Do not attach the entire pack to every coder. Select only the skills that match the detected service stack in Project Brain and Service Brain.

## Installed stack skills

### Frontend, React, Vercel

Source: https://skills.sh/vercel-labs/agent-skills

- `vercel-react-best-practices`
- `web-design-guidelines`
- `vercel-composition-patterns`
- `vercel-react-native-skills`
- `deploy-to-vercel`

### Next.js

Source: https://skills.sh/vercel-labs/next-skills

- `next-best-practices`
- `next-cache-components`

### UI and design systems

Sources: https://skills.sh/shadcn/ui and https://skills.sh/wshobson/agents

- `shadcn`
- `tailwind-design-system`

### TypeScript, Node.js, Python

Source: https://skills.sh/wshobson/agents

- `typescript-advanced-types`
- `nodejs-backend-patterns`
- `python-performance-optimization`

### Auth

Source: https://skills.sh/better-auth/skills

- `better-auth-best-practices`

### Databases and backend platforms

Sources: https://skills.sh/supabase/agent-skills, https://skills.sh/neondatabase/agent-skills, https://skills.sh/get-convex/agent-skills

- `supabase`
- `supabase-postgres-best-practices`
- `neon-postgres`
- `convex-quickstart`
- `convex-setup-auth`
- `convex-migration-helper`
- `convex-create-component`
- `convex-performance-audit`

### Firebase and Genkit

Source: https://skills.sh/firebase/agent-skills

- `firebase-basics`
- `firebase-auth-basics`
- `firebase-hosting-basics`
- `firebase-app-hosting-basics`
- `firebase-firestore-standard`
- `firebase-firestore-enterprise-native-mode`
- `firebase-data-connect`
- `firebase-ai-logic`
- `developing-genkit-js`
- `developing-genkit-dart`

### Mobile and Expo

Source: https://skills.sh/expo/skills

- `building-native-ui`
- `native-data-fetching`
- `expo-tailwind-setup`
- `upgrading-expo`
- `expo-cicd-workflows`
- `expo-api-routes`
- `expo-deployment`
- `expo-dev-client`

### Vue and Vite

Sources: https://skills.sh/hyf0/vue-skills and https://skills.sh/antfu/skills

- `vue-best-practices`
- `vue`
- `vite`

### CI and GitHub Actions

Source: https://skills.sh/xixu-me/skills

- `github-actions-docs`

### Azure cloud

Source: https://skills.sh/microsoft/azure-skills

- `azure-enterprise-infra-planner`
- `azure-kubernetes`
- `azure-quotas`
- `azure-upgrade`
- `microsoft-foundry`

## Attempted but not installed

These skills were requested but the source repository timed out or did not select the requested skill during installation. Retry only when the project actually needs them.

- `gh-cli`: source `https://github.com/github/awesome-copilot`, clone timed out after 60 seconds.
- `git-commit`: source `https://github.com/github/awesome-copilot`, clone timed out after 60 seconds.
- `azure-ai`: source `https://github.com/microsoft/github-copilot-for-azure`, clone timed out after 60 seconds.
- `azure-observability`: source `https://github.com/microsoft/github-copilot-for-azure`, clone timed out after 60 seconds.
- `azure-compute`: source `https://github.com/microsoft/github-copilot-for-azure`, clone timed out after 60 seconds.
- `azure-postgres`: source `https://github.com/microsoft/github-copilot-for-azure`, clone timed out after 60 seconds.
- `azure-messaging`: source `https://github.com/microsoft/github-copilot-for-azure`, clone timed out after 60 seconds.
- `azure-cloud-migrate`: source `https://github.com/microsoft/github-copilot-for-azure`, clone timed out after 60 seconds.
- `azure-hosted-copilot-sdk`: source `https://github.com/microsoft/github-copilot-for-azure`, clone timed out after 60 seconds.
- `azure-cost-optimization`: requested from `https://github.com/microsoft/azure-skills`, but the installer did not select it in the installed set.

## Agent Factory stack mapping

Use this mapping when building a service coder agent.

- React app: `vercel-react-best-practices`, `web-design-guidelines`; add `tailwind-design-system` or `shadcn` only if detected.
- Next.js app: `next-best-practices`, `next-cache-components`, `vercel-react-best-practices`; add `deploy-to-vercel` only if deployment scope includes Vercel.
- React Native or Expo app: `vercel-react-native-skills`, `building-native-ui`, `native-data-fetching`; add Expo-specific skills only when Expo is detected.
- Vue app: `vue-best-practices`, `vue`; add `vite` only when Vite is detected.
- Node.js backend: `nodejs-backend-patterns`; add `typescript-advanced-types` when TypeScript is detected.
- Python service: `python-performance-optimization` only when performance, scalability, or Python-heavy code is in scope.
- Supabase service: `supabase`, `supabase-postgres-best-practices`.
- Neon/Postgres service: `neon-postgres`; add `supabase-postgres-best-practices` only for general Postgres rules when Supabase is not involved and the skill content is applicable.
- Convex service: choose from `convex-quickstart`, `convex-setup-auth`, `convex-migration-helper`, `convex-create-component`, `convex-performance-audit` based on task type.
- Firebase service: start with `firebase-basics`; add auth, hosting, app hosting, Firestore, Data Connect, AI Logic, or Genkit skills only when those products are detected.
- Better Auth service: `better-auth-best-practices`.
- CI workflow: `github-actions-docs`.
- Azure infrastructure: choose only the relevant Azure skill: `azure-enterprise-infra-planner`, `azure-kubernetes`, `azure-quotas`, `azure-upgrade`, or `microsoft-foundry`.

## Safety notes

- Installed third-party skills run with full agent permissions. Review a skill before first use on a sensitive service.
- Visible installer output reported no Socket alerts for installed stack skills.
- Medium-risk entries visible in installer output included `web-design-guidelines`, `shadcn`, `github-actions-docs`, `azure-kubernetes`, `azure-upgrade`, and `microsoft-foundry`.
- Restart Claude/Codex after installation so newly installed skills are picked up by the agent runtime.

---

# Stack Skill Pack Batch 2 - installed on 2026-04-17

Purpose: close missing coverage for Java, Go, Rust, TailwindCSS, and MUI. Agent Factory must treat these as optional stack capabilities and attach them only when Project Brain or Service Brain detects the matching service stack.

## Installed Java and Spring skills

Sources:

- https://skills.sh/jeffallan/claude-skills/java-architect
- https://skills.sh/jeffallan/claude-skills/spring-boot-engineer
- https://skills.sh/mindrally/skills/spring-framework
- https://skills.sh/mindrally/skills/java-spring-development

Installed skills:

- <code>java-architect</code>
- <code>spring-boot-engineer</code>
- <code>spring-framework</code>
- <code>java-spring-development</code>

Use when:

- Service uses Java 17+, Java 21, Maven, Gradle, Spring Boot, Spring MVC, WebFlux, Spring Security, JPA, Hibernate, Spring Cloud, Kafka, RabbitMQ, or enterprise Java microservices.

## Installed Go skills

Sources:

- https://skills.sh/rmyndharis/antigravity-skills/golang-pro
- https://skills.sh/cxuu/golang-skills

Installed skills:

- <code>golang-pro</code>
- <code>go-code-review</code>
- <code>go-concurrency</code>
- <code>go-context</code>
- <code>go-control-flow</code>
- <code>go-data-structures</code>
- <code>go-declarations</code>
- <code>go-defensive</code>
- <code>go-documentation</code>
- <code>go-error-handling</code>
- <code>go-functional-options</code>
- <code>go-functions</code>
- <code>go-generics</code>
- <code>go-interfaces</code>
- <code>go-linting</code>
- <code>go-logging</code>
- <code>go-naming</code>
- <code>go-packages</code>
- <code>go-performance</code>
- <code>go-style-core</code>
- <code>go-testing</code>

Use when:

- Service uses Go modules, Gin, Echo, Fiber, gRPC, REST APIs, CLIs, concurrency-heavy services, context cancellation, performance-sensitive services, or idiomatic Go review/test work.

## Installed Rust skills

Sources:

- https://skills.sh/mindrally/skills/rust
- https://skills.sh/nevaberry/nevaberry-plugins/rust-knowledge-patch

Installed skills:

- <code>rust</code>
- <code>rust-knowledge-patch</code>
- <code>tokio-knowledge-patch</code>
- <code>axum-knowledge-patch</code>
- <code>serde-knowledge-patch</code>
- <code>sqlx-knowledge-patch</code>
- <code>tauri-knowledge-patch</code>

Use when:

- Service uses Rust, Cargo, Tokio, Axum, Actix, Serde, SQLx, Tauri, async Rust, systems programming, performance-critical services, or Rust 2024 edition features.

## Installed UI framework skills

Sources:

- https://skills.sh/mindrally/skills/tailwindcss
- https://skills.sh/blencorp/claude-code-kit/mui

Installed skills:

- <code>tailwindcss</code>
- <code>mui</code>

Use when:

- Service uses TailwindCSS utilities, Tailwind v4 migration, utility-first component styling, MUI v7, Material UI themes, MUI sx prop, MUI slots or slotProps, responsive Material UI components, or MUI with Tailwind CSS layers.

## Attempted but not installed in Batch 2

- <code>rust-engineer</code>: source <code>https://github.com/404kidwiz/claude-supercode-skills</code> failed with authentication error during clone.
- <code>rust</code> from <code>https://github.com/nevaberry/nevaberry-plugins</code>: wrong skill name. Correct installed skill is <code>rust-knowledge-patch</code>.

## Agent Factory stack mapping extension

- Java service: start with <code>java-architect</code>. Add <code>spring-boot-engineer</code>, <code>spring-framework</code>, or <code>java-spring-development</code> only when Spring/Spring Boot evidence exists.
- Go service: start with <code>golang-pro</code> and <code>go-style-core</code>. Add targeted Go skills for the task, such as <code>go-concurrency</code>, <code>go-context</code>, <code>go-error-handling</code>, <code>go-testing</code>, or <code>go-performance</code>.
- Rust service: start with <code>rust</code> and <code>rust-knowledge-patch</code>. Add <code>tokio-knowledge-patch</code>, <code>axum-knowledge-patch</code>, <code>serde-knowledge-patch</code>, <code>sqlx-knowledge-patch</code>, or <code>tauri-knowledge-patch</code> only when those crates/frameworks are detected.
- Tailwind UI service: use <code>tailwindcss</code>. Add <code>tailwind-design-system</code> only for design-system level work.
- MUI UI service: use <code>mui</code>. If the same service also uses Tailwind, include both <code>mui</code> and <code>tailwindcss</code> and note CSS layer/order constraints in the generated coder agent.

## Batch 2 security notes

Installer output reported 0 Socket alerts for all installed Batch 2 skills. Most installed Batch 2 skills were Low Risk. The <code>rust</code> skill from mindrally reported Gen Low Risk and Snyk Low Risk.

---

# Stack Skill Pack Batch 3 - installed on 2026-04-17

Purpose: extend coder-agent coverage to broader full-stack projects: .NET/C#, PHP/Laravel, Ruby/Rails, Python backend, Angular, Svelte, Astro, Flutter, Android/Kotlin, database/ORM, and frontend quality skills. Agent Factory must still attach only the relevant subset per service.

## Installed .NET and C# skills

Sources:

- https://skills.sh/mindrally/skills/aspnet-core
- https://skills.sh/mindrally/skills/blazor
- https://skills.sh/jeffallan/claude-skills/csharp-developer
- https://skills.sh/aaronontheweb/dotnet-skills/modern-csharp-coding-standards

Installed skills:

- <code>aspnet-core</code>
- <code>blazor</code>
- <code>csharp-developer</code>
- <code>modern-csharp-coding-standards</code>

Use when:

- Service uses C#, .NET 8+, ASP.NET Core, Minimal APIs, controllers, Entity Framework Core, Blazor Server, Blazor WASM, xUnit, NUnit, or enterprise .NET patterns.

## Installed PHP and Laravel skills

Sources:

- https://skills.sh/mindrally/skills/php-development
- https://skills.sh/mindrally/skills/laravel-development
- https://skills.sh/1weiho/laravel-upgrade-skill/laravel-upgrade

Installed skills:

- <code>php-development</code>
- <code>laravel-development</code>
- <code>laravel-upgrade</code>

Use when:

- Service uses PHP 8+, Composer, PSR standards, Laravel, Eloquent, migrations, queues, middleware, validation, Blade, Sail, or Laravel version upgrades.

## Installed Ruby and Rails skills

Sources:

- https://skills.sh/mindrally/skills/ruby
- https://skills.sh/mindrally/skills/ruby-rails
- https://skills.sh/mindrally/skills/rspec
- https://skills.sh/nevaberry/nevaberry-plugins/rails-knowledge-patch

Installed skills:

- <code>ruby</code>
- <code>ruby-rails</code>
- <code>rspec</code>
- <code>rails-knowledge-patch</code>

Use when:

- Service uses Ruby 3.x, Rails, ActiveRecord, Rails MVC, Rails caching, service objects, RSpec, FactoryBot, or Rails version-specific behavior.

## Installed Python backend skills

Sources:

- https://skills.sh/mindrally/skills/fastapi-python
- https://skills.sh/mindrally/skills/fastapi-microservices-serverless
- https://skills.sh/mindrally/skills/rest-api-django
- https://skills.sh/mindrally/skills/python-testing
- https://skills.sh/mindrally/skills/python-uv
- https://skills.sh/nevaberry/nevaberry-plugins/django-knowledge-patch
- https://skills.sh/nevaberry/nevaberry-plugins/fastapi-knowledge-patch

Installed skills:

- <code>fastapi-python</code>
- <code>fastapi-microservices-serverless</code>
- <code>rest-api-django</code>
- <code>python-testing</code>
- <code>python-uv</code>
- <code>django-knowledge-patch</code>
- <code>fastapi-knowledge-patch</code>

Use when:

- Service uses Python backend APIs, FastAPI, async Python, Pydantic, Django REST Framework, pytest, uv dependency management, serverless Python, or microservice Python APIs.

## Installed frontend framework skills

Sources:

- https://skills.sh/mindrally/skills/angular
- https://skills.sh/mindrally/skills/angular-development
- https://skills.sh/mindrally/skills/svelte
- https://skills.sh/mindrally/skills/sveltekit
- https://skills.sh/mindrally/skills/astro
- https://skills.sh/nevaberry/nevaberry-plugins/angular-knowledge-patch
- https://skills.sh/nevaberry/nevaberry-plugins/svelte-knowledge-patch
- https://skills.sh/nevaberry/nevaberry-plugins/astro-knowledge-patch

Installed skills:

- <code>angular</code>
- <code>angular-development</code>
- <code>angular-knowledge-patch</code>
- <code>svelte</code>
- <code>sveltekit</code>
- <code>svelte-knowledge-patch</code>
- <code>astro</code>
- <code>astro-knowledge-patch</code>

Use when:

- Service uses Angular, Angular standalone components, Angular signals, Svelte 5, SvelteKit, Astro, islands architecture, SSR, SSG, or framework-specific routing/data loading.

## Installed mobile/native skills

Sources:

- https://skills.sh/mindrally/skills/flutter
- https://skills.sh/mindrally/skills/kotlin-development
- https://skills.sh/mindrally/skills/android-development
- https://skills.sh/nevaberry/nevaberry-plugins/flutter-knowledge-patch
- https://skills.sh/nevaberry/nevaberry-plugins/kotlin-knowledge-patch
- https://skills.sh/nevaberry/nevaberry-plugins/swift-knowledge-patch

Installed skills:

- <code>flutter</code>
- <code>flutter-knowledge-patch</code>
- <code>kotlin-development</code>
- <code>kotlin-knowledge-patch</code>
- <code>android-development</code>
- <code>swift-knowledge-patch</code>

Use when:

- Service uses Flutter, Dart, Riverpod, Bloc, Android Kotlin, Jetpack Compose, Kotlin coroutines, Kotlin Multiplatform, or Swift/iOS-specific code.

## Installed Node backend, API, ORM, and database skills

Sources:

- https://skills.sh/mindrally/skills/nestjs-clean-typescript
- https://skills.sh/mindrally/skills/fastify-typescript
- https://skills.sh/mindrally/skills/koa-typescript
- https://skills.sh/mindrally/skills/graphql
- https://skills.sh/mindrally/skills/prisma
- https://skills.sh/mindrally/skills/prisma-development
- https://skills.sh/mindrally/skills/drizzle-orm
- https://skills.sh/mindrally/skills/typeorm
- https://skills.sh/mindrally/skills/postgresql-best-practices
- https://skills.sh/mindrally/skills/mysql-best-practices
- https://skills.sh/mindrally/skills/redis-best-practices
- https://skills.sh/nevaberry/nevaberry-plugins/postgresql-knowledge-patch
- https://skills.sh/nevaberry/nevaberry-plugins/prisma-knowledge-patch
- https://skills.sh/nevaberry/nevaberry-plugins/drizzle-knowledge-patch

Installed skills:

- <code>nestjs-clean-typescript</code>
- <code>fastify-typescript</code>
- <code>koa-typescript</code>
- <code>graphql</code>
- <code>prisma</code>
- <code>prisma-development</code>
- <code>prisma-knowledge-patch</code>
- <code>drizzle-orm</code>
- <code>drizzle-knowledge-patch</code>
- <code>typeorm</code>
- <code>postgresql-best-practices</code>
- <code>postgresql-knowledge-patch</code>
- <code>mysql-best-practices</code>
- <code>redis-best-practices</code>

Use when:

- Service uses NestJS, Fastify, Koa, GraphQL, Prisma, Drizzle, TypeORM, PostgreSQL, MySQL, Redis, database migrations, query optimization, or schema design.

## Installed frontend quality, styling, and motion skills

Source: https://skills.sh/mindrally/skills

Installed skills:

- <code>accessibility-a11y</code>
- <code>scss-best-practices</code>
- <code>postcss-best-practices</code>
- <code>styled-components-best-practices</code>
- <code>framer-motion</code>
- <code>gsap</code>
- <code>tailwind-knowledge-patch</code>

Use when:

- Service changes accessibility, SCSS, PostCSS, styled-components, Framer Motion, GSAP, animations, or Tailwind version-sensitive behavior.

## Attempted but not installed in Batch 3

- <code>moai-lang-csharp</code>: source <code>https://github.com/modu-ai/moai-adk</code> no longer exposes this skill name. Available skills in that repo are named under <code>moai-\*</code> and do not include <code>moai-lang-csharp</code>.

## Agent Factory stack mapping extension

- .NET API: <code>csharp-developer</code>, <code>modern-csharp-coding-standards</code>, <code>aspnet-core</code>. Add <code>blazor</code> only for Blazor UI.
- Laravel service: <code>php-development</code>, <code>laravel-development</code>. Add <code>laravel-upgrade</code> only for version upgrade tasks.
- Ruby/Rails service: <code>ruby</code>, <code>ruby-rails</code>, <code>rails-knowledge-patch</code>. Add <code>rspec</code> only if project policy requires tests or task touches test code.
- FastAPI service: <code>fastapi-python</code>, <code>fastapi-knowledge-patch</code>. Add <code>fastapi-microservices-serverless</code> only for serverless or cloud-native microservices.
- Django API service: <code>rest-api-django</code>, <code>django-knowledge-patch</code>.
- Angular service: <code>angular</code>, <code>angular-development</code>, <code>angular-knowledge-patch</code>.
- Svelte/SvelteKit service: <code>svelte</code>, <code>sveltekit</code>, <code>svelte-knowledge-patch</code>.
- Astro service: <code>astro</code>, <code>astro-knowledge-patch</code>.
- Flutter service: <code>flutter</code>, <code>flutter-knowledge-patch</code>.
- Android/Kotlin service: <code>android-development</code>, <code>kotlin-development</code>, <code>kotlin-knowledge-patch</code>.
- Swift/iOS service: <code>swift-knowledge-patch</code>. Ask before generating a Swift-only coder if no richer Swift skill is installed.
- NestJS service: <code>nestjs-clean-typescript</code>, plus TypeScript skills if needed.
- Fastify service: <code>fastify-typescript</code>.
- Koa service: <code>koa-typescript</code>.
- GraphQL service: <code>graphql</code>.
- Prisma service: <code>prisma</code>, <code>prisma-development</code>, <code>prisma-knowledge-patch</code>.
- Drizzle service: <code>drizzle-orm</code>, <code>drizzle-knowledge-patch</code>.
- TypeORM service: <code>typeorm</code>.
- PostgreSQL service: <code>postgresql-best-practices</code>, <code>postgresql-knowledge-patch</code>.
- MySQL service: <code>mysql-best-practices</code>.
- Redis service: <code>redis-best-practices</code>, but review before use because installer reported Snyk High Risk.

## Batch 3 security notes

Installer output reported 0 Socket alerts for most Batch 3 skills. Exceptions visible in installer output:

- <code>rails-knowledge-patch</code>: Socket reported 1 alert.
- <code>laravel-upgrade</code>: Socket reported 1 alert.
- <code>redis-best-practices</code>: Snyk reported High Risk.

For these three, Agent Factory should mark them as available but require review before first use on sensitive code.

---

# Medusa Skill Pack - installed on 2026-04-17

Purpose: add MedusaJS/headless commerce coverage so Agent Factory can generate scoped coder agents for Medusa backend, Medusa Admin customizations, storefront integrations, and e-commerce storefront work.

## Installed official Medusa skills

Source: https://skills.sh/medusajs/medusa-agent-skills

Installed skills:

- <code>building-with-medusa</code>
- <code>building-admin-dashboard-customizations</code>
- <code>building-storefronts</code>
- <code>storefront-best-practices</code>
- <code>learning-medusa</code>

Use when:

- Service uses MedusaJS, Medusa modules, workflows, API routes, module links, Medusa Admin dashboard customizations, storefront SDK integration, carts, products, checkout, payment, shipping, or e-commerce storefront UX.

## Installed community Medusa skill

Source: https://skills.sh/greedychipmunk/agent-skills

Installed skill:

- <code>medusajs-developer</code>

Use when:

- Only after review or explicit user approval because installer reported higher risk than the official Medusa skill pack.

## Agent Factory Medusa mapping

- Medusa backend service: <code>building-with-medusa</code>, plus <code>typescript-advanced-types</code>, <code>nodejs-backend-patterns</code>, and database skills detected from the project.
- Medusa Admin service: <code>building-admin-dashboard-customizations</code>, plus React/UI skills detected from the admin customization stack.
- Medusa storefront service: <code>building-storefronts</code>, <code>storefront-best-practices</code>, plus frontend framework skills such as <code>next-best-practices</code>, <code>vercel-react-best-practices</code>, <code>tailwindcss</code>, <code>mui</code>, or <code>shadcn</code> when detected.
- Medusa learning/onboarding: <code>learning-medusa</code> only when the user asks for training/tutorial guidance. Do not attach it to production coder agents by default.
- Community fallback: <code>medusajs-developer</code> only when official skills are insufficient and the user approves its use.

## Medusa implementation rules for generated coder agents

- For backend mutations, prefer Medusa workflows and workflow steps instead of placing business logic in API routes.
- Keep Medusa layer boundaries explicit: Module, Workflow, API Route, Admin, Storefront.
- For cross-module reads, require the coder to consult the Medusa skill references before implementation.
- For storefront tasks, require Medusa JS SDK usage unless the project has a documented exception.
- For admin dashboard customizations, distinguish Medusa Admin UI routes/widgets from backend API routes.
- For e-commerce storefront changes, include accessibility, mobile responsiveness, SEO, product/cart/checkout UX, and error states in the QC handoff.

## Medusa security notes

Installer output reported:

- <code>building-with-medusa</code>: Gen Safe, Socket 0 alerts, Snyk Low Risk.
- <code>building-admin-dashboard-customizations</code>: Gen Safe, Socket 0 alerts, Snyk Low Risk.
- <code>building-storefronts</code>: Gen Safe, Socket 0 alerts, Snyk Low Risk.
- <code>learning-medusa</code>: Gen Med Risk, Socket 0 alerts, Snyk Low Risk.
- <code>storefront-best-practices</code>: Gen Low Risk, Socket 0 alerts, Snyk Med Risk.
- <code>medusajs-developer</code>: Gen High Risk, Socket 0 alerts, Snyk Med Risk.

---

# Messaging, Cache, and Container Skill Pack - installed on 2026-04-17

Purpose: add coverage for event streaming, message queues, task queues, Redis/cache, Docker, Kubernetes, Terraform, and reverse-proxy/container infrastructure. Agent Factory must attach these skills only when Project Brain or Service Brain detects broker/cache/container evidence.

## Installed Kafka, messaging, and event-driven skills

Sources:

- https://skills.sh/mindrally/skills/kafka-development
- https://skills.sh/mindrally/skills/microservices
- https://skills.sh/mindrally/skills/serverless
- https://skills.sh/mindrally/skills/websocket-development
- https://skills.sh/cosmix/loom
- https://skills.sh/rand/cc-polymath

Installed skills:

- <code>kafka-development</code>
- <code>microservices</code>
- <code>serverless</code>
- <code>websocket-development</code>
- <code>loom-event-driven</code>
- <code>discover-networking</code>

Use when:

- Service uses Apache Kafka, event streaming, producers, consumers, consumer groups, topics, partitions, dead letter topics, event-driven architecture, RabbitMQ/message queue patterns, pub/sub, sagas, CQRS, event sourcing, WebSocket fanout, broker-backed real-time communication, or distributed microservice messaging.

## Installed task queue skills

Sources:

- https://skills.sh/martinholovsky/claude-skills-generator/celery-expert
- https://skills.sh/vintasoftware/django-ai-plugins/django-celery-expert

Installed skills:

- <code>celery-expert</code>
- <code>django-celery-expert</code>

Use when:

- Service uses Celery, Celery Beat, Django Celery, Python background jobs, async workers, Redis broker, RabbitMQ broker, retry policies, dead letter queues, periodic tasks, task routing, or Flower/worker monitoring.

## Installed Redis and cache skills

Sources:

- https://skills.sh/redis/agent-skills/redis-development
- https://skills.sh/upstash/redis-js/redis-js
- https://skills.sh/intellectronica/agent-skills/upstash-redis-kv
- https://skills.sh/mindrally/skills/redis-best-practices

Installed skills:

- <code>redis-development</code>
- <code>redis-js</code>
- <code>upstash-redis-kv</code>
- <code>redis-best-practices</code> already installed in Batch 3

Use when:

- Service uses Redis, Upstash Redis, Redis cache, Redis sessions, Redis Pub/Sub, Redis Streams, Redis Queue, rate limiting, distributed locks, semantic cache, vector search, Redis Query Engine, or Redis-backed background jobs.

## Installed Docker, container, and infrastructure skills

Sources:

- https://skills.sh/mindrally/skills/docker
- https://skills.sh/nevaberry/nevaberry-plugins/docker-knowledge-patch
- https://skills.sh/nevaberry/nevaberry-plugins/kubernetes-knowledge-patch
- https://skills.sh/nevaberry/nevaberry-plugins/terraform-knowledge-patch
- https://skills.sh/nevaberry/nevaberry-plugins/nginx-knowledge-patch
- https://skills.sh/nevaberry/nevaberry-plugins/traefik-knowledge-patch

Installed skills:

- <code>docker</code>
- <code>docker-knowledge-patch</code>
- <code>kubernetes-knowledge-patch</code>
- <code>terraform-knowledge-patch</code>
- <code>nginx-knowledge-patch</code>
- <code>traefik-knowledge-patch</code>

Use when:

- Service uses Dockerfile, docker-compose, container images, multi-stage builds, .dockerignore, Kubernetes manifests, Helm-like deployment files, Terraform IaC, Nginx reverse proxy, Traefik routing, ingress, container networking, or infrastructure runtime changes.

## Attempted but not installed in this pack

- <code>event-driven</code> from <code>cosmix/loom</code>: skill name changed. Correct installed skill is <code>loom-event-driven</code>.
- <code>discover-protocols</code> from <code>rand/cc-polymath</code>: skill name changed. Correct installed skill is <code>discover-networking</code>.
- <code>redis-expert</code> from <code>lammesen/skills</code>: clone failed with authentication error. Use <code>redis-development</code>, <code>redis-js</code>, and existing <code>redis-best-practices</code> instead.

## Agent Factory messaging/cache/infra mapping

- Kafka service: <code>kafka-development</code>. Add language/framework skills for the producer/consumer implementation language.
- Event-driven architecture work: <code>loom-event-driven</code>, optionally <code>microservices</code>.
- RabbitMQ/message queue service: <code>loom-event-driven</code>. Add <code>celery-expert</code> or <code>django-celery-expert</code> when the service uses Celery.
- Celery service: <code>celery-expert</code>. For Django apps, prefer <code>django-celery-expert</code> and add <code>celery-expert</code> only for lower-level broker/worker concerns.
- Redis service: <code>redis-development</code>. Add <code>redis-js</code> for Upstash/JS SDK code. Add <code>upstash-redis-kv</code> only after review because installer reported Snyk High Risk. Use <code>redis-best-practices</code> with review because earlier registry marks it Snyk High Risk.
- WebSocket/realtime service: <code>websocket-development</code>. Add Redis or RabbitMQ/event-driven skills only if the realtime layer fans out through a broker.
- Docker/container service: <code>docker</code>, <code>docker-knowledge-patch</code>.
- Kubernetes service: <code>kubernetes-knowledge-patch</code>.
- Terraform/IaC service: <code>terraform-knowledge-patch</code>.
- Nginx/Traefik proxy service: <code>nginx-knowledge-patch</code> or <code>traefik-knowledge-patch</code>.

## Evidence required before attaching these skills

- Kafka evidence: <code>kafka</code>, <code>KafkaConsumer</code>, <code>KafkaProducer</code>, <code>confluent</code>, <code>kafkajs</code>, <code>spring-kafka</code>, topic config, broker URL, Schema Registry config.
- RabbitMQ/message queue evidence: <code>rabbitmq</code>, <code>amqp</code>, <code>amqplib</code>, <code>pika</code>, queue/exchange/routing key config.
- Celery evidence: <code>celery.py</code>, <code>CELERY\_</code> settings, <code>@shared_task</code>, <code>celery beat</code>, broker URL.
- Redis evidence: <code>REDIS_URL</code>, <code>ioredis</code>, <code>@upstash/redis</code>, <code>redis</code> client package, cache/session/rate-limit config.
- Docker evidence: <code>Dockerfile</code>, <code>docker-compose.yml</code>, <code>compose.yaml</code>, <code>.dockerignore</code>.
- Kubernetes evidence: <code>deployment.yaml</code>, <code>service.yaml</code>, <code>ingress.yaml</code>, <code>kustomization.yaml</code>, Helm chart files.
- Terraform evidence: <code>.tf</code> files, Terraform modules, backend/provider config.
- Nginx/Traefik evidence: nginx config files, Traefik labels, ingress route config, reverse proxy config.

## Security notes

Installer output reported:

- <code>kafka-development</code>, <code>microservices</code>, <code>serverless</code>, <code>websocket-development</code>: Gen Safe, Socket 0 alerts, Snyk Low Risk.
- <code>loom-event-driven</code>: Gen Safe, Socket 0 alerts, Snyk Low Risk.
- <code>discover-networking</code>: Gen Safe, Socket 0 alerts, Snyk Low Risk.
- <code>django-celery-expert</code>: Gen Safe, Socket 0 alerts, Snyk Low Risk.
- <code>redis-development</code>, <code>redis-js</code>: Gen Safe, Socket 0 alerts, Snyk Low Risk.
- <code>docker</code> and infrastructure knowledge patches: Gen Safe, Socket 0 alerts, Snyk Low Risk.
- <code>celery-expert</code>: Gen Critical Risk, Socket 0 alerts, Snyk Med Risk. Require explicit review before use.
- <code>upstash-redis-kv</code>: Gen Safe, Socket 0 alerts, Snyk High Risk. Require explicit review before use.

## ReactJS and Oracle Skill Pack - installed on 2026-04-17

### ReactJS scope

Installed skills:

- react: baseline React component, hook, state, and UI implementation guidance.
- react-query: server-state, cache, mutation, invalidation, and async data guidance.
- redux-toolkit: Redux Toolkit store/slice/thunk/query architecture guidance.
- zustand-state-management: lightweight client-state store guidance.
- react-modernization: refactor and modernization guidance for older React codebases.

Factory attachment rules:

- React SPA or component-heavy frontend: attach react.
- API fetching/cache layer in React: attach react-query.
- Global application state with Redux: attach redux-toolkit.
- Lightweight global/client state: attach zustand-state-management.
- Legacy React migration or class-to-hook work: attach react-modernization.
- React plus Next.js: attach react, next-best-practices, and framework-specific UI skills such as tailwindcss, shadcn, mui, accessibility-a11y, framer-motion, or gsap when detected.

Security notes from installer:

- react, react-query, redux-toolkit: Safe / Low Risk.
- zustand-state-management: Low Risk / Low Risk.
- react-modernization: Safe / Snyk Med Risk. Review before use on sensitive repos.

### Oracle and database scope

Installed skills:

- oracle-cloud: OCI and Oracle cloud platform scope.
- query-expert: SQL query correctness and query analysis scope.
- database-architect: schema, data-model, and database architecture scope.
- database-optimizer: database performance and optimization scope.
- discover-database: onboarding/discovery support for database engines and ownership.
- oracle-database: local project skill for Oracle Database, Oracle SQL, PL/SQL, migrations, locks, tuning, and driver behavior.

Factory attachment rules:

- Oracle Database / PL/SQL / Oracle SQL: attach oracle-database plus query-expert.
- Oracle schema/migration/data-model task: attach oracle-database plus database-architect.
- Oracle performance/index/query tuning task: attach oracle-database plus database-optimizer plus query-expert.
- OCI infrastructure or managed Oracle cloud operation: attach oracle-cloud plus infra skills such as terraform-knowledge-patch, docker, kubernetes-knowledge-patch, nginx-knowledge-patch, or azure/aws equivalents if detected.
- Service code using Oracle from Java/Spring: attach oracle-database plus java-architect, spring-boot-engineer, spring-framework, or java-spring-development as appropriate.
- Service code using Oracle from .NET: attach oracle-database plus aspnet-core, csharp-developer, or modern-csharp-coding-standards as appropriate.
- Service code using Oracle from Node.js: attach oracle-database plus nodejs-backend-patterns, fastify-typescript, nestjs-clean-typescript, or koa-typescript as appropriate.
- Service code using Oracle from Python: attach oracle-database plus fastapi-python, rest-api-django, python-testing, or python-uv as appropriate.

Important gap filled locally:

- skills.sh had Oracle Cloud coverage but did not provide a clear Oracle Database / PL/SQL specialist skill in the discovered results. The local oracle-database skill exists to cover that project-critical database scope.

## Payment, Notification, AWS, and Azure Skill Pack - installed on 2026-04-17

### Payment scope

Installed skills:

- payment-platform: local mandatory guardrail for payment, billing, checkout, subscription, refund, dispute, invoice, webhook, PCI, and marketplace payment work.
- stripe-best-practices: Stripe API selection, Checkout, Billing, Connect, Treasury, migration, and launch checklist guidance.
- upgrade-stripe: Stripe API and SDK upgrade guidance.
- stripe-integration: Stripe checkout, subscription, webhook, refund, and customer-management implementation guidance.
- paypal-integration: PayPal checkout, IPN, recurring billing, refund, dispute, and international payment guidance.
- payment-integration: generic gateway integration, PCI, retries, subscription, webhook, and multi-provider guidance.
- customer-billing-ops: customer billing operations.
- finance-billing-ops: finance billing operations.
- cost-optimization: multi-cloud/provider cost optimization.

Factory attachment rules:

- Any payment task: attach payment-platform.
- Stripe task: attach payment-platform plus stripe-best-practices and stripe-integration.
- Stripe upgrade task: attach payment-platform plus upgrade-stripe.
- PayPal task: attach payment-platform plus paypal-integration.
- Multi-provider or unknown provider task: attach payment-platform plus payment-integration.
- Billing ops task: attach payment-platform plus customer-billing-ops or finance-billing-ops.
- Payment-triggered notification: also attach notification-delivery.

Security notes from installer:

- stripe-best-practices: Safe / Snyk Med Risk.
- upgrade-stripe: Safe / Snyk High Risk.
- stripe-integration: Safe / Snyk High Risk.
- paypal-integration: Safe / Snyk Med Risk.
- payment-integration: Low Risk / Snyk Med Risk.
- cost-optimization: Safe / Low Risk.

### Notification scope

Installed skills:

- notification-delivery: local mandatory architecture guardrail for email, SMS, push, in-app, webhook, retry, outbox, preferences, and delivery status.
- resend: Resend email platform routing and transactional email guidance.
- capacitor-push-notifications: mobile push notification guidance for Capacitor, Firebase, and APNs.
- unified-notifications-ops: cross-channel notification operations.
- email-ops: email operations.
- messages-ops: message operations.

Attempted but not installed:

- send-email from resend/resend-skills was listed in skills.sh search results but the live repo install selected only resend.
- twilio-phone failed because the GitHub repo required authentication or was inaccessible.

Factory attachment rules:

- Any notification task: attach notification-delivery.
- Resend/email task: attach notification-delivery plus resend and email-ops when operational workflow is in scope.
- Mobile push task: attach notification-delivery plus capacitor-push-notifications.
- Cross-channel workflow: attach notification-delivery plus unified-notifications-ops.
- Message center/SMS-like workflow: attach notification-delivery plus messages-ops, with risk review.
- Payment notification: attach notification-delivery plus payment-platform.
- AWS notification pipeline: attach notification-delivery plus cloud-platform-routing plus eventbridge, sqs, lambda, cloudwatch, and service-specific AWS skills.
- Azure notification pipeline: attach notification-delivery plus cloud-platform-routing plus azure-functions, kql, cloud-solution-architect, microsoft-docs, and existing Azure skills.

Security notes from installer:

- resend: Safe / Snyk Med Risk.
- capacitor-push-notifications: Safe / Snyk Med Risk.
- unified-notifications-ops: Safe / Low Risk.
- email-ops: Safe / Low Risk.
- messages-ops: Safe / Snyk High Risk.

### AWS scope

Installed skills:

- cloud-platform-routing: local mandatory selector and guardrail for AWS/Azure/multi-cloud work.
- aws-cloud-services: broad AWS cloud services coverage.
- lambda: AWS Lambda.
- sqs: AWS SQS.
- eventbridge: AWS EventBridge.
- iam: AWS IAM.
- s3: AWS S3.
- dynamodb: AWS DynamoDB.
- cloudwatch: AWS CloudWatch.
- cloudformation: AWS CloudFormation.
- cognito: AWS Cognito.

Attempted but not installed:

- aws-solution-architect from alirezarezvani/claude-skills was present in skills.sh search results, but the live repo no longer contained that skill name.

Factory attachment rules:

- Any AWS task: attach cloud-platform-routing.
- AWS serverless: attach lambda plus iam plus cloudwatch.
- AWS queue/event workflow: attach sqs plus eventbridge plus lambda plus cloudwatch.
- AWS object storage: attach s3 plus iam.
- AWS NoSQL: attach dynamodb plus iam plus cloudwatch.
- AWS identity: attach iam, and cognito when user/application auth is in scope.
- AWS IaC: attach cloudformation and terraform-knowledge-patch when Terraform is detected.
- Broad AWS architecture: attach cloud-platform-routing; use aws-cloud-services only when service-level skills are insufficient because installer marked it Critical/High risk.

Security notes from installer:

- aws-cloud-services: Gen Critical Risk / Snyk High Risk. Treat as restricted reference.
- cloudformation: Safe / Snyk Med Risk.
- cloudwatch, dynamodb, eventbridge, iam, s3, sqs: Safe / Low Risk.
- lambda: Safe / Snyk Med Risk.
- cognito: Low Risk / Snyk High Risk.

### Azure scope

Installed skills:

- azure-functions: Azure Functions patterns.
- cloud-solution-architect: Microsoft cloud solution architecture.
- kql: Kusto Query Language support.
- microsoft-docs: Microsoft documentation research support.
- azure-cost: Azure cost guidance.
- Existing earlier Azure skills remain available: azure-enterprise-infra-planner, azure-kubernetes, azure-quotas, azure-upgrade, microsoft-foundry.

Attempted but not installed:

- azure-ai, azure-observability, azure-compute, azure-messaging, azure-cost-optimization, azure-cloud-migrate, azure-hosted-copilot-sdk from microsoft/github-copilot-for-azure timed out during clone.
- azure-servicebus-dotnet, azure-keyvault-py, azure-ai-voicelive-py, azure-ai-document-intelligence-dotnet were listed in skills.sh search results but the live Microsoft repo did not contain those names at install time.
- azure-infra-engineer from 404kidwiz/claude-supercode-skills failed because the GitHub repo required authentication or was inaccessible.

Factory attachment rules:

- Any Azure task: attach cloud-platform-routing.
- Azure Functions task: attach azure-functions.
- Azure architecture task: attach cloud-solution-architect plus microsoft-docs.
- Azure logging/query task: attach kql, and azure-observability only if installed in a future run.
- Azure cost task: attach azure-cost plus cost-optimization.
- AKS task: attach azure-kubernetes plus kubernetes-knowledge-patch.
- Azure upgrade/migration task: attach azure-upgrade; attach azure-cloud-migrate only if installed in a future run.
- Azure AI task: attach microsoft-foundry; attach azure-ai only if installed in a future run.

## Related

- [skill-composition.md](skill-composition.md) — How skills are selected and attached to agents
- [visual-flow.md](visual-flow.md) — All workflow diagrams
- [folder-guide.md](folder-guide.md) — Full `.claude` folder reference
