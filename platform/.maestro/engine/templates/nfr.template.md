---
id: "{{PROJECT_KEY}}-NFR-{{NNN}}"
title: "{{TITLE}}"
status: draft            # draft | approved
scope_target: "mvp"      # mvp | production — right-size the targets
---

# Non-Functional Requirements

> Every NFR must be measurable and testable. Avoid vague words ("fast", "secure") — give a number/criterion.

## Performance
<!-- e.g., p95 API latency < 300ms at 50 rps; page LCP < 2.5s -->

## Scalability
<!-- expected load, growth, concurrency target -->

## Availability & Reliability
<!-- uptime target, RTO/RPO, error budget -->

## Security
<!-- authn/authz model, data protection, OWASP coverage, secret handling -->

## Privacy & Compliance
<!-- PII handling, GDPR/relevant standard, data retention -->

## Usability & Accessibility
<!-- WCAG level, key usability criteria -->

## Maintainability & Observability
<!-- logging, metrics, tracing, code quality gates -->

## Portability / Compatibility
<!-- browsers, devices, environments -->

## Verification
<!-- how each NFR above is tested/measured (links to tests) -->
