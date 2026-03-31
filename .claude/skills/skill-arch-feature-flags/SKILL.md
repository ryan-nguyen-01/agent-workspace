---
name: skill-arch-feature-flags
description: Best practices feature flags — gradual rollout, A/B testing, kill switch, targeting rules, flag lifecycle, và implementation với OpenFeature, Unleash, LaunchDarkly patterns.
---

# Skill: Feature Flags

## Khi nào cần Feature Flags

```yaml
ALWAYS use khi:
  - "Deploy code trước khi feature ready (trunk-based development)"
  - "Gradual rollout cho user base lớn (1% → 10% → 50% → 100%)"
  - "A/B testing (variant A vs B, measure conversion)"
  - "Kill switch cho features có risk (payment, new algorithm)"
  - "Beta/early access program"
  - "Ops toggles (maintenance mode, debug logging)"

NOT needed khi:
  - "Feature nhỏ, low risk, deploy xong là enable cho tất cả"
  - "Config values cố định (dùng env vars)"
```

---

## Flag Types

```yaml
release_flag:
  purpose: "Decouple deploy from release"
  lifecycle: "Short-lived (remove after 100% rollout)"
  example: "new-checkout-flow: OFF → 10% → 50% → 100% → remove flag"

experiment_flag:
  purpose: "A/B testing, measure impact"
  lifecycle: "Medium (weeks-months), remove after decision"
  example: "pricing-page-variant: control | variant-a | variant-b"

ops_flag:
  purpose: "Operational control, circuit breaker"
  lifecycle: "Long-lived, always present"
  example: "maintenance-mode: ON/OFF, enable-cache: ON/OFF"

permission_flag:
  purpose: "Feature gating per plan/tier"
  lifecycle: "Permanent"
  example: "enable-export-csv: free=OFF, pro=ON, enterprise=ON"
```

---

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────┐
│  Admin UI   │────▶│  Flag Service    │────▶│  Flag Store  │
│  (manage)   │     │  (API + rules)   │     │  (DB/Redis)  │
└─────────────┘     └────────┬─────────┘     └──────────────┘
                             │
                    ┌────────┼────────┐
                    ▼        ▼        ▼
              ┌─────────┐┌────────┐┌────────┐
              │ Backend ││Frontend││ Mobile │
              │  SDK    ││  SDK   ││  SDK   │
              └─────────┘└────────┘└────────┘
```

### Flag Evaluation Flow

```yaml
evaluation_order:
  1: "Check if flag exists → default value if not"
  2: "Check kill switch override → immediate ON/OFF"
  3: "Check user targeting rules (userId, email, attributes)"
  4: "Check segment rules (plan, country, cohort)"
  5: "Check percentage rollout (hash userId → bucket)"
  6: "Return default variant"
```

---

## Implementation

### Backend SDK Pattern

```typescript
// Feature flag service
interface FlagContext {
  userId: string
  tenantId?: string
  email?: string
  plan?: 'free' | 'pro' | 'enterprise'
  country?: string
  attributes?: Record<string, string>
}

interface FeatureFlagService {
  isEnabled(flagKey: string, context: FlagContext): Promise<boolean>
  getVariant(flagKey: string, context: FlagContext): Promise<string>
}

// Implementation with local cache + remote sync
class FeatureFlagServiceImpl implements FeatureFlagService {
  private cache: Map<string, FlagDefinition> = new Map()
  private syncInterval: NodeJS.Timer

  constructor(private readonly flagStore: FlagStore) {
    this.syncFlags()
    this.syncInterval = setInterval(() => this.syncFlags(), 30_000) // 30s
  }

  async isEnabled(flagKey: string, context: FlagContext): Promise<boolean> {
    const flag = this.cache.get(flagKey)
    if (!flag) return false // unknown flag = disabled

    if (flag.killSwitch !== undefined) return flag.killSwitch

    // User targeting
    if (flag.targetUsers?.includes(context.userId)) return true
    if (flag.excludeUsers?.includes(context.userId)) return false

    // Segment rules
    for (const rule of flag.rules ?? []) {
      if (this.matchesRule(rule, context)) return rule.enabled
    }

    // Percentage rollout
    if (flag.rolloutPercentage !== undefined) {
      const bucket = this.hashToBucket(flagKey, context.userId)
      return bucket < flag.rolloutPercentage
    }

    return flag.defaultValue
  }

  async getVariant(flagKey: string, context: FlagContext): Promise<string> {
    const flag = this.cache.get(flagKey)
    if (!flag?.variants) return 'control'

    // Consistent hashing — same user always gets same variant
    const bucket = this.hashToBucket(flagKey, context.userId)
    let cumulative = 0
    for (const variant of flag.variants) {
      cumulative += variant.weight
      if (bucket < cumulative) return variant.name
    }
    return 'control'
  }

  private hashToBucket(flagKey: string, userId: string): number {
    // Murmur3 hash → 0-100 range (deterministic)
    const hash = murmur3(`${flagKey}:${userId}`)
    return hash % 100
  }

  private matchesRule(rule: FlagRule, ctx: FlagContext): boolean {
    return rule.conditions.every(c => {
      const value = ctx[c.attribute] ?? ctx.attributes?.[c.attribute]
      switch (c.operator) {
        case 'eq': return value === c.value
        case 'in': return c.values?.includes(value)
        case 'gt': return Number(value) > Number(c.value)
        default: return false
      }
    })
  }

