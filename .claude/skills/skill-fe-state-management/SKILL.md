---
name: skill-fe-state-management
description: Best practices quản lý state trong frontend — Redux Toolkit, Zustand, Pinia, NgRx. Patterns cho server state (TanStack Query), local vs global state, và khi nào dùng gì.
---

# Skill: Frontend State Management

## Khi nào cần State Management Library

```yaml
KHÔNG cần (dùng built-in):
  - Ít state chia sẻ giữa components (< 3 levels prop drilling)
  - State chỉ cần trong 1 page/feature
  - React: useState + useContext đủ
  - Vue: reactive() + provide/inject đủ

CẦN library khi:
  - Nhiều components xa nhau cùng đọc/ghi 1 state
  - Complex state transitions (multi-step forms, shopping cart)
  - Cần time-travel debugging, action logging
  - State persist across navigation (cart, user preferences)
  - Optimistic updates cần rollback

Server state (API data) → TanStack Query / SWR (KHÔNG dùng Redux cho API cache)
Client state (UI state) → Zustand / Redux / Pinia
```

---

## Zustand (React — Recommended)

### Khi nào dùng
```yaml
when:
  - React project cần lightweight global state
  - Team muốn minimal boilerplate
  - Không cần strict architecture (middleware, actions)
pros: "Tiny (1KB), no provider, no boilerplate, TypeScript-first"
cons: "Ít structure cho large teams, không có devtools mạnh như Redux"
```

### Store Design

```typescript
import { create } from 'zustand'
import { devtools, persist, subscribeWithSelector } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'

interface CartItem {
  productId: string
  name: string
  price: number
  quantity: number
}

interface CartState {
  items: CartItem[]
  isOpen: boolean

  addItem: (item: Omit<CartItem, 'quantity'>) => void
  removeItem: (productId: string) => void
  updateQuantity: (productId: string, quantity: number) => void
  clearCart: () => void
  toggleCart: () => void

  // Computed (derived state)
  totalItems: () => number
  totalPrice: () => number
}

export const useCartStore = create<CartState>()(
  devtools(
    persist(
      immer((set, get) => ({
        items: [],
        isOpen: false,

        addItem: (item) => set((state) => {
          const existing = state.items.find(i => i.productId === item.productId)
          if (existing) {
            existing.quantity += 1
          } else {
            state.items.push({ ...item, quantity: 1 })
          }
        }),

        removeItem: (productId) => set((state) => {
          state.items = state.items.filter(i => i.productId !== productId)
        }),

        updateQuantity: (productId, quantity) => set((state) => {
          const item = state.items.find(i => i.productId === productId)
          if (item) {
            if (quantity <= 0) {
              state.items = state.items.filter(i => i.productId !== productId)
            } else {
              item.quantity = quantity
            }
          }
        }),

        clearCart: () => set({ items: [] }),
        toggleCart: () => set((state) => ({ isOpen: !state.isOpen })),

        totalItems: () => get().items.reduce((sum, i) => sum + i.quantity, 0),
        totalPrice: () => get().items.reduce((sum, i) => sum + i.price * i.quantity, 0),
      })),
      { name: 'cart-storage' } // localStorage key
    ),
    { name: 'CartStore' } // devtools label
  )
)

// ✅ Usage in component — auto re-renders on state change
function CartButton() {
  const totalItems = useCartStore((s) => s.totalItems())
  const toggleCart = useCartStore((s) => s.toggleCart)
  return <button onClick={toggleCart}>Cart ({totalItems})</button>
}

// ✅ Selector for performance — only re-render when selected state changes
function CartTotal() {
  const totalPrice = useCartStore((s) => s.totalPrice())
  return <span>${totalPrice.toFixed(2)}</span>
}
```

### Store Patterns

```typescript
// ✅ Slice pattern — split large store into slices
interface AuthSlice {
  user: User | null
  isAuthenticated: boolean
  login: (credentials: LoginDto) => Promise<void>
  logout: () => void
}

interface UISlice {
  theme: 'light' | 'dark'
  sidebarOpen: boolean
  toggleTheme: () => void
  toggleSidebar: () => void
}

const createAuthSlice: StateCreator<AuthSlice & UISlice, [], [], AuthSlice> = (set) => ({
  user: null,
  isAuthenticated: false,
  login: async (credentials) => {
    const user = await authApi.login(credentials)
    set({ user, isAuthenticated: true })
  },
  logout: () => set({ user: null, isAuthenticated: false }),
})

const createUISlice: StateCreator<AuthSlice & UISlice, [], [], UISlice> = (set) => ({
  theme: 'light',
  sidebarOpen: true,
  toggleTheme: () => set((s) => ({ theme: s.theme === 'light' ? 'dark' : 'light' })),
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
})

export const useAppStore = create<AuthSlice & UISlice>()((...args) => ({
  ...createAuthSlice(...args),
  ...createUISlice(...args),
}))
```

---

## Redux Toolkit (React — Enterprise)

### Khi nào dùng
```yaml
when:
  - Large team cần strict conventions
  - Complex state logic (nhiều reducers, middleware)
  - Cần powerful devtools (time-travel, action replay)
  - Enterprise app cần audit trail of state changes
pros: "Strict architecture, excellent devtools, middleware ecosystem"
cons: "More boilerplate, steeper learning curve"
```

### Slice Pattern

