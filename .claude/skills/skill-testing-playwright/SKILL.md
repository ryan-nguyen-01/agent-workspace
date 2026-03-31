---
name: skill-testing-playwright
description: Best practices viết E2E tests với Playwright: page objects, fixtures, visual testing, API mocking và CI integration.
---

# Skill: Playwright E2E Testing

## Setup & Config

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  timeout: 30_000,
  expect: { timeout: 5_000 },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,  // ✅ Retry on CI only
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { open: 'never' }],
    process.env.CI ? ['github'] : ['list'],
  ],

  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',  // ✅ Trace for debugging failures
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    // Setup project (auth)
    { name: 'setup', testMatch: '**/auth.setup.ts' },

    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        storageState: 'e2e/.auth/user.json',
      },
      dependencies: ['setup'],
    },
    {
      name: 'mobile',
      use: { ...devices['iPhone 14'] },
      dependencies: ['setup'],
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
})
```

## Auth Setup (Global)

```typescript
// e2e/auth.setup.ts
import { test as setup, expect } from '@playwright/test'

const authFile = 'e2e/.auth/user.json'

setup('authenticate', async ({ page }) => {
  await page.goto('/login')
  await page.getByLabel('Email').fill('test@example.com')
  await page.getByLabel('Password').fill('password123')
  await page.getByRole('button', { name: 'Sign in' }).click()

  await page.waitForURL('/dashboard')
  await expect(page.getByText('Welcome')).toBeVisible()

  // ✅ Save auth state — reused across all tests
  await page.context().storageState({ path: authFile })
})
```

## Page Object Model

```typescript
// e2e/pages/users.page.ts
import { Page, Locator, expect } from '@playwright/test'

export class UsersPage {
  readonly page: Page
  readonly heading: Locator
  readonly createButton: Locator
  readonly searchInput: Locator
  readonly userTable: Locator

  constructor(page: Page) {
    this.page = page
    this.heading = page.getByRole('heading', { name: 'Users' })
    this.createButton = page.getByRole('button', { name: 'Add User' })
    this.searchInput = page.getByPlaceholder('Search users...')
    this.userTable = page.getByRole('table')
  }

  async goto(): Promise<void> {
    await this.page.goto('/dashboard/users')
    await this.heading.waitFor()
  }

  async createUser(data: { email: string; name: string; password: string }): Promise<void> {
    await this.createButton.click()

    const dialog = this.page.getByRole('dialog')
    await dialog.getByLabel('Email').fill(data.email)
    await dialog.getByLabel('Name').fill(data.name)
    await dialog.getByLabel('Password').fill(data.password)
    await dialog.getByRole('button', { name: 'Create User' }).click()

    await dialog.waitFor({ state: 'hidden' })
  }

  async searchUsers(query: string): Promise<void> {
    await this.searchInput.fill(query)
    await this.page.waitForLoadState('networkidle')
  }

  async deleteUser(name: string): Promise<void> {
    const row = this.userTable.getByRole('row', { name: new RegExp(name) })
    await row.getByRole('button', { name: 'Delete' }).click()
    await this.page.getByRole('button', { name: 'Confirm' }).click()
    await row.waitFor({ state: 'detached' })
  }

  async getUserCount(): Promise<number> {
    const rows = this.userTable.getByRole('row')
    return (await rows.count()) - 1  // Subtract header row
  }
}
```

## Tests

```typescript
// e2e/users.spec.ts
import { test, expect } from '@playwright/test'
import { UsersPage } from './pages/users.page'

test.describe('Users management', () => {
  let usersPage: UsersPage

  test.beforeEach(async ({ page }) => {
    usersPage = new UsersPage(page)
    await usersPage.goto()
  })

  test('should display users list', async () => {
    await expect(usersPage.heading).toBeVisible()
    await expect(usersPage.userTable).toBeVisible()
    const count = await usersPage.getUserCount()
    expect(count).toBeGreaterThan(0)
  })

  test('should create new user', async ({ page }) => {
    const email = `test-${Date.now()}@example.com`

    await usersPage.createUser({
      email,
      name: 'Test User',
      password: 'Password123!',
    })

    // ✅ Verify the user appears in the list
    await expect(page.getByText(email)).toBeVisible()
  })

  test('should search users', async ({ page }) => {
    await usersPage.searchUsers('admin')

    const rows = usersPage.userTable.getByRole('row')
    const count = await rows.count()
    expect(count).toBeGreaterThanOrEqual(1)  // At least header + 1 result
  })
})
```

## API Mocking

```typescript
// ✅ Mock API responses để test edge cases
test('should show error when API fails', async ({ page }) => {
  await page.route('**/api/v1/users', route => {
    route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({ error: 'Internal server error' }),
    })
  })

  await page.goto('/dashboard/users')
  await expect(page.getByText('Failed to load users')).toBeVisible()
})

// ✅ Mock slow responses
test('should show loading state', async ({ page }) => {
  await page.route('**/api/v1/users', async route => {
    await new Promise(resolve => setTimeout(resolve, 2000))
    route.continue()
  })

  await page.goto('/dashboard/users')
  await expect(page.getByTestId('loading-spinner')).toBeVisible()
})
```

## Visual Testing

```typescript
// ✅ Screenshot comparison
test('user card visual', async ({ page }) => {
  await page.goto('/dashboard/users/123')
  await expect(page.getByTestId('user-card')).toHaveScreenshot('user-card.png', {
    maxDiffPixelRatio: 0.01,
  })
})
```

## Anti-patterns

```typescript
// ❌ Locator bằng CSS class hoặc arbitrary attributes
page.locator('.btn-primary')  // ❌ Fragile, implementation detail
page.locator('[data-v-abc123]')  // ❌ Generated attributes

// ✅ User-facing locators
page.getByRole('button', { name: 'Submit' })
page.getByLabel('Email')
page.getByTestId('submit-btn')  // Acceptable as last resort

// ❌ Hard-coded waits
await page.waitForTimeout(3000)  // ❌ Flaky!
// ✅ Wait for specific state
await expect(page.getByText('Success')).toBeVisible()

// ❌ Test phụ thuộc nhau (shared state)
test('create then delete user', ...)  // ❌ Depends on previous test!
// ✅ Mỗi test tự setup data riêng

// ❌ Không cleanup test data
// ✅ afterEach hoặc dùng unique IDs mỗi test
```
