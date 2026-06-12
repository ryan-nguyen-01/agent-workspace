# /evals

## Purpose

Run and inspect LLM eval suites — the engine of the ADLC EVAL GATE. AI behavior claims require eval
evidence, not demos (eval-driven-ai methodology, R-019-10).

## Responsible agent

qc-runner (executes; eval-engineer designs suites; coordinator routes)

## Subcommands

```text
/evals run [suite|feature]    Execute suite(s) from ai/evals/ (pin model/params; n>=3 when non-deterministic),
                              grade per grader, record scores + failures to .maestro/observability/evals/<run-id>/.
/evals status                 Latest scores vs thresholds per suite; deltas vs previous run (regression view).
/evals gaps                   Coverage review: features/prompts WITHOUT a suite, suites below minimum cases,
                              uncalibrated LLM-judges -> propose eval-engineer advisory.
/evals add <case>             Append a failure case from a bug/QC finding into the right dataset (failures
                              become permanent regression cases).
```

## Behavior

```text
1. Suites live in ai/evals/<feature>/ (dataset + grader + thresholds.yaml); results are recorded, never
   summarized from memory (R-024-04).
2. EVAL GATE: a failing suite blocks DONE for the feature; shrinking datasets or raising thresholds to
   pass is fabrication (R-019-QC4). Score distributions are reported, not best-of runs.
3. Prompt/model/RAG changes -> affected suites re-run automatically as part of verification.
```

## Required rules

```text
00-core-rules.md
08-qc-rules.md
19-autonomous-delivery-rules.md
24-purpose-chain-rules.md
```

## Output format

```text
🧪 Evals: <n suites> run — pass <x>/<n>
📈 Scores: <suite>: <metric>=<score> (threshold <t>, Δ vs prev <d>)
❌ Failures: <k> cases (tagged) — added to regression backlog
🔜 Next: <fix + re-run | gate clear>
```
