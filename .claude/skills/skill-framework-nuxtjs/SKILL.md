---
name: skill-framework-nuxtjs
description: Best practices xây dựng Nuxt 3 applications: composables, server routes, data fetching, layouts, middleware và SSR/SSG patterns.
---

# Skill: Nuxt 3

## Project Structure

```
src/
├── app.vue               # Root component
├── nuxt.config.ts
├── pages/                # File-based routing
│   ├── index.vue
│   ├── dashboard/
│   │   ├── index.vue
│   │   └── users/
│   │       ├── index.vue
│   │       └── [id].vue
│   └── [...slug].vue     # Catch-all
├── components/
│   ├── ui/               # Reusable UI
│   └── features/         # Feature components
├── composables/          # Auto-imported
├── server/
│   ├── api/              # Server routes
│   ├── middleware/
│   └── utils/
├── middleware/            # Client/server middleware
├── layouts/
└── plugins/
```

## Data Fetching

```vue
<!-- pages/dashboard/users/index.vue -->
<script setup lang="ts">
// ✅ useFetch — SSR-compatible, cached, reactive
const { data: users, pending, error, refresh } = await useFetch('/api/v1/users', {
  query: { page: 1, limit: 20 },
  transform: (data) => data.items,  // Transform response
  getCachedData: (key, nuxtApp) => nuxtApp.payload.data[key],  // Cache on client
})

// ✅ useAsyncData — for custom logic
const { data: stats } = await useAsyncData('dashboard-stats', async () => {
  const [users, orders] = await Promise.all([
    $fetch('/api/v1/stats/users'),
    $fetch('/api/v1/stats/orders'),
  ])
  return { users, orders }
}, {
  lazy: false,    // SSR wait
  server: true,   // Fetch on server
})

// ✅ Lazy fetch (không block SSR)
const { data, pending, execute } = useLazyFetch('/api/v1/heavy-data')
</script>

<template>
  <div>
    <LoadingSpinner v-if="pending" />
    <ErrorMessage v-else-if="error" :error="error" />
    <UserList v-else :users="users ?? []" @refresh="refresh" />
  </div>
</template>
```

## Server Routes (API)

```typescript
// server/api/v1/users/index.get.ts
import { z } from 'zod'

const querySchema = z.object({
  page: z.coerce.number().min(1).default(1),
  limit: z.coerce.number().min(1).max(100).default(20),
  search: z.string().optional(),
})

export default defineEventHandler(async (event) => {
  // ✅ Validate query
  const query = await getValidatedQuery(event, querySchema.parse)

  // ✅ Auth check
  const user = await requireUser(event)

  const result = await userService.findPaginated(query)
  return result
})

// server/api/v1/users/index.post.ts
const bodySchema = z.object({
  email: z.string().email(),
  name: z.string().min(2),
  password: z.string().min(8),
})

export default defineEventHandler(async (event) => {
  const body = await readValidatedBody(event, bodySchema.parse)
  const user = await userService.create(body)

  setResponseStatus(event, 201)
  return user
})

// server/api/v1/users/[id].get.ts
export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')!
  return userService.findById(id)
})
```

## Composables

```typescript
// composables/useUsers.ts
export function useUsers(options?: { page?: Ref<number>; search?: Ref<string> }) {
  const page = options?.page ?? ref(1)
  const search = options?.search ?? ref('')

  const { data, pending, refresh } = useFetch('/api/v1/users', {
    query: computed(() => ({
      page: page.value,
      search: search.value || undefined,
    })),
    watch: [page, search],
  })

  return { users: data, pending, refresh, page, search }
}

// composables/useAuth.ts
export function useAuth() {
  const user = useState<User | null>('auth.user', () => null)
  const token = useCookie('auth-token', { httpOnly: false, secure: true, sameSite: 'lax' })

  async function login(credentials: LoginDto) {
    const data = await $fetch('/api/auth/login', { method: 'POST', body: credentials })
    user.value = data.user
    token.value = data.accessToken
    await navigateTo('/dashboard')
  }

  async function logout() {
    await $fetch('/api/auth/logout', { method: 'POST' })
    user.value = null
    token.value = null
    await navigateTo('/login')
  }

  const isAuthenticated = computed(() => !!user.value)

  return { user: readonly(user), isAuthenticated, login, logout }
}
```

## Middleware

```typescript
// middleware/auth.ts — Client + server middleware
export default defineNuxtRouteMiddleware((to) => {
  const { isAuthenticated } = useAuth()

  if (!isAuthenticated.value && to.path !== '/login') {
    return navigateTo('/login', { replace: true })
  }
})

// server/middleware/auth.ts — Server-only
export default defineEventHandler(async (event) => {
  // Attach user to event context for API routes
  const token = getCookie(event, 'auth-token')
    || getRequestHeader(event, 'authorization')?.replace('Bearer ', '')

  if (token) {
    try {
      event.context.user = await verifyToken(token)
    } catch {
      // Token invalid — context.user remains undefined
    }
  }
})
```

## nuxt.config.ts

```typescript
export default defineNuxtConfig({
  devtools: { enabled: true },

  modules: [
    '@pinia/nuxt',
    '@nuxtjs/tailwindcss',
    '@vueuse/nuxt',
    'nuxt-icon',
  ],

  runtimeConfig: {
    // Server-only (không expose ra client)
    databaseUrl: process.env.DATABASE_URL,
    jwtSecret: process.env.JWT_SECRET,
    // Public (expose ra client)
    public: {
      apiBase: '/api',
      appName: 'My App',
    },
  },

  routeRules: {
    '/api/**': { cors: true },
    '/dashboard/**': { ssr: false },   // SPA mode cho dashboard
    '/blog/**': { swr: 3600 },         // ISR: stale-while-revalidate 1h
    '/': { prerender: true },           // Static prerender
  },
})
```

## Anti-patterns

```vue
<!-- ❌ useAsyncData key trùng nhau giữa các pages (cache conflict) -->
const { data } = useAsyncData('users', () => $fetch('/api/users'))
<!-- ✅ Key unique per page/context -->
const { data } = useAsyncData(`users-${route.params.id}`, ...)

<!-- ❌ $fetch trong script setup (không cache, re-fetch mỗi render) -->
const users = await $fetch('/api/users')
<!-- ✅ useFetch hoặc useAsyncData -->

<!-- ❌ Watch trong setup mà không cleanup -->
watch(something, handler)  // Memory leak nếu component unmount
<!-- ✅ watchEffect auto-cleanup hoặc onUnmounted -->
```
