---
name: skill-role-detect-stack
description: Phát hiện chính xác tech stack, framework, database, và tooling của project từ config files.
---

# Skill: Detect Tech Stack

## Mục đích
Xác định chính xác technology stack của project để Orchestrator spawn đúng agent variants và load đúng skills.

## Nguồn dữ liệu để detect (theo độ ưu tiên)
```
1. package.json / pyproject.toml / pom.xml / go.mod / Cargo.toml
2. Framework config files (next.config.js, angular.json, vite.config.ts...)
3. Docker / docker-compose files
4. CI/CD files (.github/workflows/, .gitlab-ci.yml)
5. Import patterns trong source files (nếu cần confirm)
```

## Detection Rules

### Runtime / Language
```yaml
detect_language:
  TypeScript:
    files: [tsconfig.json, "*.ts", "*.tsx"]
    confidence: high

  JavaScript:
    files: [package.json]
    no_files: [tsconfig.json]
    confidence: medium

  Python:
    files: [pyproject.toml, requirements.txt, setup.py, "*.py"]
    confidence: high

  Java:
    files: [pom.xml, "build.gradle", "*.java"]
    confidence: high

  Go:
    files: [go.mod, go.sum, "*.go"]
    confidence: high

  Rust:
    files: [Cargo.toml, "*.rs"]
    confidence: high
```

### Frontend Frameworks
```yaml
detect_frontend:
  React:
    package_deps: [react, react-dom]
    config_files: []

  Next.js:
    package_deps: [next]
    config_files: [next.config.js, next.config.ts]
    note: "Next.js implies React"

  Vue.js:
    package_deps: [vue]
    config_files: [vue.config.js]

  Nuxt.js:
    package_deps: [nuxt]
    note: "Nuxt implies Vue"

  Angular:
    package_deps: ["@angular/core"]
    config_files: [angular.json]

  Svelte:
    package_deps: [svelte]
    config_files: [svelte.config.js]
```

### Backend Frameworks
```yaml
detect_backend:
  NestJS:
    package_deps: ["@nestjs/core", "@nestjs/common"]

  Express:
    package_deps: [express]
    no_deps: ["@nestjs/core"]

  Fastify:
    package_deps: [fastify]

  FastAPI:
    python_deps: [fastapi, uvicorn]

  Django:
    python_deps: [django]

  Spring Boot:
    java_deps: ["spring-boot-starter"]
    config: [application.yml, application.properties]

  Gin (Go):
    go_deps: ["github.com/gin-gonic/gin"]

  Echo (Go):
    go_deps: ["github.com/labstack/echo"]
```

### Database
```yaml
detect_database:
  PostgreSQL:
    package_deps: [pg, psycopg2, postgresql, typeorm, prisma]
    env_patterns: [DATABASE_URL, POSTGRES_URI, PG_*]

  MySQL:
    package_deps: [mysql2, pymysql, mysql-connector]
    env_patterns: [MYSQL_URI, DATABASE_URL]

  MongoDB:
    package_deps: [mongoose, pymongo, "spring-data-mongodb"]
    env_patterns: [MONGO_URI, MONGODB_URI]

  Redis:
    package_deps: [redis, ioredis, "spring-data-redis"]
    env_patterns: [REDIS_URL, REDIS_URI, REDIS_HOST]

  SQLite:
    package_deps: [sqlite3, better-sqlite3, sqlite]
    files: ["*.sqlite", "*.db"]

  Elasticsearch:
    package_deps: ["@elastic/elasticsearch", elasticsearch-py]
    env_patterns: [ELASTICSEARCH_URL, ELASTIC_*]
```

### ORM / Query Builder
```yaml
detect_orm:
  TypeORM:
    package_deps: [typeorm]
    config_files: [ormconfig.json, typeorm.config.ts]

  Prisma:
    package_deps: ["@prisma/client"]
    files: [prisma/schema.prisma]

  Sequelize:
    package_deps: [sequelize]

  Drizzle:
    package_deps: [drizzle-orm]

  SQLAlchemy:
    python_deps: [sqlalchemy]

  Hibernate:
    java_deps: [hibernate-core]
```

### Testing
```yaml
detect_testing:
  Jest:
    package_deps: [jest, "@types/jest"]
    config_files: [jest.config.ts, jest.config.js]

  Vitest:
    package_deps: [vitest]
    config_files: [vitest.config.ts]

  Pytest:
    python_deps: [pytest]

  JUnit:
    java_deps: [junit-jupiter]

  Go Test:
    indicator: "go.mod exists + *_test.go files"
```

### Build Tools / Bundlers
```yaml
detect_build:
  Vite:
    package_deps: [vite]
    config_files: [vite.config.ts]

  Webpack:
    package_deps: [webpack]
    config_files: [webpack.config.js]

  esbuild:
    package_deps: [esbuild]

  Turbopack:
    indicator: "Next.js 13+ with --turbo flag"
```

## Output format

```yaml
detected_stack:
  language: TypeScript
  runtime: Node.js 20

  frontend:
    framework: Next.js 14
    ui_library: React 18
    styling: TailwindCSS

  backend:
    framework: NestJS 10
    api_type: REST

  database:
    primary: PostgreSQL
    cache: Redis
    orm: TypeORM

  testing:
    unit: Jest
    e2e: Supertest

  build:
    bundler: Webpack (via NestJS)
    package_manager: pnpm

  recommended_agents:
    coder: [agent-coder-nestjs, agent-coder-nextjs]
    tester: [agent-tester-jest]
```
