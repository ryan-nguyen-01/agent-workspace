---
name: skill-testing-vitest
description: Best practices viết tests với Vitest: unit tests, component tests, mocking, coverage và TypeScript support.
---

# Skill: Vitest Testing

## Setup

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'  // nếu dùng Vue

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,       // describe, it, expect không cần import
    environment: 'jsdom', // 'node' cho Node-only tests
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov'],
      thresholds: { lines: 80, functions: 80, branches: 80 },
    },
  },
})
```

## Unit Tests

```typescript
// services/user.service.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'

describe('UserService', () => {
  let service: UserService
  let mockRepo: ReturnType<typeof createMockRepo>

  function createMockRepo() {
    return {
      findById: vi.fn(),
      findByEmail: vi.fn(),
      create: vi.fn(),
      delete: vi.fn(),
    }
  }

  beforeEach(() => {
    mockRepo = createMockRepo()
    service = new UserService(mockRepo)
  })

  it('returns user when found', async () => {
    const user = buildUser({ id: '123' })
    mockRepo.findById.mockResolvedValue(user)

    const result = await service.findById('123')

    expect(result).toEqual(user)
    expect(mockRepo.findById).toHaveBeenCalledWith('123')
  })

  it('throws NotFoundError when user is missing', async () => {
    mockRepo.findById.mockResolvedValue(null)

    await expect(service.findById('999')).rejects.toThrow(NotFoundError)
  })
})
```

## Mocking

```typescript
// ✅ vi.mock — module mock
vi.mock('../lib/email', () => ({
  sendEmail: vi.fn().mockResolvedValue(undefined),
}))

// ✅ vi.spyOn — spy on existing
const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

// ✅ Mock với factory
vi.mock('../db', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../db')>()
  return {
    ...actual,
    db: {
      users: {
        findUnique: vi.fn(),
        create: vi.fn(),
      },
    },
  }
})

// ✅ Return sequence
mockRepo.findById
  .mockResolvedValueOnce(null)
  .mockResolvedValue(buildUser())

// ✅ Fake timers
vi.useFakeTimers()
vi.setSystemTime(new Date('2024-01-01'))
// ... test ...
vi.useRealTimers()
```

## Component Testing (Vue/React)

```typescript
// Vue component test
import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import UserCard from '@/components/UserCard.vue'

describe('UserCard', () => {
  it('displays user name and email', () => {
    const user = buildUser({ name: 'John Doe', email: 'john@test.com' })

    const wrapper = mount(UserCard, {
      props: { user },
    })

    expect(wrapper.text()).toContain('John Doe')
    expect(wrapper.text()).toContain('john@test.com')
  })

  it('emits delete event when delete button clicked', async () => {
    const user = buildUser()
    const wrapper = mount(UserCard, { props: { user } })

    await wrapper.find('[data-testid="delete-btn"]').trigger('click')

    expect(wrapper.emitted('delete')).toBeTruthy()
    expect(wrapper.emitted('delete')![0]).toEqual([user.id])
  })
})

// React component test (với @testing-library/react)
import { render, screen, fireEvent } from '@testing-library/react'

describe('UserCard', () => {
  it('renders user info', () => {
    const user = buildUser({ name: 'Jane Doe' })
    render(<UserCard user={user} />)
    expect(screen.getByText('Jane Doe')).toBeInTheDocument()
  })
})
```

## HTTP Mocking với MSW

```typescript
// tests/setup.ts
import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'

export const server = setupServer(
  http.get('/api/v1/users/:id', ({ params }) => {
    return HttpResponse.json(buildUser({ id: params.id as string }))
  }),

  http.post('/api/v1/users', async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json(buildUser(body as Partial<User>), { status: 201 })
  }),
)

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

// Override in specific test
it('handles 404', async () => {
  server.use(
    http.get('/api/v1/users/:id', () =>
      HttpResponse.json({ error: 'Not found' }, { status: 404 })
    )
  )
  // ... test error handling
})
```

## Test Factories

```typescript
// tests/factories.ts
import { faker } from '@faker-js/faker'

export function buildUser(overrides: Partial<User> = {}): User {
  return {
    id: faker.string.uuid(),
    email: faker.internet.email(),
    name: faker.person.fullName(),
    isActive: true,
    createdAt: faker.date.past(),
    ...overrides,
  }
}
```

## Anti-patterns

```typescript
// ❌ Testing implementation details
expect(service['_privateMethod']).toHaveBeenCalled()

// ❌ vi.mock ở trong describe/it (phải ở top level)
describe('test', () => {
  vi.mock('../lib')  // ❌ Hoisted không hoạt động đúng
})
// ✅ vi.mock ở top level file

// ❌ Không reset mocks giữa tests
// ✅ Dùng clearAllMocks trong beforeEach hoặc clearMocks: true trong config

// ❌ Async test không await
it('fetches user', () => {   // ❌ Missing async!
  expect(service.findById('123')).resolves.toBeDefined()
})
```
