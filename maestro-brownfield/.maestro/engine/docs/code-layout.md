# Code Layout Standard (Feature-based + Layered)

The folder architecture every Maestro-built component follows. solution-architect designs the concrete
layout per the approved blueprint; agent-factory scopes coders to these paths; coders keep code inside
them. Adapt names to the chosen stack idiom but keep the **feature module + layers** shape.

Principle: **organize by feature (vertical slice), layer inside each feature, share cross-cutting code
in core/shared.** A feature owns its API, business logic, data access, types, and unit tests together.

## Workspace roots

```text
apps/        user-facing applications (web, mobile, admin)
services/    deployable backend services / APIs / workers
packages/    shared libraries reused across apps/services (ui, config, types, sdk)
infra/       IaC, docker, CI/CD, deployment manifests
tests/       cross-component integration / e2e suites
docs/        PRD, requirements, UX/wireframes, HLD/LLD/ADR, ops
```

Monolith → one service (or app) with many feature modules. Microservices → one folder per service under
`services/`, each self-contained with the same internal layout; shared contracts/types live in
`packages/`.

## Backend service — `services/<service>/`

```text
services/<service>/
├── src/
│   ├── modules/<feature>/          one folder per feature (vertical slice)
│   │   ├── <feature>.controller.*  API/route layer (HTTP in/out, validation)
│   │   ├── <feature>.service.*     business logic / use-cases
│   │   ├── <feature>.repository.*  data access (DB/ORM/queries)
│   │   ├── <feature>.dto.*         request/response shapes
│   │   ├── <feature>.types.*       domain types/entities for the feature
│   │   └── <feature>.spec.*        unit tests next to the code
│   ├── core/                       config, db connection, logger, error handling, bootstrap
│   ├── shared/                     cross-feature utils, guards, middleware, interceptors
│   └── main.*                      entrypoint / app wiring
├── tests/                          integration + e2e for this service
├── <package manifest>              package.json / pyproject.toml / go.mod ...
├── .env.example                    documented env vars (never commit real .env)
└── README.md                       what it is + local run commands
```

## Frontend app — `apps/<app>/`

```text
apps/<app>/
├── src/
│   ├── features/<feature>/         vertical slice per feature
│   │   ├── components/             feature-scoped UI components
│   │   ├── hooks/                  feature hooks
│   │   ├── api/                    data fetching/mutations for the feature
│   │   ├── <feature>.types.*
│   │   └── <feature>.test.*
│   ├── shared/                     design-system usage, ui primitives, lib, hooks, utils
│   ├── app/  (or pages/)           routes/screens (framework router)
│   ├── styles/                     tokens/theme/global styles
│   └── main.* / entry              app bootstrap
├── public/ (or assets/)
├── tests/                          component/e2e tests
├── .env.example
└── README.md
```

## Shared package — `packages/<package>/`

```text
packages/<package>/
├── src/
│   ├── <area>/                     grouped by capability
│   └── index.*                     public API (export surface)
├── tests/
├── <package manifest>
└── README.md
```

## Infra & cross-component tests

```text
infra/
├── docker/                         Dockerfiles, compose for local
├── ci/                             pipeline definitions
└── deploy/                         IaC / manifests (used only in the deploy phase, R-019-00c)

tests/
├── integration/                    cross-service contracts
└── e2e/                            full user-flow tests
```

## Naming & conventions

```text
- kebab-case folders; file names follow the stack idiom (PascalCase components, etc.).
- One feature = one module folder; do not scatter a feature across unrelated layers.
- Dependencies point inward: controller → service → repository; core/shared never import a feature.
- Co-locate unit tests with the code; integration/e2e live in the component or root tests/.
- Public contracts (API DTOs, shared types) are explicit; shared code goes to shared/ or packages/.
```

## Right-sizing (MVP vs production)

```text
MVP:        fewer modules, repository may wrap the ORM directly, light shared/, skip premature splits.
Production: stricter layer boundaries, explicit interfaces/ports where it pays off, observability and
            error handling in core/, contract tests in tests/.
Pick the depth from the blueprint's scope_target; do not over-engineer an MVP.
```

## Stack mapping (keep the shape, use the idiom)

```text
NestJS    : modules/<feature> with *.module/controller/service/repository — native fit.
FastAPI   : modules/<feature> with routers/services/repositories; core/ for settings/db.
Express/Koa: same module shape, explicit layers.
Go        : internal/<feature> packages with handler/service/repo; cmd/ for main.
Next.js   : src/features/<feature> + app/ router; shared/ for ui/lib.
React/Vue : src/features/<feature> + shared/ design system.
```
