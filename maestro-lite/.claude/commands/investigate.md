# /investigate

## Purpose

Read-only investigation: answer "what is the current state of X, what are the options, what would a
change touch?" WITHOUT creating a code change. The brownfield daily driver — ask about the system,
get an evidence-backed report (current state + solution directions + impact), then decide whether to
open a task.

## Responsible agent

task-analysis (read-only mode; coordinator routes)

## Behavior

```text
1. Scope the question; load minimal context (knowledge index -> component profiles -> targeted code reads).
2. Produce a findings report (no task folder required; for big investigations create an assisted task):
   - CURRENT STATE: how it works today — every claim cites file:line / command output (R-024-04)
   - OPTIONS: 2-3 solution directions with tradeoffs (no decision made for the user)
   - IMPACT: what each option touches (components, contracts, data, regression surface)
   - UNKNOWNS: what could not be verified + the question that resolves each
3. STRICTLY read-only: no file edits, no state transitions, no task creation unless the user asks.
4. If the user picks a direction -> hand off to /analyze-task with this report as input evidence.
```

## Required rules

```text
00-core-rules.md
21-input-prerequisites-rules.md
24-purpose-chain-rules.md
```

## Output format

```text
🔎 Investigated: <question>
📍 Current state: <findings with citations>
🧭 Options: <A/B/C + tradeoffs>
💥 Impact: <per option>
❓ Unknowns: <list + resolving questions>
🔜 Next: /analyze-task "<chosen direction>" (when you decide)
```
