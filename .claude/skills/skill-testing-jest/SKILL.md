---
name: skill-testing-jest
description: Best practices viết tests với Jest: unit tests, integration tests, mocking, async testing và test organization.
---

# Skill: Jest Testing

## Test Structure

```typescript
// users/user.service.test.ts
describe('UserService', () => {
  let service: UserService
  let mockRepo: jest.Mocked<UserRepository>

  beforeEach(() => {
    mockRepo = {
      findById: jest.fn(),
      findByEmail: jest.fn(),
      create: jest.fn(),
      delete: jest.fn(),
    }
    service = new UserService(mockRepo)
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  describe('findById', () => {
    it('returns user when found', async () => {
      const user = buildUser({ id: '123' })
      mockRepo.findById.mockResolvedValue(user)

      const result = await service.findById('123')

      expect(result).toEqual(user)
      expect(mockRepo.findById).toHaveBeenCalledWith('123')
    })

    it('throws NotFoundError when user does not exist', async () => {
      mockRepo.findById.mockResolvedValue(null)

      await expect(service.findById('999')).rejects.toThrow(NotFoundError)
    })
  })
})
```

## Test Factories

```typescript
// tests/factories/user.factory.ts
import { faker } from '@faker-js/faker'

export function buildUser(overrides: Partial<User> = {}): User {
  return {
    id: faker.string.uuid(),
    email: faker.internet.email(),
    name: faker.person.fullName(),
    isActive: true,
    createdAt: new Date(),
    updatedAt: new Date(),
    ...overrides,
  }
}

export function buildCreateUserDto(overrides: Partial<CreateUserDto> = {}): CreateUserDto {
  return {
    email: faker.internet.email(),
    name: faker.person.fullName(),
    password: 'Password123!',
    ...overrides,
  }
}
```

## Mocking

```typescript
// ✅ Mock module
jest.mock('../lib/email-service', () => ({
  sendWelcomeEmail: jest.fn().mockResolvedValue(undefined),
}))

import { sendWelcomeEmail } from '../lib/email-service'
const mockSendEmail = sendWelcomeEmail as jest.MockedFunction<typeof sendWelcomeEmail>

// ✅ Spy on method
const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})
// After test
consoleSpy.mockRestore()

// ✅ Mock return values
mockRepo.findById
  .mockResolvedValueOnce(null)        // First call returns null
  .mockResolvedValue(buildUser())     // Subsequent calls return user

// ✅ Capture arguments
const createSpy = jest.spyOn(mockRepo, 'create')
await service.create(dto)
expect(createSpy).toHaveBeenCalledWith(
  expect.objectContaining({ email: dto.email })
)
```

## Async Testing

```typescript
// ✅ async/await (preferred)
it('creates user successfully', async () => {
  const dto = buildCreateUserDto()
  const user = buildUser({ email: dto.email })
  mockRepo.create.mockResolvedValue(user)

  const result = await service.create(dto)

  expect(result.email).toBe(dto.email)
})

// ✅ Test rejections
it('throws when email exists', async () => {
  mockRepo.findByEmail.mockResolvedValue(buildUser())

  await expect(service.create(buildCreateUserDto())).rejects.toThrow(
    'Email already registered'
  )
})

// ✅ Fake timers
jest.useFakeTimers()
service.scheduleCleanup()
jest.advanceTimersByTime(60_000)
expect(mockRepo.deleteInactive).toHaveBeenCalled()
jest.useRealTimers()
```

## Integration Tests

```typescript
// ✅ Supertest cho HTTP integration tests
import request from 'supertest'
import app from '../app'

describe('POST /api/v1/users', () => {
  it('creates user and returns 201', async () => {
    const dto = buildCreateUserDto()

    const response = await request(app)
      .post('/api/v1/users')
      .send(dto)
      .expect(201)

    expect(response.body).toMatchObject({
      email: dto.email,
      name: dto.name,
    })
    expect(response.body).not.toHaveProperty('password')
  })

  it('returns 400 for invalid email', async () => {
    await request(app)
      .post('/api/v1/users')
      .send({ email: 'not-an-email', name: 'Test', password: 'pass123' })
      .expect(400)
  })
})
```

## Snapshot Testing

```typescript
// ✅ Snapshot cho UI components hoặc complex objects
it('returns correct error response format', async () => {
  const error = new NotFoundError('User', '123')
  const response = formatError(error)

  expect(response).toMatchInlineSnapshot(`
    {
      "code": "NOT_FOUND",
      "message": "User '123' not found",
      "statusCode": 404,
    }
  `)
})
```

## Jest Config

```typescript
// jest.config.ts
export default {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src'],
  testMatch: ['**/*.test.ts'],
  collectCoverageFrom: ['src/**/*.ts', '!src/**/*.d.ts', '!src/main.ts'],
  coverageThresholds: {
    global: { branches: 80, functions: 80, lines: 80, statements: 80 },
  },
  setupFilesAfterFramework: ['<rootDir>/tests/setup.ts'],
}
```

## Anti-patterns

```typescript
// ❌ Test implementation details
expect(service['_cache']).toBeDefined()  // Private field!

// ❌ Test nhiều behaviors trong 1 it block
it('user service', async () => {
  // create, find, delete, update... all in one test ❌

// ❌ Non-deterministic tests (random, Date.now() without mock)
it('creates with correct timestamp', () => {
  const user = service.create(dto)
  expect(user.createdAt).toBe(new Date())  // Flaky!
})
// ✅ Mock Date
jest.setSystemTime(new Date('2024-01-01'))

// ❌ Shared mutable state giữa tests
let globalUser: User  // ❌ Dùng beforeEach
```
