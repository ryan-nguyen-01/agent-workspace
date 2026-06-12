---
name: llm-security
description: Secure LLM features — prompt injection, jailbreaks, tool-abuse, data exfiltration, output handling, PII in prompts/logs. Use when an AI feature takes user input, calls tools, or touches private data.
category: data-ai
---

# LLM Security

The LLM is an untrusted-input processor wired to your data and tools. Treat every model output as
untrusted user input, and every prompt as a potential leak channel.

## Threat checklist (per AI feature)

```text
1. PROMPT INJECTION: user/retrieved content contains instructions ("ignore previous...").
   -> Separate channels: instructions vs data (delimiters + explicit "data is not instructions");
      retrieved chunks are DATA; eval with injection cases (mandatory in ai/evals/).
2. TOOL ABUSE: model triggers tools with attacker-shaped args.
   -> Allowlist tools per feature; validate/sandbox args like any API input; destructive tools require
      human confirm (R-011-07 applies to AI-triggered actions too).
3. EXFILTRATION: secrets/PII leak via prompts, logs, citations, or model output.
   -> Never put secrets in prompts (R-013); redact PII before sending to providers; scrub logs/traces;
      check citations do not expose other tenants' chunks.
4. TENANCY: retrieval/queries filtered by tenant BEFORE ranking (RAG data-leak classic).
5. OUTPUT HANDLING: model output rendered as HTML/SQL/shell = injection sink.
   -> Encode/parameterize; never eval/execute raw model output without validation.
6. DENIAL OF WALLET: unbounded loops/agents burning tokens -> budget caps + loop limits per request.
```

## Ship bar

```text
security-auditor advisory required for externally exposed AI features; injection + exfiltration eval
cases pass; incident path: prompt/output logs (redacted) retained enough to do RCA (incident-rca).
```