  private async syncFlags() {
    const flags = await this.flagStore.getAllFlags()
    this.cache = new Map(flags.map(f => [f.key, f]))
  }
}
```

### Usage in Application Code

```typescript
// ✅ Clean usage — check flag at decision point
class CheckoutService {
  constructor(private flags: FeatureFlagService) {}

  async checkout(userId: string, cart: Cart) {
    const context: FlagContext = { userId, plan: user.plan }

    if (await this.flags.isEnabled('new-checkout-flow', context)) {
      return this.newCheckoutFlow(cart)
    }
    return this.legacyCheckoutFlow(cart)
  }
}

// ✅ A/B test — track variant for analytics
class PricingPageController {
  async getPricingPage(req: Request) {
    const variant = await this.flags.getVariant('pricing-experiment', {
      userId: req.user.id,
      country: req.user.country,
    })

    // Track which variant user saw
    await this.analytics.track('pricing_page_viewed', {
      userId: req.user.id,
      variant,
    })

    return { variant, prices: this.getPricesForVariant(variant) }
  }
}

// ✅ Kill switch — instant disable
class PaymentService {
  async processPayment(dto: PaymentDto) {
    if (!await this.flags.isEnabled('payments-enabled', { userId: dto.userId })) {
      throw new ServiceUnavailableException('Payments temporarily disabled')
    }
    // proceed...
  }
}
```

### Frontend SDK

```typescript
// React hook
function useFeatureFlag(flagKey: string): boolean {
  const { user } = useAuth()
  const [enabled, setEnabled] = useState(false)

  useEffect(() => {
    flagService.isEnabled(flagKey, {
      userId: user.id,
      plan: user.plan,
    }).then(setEnabled)
  }, [flagKey, user.id])

  return enabled
}

// Usage
function Dashboard() {
  const showNewWidget = useFeatureFlag('dashboard-new-widget')

  return (
    <div>
      <StatsGrid />
      {showNewWidget ? <NewWidget /> : <LegacyWidget />}
    </div>
  )
}

// Variant hook for A/B tests
function useVariant(flagKey: string): string {
  const { user } = useAuth()
  const [variant, setVariant] = useState('control')

  useEffect(() => {
    flagService.getVariant(flagKey, { userId: user.id }).then(setVariant)
  }, [flagKey, user.id])

  return variant
}
```

---

## Flag Database Schema

```sql
CREATE TABLE feature_flags (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  key VARCHAR(100) NOT NULL UNIQUE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  type VARCHAR(20) NOT NULL DEFAULT 'release',  -- release, experiment, ops, permission
  default_value BOOLEAN NOT NULL DEFAULT false,
  kill_switch BOOLEAN,
  rollout_percentage INT CHECK (rollout_percentage BETWEEN 0 AND 100),
  target_users TEXT[],           -- specific user IDs
  exclude_users TEXT[],
  rules JSONB DEFAULT '[]',     -- targeting rules
  variants JSONB,               -- A/B test variants
  created_by VARCHAR(100),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ        -- auto-cleanup reminder
);

-- Audit log for flag changes
CREATE TABLE flag_audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  flag_key VARCHAR(100) NOT NULL,
  action VARCHAR(50) NOT NULL,   -- created, updated, enabled, disabled, deleted
  changed_by VARCHAR(100) NOT NULL,
  old_value JSONB,
  new_value JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Flag Lifecycle

```yaml
lifecycle:
  1_create: "Define flag with default OFF"
  2_develop: "Code behind flag, deploy to production (still OFF)"
  3_test: "Enable for internal team (target_users: [team IDs])"
  4_canary: "Enable for 1-5% of users (rollout_percentage: 5)"
  5_ramp: "Gradually increase: 10% → 25% → 50% → 100%"
  6_stable: "Flag at 100% for 1-2 weeks, monitor metrics"
  7_cleanup: "Remove flag from code + database"

cleanup_rules:
  - "Release flags: remove within 2 weeks of 100% rollout"
  - "Experiment flags: remove after decision made"
  - "Ops flags: keep indefinitely (documented)"
  - "Set expires_at when creating flag → alert if not cleaned up"
  - "CI check: warn if flag older than 90 days still in code"

stale_flag_detection: |
  // CI script to detect stale flags
  const flags = await db.query(`
    SELECT key, type, created_at FROM feature_flags
    WHERE type = 'release'
    AND rollout_percentage = 100
    AND updated_at < NOW() - INTERVAL '14 days'
  `)
  if (flags.length > 0) {
    console.warn(`Stale flags to clean up: ${flags.map(f => f.key).join(', ')}`)
  }
```

---

## Anti-patterns

```yaml
flag_in_flag:
  bad: "if (flagA && flagB && !flagC) — nested flag dependencies"
  fix: "Flags should be independent. Combine into 1 flag if tightly coupled."

permanent_release_flag:
  bad: "Release flag still in code 6 months after 100% rollout"
  fix: "Set expiry, CI warns on stale flags, schedule cleanup."

no_default:
  bad: "Flag service down → crash"
  fix: "Always have safe default. Flag check should never throw."

testing_only_with_flag_on:
  bad: "Tests only test new code path — legacy path untested"
  fix: "Test BOTH paths: flag ON and flag OFF"

client_side_sensitive:
  bad: "Secret feature visible in client bundle even when flag OFF"
  fix: "Server-side flag check for sensitive features. Client only gets boolean."
```
