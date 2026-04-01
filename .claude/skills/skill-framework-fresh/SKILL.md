---
name: skill-framework-fresh
description: Best practices Fresh (Deno) — Islands architecture, file-based routing, JSX, zero build step, edge deployment.
---

# Skill: Fresh (Deno)

## Khi nào dùng

- Deno ecosystem, edge-first deployment (Deno Deploy)
- Muốn Islands architecture — minimal client JS
- Zero build step, JSX server rendering
- TypeScript native, no config overhead

---

## Project structure

```
routes/
  index.tsx             # /
  users/
    index.tsx           # /users
    [id].tsx            # /users/:id
  api/
    users.ts            # API route (JSON)
islands/
  Counter.tsx           # Interactive island (ships JS)
  SearchBar.tsx
components/
  UserCard.tsx          # Server-only component (no JS)
static/
  styles.css
fresh.config.ts
deno.json
```

---

## Route component

```tsx
// routes/users/index.tsx
import { PageProps } from "$fresh/server.ts";
import { Handlers } from "$fresh/server.ts";
import UserCard from "../../components/UserCard.tsx";

interface Data {
  users: User[];
}

// Handlers = server-side data fetching
export const handler: Handlers<Data> = {
  async GET(req, ctx) {
    const users = await db.user.findMany();
    return ctx.render({ users });
  },
};

// Component receives pre-rendered data
export default function UsersPage({ data }: PageProps<Data>) {
  return (
    <div>
      <h1>Users</h1>
      {data.users.map((user) => (
        <UserCard key={user.id} user={user} />
      ))}
    </div>
  );
}
```

---

## Dynamic route

```tsx
// routes/users/[id].tsx
import { Handlers, PageProps } from "$fresh/server.ts";

interface Data {
  user: User;
}

export const handler: Handlers<Data> = {
  async GET(req, ctx) {
    const { id } = ctx.params;
    const user = await db.user.findUnique({ where: { id } });
    if (!user) return ctx.renderNotFound();

    return ctx.render({ user });
  },

  async DELETE(req, ctx) {
    await db.user.delete({ where: { id: ctx.params.id } });
    return new Response(null, {
      status: 303,
      headers: { Location: "/users" },
    });
  },
};

export default function UserPage({ data }: PageProps<Data>) {
  return <div>{data.user.name}</div>;
}
```

---

## API routes (JSON)

```typescript
// routes/api/users.ts
import { Handlers } from "$fresh/server.ts";

export const handler: Handlers = {
  async GET(req) {
    const url = new URL(req.url);
    const q = url.searchParams.get("q") ?? "";
    const users = await db.user.findMany({ where: { name: { contains: q } } });
    return Response.json(users);
  },

  async POST(req) {
    const body = await req.json();
    const user = await db.user.create({ data: body });
    return Response.json(user, { status: 201 });
  },
};
```

---

## Islands (interactive components)

```tsx
// islands/Counter.tsx
import { useSignal } from "@preact/signals";

// Islands được hydrate trên client, ship JS
export default function Counter({ initialCount }: { initialCount: number }) {
  const count = useSignal(initialCount);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => count.value++}>+</button>
      <button onClick={() => count.value--}>-</button>
    </div>
  );
}
```

```tsx
// routes/index.tsx — dùng island trong route
import Counter from "../islands/Counter.tsx";

export default function Home() {
  return (
    <div>
      <h1>Home</h1>
      {/* Island được hydrate với props này */}
      <Counter initialCount={0} />
    </div>
  );
}
```

---

## Middleware

```typescript
// routes/_middleware.ts
import { MiddlewareHandler } from "$fresh/server.ts";

// Auth middleware
export const handler: MiddlewareHandler = async (req, ctx) => {
  const session = await getSession(req);

  // Protected routes
  if (!session && ctx.url.pathname.startsWith("/dashboard")) {
    return Response.redirect(new URL("/login", req.url));
  }

  // Pass session to route handlers
  ctx.state.session = session;
  return ctx.next();
};
```

---

## Shared layout (\_app.tsx)

```tsx
// routes/_app.tsx
import { PageProps } from "$fresh/server.ts";

export default function App({ Component, url }: PageProps) {
  return (
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <title>My App</title>
        <link rel="stylesheet" href="/styles.css" />
      </head>
      <body>
        <nav>
          <a href="/">Home</a>
          <a href="/users">Users</a>
        </nav>
        <main>
          <Component />
        </main>
      </body>
    </html>
  );
}
```

---

## Config

```typescript
// fresh.config.ts
import { defineConfig } from "$fresh/server.ts";
import tailwind from "$fresh/plugins/tailwind.ts";

export default defineConfig({
  plugins: [tailwind()],
});
```

```jsonc
// deno.json
{
  "tasks": {
    "dev": "deno run -A --watch=static/,routes/ dev.ts",
    "start": "deno run -A main.ts",
    "build": "deno run -A dev.ts build",
  },
  "imports": {
    "$fresh/": "https://deno.land/x/fresh@1.6.8/",
    "preact": "https://esm.sh/preact@10.22.0",
    "@preact/signals": "https://esm.sh/@preact/signals@1.2.3",
  },
}
```

---

## Checklist

- ✅ Islands chỉ cho interactive components — không wrap static content
- ✅ `_middleware.ts` cho auth/logging theo path prefix
- ✅ API routes trong `routes/api/` trả về `Response.json()`
- ✅ `ctx.renderNotFound()` cho 404
- ✅ Static files trong `static/` — served as-is
- ✅ Deploy trên Deno Deploy: `deployctl deploy --project=my-app`
