---
name: skill-testing-load
description: Best practices load & performance testing — k6, Artillery, test scenarios (smoke, load, stress, spike, soak), metrics (latency, throughput, error rate), SLA validation, và CI integration.
---

# Skill: Load & Performance Testing

## Test Types

```
┌─────────────┬────────────────┬──────────────┬─────────────────────────┐
│ Type        │ VUs            │ Duration     │ Purpose                 │
├─────────────┼────────────────┼──────────────┼─────────────────────────┤
│ Smoke       │ 1-5            │ 1 min        │ Verify script works     │
│ Load        │ Expected (100) │ 10-30 min    │ Validate SLA at normal  │
│ Stress      │ 2-3x expected  │ 10-30 min    │ Find breaking point     │
│ Spike       │ 0 → 500 → 0   │ 5 min        │ Test sudden burst       │
│ Soak        │ Expected       │ 2-8 hours    │ Find memory leaks, drift│
└─────────────┴────────────────┴──────────────┴─────────────────────────┘
```

---

## k6 (Recommended — JS-based, Grafana ecosystem)

### Basic Test

```javascript
import http from 'k6/http'
import { check, sleep } from 'k6'

export const options = {
  stages: [
    { duration: '1m', target: 50 },    // ramp up to 50 VUs
    { duration: '5m', target: 50 },    // stay at 50 VUs
    { duration: '1m', target: 0 },     // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],   // 95% requests < 500ms
    http_req_failed: ['rate<0.01'],     // < 1% errors
    http_reqs: ['rate>100'],            // > 100 RPS
  },
}

const BASE_URL = __ENV.BASE_URL || 'https://api.myapp.com'

export default function () {
  // Login
  const loginRes = http.post(`${BASE_URL}/auth/login`, JSON.stringify({
    email: `user${__VU}@test.com`,
    password: 'testpassword',
  }), { headers: { 'Content-Type': 'application/json' } })

  check(loginRes, {
    'login status 200': (r) => r.status === 200,
    'has access token': (r) => r.json('accessToken') !== undefined,
  })

  const token = loginRes.json('accessToken')
  const authHeaders = { headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' } }

  // Get orders
  const ordersRes = http.get(`${BASE_URL}/orders?page=1&limit=20`, authHeaders)
  check(ordersRes, {
    'orders status 200': (r) => r.status === 200,
    'has orders': (r) => r.json('data').length > 0,
  })

  // Create order
  const createRes = http.post(`${BASE_URL}/orders`, JSON.stringify({
    items: [{ productId: 'prod-1', quantity: 1 }],
  }), authHeaders)

  check(createRes, {
    'create status 201': (r) => r.status === 201,
  })

  sleep(1) // think time between iterations
}
```

### Scenario Patterns

```javascript
// Stress test — find breaking point
export const options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 200 },   // increase
    { duration: '5m', target: 200 },
    { duration: '2m', target: 300 },   // increase more
    { duration: '5m', target: 300 },
    { duration: '2m', target: 0 },     // ramp down
  ],
}

// Spike test — sudden burst
export const options = {
  stages: [
    { duration: '1m', target: 10 },    // warm up
    { duration: '10s', target: 500 },   // spike!
    { duration: '2m', target: 500 },    // hold spike
    { duration: '10s', target: 10 },    // drop
    { duration: '2m', target: 10 },     // recovery
    { duration: '1m', target: 0 },
  ],
}

// Multiple scenarios — realistic user mix
export const options = {
  scenarios: {
    browse: {
      executor: 'constant-vus',
      vus: 80,
      duration: '10m',
      exec: 'browseProducts',       // 80% of users browse
    },
    purchase: {
      executor: 'constant-vus',
      vus: 15,
      duration: '10m',
      exec: 'purchaseFlow',         // 15% purchase
    },
    admin: {
      executor: 'constant-vus',
      vus: 5,
      duration: '10m',
      exec: 'adminDashboard',       // 5% admin
    },
  },
}
```

### Custom Metrics

```javascript
import { Trend, Counter, Rate } from 'k6/metrics'

const orderCreationTime = new Trend('order_creation_duration')
const ordersCreated = new Counter('orders_created')
const orderFailRate = new Rate('order_fail_rate')

export default function () {
  const start = Date.now()
  const res = http.post(`${BASE_URL}/orders`, payload, headers)
  const duration = Date.now() - start

  orderCreationTime.add(duration)

  if (res.status === 201) {
    ordersCreated.add(1)
    orderFailRate.add(false)
  } else {
    orderFailRate.add(true)
  }
}
```

---

## Artillery (YAML-based, good for CI)

```yaml
# load-test.yml
config:
  target: "https://api.myapp.com"
  phases:
    - duration: 60
      arrivalRate: 10
      name: "Warm up"
    - duration: 300
      arrivalRate: 50
      name: "Sustained load"
    - duration: 60
      arrivalRate: 100
      name: "Peak"
  defaults:
    headers:
      Content-Type: "application/json"
  ensure:
    thresholds:
      - http.response_time.p95: 500
      - http.codes.200: { min: 95 }

scenarios:
  - name: "User flow"
    flow:
      - post:
          url: "/auth/login"
          json:
            email: "{{ $randomString() }}@test.com"
            password: "testpassword"
          capture:
            json: "$.accessToken"
            as: "token"
      - get:
          url: "/orders"
          headers:
            Authorization: "Bearer {{ token }}"
          expect:
            - statusCode: 200
```

---

## Key Metrics & SLA

```yaml
latency:
  p50: "Median — typical user experience"
  p95: "95th percentile — most users"
  p99: "99th percentile — worst case (excluding outliers)"
  targets:
    api: "p95 < 500ms, p99 < 1000ms"
    page_load: "p95 < 2s"
    search: "p95 < 200ms"

throughput:
  rps: "Requests per second (sustainable)"
  target: "Handle 2x expected peak traffic"

error_rate:
  target: "< 0.1% at normal load, < 1% at peak"
  types: [5xx, timeout, connection_refused]

saturation:
  cpu: "< 70% at normal load"
  memory: "< 80%, no leaks in soak test"
  connections: "DB pool not exhausted"
  queue: "No unbounded growth"
```

---

## CI Integration

```yaml
# .github/workflows/load-test.yml
name: Load Test
on:
  schedule:
    - cron: '0 2 * * 1'  # weekly Monday 2am
  workflow_dispatch:

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run k6 load test
        uses: grafana/k6-action@v0.3
        with:
          filename: tests/load/api-load.js
          flags: --out json=results.json
        env:
          BASE_URL: ${{ secrets.STAGING_URL }}

      - name: Check thresholds
        run: |
          # k6 exits with code 99 if thresholds fail
          echo "Load test passed all thresholds"

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: k6-results
          path: results.json
```

---

## Anti-patterns

```yaml
test_from_same_network:
  bad: "Load test from same datacenter as server → unrealistic latency"
  fix: "Test from different region or use distributed load generation"

no_think_time:
  bad: "VU sends requests as fast as possible → unrealistic"
  fix: "Add sleep(1-3) between requests to simulate real user behavior"

single_endpoint:
  bad: "Hammer only POST /orders — doesn't reflect real traffic mix"
  fix: "Multiple scenarios: 80% browse, 15% purchase, 5% admin"

ignore_error_rate:
  bad: "Server handles 1000 RPS! (but 30% are 5xx errors)"
  fix: "Track error rate alongside throughput. 1000 RPS with 0.1% errors."

no_baseline:
  bad: "Load test once, never again"
  fix: "Run weekly in CI, compare against baseline, alert on regression"
```
