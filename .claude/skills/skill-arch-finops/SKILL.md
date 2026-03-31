---
name: skill-arch-finops
description: Cloud cost optimization (FinOps) — right-sizing, spot/preemptible instances, reserved capacity, storage tiering, idle resource cleanup, cost allocation tags, budget alerts, và cost-aware architecture.
---

# Skill: FinOps (Cloud Cost Optimization)

## Cost-Aware Architecture

```yaml
principle: "Design for cost from the start — not optimize after the bill arrives"

cost_hierarchy:
  1_eliminate: "Don't run what you don't need"
  2_right_size: "Match resources to actual usage"
  3_reserve: "Commit for predictable workloads"
  4_spot: "Use excess capacity for fault-tolerant workloads"
  5_optimize: "Improve code/queries to use fewer resources"
```

---

## Compute Optimization

```yaml
right_sizing:
  problem: "Running m5.xlarge (4 vCPU, 16GB) when actual usage is 0.5 vCPU, 2GB"
  process:
    1: "Monitor CPU/memory utilization for 2 weeks"
    2: "If avg CPU < 30% → downsize"
    3: "If avg memory < 50% → downsize"
    4: "Right-size iteratively (don't jump from xlarge to small)"

  kubernetes: |
    # Set requests = actual usage, limits = burst capacity
    resources:
      requests:
        cpu: 100m      # based on actual p50 usage
        memory: 128Mi
      limits:
        cpu: 500m      # burst capacity
        memory: 512Mi
    # VPA (Vertical Pod Autoscaler) auto-adjusts

spot_instances:
  savings: "60-90% vs on-demand"
  good_for: "Stateless workers, batch jobs, CI/CD, dev/staging"
  bad_for: "Databases, stateful services, real-time critical"
  strategy: |
    # AWS: Spot Fleet with diversification
    # Mix instance types to reduce interruption risk
    # Always have on-demand fallback for critical services

reserved_instances:
  savings: "30-60% vs on-demand (1-3 year commitment)"
  good_for: "Predictable baseline workload (production DB, core API)"
  tips:
    - "Start with 1-year no-upfront (flexibility)"
    - "Only reserve after 3+ months of stable usage data"
    - "Use Savings Plans (flexible across instance types)"

auto_scaling:
  - "Scale down aggressively during off-hours (nights, weekends)"
  - "Use scheduled scaling for predictable patterns"
  - "Scale to zero for dev/staging environments (Knative, Karpenter)"
```

---

## Database Cost

```yaml
optimization:
  right_size_db: "Monitor connections, CPU, IOPS — downsize if underutilized"
  read_replicas: "Route read queries to cheaper read replicas"
  connection_pooling: "PgBouncer reduces connection overhead (fewer DB instances needed)"

  reserved_instances: "Production DB = predictable → reserve for 30-50% savings"

  storage:
    - "Use gp3 (not gp2) for EBS — cheaper per IOPS"
    - "Enable auto-scaling storage (don't over-provision)"
    - "Archive old data to cheaper storage (S3, Glacier)"

  query_optimization:
    - "Slow queries = more CPU = bigger instance needed"
    - "Add indexes for common queries"
    - "EXPLAIN ANALYZE top 10 slowest queries monthly"
    - "Pagination instead of loading entire tables"

  managed_vs_self:
    managed: "RDS/Cloud SQL — easier but 30-40% more expensive"
    self_hosted: "EC2 + PostgreSQL — cheaper but ops overhead"
    recommendation: "Managed until DB cost > $1000/month, then evaluate"
```

---

## Storage Cost

```yaml
s3_tiering:
  standard: "Frequent access — $0.023/GB/month"
  infrequent: "Monthly access — $0.0125/GB (50% cheaper)"
  glacier_instant: "Quarterly access — $0.004/GB"
  glacier_deep: "Annual access — $0.00099/GB (99% cheaper than standard)"

lifecycle_rules: |
  # Auto-transition objects based on age
  {
    "Rules": [{
      "ID": "archive-old-data",
      "Status": "Enabled",
      "Transitions": [
        { "Days": 90, "StorageClass": "STANDARD_IA" },
        { "Days": 365, "StorageClass": "GLACIER_IR" },
        { "Days": 730, "StorageClass": "DEEP_ARCHIVE" }
      ],
      "Expiration": { "Days": 2555 }  // delete after 7 years
    }]
  }

cleanup:
  - "Delete incomplete multipart uploads (they accumulate cost)"
  - "Enable S3 Intelligent-Tiering for unpredictable access patterns"
  - "Compress before storing (gzip, zstd)"
  - "Use appropriate format (Parquet for analytics, not CSV)"
```

---

## Idle Resource Cleanup

```yaml
common_waste:
  - "Unattached EBS volumes (detached but still billing)"
  - "Idle load balancers (no targets)"
  - "Unused Elastic IPs ($3.6/month each)"
  - "Old snapshots and AMIs"
  - "Dev/staging running 24/7 (schedule shutdown)"
  - "Orphaned Lambda functions"
  - "Unused NAT Gateways ($32/month + data)"

automation: |
  # AWS: schedule dev environment shutdown
  # EventBridge rule: stop at 8PM, start at 8AM (weekdays only)
  # Saves 65% on dev/staging compute costs

  # Kubernetes: scale to zero off-hours
  kubectl scale deployment api --replicas=0  # 8PM
  kubectl scale deployment api --replicas=2  # 8AM
```

---

## Cost Allocation & Monitoring

```yaml
tagging:
  required_tags:
    - "Environment: production | staging | dev"
    - "Team: backend | frontend | platform"
    - "Service: api | worker | web"
    - "CostCenter: engineering | marketing"
  enforcement: "AWS SCP / Tag Policy — block untagged resources"

budget_alerts:
  - "Monthly budget per team/service"
  - "Alert at 50%, 80%, 100% of budget"
  - "Anomaly detection (sudden cost spike)"

tools:
  aws: "Cost Explorer, Budgets, Trusted Advisor"
  gcp: "Billing Reports, Recommender"
  multi_cloud: "Infracost (IaC cost estimation), Kubecost (K8s cost)"

review:
  weekly: "Top 5 cost drivers, any anomalies"
  monthly: "Full cost review, right-sizing recommendations"
  quarterly: "Reserved instance evaluation, architecture review"
```

---

## Anti-patterns

```yaml
over_provisioning:
  bad: "Production runs on m5.4xlarge 'just in case' — 10% utilized"
  fix: "Start small, monitor, scale up when needed"

no_auto_scaling:
  bad: "Fixed 10 instances 24/7 — peak is 2 hours/day"
  fix: "Auto-scale: 2 instances baseline, scale to 10 during peak"

dev_always_on:
  bad: "Dev/staging environment running nights and weekends"
  fix: "Schedule shutdown (save 65%+)"

no_cost_visibility:
  bad: "One big AWS bill — no idea which service costs what"
  fix: "Tag everything, set per-service budgets, weekly review"

premature_multi_az:
  bad: "Dev environment deployed across 3 AZs with redundant DBs"
  fix: "Multi-AZ for production only. Single AZ for dev/staging."
```
