# Eval-Driven AI Development

Eval-Driven AI Development is for products where model behavior, retrieval, prompt quality, data
quality, tool use, or agent behavior is part of the product surface.

Legacy alias: `ai-native`.

## Use When

- The product includes LLM features, RAG, agents, copilots, recommendations, classification, or extraction.
- Correctness depends on prompts, tools, datasets, embeddings, model routing, or evals.
- The team needs to iterate from hypothesis to measurable behavior.
- User verification is required because private data or environments are unavailable to the agent.

## Lifecycle

```text
Hypothesis -> Data / Context -> Prototype -> Evaluation -> Safety Review
           -> Product Integration -> Observability -> Feedback Memory
```

## Required Artifacts

| Concern | Artifact |
| --- | --- |
| Product goal | PRD or feature spec |
| Data/context | input index, dataset notes, privacy constraints |
| Model behavior | eval cases, expected outputs, refusal/safety rules |
| Architecture | HLD/LLD for model routing, retrieval, tools, and fallbacks |
| Verification | agent-owned eval results, user-owned checks, or shared verification |
| Learning | memory update for prompts, failure modes, and regression cases |

## Agent Rules

- Never claim model quality without eval evidence or clearly marked user verification.
- Track prompt, retrieval, tool, and data changes as product behavior changes.
- Treat PII, credentials, private datasets, and raw transcripts as sensitive.
- Prefer small measurable experiments before large AI architecture commitments.
- Add regression cases for failures that users or QC discover.
