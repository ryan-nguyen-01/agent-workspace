---
name: skill-lang-typescript
description: Best practices viết TypeScript production-ready: type safety, strict mode, patterns và anti-patterns phổ biến.
---

# Skill: TypeScript

## Compiler Config chuẩn
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "exactOptionalPropertyTypes": true
  }
}
```

## Type Definitions

### Dùng `interface` cho object shapes, `type` cho unions/intersections
```typescript
// ✅ interface cho object
interface User {
  id: string
  email: string
  createdAt: Date
}

// ✅ type cho union, intersection, mapped types
type Status = 'active' | 'inactive' | 'banned'
type AdminUser = User & { permissions: string[] }
```

### Không dùng `any` — dùng `unknown` khi type chưa biết
```typescript
// ❌ Sai
function parse(data: any) { return data.name }

// ✅ Đúng
function parse(data: unknown): string {
  if (typeof data === 'object' && data !== null && 'name' in data) {
    return String((data as Record<string, unknown>).name)
  }
  throw new Error('Invalid data shape')
}
```

### Readonly cho data không mutate
```typescript
// ✅ Immutable config
interface Config {
  readonly apiUrl: string
  readonly timeout: number
}

// ✅ Readonly arrays
function processItems(items: ReadonlyArray<string>): void {}
```

### Generic constraints
```typescript
// ✅ Constrain generics properly
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key]
}
```

## Async Patterns

### Luôn type Promise return
```typescript
// ✅ Explicit return type
async function fetchUser(id: string): Promise<User> {
  const data = await db.users.findOne(id)
  if (!data) throw new NotFoundException(`User ${id} not found`)
  return data
}
```

### Error handling với custom Error types
```typescript
class AppError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode: number = 500
  ) {
    super(message)
    this.name = 'AppError'
  }
}

class NotFoundError extends AppError {
  constructor(resource: string) {
    super(`${resource} not found`, 'NOT_FOUND', 404)
  }
}
```

## Enums vs Union Types

### Dùng `as const` object thay vì enum
```typescript
// ❌ Tránh numeric enum
enum Direction { Up, Down, Left, Right }

// ✅ Dùng string union
type Direction = 'up' | 'down' | 'left' | 'right'

// ✅ Hoặc const object nếu cần iterate
const DIRECTION = {
  UP: 'up',
  DOWN: 'down',
  LEFT: 'left',
  RIGHT: 'right',
} as const
type Direction = typeof DIRECTION[keyof typeof DIRECTION]
```

## Utility Types hay dùng
```typescript
Partial<T>          // tất cả fields optional
Required<T>         // tất cả fields required
Pick<T, K>          // chỉ lấy một số fields
Omit<T, K>          // bỏ một số fields
Record<K, V>        // object với key-value types
Readonly<T>         // immutable
NonNullable<T>      // loại bỏ null | undefined
ReturnType<F>       // lấy return type của function
Parameters<F>       // lấy parameter types của function
```

## Anti-patterns phổ biến

```typescript
// ❌ Type assertion không cần thiết
const user = data as User

// ✅ Type guard
function isUser(data: unknown): data is User {
  return typeof data === 'object' && data !== null
    && 'id' in data && 'email' in data
}

// ❌ Non-null assertion operator (!.) tràn lan
const name = user!.profile!.name!

// ✅ Optional chaining + nullish coalescing
const name = user?.profile?.name ?? 'Anonymous'

// ❌ Bỏ qua error type
catch (e) { console.log(e.message) }

// ✅ Type narrow error
catch (e) {
  const message = e instanceof Error ? e.message : String(e)
  console.log(message)
}
```

## Import/Export chuẩn
```typescript
// ✅ Named exports (dễ tree-shake)
export class UserService {}
export interface UserDto {}

// ✅ Re-export từ index
// src/user/index.ts
export { UserService } from './user.service'
export type { UserDto, CreateUserDto } from './user.dto'
```
