---
inclusion: always
---

# Product

`maestro` is a **coordinator-driven multi-agent framework** for building software — a "software company
of agents". It is a control plane installed into a project so every request flows through a governed
workflow: classify → (blueprint) → analyze → plan → dev → verify → QC → memory.

## What it provides

- A single entrypoint (`/coord`) and an autonomous build-to-done mode (`/ship`) with a self-heal loop.
- A blueprint gate: the user approves scope (MVP/production), architecture (monolith/microservices),
  tech stack, features, and UI/UX (a viewable HTML/CSS prototype) **before** coding.
- Real-user QC across UI/API/UX/edge; "done" requires zero open bugs and local verification.
- Standards: Code Layout, BA documentation (BRD/PRD/US/UC/BR/NFR/RTM), and Git-flow.

## Who & why

For builders who want consistent, governed, auditable delivery from idea to a locally-runnable product,
with humans deciding at three points: approve blueprint → accept local result → allow deploy. Everything
between is automated, evidence-based, and never fabricated.

This repository is the framework itself (the control plane), not an end-product application.
