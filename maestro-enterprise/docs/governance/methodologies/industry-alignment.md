# Industry Alignment

This document maps `maestro` methodology terms to current production-agent system patterns.
It is an alignment contract, not a dependency list. The workspace should borrow durable ideas from
the wider ecosystem without becoming locked to one vendor runtime.

## Alignment Principles

1. Risk-based routing comes first. The coordinator selects the smallest execution mode that preserves
   correctness, then applies Spec-Driven Development, Eval-Driven AI Development, or Enterprise Agent
   Governance as overlays when evidence requires it.
2. Methodologies are policy overlays, not separate engines. One task may use Risk-Based Workflow Routing
   plus Spec-Driven Development, Eval-Driven AI Development, Enterprise Agent Governance, or a combination.
3. Runs are execution instances. A task describes intent; a run records one attempt, including
   checkpoints, trace links, eval evidence, approvals, and reports.
4. Durable execution is a first-class requirement for long work. Tasks that may span sessions need
   checkpoints, continuation handoffs, and resumable state.
5. Artifacts are named, versioned, and addressable. PRDs, HLDs, ADRs, evals, audit logs, design specs,
   and handoffs must live in stable roots instead of being trapped in chat history.
6. Evals, traces, and verification evidence carry quality claims. Agents must not claim model quality,
   production readiness, or completion without the matching evidence or an explicit user-owned check.
7. Human-in-the-loop is a normal operating mode. If the agent lacks access to data, environments, or
   authority, it records the gap and assigns verification to `user` or `shared`.
8. Tool scope is explicit. Agents, skills, commands, hooks, and component boundaries are routed through
   registries so specialized workers do not guess their authority.
9. Enterprise autonomy requires ownership. Production agents need an accountable owner, Agent Mission,
   Behavior Contract, Autonomy Policy, Agent Definition, Eval Suite, and Audit Log before they operate
   beyond assisted development.

## Industry Pattern Mapping

| Industry pattern | Workspace mapping | Why it matters |
| --- | --- | --- |
| Agent tools, subagents, skills, hooks, and plugins | `.claude/`, `.codex/`, `.cursor/`, `.gemini/`, plus `.maestro/registry/agents.yaml` and `.maestro/registry/skills.yaml` | Keeps tool capability additive and discoverable while preserving project-specific scope. |
| Durable workflows, checkpoints, resume, and human interrupts | `.maestro/work/runs/`, `.maestro/memory/tasks/`, `.maestro/runtime/`, checkpoint and continuation handoff templates | Lets large tasks survive long conversations, failures, and user verification pauses. |
| Session, state, memory, and artifacts | `.maestro/memory/sessions/`, `.maestro/knowledge/`, `.maestro/design/`, `.maestro/decision/`, `.maestro/registry/artifacts.yaml` | Separates short-term conversation state from durable product knowledge and official deliverables. |
| Agent tracing, trace grading, eval datasets, and regression evals | `.maestro/observability/traces/`, `.maestro/observability/evals/`, Eval-Driven AI Development lifecycle, Dev Verification, QC Runner, Eval Suite | Makes quality claims reproducible and prevents "demo looked good" from becoming a release gate. |
| Graph or workflow orchestration for business processes | Risk-Based Workflow Routing and the governed state machine in `.maestro/engine/workflow.md` | Allows fast direct work and controlled multi-agent delivery in the same product workspace. |
| Enterprise agent governance and durable operations | `.maestro/governance/`, Enterprise Agent Governance artifacts, `.maestro/observability/audit/`, `.maestro/work/`, `docs/operations/` | Gives autonomous agents owners, contracts, audit trails, incident paths, and retirement decisions. |
| Model and provider abstraction | `.maestro/config/model-routing.yaml` and agent model profiles | Keeps methodology independent from a single model vendor or IDE harness. |

## Methodology Mapping

| Workspace methodology | World-standard equivalent | Use it for |
| --- | --- | --- |
| Risk-Based Workflow Routing | Risk-based routing, progressive delivery, human-in-the-loop escalation | Fast work, mixed trust environments, and user-owned verification. |
| Spec-Driven Development | Spec-driven and document-led software delivery | New products, PRD-to-release traceability, architecture, and implementation planning. |
| Eval-Driven AI Development | Eval-driven agent or LLM product development | RAG, prompts, model routing, datasets, tools, safety behavior, and regression checks. |
| Enterprise Agent Governance | Governed autonomous-agent operation | Production agents, multi-team platforms, compliance, audit, cost control, and long-lived missions. |

## Coordinator Contract

When methodology matters, the coordinator should decide in this order:

1. Select execution mode: `direct`, `assisted`, or `governed`.
2. Select primary methodology: usually `risk-based-routing`, unless one specialized method dominates
   the task.
3. Add overlays:
   - `spec-driven-development` when product documents, design, architecture, or release traceability
     drives the work.
   - `eval-driven-ai` when model behavior, prompts, RAG, data, tools, or evals are part of the product
     surface.
   - `enterprise-agent-governance` when autonomous production behavior, accountable ownership, audit,
     or cross-team governance is required.
4. Record required artifacts and verification owner.
5. Create a run when work needs durable execution, eval cycles, trace evidence, human-in-the-loop, or
   replay.
6. Record any blocked evidence as user-owned or shared verification instead of fabricating certainty.

## Application Rules

- Do not copy an external framework one-to-one. Keep the local source of truth in `.maestro/` and `docs/`.
- Do not force heavy artifacts on direct tasks. Small reversible work should stay fast.
- Do not treat Eval-Driven AI Development as only prompt engineering. It includes data, retrieval,
  tools, evals, safety, observability, and product integration.
- Do not treat Enterprise Agent Governance as only "many agents." It starts when autonomous behavior needs
  ownership, contracts, eval gates, audit, and operational control.
- Do not store private session data, secrets, transcripts, or environment-only evidence in shared docs.

## Reference Sources

- Claude Code subagents: https://code.claude.com/docs/en/subagents
- Claude Code hooks: https://code.claude.com/docs/en/hooks
- Claude Code plugins: https://code.claude.com/docs/en/plugins
- LangGraph durable execution: https://docs.langchain.com/oss/python/langgraph/durable-execution
- LangGraph persistence: https://docs.langchain.com/oss/python/langgraph/persistence
- OpenAI agent evals: https://platform.openai.com/docs/guides/agent-evals
- OpenAI trace grading: https://platform.openai.com/docs/guides/trace-grading
- OpenAI Agents SDK tracing: https://openai.github.io/openai-agents-python/tracing/
- Google ADK sessions, state, and memory: https://google.github.io/adk-docs/sessions/
- Google ADK artifacts: https://google.github.io/adk-docs/artifacts/
- Google ADK evaluation: https://google.github.io/adk-docs/evaluate/
- Microsoft Agent Framework overview: https://learn.microsoft.com/en-us/agent-framework/overview/
- Microsoft Agent Framework workflows: https://learn.microsoft.com/en-us/agent-framework/user-guide/workflows/overview
