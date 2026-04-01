---
name: skill-framework-tanstack-start
description: Best practices TanStack Start — full-stack React với TanStack Router, server functions, type-safe data loading, và production patterns.
---

# Skill: TanStack Start

## Khi nào dùng

- Full-stack React app muốn end-to-end type safety
- Dùng TanStack Router (không dùng Next.js App Router)
- Cần server functions + streaming SSR

---

## Project structure

```
src/
  router.tsx           # Router instance
  routeTree.gen.ts     # Auto-generated route tree
  routes/
    __root.tsx         # Root layout
    index.tsx          # /
    users/
      index.tsx        # /users
      $userId.tsx      # /users/:userId
  api/
    users.ts           # Server functions
  components/
  lib/
    db.ts
```

---

## Router setup

```tsx
// router.tsx
import { createRouter } from "@tanstack/react-router";
import { routeTree } from "./routeTree.gen";

export const router = createRouter({
  routeTree,
  defaultPreload: "intent",
  defaultPreloadStaleTime: 0,
});

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}
```

---

## Routes

```tsx
// routes/__root.tsx
import { createRootRoute, Outlet } from "@tanstack/react-router";

export const Route = createRootRoute({
  component: () => (
    <html>
      <body>
        <Outlet />
      </body>
    </html>
  ),
});

// routes/users/$userId.tsx
import { createFileRoute } from "@tanstack/react-router";
import { getUser } from "../api/users";

export const Route = createFileRoute("/users/$userId")({
  // ✅ loader runs on server (and client for navigation)
  loader: ({ params }) => getUser({ data: params.userId }),

  component: function UserPage() {
    const user = Route.useLoaderData();
    return <div>{user.name}</div>;
  },
});
```

---

## Server functions

```typescript
// api/users.ts
import { createServerFn } from "@tanstack/start";
import { z } from "zod";

// ✅ createServerFn — type-safe RPC over HTTP
export const getUser = createServerFn({ method: "GET" })
  .validator(z.string().uuid())
  .handler(async ({ data: id }) => {
    const user = await db.user.findUnique({ where: { id } });
    if (!user) throw new Error(`User ${id} not found`);
    return user;
  });

export const createUser = createServerFn({ method: "POST" })
  .validator(
    z.object({
      email: z.string().email(),
      name: z.string().min(1),
    }),
  )
  .handler(async ({ data }) => {
    return db.user.create({ data });
  });
```

---

## Data mutations

```tsx
import { useServerFn } from "@tanstack/start";
import { createUser } from "../api/users";

function CreateUserForm() {
  const create = useServerFn(createUser);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    await create({
      data: {
        email: form.get("email") as string,
        name: form.get("name") as string,
      },
    });
  }

  return (
    <form onSubmit={handleSubmit}>
      <input name="email" type="email" required />
      <input name="name" required />
      <button type="submit">Create</button>
    </form>
  );
}
```

---

## Search params (type-safe)

```tsx
import { createFileRoute } from "@tanstack/react-router";
import { z } from "zod";

const searchSchema = z.object({
  page: z.number().default(1),
  q: z.string().optional(),
  role: z.enum(["user", "admin"]).optional(),
});

export const Route = createFileRoute("/users/")({
  validateSearch: searchSchema,
  loaderDeps: ({ search }) => search,
  loader: ({ deps }) => getUsers({ data: deps }),

  component: function UsersPage() {
    const users = Route.useLoaderData();
    const search = Route.useSearch();
    const navigate = Route.useNavigate();

    return (
      <div>
        <input
          value={search.q ?? ""}
          onChange={(e) =>
            navigate({ search: (prev) => ({ ...prev, q: e.target.value }) })
          }
        />
      </div>
    );
  },
});
```

---

## Auth pattern

```tsx
// routes/__root.tsx — auth context
import { createRootRouteWithContext } from "@tanstack/react-router";
import type { QueryClient } from "@tanstack/react-query";

interface RouterContext {
  queryClient: QueryClient;
  session: Session | null;
}

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootComponent,
});

// Protected route
export const Route = createFileRoute("/dashboard")({
  beforeLoad: ({ context }) => {
    if (!context.session) throw redirect({ to: "/login" });
  },
  component: Dashboard,
});
```

---

## TanStack Query integration

```tsx
import { queryOptions, useSuspenseQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";

const userQueryOptions = (id: string) =>
  queryOptions({
    queryKey: ["users", id],
    queryFn: () => getUser({ data: id }),
  });

export const Route = createFileRoute("/users/$userId")({
  loader: ({ context: { queryClient }, params }) =>
    queryClient.ensureQueryData(userQueryOptions(params.userId)),

  component: function UserPage() {
    const { userId } = Route.useParams();
    const { data: user } = useSuspenseQuery(userQueryOptions(userId));
    return <div>{user.name}</div>;
  },
});
```

---

## Config (app.config.ts)

```typescript
import { defineConfig } from "@tanstack/start/config";

export default defineConfig({
  server: {
    preset: "node-server", // vercel, netlify, cloudflare-pages
  },
  vite: {
    plugins: [],
  },
});
```

---

## Checklist

- ✅ Dùng `createServerFn` với `.validator(zod)` cho mọi server function
- ✅ `loaderDeps` để re-trigger loader khi search params thay đổi
- ✅ `queryClient.ensureQueryData` trong loader để prefetch
- ✅ `Suspense` + `ErrorBoundary` cho async routes
- ✅ `beforeLoad` guard cho protected routes
