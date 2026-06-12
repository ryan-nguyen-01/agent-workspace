# Methodologies

This directory contains the official delivery playbooks for `maestro`.

The active setting lives in `.maestro/methodology.yaml`. The coordinator reads that file first, then uses
these documents to choose the right operating style for the work in front of it.

## Available Playbooks

| Methodology | Use when | Default posture |
| --- | --- | --- |
| [Risk-Based Workflow Routing](risk-based-routing.md) | The project needs to switch between fast and governed work. | Select the smallest flow that still preserves safety. |
| [Spec-Driven Development](spec-driven-development.md) | Work is document-led, auditable, or spans design through release. | Governed lifecycle with explicit artifacts. |
| [Eval-Driven AI Development](eval-driven-ai.md) | Model behavior, RAG, prompts, tools, or evals are part of the product. | Hypothesis, evaluation, safety, and iteration. |
| [Enterprise Agent Governance](enterprise-agent-governance.md) | Production agents, multiple teams, systems, environments, or compliance boundaries are involved. | Governed agent operation with owner, contract, eval, and audit controls. |

Use [selection-matrix.md](selection-matrix.md) when a request could fit more than one methodology.
Use [industry-alignment.md](industry-alignment.md) to map workspace methodology names to current
production-agent patterns such as durable workflows, human-in-the-loop, eval-driven AI, trace evidence,
artifact management, plugins, hooks, and enterprise agent governance.

Legacy aliases are still accepted for older workspaces:

| Legacy alias | Canonical term |
| --- | --- |
| `adaptive` | `risk-based-routing` |
| `adlc` | `spec-driven-development` |
| `ai-native` | `eval-driven-ai` |
| `agentic-enterprise`, `ae` | `enterprise-agent-governance` |
