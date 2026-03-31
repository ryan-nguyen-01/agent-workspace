---
name: skill-arch-disaster-recovery
description: Disaster Recovery (DR) — RTO/RPO definitions, backup strategies, failover procedures, multi-region architecture, database recovery, runbook templates, và DR testing.
---

# Skill: Disaster Recovery

## RTO & RPO

```
RPO (Recovery Point Objective)          RTO (Recovery Time Objective)
"How much data can we lose?"            "How long can we be down?"

  ←───── data loss ─────→              ←──── downtime ────→
  Last backup         Disaster          Disaster         Recovered
       │                  │                 │                │
       ▼                  ▼                 ▼                ▼
  ─────●──────────────────●─────────────────●────────────────●─────
```

```yaml
tiers:
  tier_1_critical: # Payment, auth, core API
    rpo: "< 1 minute (synchronous replication)"
    rto: "< 15 minutes (automatic failover)"
    strategy: "Multi-AZ, synchronous standby, auto-failover"

  tier_2_important: # User data, orders, content
    rpo: "< 1 hour (async replication + WAL archiving)"
    rto: "< 1 hour (warm standby)"
    strategy: "Async replica, point-in-time recovery"

  tier_3_standard: # Analytics, logs, reports
    rpo: "< 24 hours (daily backup)"
    rto: "< 4 hours (cold restore)"
    strategy: "Daily snapshots, S3 backup"
```

---

## Backup Strategies

### Database Backups

```yaml
postgresql:
  continuous_archiving:
    method: "WAL (Write-Ahead Log) archiving to S3"
    rpo: "Minutes (continuous)"
    restore: "Point-in-time recovery to any second"
    config: |
      # postgresql.conf
      archive_mode = on
      archive_command = 'aws s3 cp %p s3://backups/wal/%f'

  automated_snapshots:
    method: "pg_dump or RDS automated snapshots"
    frequency: "Every 6 hours + before major changes"
    retention: "Daily: 30 days, Weekly: 1 year, Monthly: 7 years"
    command: |
      pg_dump -Fc -h localhost -U app mydb > backup_$(date +%Y%m%d_%H%M%S).dump
      aws s3 cp backup_*.dump s3://backups/daily/

  rds_automated:
    snapshots: "Automated daily, retained 35 days"
    pitr: "Point-in-time recovery within retention window"
    cross_region: "Copy snapshots to DR region"

verification:
  - "Test restore WEEKLY (automated)"
  - "Full DR drill QUARTERLY"
  - "Verify backup integrity (checksum)"
  - "Monitor backup job failures → alert immediately"
```

### Application & Infrastructure Backups

```yaml
infrastructure_as_code:
  backup: "Git repo IS the backup — Terraform/K8s manifests"
  restore: "terraform apply / kubectl apply — recreate from code"
  prerequisite: "ALL infrastructure changes via IaC (no manual changes)"

secrets:
  backup: "Vault auto-backup, AWS Secrets Manager cross-region replication"
  restore: "Restore from backup or re-create from documented rotation procedure"

file_storage:
  s3: "Cross-region replication enabled"
  config: |
    # S3 cross-region replication
    aws s3api put-bucket-replication --bucket primary-bucket \
      --replication-configuration '{
        "Rules": [{
          "Status": "Enabled",
          "Destination": { "Bucket": "arn:aws:s3:::dr-bucket" }
        }]
      }'
```

---

## Failover Procedures

### Database Failover

```yaml
automated_failover:
  aws_rds:
    trigger: "Primary unhealthy for 60 seconds"
    process: "RDS promotes standby → DNS endpoint auto-updates"
    rto: "1-2 minutes"
    action: "None (automatic). Monitor alerts."

  manual_failover:
    trigger: "Region outage, corruption, or automated failover fails"
    steps:
      1: "Confirm primary is truly down (not just monitoring flap)"
      2: "Promote read replica to primary"
      3: "Update connection strings (or DNS failover)"
      4: "Verify application connectivity"
      5: "Notify team via incident channel"
    command: |
      # AWS RDS — promote replica
      aws rds promote-read-replica --db-instance-identifier mydb-replica

      # PostgreSQL manual
      pg_ctl promote -D /var/lib/postgresql/data
```

### Application Failover

