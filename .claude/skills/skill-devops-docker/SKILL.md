---
name: skill-devops-docker
description: Best practices viết Dockerfile và docker-compose: multi-stage builds, layer optimization, security hardening, health checks và production patterns.
---

# Skill: Docker

## Multi-stage Dockerfile — Node.js

```dockerfile
# ✅ Multi-stage build — production image nhỏ, không chứa dev dependencies
FROM node:20-alpine AS base
WORKDIR /app
RUN corepack enable

# Stage 1: Install dependencies
FROM base AS deps
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# Stage 2: Build
FROM base AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN pnpm build

# Stage 3: Production
FROM base AS runner
ENV NODE_ENV=production

# ✅ Non-root user (security)
RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 appuser
USER appuser

COPY --from=builder --chown=appuser:nodejs /app/dist ./dist
COPY --from=deps --chown=appuser:nodejs /app/node_modules ./node_modules
COPY --chown=appuser:nodejs package.json ./

EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://localhost:3000/health || exit 1

CMD ["node", "dist/main.js"]
```

## Multi-stage Dockerfile — Java Spring Boot

```dockerfile
FROM eclipse-temurin:21-jdk-alpine AS builder
WORKDIR /app

# ✅ Cache Gradle/Maven dependencies
COPY gradlew build.gradle.kts settings.gradle.kts ./
COPY gradle ./gradle
RUN ./gradlew dependencies --no-daemon

COPY src ./src
RUN ./gradlew bootJar --no-daemon -x test

# ✅ Layered JARs (Spring Boot 2.3+)
FROM eclipse-temurin:21-jre-alpine AS extractor
WORKDIR /extracted
COPY --from=builder /app/build/libs/*.jar app.jar
RUN java -Djarmode=layertools -jar app.jar extract

FROM eclipse-temurin:21-jre-alpine AS runner
WORKDIR /app

RUN addgroup --system spring && adduser --system --ingroup spring spring
USER spring:spring

# ✅ Copy layers separately (better caching)
COPY --from=extractor /extracted/dependencies/ ./
COPY --from=extractor /extracted/spring-boot-loader/ ./
COPY --from=extractor /extracted/snapshot-dependencies/ ./
COPY --from=extractor /extracted/application/ ./

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD wget -qO- http://localhost:8080/actuator/health || exit 1

ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-XX:MaxRAMPercentage=75.0", "org.springframework.boot.loader.launch.JarLauncher"]
```

## Multi-stage Dockerfile — Python

```dockerfile
FROM python:3.12-slim AS base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

FROM base AS builder
RUN pip install uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

FROM base AS runner
WORKDIR /app

RUN useradd --system --create-home appuser
USER appuser

COPY --from=builder /app/.venv /app/.venv
COPY --chown=appuser . .

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

## docker-compose (Development)

```yaml
# docker-compose.yml
services:
  app:
    build:
      context: .
      target: runner
    ports:
      - "3000:3000"
    environment:
      NODE_ENV: development
      DATABASE_URL: postgresql://postgres:password@db:5432/myapp
      REDIS_URL: redis://redis:6379
    volumes:
      - ./src:/app/src:ro     # ✅ Hot reload in dev
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: myapp
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --requirepass password
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "--pass", "password", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

volumes:
  postgres_data:
  redis_data:
```

## .dockerignore

```
node_modules
.git
.gitignore
*.md
.env*
dist
coverage
.nyc_output
Dockerfile*
docker-compose*
.claude
.agent
```

## Anti-patterns

```dockerfile
# ❌ Chạy với root user
# ✅ Tạo non-root user và USER directive

# ❌ COPY . . trước khi install dependencies (mất cache)
COPY . .
RUN npm install   # ❌ Rebuild mỗi code thay đổi!
# ✅ Copy package.json trước, install, rồi mới COPY source

# ❌ Không dùng .dockerignore → node_modules vào image
# ❌ Single layer với nhiều RUN commands
RUN apt-get update
RUN apt-get install -y curl  # ❌ Nhiều layers
# ✅ Chain với &&
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# ❌ Hardcode secrets trong Dockerfile hoặc docker-compose
ENV DB_PASSWORD=mysecret  # ❌ Committed vào git!
# ✅ .env file (gitignored) hoặc secret management (Vault, AWS Secrets)
```
