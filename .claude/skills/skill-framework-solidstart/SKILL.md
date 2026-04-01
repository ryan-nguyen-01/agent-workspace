---
name: skill-framework-solidstart
description: Best practices SolidStart — SolidJS meta-framework, file-based routing, server functions, streaming SSR, và production patterns.
---

# Skill: SolidStart

## Khi nào dùng

- Full-stack app với SolidJS (fine-grained reactivity, nhỏ hơn React)
- Cần streaming SSR, server functions, islands architecture
- Alternative to Next.js / Remix nhưng dùng SolidJS

---

## Project structure

```
src/
  app.tsx             # Root component
  entry-client.tsx    # Client entry
  entry-server.tsx    # Server entry
  routes/
    index.tsx         # /
    about.tsx         # /about
    users/
      index.tsx       # /users
      [id].tsx        # /users/:id
    api/
      users.ts        # API route
  components/
    ui/
  lib/
    db.ts
    auth.ts
  server/
    users.ts          # Server functions
```

---

## Routing

```tsx
// File-based routing (similar to Remix/Next.js)

// routes/index.tsx
export default function Home() {
  return <h1>Home</h1>;
}

// routes/users/[id].tsx
import { useParams } from "@solidjs/router";
import { createAsync } from "@solidjs/router";
import { getUser } from "~/server/users";

export default function UserPage() {
  const params = useParams();
  const user = createAsync(() => getUser(params.id));

  return (
    <Suspense fallback={<p>Loading...</p>}>
      <Show when={user()} fallback={<p>Not found</p>}>
        {(u) => <div>{u().name}</div>}
      </Show>
    </Suspense>
  );
}
```

---

## Server functions

```typescript
// server/users.ts
"use server";
import { db } from "~/lib/db";
import { getSession } from "~/lib/auth";

export async function getUser(id: string) {
  return db.user.findUnique({ where: { id } });
}

export async function createUser(data: { email: string; name: string }) {
  const session = await getSession();
  if (!session) throw new Error("Unauthorized");

  return db.user.create({ data });
}

// Use in component
import { createAsync, action } from "@solidjs/router";
import { getUser, createUser } from "~/server/users";

const createUserAction = action(createUser);

export default function Page() {
  const user = createAsync(() => getUser("123"));
  // ...
}
```

---

## Reactive primitives

```tsx
import { createSignal, createMemo, createEffect, Show, For } from 'solid-js'

// ✅ Fine-grained reactivity — chỉ update đúng DOM node
const [count, setCount] = createSignal(0)
const doubled = createMemo(() => count() * 2)

createEffect(() => {
  console.log('count changed:', count())
})

// ✅ Conditional rendering
<Show when={user()} fallback={<Login />}>
  {(u) => <Profile user={u()} />}
</Show>

// ✅ List rendering
<For each={items()}>
  {(item) => <Item item={item} />}
</For>
```

---

## Data loading patterns

```tsx
import { createAsync, cache } from "@solidjs/router";

// Cache server function results
const getUsers = cache(async () => {
  "use server";
  return db.user.findMany();
}, "users");

export const route = {
  preload: () => getUsers(), // preload on navigation
};

export default function UsersPage() {
  const users = createAsync(() => getUsers());

  return (
    <Suspense>
      <For each={users()}>{(user) => <UserCard user={user} />}</For>
    </Suspense>
  );
}
```

---

## Forms & Mutations

```tsx
import { action, useAction, useSubmission } from "@solidjs/router";
import { createUser } from "~/server/users";

const create = action(createUser);

export default function CreateUserForm() {
  const submit = useAction(create);
  const submission = useSubmission(create);

  return (
    <form action={create} method="post">
      <input name="email" type="email" required />
      <input name="name" required />
      <button type="submit" disabled={submission.pending}>
        {submission.pending ? "Creating..." : "Create"}
      </button>
    </form>
  );
}
```

---

## API routes

```typescript
// routes/api/users.ts
import type { APIEvent } from "@solidjs/start/server";
import { db } from "~/lib/db";

export async function GET({ params }: APIEvent) {
  const users = await db.user.findMany();
  return Response.json(users);
}

export async function POST({ request }: APIEvent) {
  const body = await request.json();
  const user = await db.user.create({ data: body });
  return Response.json(user, { status: 201 });
}
```

---

## Performance checklist

- ✅ SolidJS có fine-grained reactivity — không cần `memo` manual như React
- ✅ `Suspense` + `createAsync` cho async data
- ✅ `lazy()` cho code splitting
- ✅ Islands architecture cho minimal JS hydration
- ✅ Streaming SSR với SolidStart server

---

## Config (app.config.ts)

```typescript
import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  server: {
    preset: "node-server", // hoặc 'cloudflare', 'netlify', 'vercel'
  },
  vite: {
    plugins: [],
  },
});
```
