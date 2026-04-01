---
name: skill-framework-qwik
description: Best practices Qwik/QwikCity — resumability, lazy loading, routing, loaders, actions, và production deployment.
---

# Skill: Qwik / QwikCity

## Khi nào dùng

- App cần Time-to-Interactive cực nhanh (resumability, zero hydration)
- E-commerce, marketing pages cần Core Web Vitals cao
- Alternative to Next.js với approach khác biệt

---

## Core concept: Resumability

- Qwik **không hydrate** — serialize state vào HTML, resume trực tiếp
- JS chỉ load khi user interact (lazy on demand)
- Khác với hydration của React/Vue

---

## Project structure (QwikCity)

```
src/
  routes/
    index.tsx         # /
    layout.tsx        # Root layout
    users/
      index.tsx       # /users
      [id]/
        index.tsx     # /users/:id
    api/
      users/
        index.ts      # API endpoint
  components/
    ui/
  lib/
    db.ts
  root.tsx            # HTML root
  entry.ssr.tsx
  entry.preview.tsx
public/
  favicon.ico
```

---

## Routing & Components

```tsx
// routes/index.tsx
import { component$ } from "@builder.io/qwik";
import { routeLoader$ } from "@builder.io/qwik-city";

export const useUserData = routeLoader$(async (requestEvent) => {
  const users = await db.user.findMany();
  return users;
});

export default component$(() => {
  const users = useUserData(); // Signal

  return (
    <ul>
      {users.value.map((u) => (
        <li key={u.id}>{u.name}</li>
      ))}
    </ul>
  );
});
```

---

## $ suffix — Serialization boundary

```tsx
import { component$, useSignal, useStore, $ } from "@builder.io/qwik";

// ✅ component$ — lazy loadable component
export default component$(() => {
  const count = useSignal(0);
  const store = useStore({ items: [] as string[] });

  // ✅ $() — lazy event handler (only loaded on click)
  const handleClick = $(() => {
    count.value++;
  });

  return <button onClick$={handleClick}>Count: {count.value}</button>;
});
```

---

## routeLoader$ (Server data)

```typescript
import { routeLoader$, type RequestHandler } from "@builder.io/qwik-city";

// ✅ Route guard
export const onGet: RequestHandler = async ({ cookie, redirect }) => {
  const token = cookie.get("token");
  if (!token) {
    throw redirect(302, "/login");
  }
};

// ✅ Data loader
export const useProduct = routeLoader$(async ({ params, error }) => {
  const product = await db.product.findUnique({ where: { id: params.id } });
  if (!product) throw error(404, "Product not found");
  return product;
});
```

---

## routeAction$ (Form mutations)

```tsx
import { component$ } from "@builder.io/qwik";
import { routeAction$, zod$, Form, z } from "@builder.io/qwik-city";

export const useCreateUser = routeAction$(
  async (data, { redirect }) => {
    await db.user.create({ data });
    throw redirect(302, "/users");
  },
  zod$({
    email: z.string().email(),
    name: z.string().min(1),
  }),
);

export default component$(() => {
  const create = useCreateUser();

  return (
    <Form action={create}>
      <input name="email" type="email" />
      <input name="name" />
      <button type="submit">Create</button>
      {create.value?.fieldErrors?.email && (
        <p>{create.value.fieldErrors.email}</p>
      )}
    </Form>
  );
});
```

---

## API routes

```typescript
// routes/api/users/index.ts
import type { RequestHandler } from "@builder.io/qwik-city";

export const onGet: RequestHandler = async ({ json }) => {
  const users = await db.user.findMany();
  json(200, users);
};

export const onPost: RequestHandler = async ({ request, json }) => {
  const body = await request.json();
  const user = await db.user.create({ data: body });
  json(201, user);
};
```

---

## Middleware

```typescript
// routes/plugin@auth.ts (global middleware)
import type { RequestHandler } from "@builder.io/qwik-city";

export const onRequest: RequestHandler = async ({
  cookie,
  redirect,
  pathname,
}) => {
  const publicPaths = ["/login", "/register"];
  if (publicPaths.includes(pathname)) return;

  const token = cookie.get("token")?.value;
  if (!token) throw redirect(302, "/login");
};
```

---

## Performance checklist

- ✅ Dùng `routeLoader$` cho server data — tránh client fetching
- ✅ Lazy load components với dynamic imports
- ✅ `useStore` cho complex state, `useSignal` cho primitives
- ✅ Minimize `$` boundaries — chúng tạo lazy chunks
- ✅ Dùng Qwik Insights để analyze bundle

---

## Deployment

```typescript
// vite.config.ts — choose adapter
import { qwikVite } from "@builder.io/qwik/optimizer";
import { qwikCity } from "@builder.io/qwik-city/vite";
import { nodeServerAdapter } from "@builder.io/qwik-city/adapters/node-server/vite";

export default defineConfig({
  plugins: [
    qwikCity(),
    qwikVite(),
    nodeServerAdapter(), // hoặc cloudflarePages(), vercel(), netlify()...
  ],
});
```
