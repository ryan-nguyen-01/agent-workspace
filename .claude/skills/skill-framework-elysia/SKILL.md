---
name: skill-framework-elysia
description: Best practices Elysia.js — TypeScript-first Bun framework, routing, validation, plugins, lifecycle hooks, và production patterns.
---

# Skill: Elysia.js

## Khi nào dùng

- Backend API chạy trên Bun (hiệu năng cao)
- TypeScript-first, end-to-end type safety với Eden Treaty
- Muốn integration với tRPC-style client typing

---

## Project structure

```
src/
  index.ts          # entry point
  app.ts            # Elysia instance
  routes/
    user.route.ts
    auth.route.ts
  services/
    user.service.ts
  models/
    user.model.ts   # Elysia model (TypeBox)
  plugins/
    auth.plugin.ts
    db.plugin.ts
```

---

## App setup

```typescript
import { Elysia } from "elysia";
import { cors } from "@elysiajs/cors";
import { userRoute } from "./routes/user.route";
import { authRoute } from "./routes/auth.route";

export const app = new Elysia()
  .use(cors())
  .use(authRoute)
  .use(userRoute)
  .listen(3000);

console.log(`Server running at ${app.server?.hostname}:${app.server?.port}`);
```

---

## Routes & Validation

```typescript
import { Elysia, t } from "elysia";

export const userRoute = new Elysia({ prefix: "/users" })
  .post(
    "/",
    async ({ body, set }) => {
      // body is fully typed
      const user = await createUser(body);
      set.status = 201;
      return user;
    },
    {
      body: t.Object({
        email: t.String({ format: "email" }),
        name: t.String({ minLength: 1 }),
        password: t.String({ minLength: 8 }),
      }),
      response: t.Object({
        id: t.String(),
        email: t.String(),
        name: t.String(),
      }),
    },
  )

  .get(
    "/:id",
    async ({ params, error }) => {
      const user = await findUser(params.id);
      if (!user) return error(404, "User not found");
      return user;
    },
    {
      params: t.Object({ id: t.String() }),
    },
  );
```

---

## Plugins (Reusable logic)

```typescript
import { Elysia } from "elysia";
import { PrismaClient } from "@prisma/client";

// ✅ Plugin pattern — decorate với shared dependencies
export const dbPlugin = new Elysia({ name: "db" })
  .decorate("db", new PrismaClient())
  .onStop(({ decorator }) => decorator.db.$disconnect());

// Auth plugin
export const authPlugin = new Elysia({ name: "auth" })
  .use(jwt({ name: "jwt", secret: process.env.JWT_SECRET! }))
  .derive(async ({ headers, jwt, error }) => {
    const token = headers.authorization?.replace("Bearer ", "");
    if (!token) return error(401, "Unauthorized");
    const user = await jwt.verify(token);
    if (!user) return error(401, "Invalid token");
    return { currentUser: user };
  });
```

---

## Lifecycle hooks

```typescript
new Elysia()
  .onRequest(({ request }) => {
    // Rate limiting, logging
  })
  .onBeforeHandle(({ currentUser }) => {
    // Auth checks
  })
  .onAfterHandle(({ response }) => {
    // Response transformation
  })
  .onError(({ code, error, set }) => {
    if (code === "NOT_FOUND") {
      set.status = 404;
      return { error: "Not found" };
    }
    console.error(error);
    set.status = 500;
    return { error: "Internal Server Error" };
  });
```

---

## Eden Treaty (E2E type safety)

```typescript
// Server
export type App = typeof app;

// Client
import { treaty } from "@elysiajs/eden";
import type { App } from "../server";

const client = treaty<App>("http://localhost:3000");

// Fully typed!
const { data, error } = await client.users.post({
  email: "user@example.com",
  name: "User",
  password: "secret123",
});
```

---

## Security checklist

- ✅ Validate tất cả input với `t.*` TypeBox schemas
- ✅ Rate limit với `@elysiajs/rate-limit`
- ✅ CORS restrict origins trong production
- ✅ JWT secret đủ entropy (≥32 chars)
- ✅ Không expose stack trace trong response lỗi

---

## Testing

```typescript
import { describe, it, expect } from "bun:test";
import { app } from "../src/app";

describe("Users API", () => {
  it("POST /users → 201", async () => {
    const res = await app.handle(
      new Request("http://localhost/users", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: "test@test.com",
          name: "Test",
          password: "pass1234",
        }),
      }),
    );
    expect(res.status).toBe(201);
  });
});
```

---

## Key packages

| Package                | Purpose                    |
| ---------------------- | -------------------------- |
| `elysia`               | Core                       |
| `@elysiajs/cors`       | CORS                       |
| `@elysiajs/jwt`        | JWT                        |
| `@elysiajs/eden`       | Type-safe client           |
| `@elysiajs/swagger`    | Auto-generate Swagger docs |
| `@elysiajs/rate-limit` | Rate limiting              |
| `@elysiajs/bearer`     | Bearer token extraction    |
