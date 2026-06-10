# Governance

This directory is the agent-readable governance control plane.

Official human-facing governance documents remain under `docs/governance/`. This directory stores
indexes and operational governance metadata that agents need for routing, approvals, risk, and
production-agent operation.

## Domains

```text
governance/
├── agents/     Production-agent ownership, lifecycle, and contract indexes.
├── approvals/  Approval decisions and gate references.
└── risk/       Risk classification, escalation, and exception indexes.
```

Do not duplicate official policy bodies from `docs/governance/`; link to them.