```typescript
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'

// Async thunk
export const fetchUsers = createAsyncThunk(
  'users/fetchAll',
  async (params: { page: number; limit: number }, { rejectWithValue }) => {
    try {
      const response = await api.getUsers(params)
      return response.data
    } catch (error) {
      return rejectWithValue(error.response?.data?.message ?? 'Failed to fetch users')
    }
  }
)

interface UsersState {
  items: User[]
  selectedId: string | null
  status: 'idle' | 'loading' | 'succeeded' | 'failed'
  error: string | null
  pagination: { page: number; total: number; pageSize: number }
}

const initialState: UsersState = {
  items: [],
  selectedId: null,
  status: 'idle',
  error: null,
  pagination: { page: 1, total: 0, pageSize: 20 },
}

const usersSlice = createSlice({
  name: 'users',
  initialState,
  reducers: {
    selectUser: (state, action: PayloadAction<string>) => {
      state.selectedId = action.payload
    },
    clearSelection: (state) => {
      state.selectedId = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchUsers.pending, (state) => {
        state.status = 'loading'
        state.error = null
      })
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.status = 'succeeded'
        state.items = action.payload.data
        state.pagination = action.payload.pagination
      })
      .addCase(fetchUsers.rejected, (state, action) => {
        state.status = 'failed'
        state.error = action.payload as string
      })
  },
})

export const { selectUser, clearSelection } = usersSlice.actions

// Selectors
export const selectAllUsers = (state: RootState) => state.users.items
export const selectUserById = (state: RootState, id: string) =>
  state.users.items.find(u => u.id === id)
export const selectUsersStatus = (state: RootState) => state.users.status
```

### RTK Query (Server State)

```typescript
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: '/api/v1',
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token
      if (token) headers.set('Authorization', `Bearer ${token}`)
      return headers
    },
  }),
  tagTypes: ['User', 'Order'],
  endpoints: (builder) => ({
    getUsers: builder.query<PaginatedResponse<User>, { page: number }>({
      query: ({ page }) => `/users?page=${page}`,
      providesTags: (result) =>
        result
          ? [...result.data.map(({ id }) => ({ type: 'User' as const, id })), 'User']
          : ['User'],
    }),
    createUser: builder.mutation<User, CreateUserDto>({
      query: (body) => ({ url: '/users', method: 'POST', body }),
      invalidatesTags: ['User'],
    }),
  }),
})

export const { useGetUsersQuery, useCreateUserMutation } = apiSlice
```

---

## Pinia (Vue 3 — Official)

### Store Design

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// ✅ Composition API style (recommended)
export const useCartStore = defineStore('cart', () => {
  const items = ref<CartItem[]>([])
  const isOpen = ref(false)

  const totalItems = computed(() =>
    items.value.reduce((sum, i) => sum + i.quantity, 0)
  )
  const totalPrice = computed(() =>
    items.value.reduce((sum, i) => sum + i.price * i.quantity, 0)
  )

  function addItem(item: Omit<CartItem, 'quantity'>) {
    const existing = items.value.find(i => i.productId === item.productId)
    if (existing) {
      existing.quantity++
    } else {
      items.value.push({ ...item, quantity: 1 })
    }
  }

  function removeItem(productId: string) {
    items.value = items.value.filter(i => i.productId !== productId)
  }

  function clearCart() {
    items.value = []
  }

  return { items, isOpen, totalItems, totalPrice, addItem, removeItem, clearCart }
}, {
  persist: true, // pinia-plugin-persistedstate
})
```

---

## TanStack Query (Server State — Framework Agnostic)

```typescript
// ✅ Server state management — NOT in Redux/Zustand
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

function useUsers(page: number) {
  return useQuery({
    queryKey: ['users', { page }],
    queryFn: () => api.getUsers({ page }),
    staleTime: 5 * 60 * 1000,    // 5min before refetch
    gcTime: 10 * 60 * 1000,      // 10min cache
    placeholderData: keepPreviousData,
  })
}

function useCreateUser() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CreateUserDto) => api.createUser(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
    },
    // Optimistic update
    onMutate: async (newUser) => {
      await queryClient.cancelQueries({ queryKey: ['users'] })
      const previous = queryClient.getQueryData(['users'])
      queryClient.setQueryData(['users'], (old: any) => ({
        ...old,
        data: [...old.data, { ...newUser, id: 'temp' }],
      }))
      return { previous }
    },
    onError: (_err, _vars, context) => {
      queryClient.setQueryData(['users'], context?.previous)
    },
  })
}
```

---

## Decision Matrix

```
┌──────────────────────┬──────────────┬─────────────┬──────────┐
│ Scenario             │ Client State │ Server State│ Both     │
├──────────────────────┼──────────────┼─────────────┼──────────┤
│ React small/medium   │ Zustand      │ TanStack Q  │ Both     │
│ React enterprise     │ Redux TK     │ RTK Query   │ Both     │
│ Vue 3                │ Pinia        │ TanStack Q  │ Both     │
│ Angular              │ NgRx/Signals │ HttpClient  │ NgRx     │
│ Next.js (RSC)        │ Zustand      │ Server Comp │ Minimal  │
└──────────────────────┴──────────────┴─────────────┴──────────┘
```

---

## Anti-patterns

```yaml
redux_for_everything:
  bad: "Store API responses, form state, UI toggles ALL in Redux"
  fix: "Server state → TanStack Query. Form state → react-hook-form. UI → local useState"

prop_drilling_fear:
  bad: "Use global store because component is 2 levels deep"
  fix: "2-3 levels prop drilling is FINE. Global store for truly shared state only"

mutating_state:
  bad: "state.items.push(item) without immer"
  fix: "Use immer middleware or spread operator for immutable updates"

no_selectors:
  bad: "useStore() — subscribe to entire store, re-render on ANY change"
  fix: "useStore(s => s.specificField) — subscribe to only what you need"

derived_state_in_store:
  bad: "Store totalPrice as state, manually update on every item change"
  fix: "Compute derived values: computed() (Vue/Pinia), selector (Redux), getter function (Zustand)"
```
