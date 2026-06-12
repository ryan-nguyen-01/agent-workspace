---
name: llm-evals
description: Build and run eval suites for LLM features — datasets, graders (code + LLM-judge), thresholds, regression evals; powers the ADLC eval gate. Use before claiming any AI behavior works or changing prompts/models/RAG.
category: data-ai
---

# LLM Evals (the eval gate's engine)

"Looked good in a demo" is not evidence (R-019-10). AI behavior claims require eval runs with recorded
scores. Quality claims about model/agent behavior = eval evidence, by rule (eval-driven-ai methodology).

## Anatomy of a suite (ai/evals/<feature>/)

```text
dataset.jsonl    cases: { input, expected | rubric, tags }   — 20-50 cases beats 0; grow from real failures
grader           how a case passes:
                 - code grader: exact/regex/schema/contains — deterministic, prefer when possible
                 - LLM-judge: rubric prompt + judge model — for open-ended quality; calibrate vs human
                   labels on a sample first (judges drift!)
thresholds.yaml  pass bar per metric (e.g. grounded >= 0.9, refusal-correctness >= 0.95)
results/         every run recorded: model+prompt version, scores, failures (-> observability/evals)
```

## When evals run (non-negotiable in ADLC)

```text
- Before DONE on any AI feature (EVAL GATE — in addition to standard QC).
- On EVERY change to: prompt, model id/params, RAG pipeline, tool definitions.
- Regression: previous suites must not drop below threshold (track score deltas in the journal).
```

## Designing cases that catch real failures

```text
Happy path + hard negatives ("not in corpus" -> must refuse) + injection attempts (see llm-security)
+ format violations + edge inputs (long/empty/multilingual) + tag by feature for triage.
Non-determinism: pin temperature/seed where supported; otherwise run n>=3 and grade pass-rate, not
single-shot; thresholds are rates, not exact-match.
```

## Honesty bars

```text
Never hand-pick the passing run. Report the score distribution. A failed eval blocks DONE — shrinking
the dataset or raising thresholds to pass is fabrication (R-019-QC4 applies to evals too).
```
