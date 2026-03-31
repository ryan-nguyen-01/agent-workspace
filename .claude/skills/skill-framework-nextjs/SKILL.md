---
name: skill-framework-nextjs
description: Best practices xây dựng Next.js 14+ applications: App Router, Server Components, Server Actions, data fetching và performance patterns.
---

# Skill: Next.js 14+ (App Router)

## Project Structure

```
src/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Home page
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   └── layout.tsx
│   └── dashboard/
│       ├── page.tsx
│       └── users/
│           ├── page.tsx
│           └── [id]/page.tsx
├── components/
│   ├── ui/                 # Reusable UI components
│   └── features/           # Feature-specific components
├── lib/
│   ├── api/                # API client functions
│   ├── db/                 # Database client
│   └── auth/               # Auth utilities
├── server/
│   ├── actions/            # Server Actions
│   └── queries/            # Server-side data fetching
└── types/
```

## Server Components (default)

```typescript
// app/dashboard/users/page.tsx
// ✅ Server Component — fetch trực tiếp, không cần useEffect
import { getUsers } from '@/server/queries/users'
import { UserList } from '@/components/features/UserList'

interface Props {
  searchParams: { page?: string; search?: string }
}

export default async function UsersPage({ searchParams }: Props) {
  const page = Number(searchParams.page) || 1
  const users = await getUsers({ page, search: searchParams.search })

  return (
    <section>
      <h1>Users</h1>
      <UserList users={users} />
    </section>
  )
}

// ✅ Metadata
export const metadata = {
  title: 'Users | Dashboard',
}
```

## Server Queries

```typescript
// server/queries/users.ts
import { db } from '@/lib/db'
import { cache } from 'react'

// ✅ cache() deduplicates calls within same render
export const getUser = cache(async (id: string) => {
  return db.user.findUnique({ where: { id } })
})

export async function getUsers({ page = 1, search }: {
  page?: number
  search?: string
}) {
  return db.user.findMany({
    where: search ? {
      OR: [
        { name: { contains: search, mode: 'insensitive' } },
        { email: { contains: search, mode: 'insensitive' } },
      ],
    } : undefined,
    skip: (page - 1) * 20,
    take: 20,
    orderBy: { createdAt: 'desc' },
  })
}
```

## Server Actions

```typescript
// server/actions/users.ts
'use server'
import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'
import { z } from 'zod'

const createUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(2),
  password: z.string().min(8),
})

export async function createUser(formData: FormData) {
  const result = createUserSchema.safeParse({
    email: formData.get('email'),
    name: formData.get('name'),
    password: formData.get('password'),
  })

  if (!result.success) {
    return { error: result.error.flatten() }
  }

  await db.user.create({ data: result.data })
  revalidatePath('/dashboard/users')
  redirect('/dashboard/users')
}

export async function deleteUser(id: string) {
  await db.user.delete({ where: { id } })
  revalidatePath('/dashboard/users')
}
```

## Client Components — chỉ khi cần

```typescript
// components/features/SearchInput.tsx
'use client'  // ✅ Chỉ mark khi cần interactivity

import { useRouter, useSearchParams } from 'next/navigation'
import { useTransition } from 'react'

export function SearchInput() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [isPending, startTransition] = useTransition()

  const handleSearch = (term: string) => {
    startTransition(() => {
      const params = new URLSearchParams(searchParams)
      if (term) params.set('search', term)
      else params.delete('search')
      router.replace(`/dashboard/users?${params}`)
    })
  }

  return (
    <input
      defaultValue={searchParams.get('search') ?? ''}
      onChange={e => handleSearch(e.target.value)}
      placeholder="Search users..."
    />
  )
}
```

## Loading & Error States

```typescript
// app/dashboard/users/loading.tsx
export default function Loading() {
  return <UserListSkeleton />
}

// app/dashboard/users/error.tsx
'use client'
export default function Error({
  error,
  reset,
}: {
  error: Error
  reset: () => void
}) {
  return (
    <div>
      <h2>Something went wrong</h2>
      <button onClick={reset}>Try again</button>
    </div>
  )
}
```

## API Routes (Route Handlers)

```typescript
// app/api/v1/users/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'

export async function GET(request: NextRequest) {
  const session = await getServerSession()
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const users = await getUsers({})
  return NextResponse.json(users)
}

export async function POST(request: NextRequest) {
  const body = await request.json()
  // validate + create...
  return NextResponse.json(newUser, { status: 201 })
}
```

## Anti-patterns

```typescript
// ❌ 'use client' trên root layout (mất Server Components)
// ❌ Fetch trong useEffect khi Server Component đủ dùng
// ❌ Props drilling — dùng Server Components composition thay thế

// ❌ Không cache server queries
async function getUser(id: string) {  // Gọi nhiều lần = nhiều DB queries
  return db.user.findUnique({ where: { id } })
}
// ✅ Wrap với cache()

// ❌ Client Component quá rộng — push 'use client' xuống sâu nhất có thể
// 'use client' trên page.tsx = toàn bộ subtree là client
```
