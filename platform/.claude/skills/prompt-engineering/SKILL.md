---
name: prompt-engineering
description: Design, structure, version, and regression-test prompts for LLM features — system prompts, few-shot, output contracts, prompt-as-code discipline. Use when writing or changing any prompt in an AI product.
category: data-ai
---

# Prompt Engineering (prompt-as-code)

Prompts are CODE: versioned, reviewed, and regression-tested. A prompt edit without evals is an
untested deploy (R-019-10).

## Structure

```text
- System prompt: role + hard constraints + output contract first; context second; examples last.
- Output contract: specify format precisely (JSON schema/keys, language, length); validate downstream —
  never parse free text by hope.
- Few-shot: 2-5 GOLD examples beat 20 mediocre ones; cover one edge case explicitly.
- Variables: template placeholders typed and documented ({{user_query}}, {{context}}); never
  string-concat untrusted input into instructions (see llm-security).
```

## Discipline

```text
- Live in ai/prompts/, versioned (v1, v2...) with a CHANGELOG line per change: what + why + eval delta.
- Every prompt has a paired eval set (ai/evals/) — changing the prompt re-runs it (EVAL GATE).
- Pin model + params per prompt (model id, temperature, max tokens) — "works on my model" is real.
- Measure before optimizing: collect failure cases into the eval set, then iterate.
- Token budget: know each prompt's input/output cost; context stuffing is a cost and quality bug.
```

## Anti-patterns

```text
Editing a prompt in production without evals; vague instructions ("be helpful"); contradictory rules;
prompt logic that belongs in code (use code for deterministic transforms); one mega-prompt doing 5 jobs
(split per task); secrets/PII pasted into prompts (R-013).
```
