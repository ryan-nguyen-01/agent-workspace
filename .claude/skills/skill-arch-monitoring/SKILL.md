---
name: skill-arch-monitoring
description: Monitoring & observability architecture — metrics pipeline (Prometheus/Grafana), alerting strategy, dashboard design, SLI/SLO/SLA, incident management, và on-call practices.
---

# Skill: Monitoring Architecture

## Three Pillars of Observability

```
LOGS — What happened (discrete events)
  → "User 123 failed login at 10:32:15 — wrong password"
  → Tools: ELK Stack, Loki, CloudWatch Logs

METRICS — How much / how fast (aggregated numbers)
  → "HTTP 5xx rate = 2.3% in last 5 minutes"
  → Tools: Prometheus, Datadog, CloudWatch Metrics

TRACES — How request flows through system (distributed)
  → "Request abc took 450ms: API(50ms) → Service(100ms) → DB(300ms)"
  → Tools: Jaeger, Zipkin, OpenTelemetry, Datadog APM
```

---

## Metrics Pipeline

### Architecture

```
Application → Prometheus (scrape) → PromQL queries
                                        ↓
                                   Grafana (dashboards)
                                        ↓
                                   Alertmanager → PagerDuty/Slack/Email

Alternative (push-based):
Application → StatsD/Telegraf → InfluxDB/Datadog → Dashboards + Alerts
```

### Metric Types

```yaml
counter:
  description: Monotonically increasing value (resets on restart)
  examples: [total_requests, total_errors, bytes_sent]
  usage: Rate of change — rate(http_requests_total[5m])

gauge:
  description: Value that goes up and down
  examples: [active_connections, cpu_usage, queue_depth, memory_usage]
  usage: Current value — node_memory_available_bytes

histogram:
  description: Distribution of values (bucketed)
  examples: [request_duration, response_size, batch_size]
  usage: Percentiles — histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

summary:
  description: Pre-calculated percentiles (client-side)
  examples: [request_duration_p50, request_duration_p99]
  usage: Directly query percentile
  note: "Prefer histogram over summary (aggregatable across instances)"
```

### Essential Metrics (RED + USE)

```yaml
RED (for services):
  Rate: "Requests per second"
  Errors: "Error rate (5xx / total)"
  Duration: "Latency percentiles (P50, P95, P99)"
  implementation: |
    // Prometheus client (Node.js)
    const httpRequestDuration = new Histogram({
      name: 'http_request_duration_seconds',
      help: 'Duration of HTTP requests',
      labelNames: ['method', 'route', 'status_code'],
      buckets: [0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10],
    })

    const httpRequestTotal = new Counter({
      name: 'http_requests_total',
      help: 'Total HTTP requests',
      labelNames: ['method', 'route', 'status_code'],
    })

    // Middleware
    app.use((req, res, next) => {
      const end = httpRequestDuration.startTimer()
      res.on('finish', () => {
        const labels = { method: req.method, route: req.route?.path || req.path, status_code: res.statusCode }
        end(labels)
        httpRequestTotal.inc(labels)
      })
      next()
    })

USE (for resources):
  Utilization: "% resource busy (CPU, memory, disk)"
  Saturation: "Queue depth, thread pool wait time"
  Errors: "Resource errors (disk I/O errors, OOM kills)"

business_metrics:
  examples:
    - "orders_created_total (by payment_method, currency)"
    - "revenue_total (by product_category)"
    - "user_registrations_total (by source)"
    - "active_users_gauge (DAU, MAU)"
    - "cart_abandonment_rate"
```

### Custom Metrics Examples

```typescript
// Database connection pool
const dbPoolGauge = new Gauge({
  name: 'db_pool_connections',
  help: 'Database connection pool status',
  labelNames: ['state'], // active, idle, waiting
})

// Queue metrics
const queueDepth = new Gauge({
  name: 'queue_depth',
  help: 'Number of messages in queue',
  labelNames: ['queue_name'],
})

const queueProcessingDuration = new Histogram({
  name: 'queue_processing_duration_seconds',
  help: 'Time to process queue message',
  labelNames: ['queue_name', 'status'],
  buckets: [0.1, 0.5, 1, 5, 10, 30, 60],
})

// Cache hit rate
const cacheOperations = new Counter({
  name: 'cache_operations_total',
  help: 'Cache operations',
  labelNames: ['operation', 'result'], // get/set, hit/miss
})

// External API calls
const externalApiDuration = new Histogram({
  name: 'external_api_duration_seconds',
  help: 'External API call duration',
  labelNames: ['service', 'endpoint', 'status'],
})
```

---

## SLI / SLO / SLA

