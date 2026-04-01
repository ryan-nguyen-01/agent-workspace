---
name: skill-framework-fastify
description: Best practices xây dựng Fastify applications — plugins, schema validation, serialization, hooks, TypeScript, và production patterns.
---

# Skill: Fastify

## Khi nào dùng

- REST API Node.js cần hiệu năng cao (nhanh hơn Express ~65%)
- Muốn built-in JSON schema validation & serialization
- Project TypeScript cần typed routes

---

## Project structure

```
src/
  app.ts              # build Fastify instance, register plugins
  server.ts           # entry point, start server
  routes/
    index.ts          # aggregate routes
    users/
      index.ts        # route handler
      schema.ts       # JSON Schema hoặc Zod/TypeBox
  plugins/
    db.ts             # database plugin
    auth.ts           # auth plugin
    sensible.ts       # @fastify/sensible
  services/
    user.service.ts
  repositories/
    user.repo.ts
  types/
    index.ts
```

---

## App setup

```typescript
import Fastify from "fastify";
import { TypeBoxTypeProvider } from "@fastify/type-provider-typebox";

export function buildApp() {
  const app = Fastify({
    logger: {
      level: process.env.LOG_LEVEL ?? "info",
      transport:
        process.env.NODE_ENV === "development"
          ? { target: "pino-pretty" }
          : undefined,
    },
  }).withTypeProvider<TypeBoxTypeProvider>();

  // Register plugins
  app.register(import("./plugins/db"));
  app.register(import("./plugins/auth"));
  app.register(import("./routes"), { prefix: "/api/v1" });

  return app;
}
```

---

## Routes với TypeBox (recommended)

```typescript
import { Type } from "@sinclair/typebox";
import type { FastifyPluginAsyncTypebox } from "@fastify/type-provider-typebox";

const CreateUserBody = Type.Object({
  email: Type.String({ format: "email" }),
  name: Type.String({ minLength: 1, maxLength: 100 }),
  password: Type.String({ minLength: 8 }),
});

const UserResponse = Type.Object({
  id: Type.String(),
  email: Type.String(),
  name: Type.String(),
  createdAt: Type.String(),
});

const plugin: FastifyPluginAsyncTypebox = async (app) => {
  app.post(
    "/users",
    {
      schema: {
        body: CreateUserBody,
        response: { 201: UserResponse },
      },
    },
    async (request, reply) => {
      const user = await app.userService.create(request.body);
      return reply.status(201).send(user);
    },
  );

  app.get(
    "/users/:id",
    {
      schema: {
        params: Type.Object({ id: Type.String() }),
        response: { 200: UserResponse },
      },
    },
    async (request, reply) => {
      const user = await app.userService.findById(request.params.id);
      if (!user) return reply.notFound(`User ${request.params.id} not found`);
      return user;
    },
  );
};

export default plugin;
```

---

## Plugins (Dependency Injection)

```typescript
// plugins/db.ts — decorate app với db client
import fp from "fastify-plugin";
import { PrismaClient } from "@prisma/client";

export default fp(
  async (app) => {
    const prisma = new PrismaClient();
    await prisma.$connect();

    app.decorate("db", prisma);

    app.addHook("onClose", async () => {
      await prisma.$disconnect();
    });
  },
  { name: "db" },
);

// typescript type augmentation
declare module "fastify" {
  interface FastifyInstance {
    db: PrismaClient;
  }
}
```

---

## Hooks

```typescript
// Lifecycle: onRequest → preParsing → preValidation → preHandler → handler → preSerialization → onSend → onResponse

app.addHook("onRequest", async (request, reply) => {
  // Auth check, rate limit
});

app.addHook("preHandler", async (request, reply) => {
  // Business rule checks
});

app.addHook("onResponse", async (request, reply) => {
  // Metrics, logging
});
```

---

## Error handling

```typescript
import fp from "fastify-plugin";

export default fp(async (app) => {
  app.setErrorHandler((error, request, reply) => {
    // @fastify/sensible errors (404, 401, etc.)
    if (error.statusCode) {
      return reply.status(error.statusCode).send({
        error: error.message,
        statusCode: error.statusCode,
      });
    }

    // Domain errors
    if (error instanceof NotFoundError) {
      return reply.status(404).send({ error: error.message });
    }

    // Unhandled
    app.log.error(error);
    reply.status(500).send({ error: "Internal Server Error" });
  });
});
```

---

## Auth middleware (JWT)

```typescript
import fp from "fastify-plugin";
import fastifyJwt from "@fastify/jwt";

export default fp(async (app) => {
  app.register(fastifyJwt, {
    secret: process.env.JWT_SECRET!,
  });

  app.decorate(
    "authenticate",
    async (request: FastifyRequest, reply: FastifyReply) => {
      try {
        await request.jwtVerify();
      } catch {
        reply.unauthorized("Invalid token");
      }
    },
  );
});

// Use in routes
app.get(
  "/me",
  {
    onRequest: [app.authenticate],
    schema: { response: { 200: UserResponse } },
  },
  async (request) => {
    return request.user;
  },
);
```

---

## Performance checklist

- ✅ Dùng JSON schema để fast serialization (response schema bắt buộc)
- ✅ Tránh `JSON.stringify` thủ công — Fastify xử lý
- ✅ Dùng `@fastify/compress` cho response compression
- ✅ Enable `trustProxy` nếu sau load balancer
- ✅ Dùng connection pooling cho DB

---

## Testing

```typescript
import { buildApp } from "../src/app";

describe("Users API", () => {
  let app: ReturnType<typeof buildApp>;

  beforeAll(async () => {
    app = buildApp();
    await app.ready();
  });

  afterAll(() => app.close());

  it("POST /api/v1/users → 201", async () => {
    const res = await app.inject({
      method: "POST",
      url: "/api/v1/users",
      payload: {
        email: "test@example.com",
        name: "Test",
        password: "secret123",
      },
    });
    expect(res.statusCode).toBe(201);
  });
});
```

---

## Key packages

| Package                          | Purpose                        |
| -------------------------------- | ------------------------------ |
| `fastify`                        | Core                           |
| `@fastify/type-provider-typebox` | TypeBox type provider          |
| `@sinclair/typebox`              | JSON Schema + TypeScript types |
| `@fastify/jwt`                   | JWT auth                       |
| `@fastify/cors`                  | CORS                           |
| `@fastify/compress`              | Compression                    |
| `@fastify/sensible`              | HTTP errors helpers            |
| `@fastify/rate-limit`            | Rate limiting                  |
| `fastify-plugin`                 | `fp()` for plugin DI           |
