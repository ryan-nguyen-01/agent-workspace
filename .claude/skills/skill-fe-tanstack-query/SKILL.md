---
name: skill-fe-tanstack-query
description: Best practices TanStack Query (React Query) — useQuery, useMutation, queryClient, cache invalidation, optimistic updates, SSR với Next.js/SolidStart/Nuxt.
---

# Skill: TanStack Query

## Khi nào dùng

- Fetch, cache, và sync server state trong React/Vue/Solid
- Thay thế `useEffect + useState` cho data fetching
- Cần pagination, infinite scroll, optimistic updates

---

## Setup

```typescript
// main.tsx
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { ReactQueryDevtools } from "@tanstack/react-query-devtools"

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,   // 5 min — fresh period
      gcTime: 1000 * 60 * 30,     // 30 min — in-memory cache
      retry: 1,
      refetchOnWindowFocus: true,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <MyApp />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}
```

---

## queryOptions pattern (recommended)

```typescript
// queries/users.ts — ✅ centralize query definitions
import { queryOptions } from "@tanstack/react-query";
import { api } from "../lib/api";

export const userQueries = {
  all: () =>
    queryOptions({
      queryKey: ["users"],
      queryFn: () => api.get("/users"),
    }),

  list: (params: { page: number; q?: string }) =>
    queryOptions({
      queryKey: ["users", "list", params],
      queryFn: () => api.get("/users", { params }),
    }),

  detail: (id: string) =>
    queryOptions({
      queryKey: ["users", "detail", id],
      queryFn: () => api.get(`/users/${id}`),
      enabled: !!id, // chỉ fetch khi có id
    }),
};
```

---

## useQuery

```typescript
import { useSuspenseQuery } from "@tanstack/react-query"
import { userQueries } from "../queries/users"

// ✅ useSuspenseQuery — cleaner, hoạt động với Suspense
function UserDetail({ id }: { id: string }) {
  const { data: user } = useSuspenseQuery(userQueries.detail(id))
  return <div>{user.name}</div>
}

// Wrapping component
function UserDetailPage({ id }: { id: string }) {
  return (
    <Suspense fallback={<Spinner />}>
      <ErrorBoundary fallback={<Error />}>
        <UserDetail id={id} />
      </ErrorBoundary>
    </Suspense>
  )
}

// Regular useQuery — manual loading/error states
function UserList() {
  const [page, setPage] = useState(1)
  const { data, isPending, isError } = useQuery(userQueries.list({ page }))

  if (isPending) return <Spinner />
  if (isError) return <Error />

  return <ul>{data.users.map(u => <li key={u.id}>{u.name}</li>)}</ul>
}
```

---

## useMutation

```typescript
import { useMutation, useQueryClient } from "@tanstack/react-query"

function CreateUserForm() {
  const queryClient = useQueryClient()

  const createUser = useMutation({
    mutationFn: (data: CreateUserInput) => api.post("/users", data),

    // ✅ Invalidate sau khi thành công
    onSuccess: (newUser) => {
      queryClient.invalidateQueries({ queryKey: ["users"] })
    },

    onError: (error) => {
      toast.error(error.message)
    },
  })

  return (
    <form onSubmit={(e) => {
      e.preventDefault()
      const form = new FormData(e.currentTarget)
      createUser.mutate({ email: form.get("email") as string })
    }}>
      <input name="email" />
      <button type="submit" disabled={createUser.isPending}>
        {createUser.isPending ? "Creating..." : "Create"}
      </button>
    </form>
  )
}
```

---

## Optimistic updates

```typescript
const deleteUser = useMutation({
  mutationFn: (id: string) => api.delete(`/users/${id}`),

  onMutate: async (id) => {
    // Cancel in-flight queries
    await queryClient.cancelQueries({ queryKey: ["users"] });

    // Snapshot current data for rollback
    const prev = queryClient.getQueryData(["users"]);

    // Optimistically update cache
    queryClient.setQueryData(["users"], (old: User[]) =>
      old.filter((u) => u.id !== id),
    );

    return { prev };
  },

  onError: (err, id, ctx) => {
    // Rollback on error
    queryClient.setQueryData(["users"], ctx?.prev);
  },

  onSettled: () => {
    // Always refetch after success or error
    queryClient.invalidateQueries({ queryKey: ["users"] });
  },
});
```

---

## Pagination & Infinite scroll

```typescript
// Pagination
function PaginatedList() {
  const [page, setPage] = useState(1)
  const { data, placeholderData } = useQuery({
    ...userQueries.list({ page }),
    placeholderData: keepPreviousData, // ✅ No loading flash between pages
  })

  return (
    <>
      {data?.users.map(u => <UserRow key={u.id} user={u} />)}
      <button onClick={() => setPage(p => p - 1)} disabled={page === 1}>Prev</button>
      <button onClick={() => setPage(p => p + 1)} disabled={!data?.hasNextPage}>Next</button>
    </>
  )
}

// Infinite scroll
import { useInfiniteQuery } from "@tanstack/react-query"

function InfiniteList() {
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage } = useInfiniteQuery({
    queryKey: ["users", "infinite"],
    queryFn: ({ pageParam = 1 }) => api.get("/users", { params: { page: pageParam } }),
    initialPageParam: 1,
    getNextPageParam: (lastPage, pages) =>
      lastPage.hasNextPage ? pages.length + 1 : undefined,
  })

  const users = data?.pages.flatMap(p => p.users) ?? []

  return (
    <>
      {users.map(u => <UserRow key={u.id} user={u} />)}
      <button onClick={() => fetchNextPage()} disabled={!hasNextPage || isFetchingNextPage}>
        {isFetchingNextPage ? "Loading..." : "Load more"}
      </button>
    </>
  )
}
```

---

## SSR với Next.js (App Router)

```typescript
// Server component — prefetch trên server
import { dehydrate, HydrationBoundary, QueryClient } from "@tanstack/react-query"
import { userQueries } from "@/queries/users"

export default async function UsersPage() {
  const queryClient = new QueryClient()
  await queryClient.prefetchQuery(userQueries.list({ page: 1 }))

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <UserList />
    </HydrationBoundary>
  )
}
```

---

## Cache manipulation

```typescript
const queryClient = useQueryClient()

// Set data programmatically (e.g., from WebSocket)
queryClient.setQueryData(userQueries.detail(id).queryKey, updatedUser)

// Refetch specific query
queryClient.refetchQueries({ queryKey: ["users"] })

// Remove from cache
queryClient.removeQueries({ queryKey: ["users", "detail", id] })

// Prefetch on hover
<button
  onMouseEnter={() => queryClient.prefetchQuery(userQueries.detail(userId))}
>
  View User
</button>
```

---

## Checklist

- ✅ `queryOptions()` — centralize key + fn definitions (tránh typos)
- ✅ `useSuspenseQuery` + `<Suspense>` thay vì kiểm tra `isPending`
- ✅ `invalidateQueries` sau mỗi mutation thành công
- ✅ `placeholderData: keepPreviousData` cho pagination
- ✅ `staleTime > 0` để tránh refetch không cần thiết
- ✅ `enabled: false` pattern để fetch theo điều kiện