```yaml
SLI (Service Level Indicator):
  description: "Metric that measures service quality"
  examples:
    availability: "% of successful requests (non-5xx)"
    latency: "% of requests < 200ms"
    throughput: "Requests per second capacity"
    correctness: "% of correct results"
    freshness: "Data age (for async systems)"

SLO (Service Level Objective):
  description: "Target value for an SLI"
  examples:
    - "Availability SLO: 99.9% (43.8 min downtime/month)"
    - "Latency SLO: P99 < 500ms"
    - "Error SLO: Error rate < 0.1%"
  error_budget: |
    100% - SLO = Error Budget
    99.9% SLO → 0.1% error budget → 43.8 min/month
    
    Error budget > 0: Ship features faster
    Error budget depleted: Freeze features, focus on reliability

SLA (Service Level Agreement):
  description: "Contract with consequences (financial penalties)"
  rule: "SLA < SLO (SLO is stricter internal target)"
  example: |
    SLO: 99.95% (internal target)
    SLA: 99.9% (customer contract — credit if breached)

availability_table:
  "99%":     "7.3 hours/month downtime"
  "99.9%":   "43.8 minutes/month"
  "99.95%":  "21.9 minutes/month"
  "99.99%":  "4.38 minutes/month"
  "99.999%": "26.3 seconds/month (Google-level)"
```

---

## Alerting Strategy

### Alert Severity

```yaml
P1_critical:
  description: "Service down, data loss risk, revenue impact"
  examples:
    - "API error rate > 10% for 5 minutes"
    - "Database unreachable"
    - "Payment processing failing"
  response: "Page on-call immediately, 15 min response time"
  channel: PagerDuty + phone call

P2_high:
  description: "Degraded performance, partial outage"
  examples:
    - "P99 latency > 5s for 10 minutes"
    - "Error rate > 1% for 10 minutes"
    - "Queue depth > 10K for 15 minutes"
  response: "Page on-call, 30 min response time"
  channel: PagerDuty + Slack

P3_warning:
  description: "Anomaly, may become problem"
  examples:
    - "CPU > 80% for 30 minutes"
    - "Disk usage > 85%"
    - "Certificate expires in 14 days"
    - "Error budget burn rate elevated"
  response: "Review during business hours"
  channel: Slack only

P4_info:
  description: "Informational, no action needed"
  examples:
    - "Deployment completed"
    - "Daily backup completed"
    - "Auto-scaling triggered"
  response: "No response needed"
  channel: Slack (low-priority channel)
```

### Alert Rules (Prometheus)

```yaml
# Availability
- alert: HighErrorRate
  expr: |
    sum(rate(http_requests_total{status_code=~"5.."}[5m]))
    / sum(rate(http_requests_total[5m])) > 0.01
  for: 5m
  labels:
    severity: P2
  annotations:
    summary: "Error rate > 1% for 5 minutes"
    dashboard: "https://grafana.myapp.com/d/api-overview"

# Latency
- alert: HighLatency
  expr: |
    histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
    > 2
  for: 10m
  labels:
    severity: P2
  annotations:
    summary: "P99 latency > 2s for 10 minutes"

# Saturation
- alert: HighCPU
  expr: |
    avg(rate(process_cpu_seconds_total[5m])) > 0.8
  for: 30m
  labels:
    severity: P3

# Error budget burn
- alert: ErrorBudgetBurn
  expr: |
    1 - (sum(rate(http_requests_total{status_code!~"5.."}[1h]))
    / sum(rate(http_requests_total[1h]))) > 0.001 * 24
  for: 1h
  labels:
    severity: P2
  annotations:
    summary: "Error budget burning 24x faster than sustainable"
```

### Alert Anti-patterns

```yaml
alert_fatigue:
  bad: "100 alerts/day — team ignores all"
  fix: "Reduce to actionable alerts only, tune thresholds"

no_runbook:
  bad: "Alert fires, on-call doesn't know what to do"
  fix: "Every alert links to runbook with diagnosis + remediation steps"

alerting_on_causes:
  bad: "Alert: CPU high on server 3"
  fix: "Alert on symptoms: error rate high, latency high (user impact)"

missing_for_duration:
  bad: "Alert on single data point (transient spike)"
  fix: "Always use 'for' duration: 5m minimum"

no_escalation:
  bad: "Alert goes to Slack, nobody responds for 2 hours"
  fix: "PagerDuty with escalation: on-call → backup → manager"
```

---

## Dashboard Design

### Golden Signals Dashboard

