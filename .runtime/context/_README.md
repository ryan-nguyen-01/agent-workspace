# `.runtime/context`

This directory is the durable context and runtime memory for `.claude` agents.

Agents read `index.yaml` first, then open only the memory files relevant to the current task. This prevents each new conversation from rereading the whole brain.

## Required files

```text
index.yaml               Small routing index for selective reads
project-brain.yaml       Project-level memory, policies, freshness
service-catalog.yaml     Service inventory and source-code paths
agent-registry.yaml      Generated service coders and approved scopes
test-policy.yaml         Per-service test and manual verification policy
skill-registry.yaml      Stack-to-skill selection registry
workflow-state.yaml      Current workflow state
summary.md               Human-readable short project memory
architecture.md          Durable architecture and flow notes
conventions.md           Durable coding conventions
common/generics.md       Reusable asset index
feedback/                Patterns and anti-patterns
services/<service>.yaml  Per-service brain and service-specific memory
```

Application source code does not live here. It lives in local clones under `services/<service-name>` or another path recorded in `service-catalog.yaml`.

Do not store secrets, passwords, raw tokens, or long logs here.
