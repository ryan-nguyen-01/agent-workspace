---
name: skill-framework-vuejs
description: Best practices xây dựng Vue 3 applications: Composition API, composables, Pinia state management, TypeScript integration và performance patterns.
---

# Skill: Vue 3 (Composition API)

## Component Structure

```vue
<!-- UserCard.vue -->
<script setup lang="ts">
// ✅ <script setup> — recommended syntax
interface Props {
  userId: string
  onEdit?: (id: string) => void
}

const props = defineProps<Props>()
const emit = defineEmits<{
  edit: [id: string]
  delete: [id: string]
}>()

const { data: user, pending, error } = useUser(props.userId)

function handleEdit() {
  emit('edit', props.userId)
  props.onEdit?.(props.userId)
}
</script>

<template>
  <article v-if="!pending && user" class="user-card">
    <h2>{{ user.name }}</h2>
    <p>{{ user.email }}</p>
    <button @click="handleEdit">Edit</button>
  </article>
  <Skeleton v-else-if="pending" />
  <ErrorMessage v-else-if="error" :error="error" />
</template>
```

## Composables — Logic tách khỏi UI

```typescript
// composables/useUser.ts
import { useQuery } from '@tanstack/vue-query'

export function useUser(userId: MaybeRef<string>) {
  return useQuery({
    queryKey: computed(() => ['users', toValue(userId)]),
    queryFn: () => userApi.findById(toValue(userId)),
    enabled: computed(() => !!toValue(userId)),
    staleTime: 5 * 60 * 1000,
  })
}

// composables/useUserForm.ts
import { reactive, computed } from 'vue'
import { z } from 'zod'

const schema = z.object({
  email: z.string().email(),
  name: z.string().min(2),
  password: z.string().min(8),
})

export function useUserForm() {
  const form = reactive({ email: '', name: '', password: '' })
  const errors = reactive<Partial<typeof form>>({})

  const isValid = computed(() => {
    return schema.safeParse(form).success
  })

  function validate(): boolean {
    const result = schema.safeParse(form)
    if (!result.success) {
      const flat = result.error.flatten().fieldErrors
      Object.assign(errors, flat)
      return false
    }
    Object.keys(errors).forEach(k => delete (errors as any)[k])
    return true
  }

  return { form, errors, isValid, validate }
}
```

## Pinia Store

```typescript
// stores/user.store.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// ✅ Setup store (Composition API style) — preferred
export const useUserStore = defineStore('user', () => {
  const users = ref<User[]>([])
  const currentUser = ref<User | null>(null)

  const activeUsers = computed(() =>
    users.value.filter(u => u.isActive)
  )

  async function fetchUsers() {
    users.value = await userApi.list()
  }

  async function createUser(data: CreateUserDto) {
    const user = await userApi.create(data)
    users.value.push(user)
    return user
  }

  function setCurrentUser(user: User | null) {
    currentUser.value = user
  }

  return {
    users: readonly(users),
    currentUser: readonly(currentUser),
    activeUsers,
    fetchUsers,
    createUser,
    setCurrentUser,
  }
})
```

## Reactive Patterns

```typescript
// ✅ toRef / toValue cho MaybeRef
function useSearch(query: MaybeRef<string>) {
  const results = ref<User[]>([])

  watchEffect(async () => {
    const q = toValue(query)
    if (!q) { results.value = []; return }
    results.value = await userApi.search(q)
  })

  return { results }
}

// ✅ watchEffect vs watch
// watchEffect: tự track dependencies, chạy ngay
watchEffect(() => {
  console.log('User changed:', user.value?.name)
})

// watch: kiểm soát khi nào chạy, có oldValue
watch(userId, async (newId, oldId) => {
  if (newId !== oldId) await fetchUser(newId)
}, { immediate: true })

// ✅ Shallow ref cho large objects
const users = shallowRef<User[]>([])
// Update cần thay thế array, không mutate
users.value = [...users.value, newUser]
```

## TypeScript với Vue

```typescript
// ✅ Props với complex types
interface TableProps<T> {
  items: T[]
  columns: Array<{ key: keyof T; label: string }>
  onRowClick?: (item: T) => void
}

// Generic component (Vue 3.3+)
const props = defineProps<TableProps<User>>()

// ✅ Emit types
const emit = defineEmits<{
  'update:modelValue': [value: string]
  submit: [data: FormData]
  cancel: []
}>()

// ✅ Template ref typing
const inputRef = useTemplateRef<HTMLInputElement>('myInput')
// Hoặc: const inputRef = ref<HTMLInputElement | null>(null)
```

## Performance

```typescript
// ✅ v-memo cho expensive list items
// Re-render chỉ khi user.id hoặc user.updatedAt thay đổi
<template>
  <li v-for="user in users" :key="user.id" v-memo="[user.id, user.updatedAt]">
    <UserCard :user="user" />
  </li>
</template>

// ✅ defineAsyncComponent cho code splitting
const AdminPanel = defineAsyncComponent({
  loader: () => import('./AdminPanel.vue'),
  loadingComponent: Spinner,
  errorComponent: ErrorDisplay,
  delay: 200,
})
```

## Anti-patterns

```typescript
// ❌ Mutate props trực tiếp
props.user.name = 'New Name'  // ❌
// ✅ emit event để parent update

// ❌ Reactive object destructure mất reactivity
const { name, email } = user.value  // ❌ Mất reactive
// ✅ Dùng toRefs
const { name, email } = toRefs(user)

// ❌ v-if + v-for trên cùng element
<li v-for="user in users" v-if="user.active" :key="user.id">  // ❌
// ✅ computed để filter trước
<li v-for="user in activeUsers" :key="user.id">

// ❌ Options API cho code mới
export default {
  data() { return { users: [] } },  // ❌ Dùng Composition API
}
```
