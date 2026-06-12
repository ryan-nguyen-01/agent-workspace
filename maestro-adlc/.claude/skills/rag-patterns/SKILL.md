---
name: rag-patterns
description: Retrieval-Augmented Generation done right — chunking, embeddings, retrieval quality, citations, freshness, and retrieval evals. Use when building or debugging any RAG feature.
category: data-ai
---

# RAG Patterns

Most "the AI answers wrong" bugs in RAG are RETRIEVAL bugs. Evaluate retrieval separately from
generation, always.

## Pipeline decisions (record each in the LLD)

```text
1. Chunking: by structure (headings/sections) > fixed tokens; keep titles/breadcrumbs in the chunk;
   200-800 tokens typical; overlap only when sections are interdependent.
2. Embeddings: one model consistently; re-embed on model change (version the index!).
3. Retrieval: top-k + similarity threshold; hybrid (BM25 + vector) for jargon/IDs; metadata filters
   (tenant, date, doctype) BEFORE similarity, not after.
4. Context assembly: dedupe, order by relevance, fit the budget; include source ids for citations.
5. Answering: instruct "answer ONLY from context; say 'not found' otherwise" — and EVAL that it does.
6. Citations: every claim maps to a chunk id the UI can show; uncited claims are hallucination risk.
```

## Freshness & sync

```text
Source-of-truth changes -> re-index path must exist (job/trigger), or the product confidently serves
stale answers. Track index version + last-sync in observability.
```

## Eval retrieval separately (ai/evals/)

```text
- Retrieval evals: golden question -> expected chunk ids (recall@k, MRR). Run on chunking/embedding/
  threshold changes.
- Generation evals: question + fixed context -> expected answer properties (grounded, cites, refuses
  when absent).
- "Not in corpus" questions are mandatory eval cases: the right answer is a refusal.
```

## Anti-patterns

```text
Stuffing whole documents as context; ignoring tenancy/security filters in retrieval (data leak!);
evaluating only end-to-end so you cannot tell retrieval bugs from prompt bugs; no stale-index story.
```
