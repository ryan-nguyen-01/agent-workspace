---
name: skill-testing-fixtures
description: Best practices test data management — factories, seeders, fake data generation, database fixtures, environment setup, data isolation, và snapshot testing.
---

# Skill: Test Fixtures & Data Seeding

## Data Layers

```yaml
unit_tests: "In-memory mocks/stubs — no DB needed"
integration_tests: "Test DB with seeded data — reset between tests"
e2e_tests: "Dedicated test environment with realistic data"
development: "Local DB with dev seed data"
staging: "Anonymized production snapshot OR rich seed data"
demo: "Curated showcase data for sales/onboarding"
```

---

## Factories (Recommended Pattern)

```typescript
// ✅ Factory pattern — generate test entities with sensible defaults
import { faker } from '@faker-js/faker'

// factories/user.factory.ts
interface UserFactory {
  id?: string
  email?: string
  name?: string
  role?: string
  tenantId?: string
  createdAt?: Date
}

function createUser(overrides: Partial<UserFactory> = {}): UserFactory {
  return {
    id: faker.string.uuid(),
    email: faker.internet.email(),
    name: faker.person.fullName(),
    role: 'member',
    tenantId: faker.string.uuid(),
    createdAt: faker.date.recent({ days: 30 }),
    ...overrides,  // caller can override any field
  }
}

function createUsers(count: number, overrides: Partial<UserFactory> = {}): UserFactory[] {
  return Array.from({ length: count }, () => createUser(overrides))
}

// factories/order.factory.ts
function createOrder(overrides: Partial<OrderFactory> = {}): OrderFactory {
  return {
    id: faker.string.uuid(),
    userId: faker.string.uuid(),
    status: 'pending',
    totalAmount: parseFloat(faker.commerce.price({ min: 10, max: 500 })),
    items: [createOrderItem(), createOrderItem()],
    createdAt: faker.date.recent({ days: 7 }),
    ...overrides,
  }
}

function createOrderItem(overrides = {}) {
  return {
    productId: faker.string.uuid(),
    name: faker.commerce.productName(),
    quantity: faker.number.int({ min: 1, max: 5 }),
    unitPrice: parseFloat(faker.commerce.price({ min: 5, max: 100 })),
    ...overrides,
  }
}

// ✅ Usage in tests
describe('OrderService', () => {
  it('should calculate total correctly', () => {
    const order = createOrder({
      items: [
        createOrderItem({ quantity: 2, unitPrice: 10 }),
        createOrderItem({ quantity: 1, unitPrice: 25 }),
      ],
    })
    expect(calculateTotal(order)).toBe(45)
  })

  it('should reject order for inactive user', async () => {
    const user = createUser({ role: 'member' })
    const order = createOrder({ userId: user.id })
    // ...
  })
})
```

### Prisma Factory (DB-backed)

```typescript
// factories/prisma-user.factory.ts
async function createDbUser(
  prisma: PrismaClient,
  overrides: Partial<Prisma.UserCreateInput> = {},
) {
  return prisma.user.create({
    data: {
      email: faker.internet.email(),
      name: faker.person.fullName(),
      password: await hash('TestPassword123!'),
      role: 'member',
      ...overrides,
    },
  })
}

async function createDbOrder(
  prisma: PrismaClient,
  userId: string,
  overrides: Partial<Prisma.OrderCreateInput> = {},
) {
  return prisma.order.create({
    data: {
      userId,
      status: 'pending',
      totalAmount: parseFloat(faker.commerce.price()),
      items: {
        create: [
          { productId: faker.string.uuid(), quantity: 1, unitPrice: 29.99 },
        ],
      },
      ...overrides,
    },
    include: { items: true },
  })
}
```

---

## Seeders