```yaml
layout:
  row_1_overview:
    - "Request rate (req/s) — time series"
    - "Error rate (%) — time series + threshold line"
    - "P50/P95/P99 latency — time series"
    - "Active instances — gauge"

  row_2_errors:
    - "Errors by status code (4xx, 5xx) — stacked area"
    - "Errors by endpoint — table"
    - "Error log stream — live tail"

  row_3_saturation:
    - "CPU usage per instance — time series"
    - "Memory usage per instance — time series"
    - "DB connection pool — gauge"
    - "Queue depth — time series"

  row_4_dependencies:
    - "External API latency — per service"
    - "Database query duration — histogram"
    - "Cache hit rate — percentage"
    - "Queue processing rate — req/s"

best_practices:
  - "Time range selector: 1h, 6h, 24h, 7d, 30d"
  - "Annotations: deployments, incidents, config changes"
  - "SLO burn rate overlay on key charts"
  - "Link to runbook from dashboard title"
  - "Red/yellow/green thresholds on gauges"
```

---

## Structured Logging

```typescript
// ✅ Structured JSON log format
interface LogEntry {
  timestamp: string       // ISO 8601
  level: 'debug' | 'info' | 'warn' | 'error' | 'fatal'
  service: string         // "order-service"
  message: string
  requestId: string       // correlate across services
  traceId?: string        // distributed tracing
  userId?: string         // who triggered (masked)
  context: Record<string, unknown>  // structured data
  error?: {
    name: string
    message: string
    stack: string
  }
}

// ✅ Example log entries
{"timestamp":"2025-01-15T10:30:00Z","level":"info","service":"order-service","message":"Order created","requestId":"req-abc","userId":"usr-***123","context":{"orderId":"ord-456","total":99.99,"items":3}}

{"timestamp":"2025-01-15T10:30:01Z","level":"error","service":"payment-service","message":"Payment failed","requestId":"req-abc","traceId":"trace-xyz","context":{"orderId":"ord-456","provider":"stripe"},"error":{"name":"StripeError","message":"Card declined","stack":"..."}}
```

### Log Levels

```yaml
debug: "Detailed diagnostic info — DEV only, never production"
info: "Normal operations — request handled, job completed"
warn: "Something unexpected but handled — retry succeeded, deprecated API used"
error: "Failure requiring attention — external API down, validation unexpected"
fatal: "System cannot continue — DB connection lost, out of memory"

rules:
  - "Production: info and above (no debug)"
  - "Every error log MUST have context for debugging"
  - "NEVER log PII (email, phone) or secrets"
  - "Include requestId in EVERY log entry"
```

---

## Incident Management

```yaml
lifecycle:
  detect: "Alert fires or user reports"
  triage: "Assess severity (P1-P4), assign incident commander"
  mitigate: "Stop the bleeding (rollback, scale up, failover)"
  resolve: "Fix root cause"
  postmortem: "Blameless analysis within 48h"

severity:
  P1: "Complete outage, data loss — all hands"
  P2: "Major feature broken, significant user impact"
  P3: "Minor feature broken, workaround exists"
  P4: "Cosmetic issue, no user impact"

communication:
  internal: "Slack #incidents channel, status updates every 15min (P1) / 30min (P2)"
  external: "Status page update within 10min of P1"

postmortem_template: |
  ## Incident: {title}
  **Severity:** P{n} | **Duration:** {Xh Ym} | **Date:** {date}

  ### Timeline
  - {time}: Alert fired / issue reported
  - {time}: On-call acknowledged
  - {time}: Root cause identified
  - {time}: Mitigation applied
  - {time}: Fully resolved

  ### Root Cause
  {What actually went wrong — technical detail}

  ### Impact
  - Users affected: {n}
  - Duration: {Xh Ym}
  - Revenue impact: ${n} (if applicable)

  ### What Went Well
  - {Detection was fast, runbook was helpful, etc.}

  ### What Went Wrong
  - {Detection was slow, no runbook, wrong escalation, etc.}

  ### Action Items
  | Action | Owner | Due Date | Status |
  |--------|-------|----------|--------|
  | Add monitoring for X | @engineer | 2025-01-22 | TODO |
  | Update runbook for Y | @sre | 2025-01-20 | TODO |
```

---

## Anti-patterns

```yaml
monitoring_after_launch:
  bad: "Ship first, add monitoring later"
  fix: "Monitoring is part of definition of done"

vanity_dashboards:
  bad: "Dashboard shows total requests ever (useless)"
  fix: "Show rate of change, percentiles, error ratios"

no_correlation:
  bad: "Logs, metrics, traces in separate tools, no link"
  fix: "Shared requestId/traceId across all three"

alert_on_every_error:
  bad: "Alert on every 500 error (single occurrences)"
  fix: "Alert on error RATE exceeding threshold over time window"

no_baseline:
  bad: "Don't know what 'normal' looks like"
  fix: "Establish baselines, alert on deviation"
```
