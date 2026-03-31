---
name: skill-framework-react
description: Best practices xây dựng React applications: component patterns, hooks, state management, performance optimization và TypeScript integration.
---

# Skill: React (18+)

## Component Structure

```typescript
// ✅ Functional component với TypeScript
interface UserCardProps {
  userId: string
  onEdit?: (id: string) => void
}

export function UserCard({ userId, onEdit }: UserCardProps) {
  const { data: user, isLoading, error } = useUser(userId)

  if (isLoading) return <Skeleton />
  if (error) return <ErrorMessage error={error} />
  if (!user) return null

  return (
    <article className="user-card">
      <h2>{user.name}</h2>
      <p>{user.email}</p>
      {onEdit && (
        <button onClick={() => onEdit(userId)}>Edit</button>
      )}
    </article>
  )
}
```

## Custom Hooks — Logic tách khỏi UI

```typescript
// ✅ Data fetching hook với React Query
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

function useUser(userId: string) {
  return useQuery({
    queryKey: ['users', userId],
    queryFn: () => userApi.findById(userId),
    enabled: !!userId,
    staleTime: 5 * 60 * 1000,  // 5 minutes
  })
}

function useCreateUser() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: userApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
    },
  })
}

// ✅ Form hook
function useUserForm(initialValues: CreateUserDto) {
  const [values, setValues] = useState(initialValues)
  const [errors, setErrors] = useState<Partial<CreateUserDto>>({})

  const handleChange = (field: keyof CreateUserDto) =>
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setValues(prev => ({ ...prev, [field]: e.target.value }))
    }

  const validate = (): boolean => {
    const newErrors: Partial<CreateUserDto> = {}
    if (!values.email) newErrors.email = 'Email is required'
    if (!values.name || values.name.length < 2) newErrors.name = 'Min 2 characters'
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  return { values, errors, handleChange, validate }
}
```

## State Management

```typescript
// ✅ useReducer cho complex state
type Action =
  | { type: 'SET_LOADING' }
  | { type: 'SET_DATA'; payload: User[] }
  | { type: 'SET_ERROR'; payload: string }

interface State {
  users: User[]
  loading: boolean
  error: string | null
}

function userReducer(state: State, action: Action): State {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: true, error: null }
    case 'SET_DATA':
      return { ...state, loading: false, users: action.payload }
    case 'SET_ERROR':
      return { ...state, loading: false, error: action.payload }
  }
}

// ✅ Context + useReducer cho shared state
const UserContext = createContext<{
  state: State
  dispatch: React.Dispatch<Action>
} | null>(null)

export function useUserContext() {
  const ctx = useContext(UserContext)
  if (!ctx) throw new Error('useUserContext must be used within UserProvider')
  return ctx
}
```

## Performance

```typescript
// ✅ memo cho expensive renders
const UserList = memo(function UserList({ users }: { users: User[] }) {
  return (
    <ul>
      {users.map(user => <UserItem key={user.id} user={user} />)}
    </ul>
  )
})

// ✅ useCallback cho stable references
const handleDelete = useCallback(async (id: string) => {
  await deleteUser(id)
  onRefresh()
}, [deleteUser, onRefresh])

// ✅ useMemo cho expensive computations
const sortedUsers = useMemo(
  () => [...users].sort((a, b) => a.name.localeCompare(b.name)),
  [users]
)

// ✅ Lazy loading
const AdminPanel = lazy(() => import('./AdminPanel'))

<Suspense fallback={<Spinner />}>
  {isAdmin && <AdminPanel />}
</Suspense>
```

## Error Boundary

```typescript
// ✅ Error boundary component
class ErrorBoundary extends Component<
  { children: ReactNode; fallback: ReactNode },
  { hasError: boolean }
> {
  state = { hasError: false }

  static getDerivedStateFromError(): { hasError: boolean } {
    return { hasError: true }
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error('Component error:', error, info)
  }

  render() {
    if (this.state.hasError) return this.props.fallback
    return this.props.children
  }
}

// Usage
<ErrorBoundary fallback={<ErrorPage />}>
  <UserDashboard />
</ErrorBoundary>
```

## Form với React Hook Form + Zod

```typescript
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

const schema = z.object({
  email: z.string().email(),
  name: z.string().min(2),
  password: z.string().min(8),
})

type FormData = z.infer<typeof schema>

function CreateUserForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const { mutate, isPending } = useCreateUser()

  return (
    <form onSubmit={handleSubmit(data => mutate(data))}>
      <input {...register('email')} />
      {errors.email && <span>{errors.email.message}</span>}
      <button type="submit" disabled={isPending}>Submit</button>
    </form>
  )
}
```

## Anti-patterns

```typescript
// ❌ useEffect cho data fetching (dùng React Query thay thế)
useEffect(() => {
  fetch('/api/users').then(r => r.json()).then(setUsers)
}, [])

// ❌ Prop drilling > 2 levels (dùng context hoặc composition)
<A user={user}>
  <B user={user}>
    <C user={user} />  // ❌ Quá sâu

// ❌ Index làm key khi list có thể reorder
{users.map((u, i) => <User key={i} />)}  // ❌ Dùng u.id

// ❌ Mutation trong render
function Component() {
  someArray.push(item)  // ❌ Side effect trong render
  return <div />
}
```