```typescript
// seeds/development.ts — rich dev data
async function seedDevelopment(prisma: PrismaClient) {
  console.log('Seeding development data...')

  // Create tenant
  const tenant = await prisma.tenant.create({
    data: { name: 'Acme Corp', slug: 'acme', plan: 'pro' },
  })

  // Create users
  const admin = await createDbUser(prisma, {
    email: 'admin@acme.com',
    name: 'Admin User',
    role: 'admin',
    tenantId: tenant.id,
  })

  const users = await Promise.all(
    Array.from({ length: 20 }, () =>
      createDbUser(prisma, { tenantId: tenant.id })
    )
  )

  // Create orders for each user
  for (const user of users) {
    const orderCount = faker.number.int({ min: 0, max: 10 })
    for (let i = 0; i < orderCount; i++) {
      await createDbOrder(prisma, user.id)
    }
  }

  console.log(`Seeded: 1 tenant, 21 users, ${await prisma.order.count()} orders`)
}

// seeds/test.ts — minimal test data
async function seedTest(prisma: PrismaClient) {
  const tenant = await prisma.tenant.create({
    data: { name: 'Test Org', slug: 'test', plan: 'free' },
  })

  const user = await createDbUser(prisma, {
    email: 'test@test.com',
    tenantId: tenant.id,
  })

  return { tenant, user }
}

// package.json script
// "seed": "ts-node prisma/seeds/development.ts"
// "seed:test": "ts-node prisma/seeds/test.ts"
```

```python
# Django — management command
# python manage.py seed --mode=development

from django.core.management.base import BaseCommand
from faker import Faker

fake = Faker()

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--mode', default='development')

    def handle(self, *args, **options):
        if options['mode'] == 'development':
            self.seed_development()
        elif options['mode'] == 'test':
            self.seed_test()

    def seed_development(self):
        for _ in range(20):
            user = User.objects.create(
                email=fake.email(),
                name=fake.name(),
            )
            for _ in range(random.randint(0, 10)):
                Order.objects.create(
                    user=user,
                    total=fake.pydecimal(min_value=10, max_value=500),
                )
```

---

## Test Database Isolation

```typescript
// ✅ Reset DB between test suites (not between individual tests)
beforeAll(async () => {
  await prisma.$executeRaw`TRUNCATE TABLE orders, users, tenants CASCADE`
  testData = await seedTest(prisma)
})

afterAll(async () => {
  await prisma.$disconnect()
})

// ✅ Transaction rollback per test (faster than truncate)
beforeEach(async () => {
  await prisma.$executeRaw`BEGIN`
})
afterEach(async () => {
  await prisma.$executeRaw`ROLLBACK`
})

// ✅ Parallel test isolation — each worker gets own schema
// Jest: use --shard or testPathPattern to partition
// Vitest: use test.concurrent with isolated DB per worker
const DB_URL = `postgresql://localhost/myapp_test_${process.env.JEST_WORKER_ID}`
```

---

## Fake Data Best Practices

```yaml
realistic_but_safe:
  - "Use faker for names, emails, addresses — never real PII"
  - "Use consistent seed for reproducible tests: faker.seed(12345)"
  - "Phone numbers: use 555-xxxx range (reserved for fiction)"
  - "Credit cards: use Stripe test numbers (4242 4242 4242 4242)"

consistency:
  - "Related data must be consistent (order.userId must exist in users)"
  - "Dates should be logical (createdAt < updatedAt, order.date < shipment.date)"
  - "Amounts should be positive, quantities should be integers"

volume:
  development: "10-50 of each entity (enough to see pagination, charts)"
  performance: "10K-100K rows (load testing seed)"
  edge_cases: "Empty states, max-length strings, unicode, special chars"
```

---

## Anti-patterns

```yaml
shared_test_data:
  bad: "All tests share same DB data — test A modifies, test B fails"
  fix: "Reset/rollback between tests. Each test creates its own data."

hardcoded_ids:
  bad: "expect(user.id).toBe('550e8400-e29b-...')"
  fix: "Use factory-generated data, assert on properties not IDs"

real_pii_in_seeds:
  bad: "Seed with real customer emails/names from production"
  fix: "Always use faker. Anonymize if copying production data."

no_edge_cases:
  bad: "Only test happy path with perfect data"
  fix: "Factory overrides for edge cases: empty strings, null, max values"
```