```yaml
multi_az (same region):
  architecture: "Load balancer → instances across 2-3 AZs"
  failover: "Automatic — LB routes around unhealthy AZ"
  cost: "Minimal (same region, cross-AZ traffic ~$0.01/GB)"

multi_region (cross region):
  architecture: "DNS failover (Route53) → primary region + DR region"
  modes:
    active_passive:
      primary: "us-east-1 (serves all traffic)"
      dr: "eu-west-1 (warm standby, receives replicated data)"
      failover: "DNS switch to DR region (manual or health-check based)"
      rto: "5-15 minutes"

    active_active:
      regions: "Both serve traffic (geo-routing)"
      complexity: "High — data sync, conflict resolution"
      rto: "Near zero (traffic auto-routes)"
      cost: "2x infrastructure"

  dns_failover: |
    # Route53 health check failover
    aws route53 create-health-check --caller-reference $(date +%s) \
      --health-check-config '{
        "IPAddress": "primary-lb-ip",
        "Port": 443,
        "Type": "HTTPS",
        "ResourcePath": "/health",
        "FailureThreshold": 3
      }'
```

---

## DR Runbook Template

```markdown
# DR Runbook: [Service Name]

## Trigger Conditions
- [ ] Primary region unreachable for > 5 minutes
- [ ] Database corruption detected
- [ ] Authorized by: on-call lead + engineering manager

## Pre-Failover Checks (2 min)
1. Confirm outage is real (not monitoring false positive)
2. Check primary region status page
3. Notify incident channel: "Initiating DR failover for [service]"

## Failover Steps (10 min)
1. [ ] Promote DR database replica
   ```
   aws rds promote-read-replica --db-instance-identifier mydb-dr
   ```
2. [ ] Update application config to point to DR database
3. [ ] Scale up DR application instances
   ```
   kubectl scale deployment api --replicas=5 --context=dr-cluster
   ```
4. [ ] Switch DNS to DR region
   ```
   aws route53 change-resource-record-sets --hosted-zone-id Z123 \
     --change-batch '{"Changes":[{"Action":"UPSERT","ResourceRecordSet":{...}}]}'
   ```
5. [ ] Verify health checks passing on DR

## Post-Failover Verification (5 min)
- [ ] Application responding (curl health endpoint)
- [ ] Database queries working (check key page loads)
- [ ] Background jobs processing
- [ ] Monitoring dashboards showing DR metrics

## Communication
- [ ] Update status page: "Operating in DR mode"
- [ ] Notify stakeholders via email/Slack
- [ ] Estimated time to full recovery: [X hours]

## Failback (when primary recovered)
1. [ ] Resync data from DR → primary
2. [ ] Verify primary database integrity
3. [ ] Gradually shift traffic back (10% → 50% → 100%)
4. [ ] Confirm primary fully operational
5. [ ] Demote DR back to standby mode
```

---

## DR Testing

```yaml
testing_schedule:
  monthly: "Backup restore test (verify backups work)"
  quarterly: "Full failover drill (practice runbook)"
  annually: "Chaos engineering (simulate region failure)"

backup_restore_test: |
  1. Take latest backup
  2. Restore to isolated environment
  3. Run smoke tests against restored DB
  4. Verify row counts match production
  5. Log result: PASS/FAIL + duration

failover_drill: |
  1. Schedule maintenance window
  2. Simulate primary failure
  3. Execute DR runbook
  4. Measure actual RTO
  5. Verify RPO (check data gap)
  6. Failback to primary
  7. Post-drill review: what worked, what didn't

chaos_engineering:
  tools: [Chaos Monkey, Gremlin, LitmusChaos]
  experiments:
    - "Kill random pod → verify auto-restart"
    - "Block network to DB → verify circuit breaker"
    - "Fill disk → verify alerting triggers"
    - "Simulate AZ failure → verify cross-AZ failover"
```

---

## Anti-patterns

```yaml
untested_backups:
  bad: "Backups running daily but never tested restore"
  fix: "Monthly automated restore test. A backup you can't restore is no backup."

no_runbook:
  bad: "DR procedure is in someone's head"
  fix: "Written runbook, practiced quarterly, accessible to all on-call"

single_region:
  bad: "Everything in us-east-1 — entire app dies if region goes down"
  fix: "At minimum: cross-region backup. Ideal: multi-AZ with cross-region DR."

manual_only_failover:
  bad: "Failover requires 5 manual steps at 3 AM"
  fix: "Automate common failures (health-check based DNS failover)"

no_failback_plan:
  bad: "Failover to DR but no plan to return to primary"
  fix: "Failback is part of the runbook. Test it."
```
