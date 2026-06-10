# Visual Workflow

Flow diagrams for Maestro, written in **Mermaid** (text) so both humans and AI agents can read and
update them. They reflect the current architecture: Direction gate, prerequisites, decomposition,
real-user QC, Git-flow.

> Rendering: GitHub and most viewers render Mermaid natively. **VS Code's built-in Markdown
> preview does NOT** — install the "Markdown Preview Mermaid Support" extension, or view the file on
> GitHub.

## 1. System overview

```mermaid
flowchart TD
  U["User: command or natural language"] --> C["Coordinator: single entrypoint"]
  C --> CL{"Classify scope and mode"}
  CL -->|framework| FM["Targeted edits"]
  CL -->|idea or greenfield| DG["Direction gate: Blueprint approval"]
  CL -->|approved spec| TA["Task Analysis"]
  DG -->|approved| TA
  TA --> SA["Solution Architect when needed"]
  SA --> PL["Coder Leader: decompose and assign"]
  PL --> CO["Service and built-in coders"]
  CO --> DV["Dev Verification"]
  DV --> QC["QC Runner: full test cases"]
  QC -->|bug| BR["Bug Router"]
  BR --> CO
  QC -->|pass| MEM["Memory Update"]
  MEM --> DONE["DONE"]
  C -.reads.-> KB[("Knowledge, Registry, Rules")]
```

## 2. Bootstrap: onboarding and coder creation

```mermaid
flowchart TD
  S["Request"] --> Q{"Project Brain fresh?"}
  Q -->|no or stale| ON["Onboarding: scan project"]
  ON --> AF["Agent Factory: propose coders"]
  AF -->|user approval R-011-01| RC["Coders ready"]
  Q -->|yes| RC
  Q -->|framework| FM["Skip onboarding"]
```

## 3. Task execution: full pipeline

```mermaid
flowchart TD
  I["Idea or task"] --> DG{"Idea or greenfield?"}
  DG -->|yes| BP["Blueprint gate: scope, architecture, stack, UI-UX. User approves. R-019-0a"]
  DG -->|approved spec| TA
  BP -->|approved| TA["Task Analysis: AC plus decompose. R-022"]
  TA --> PR{"Prerequisites ok? R-021"}
  PR -->|missing| ASK["Refuse: report missing docs. No guessing"]
  PR -->|ok| ARC["Architecture review when required"]
  ARC --> PLAN["Coder Leader: small tasks plus context_bundle"]
  PLAN --> CODE["Coders build per Code Layout"]
  CODE --> DV{"Dev Verification: min 80 percent plus critical checks"}
  DV -->|fail| CODE
  DV -->|Code Done| HO["QC Handoff"]
  HO --> QC["QC Runner: full test cases"]
  QC -->|bug| BUG["Bug Router"]
  BUG --> CODE
  QC -->|pass and zero bugs| MEM["Memory Update"]
  MEM --> DONE["DONE local"]
```

## 4. QC and bug routing

```mermaid
flowchart TD
  HO["QC Handoff"] --> QC["QC Runner: derive full test cases. R-022-08"]
  QC --> R{"Result"}
  R -->|blocker bug| SB["Stop immediately"]
  SB --> BR["Bug Router"]
  R -->|non blocker bug| BR
  BR --> FIX["Dev fix"]
  FIX --> RT["Re-QC: bug scope plus regression"]
  RT --> R
  R -->|all pass and zero open bugs| QD["QC_DONE"]
```

## 5. State machine

```mermaid
stateDiagram-v2
  [*] --> NEW
  NEW --> ANALYZED
  ANALYZED --> ARCHITECTURE_REVIEWING
  ARCHITECTURE_REVIEWING --> PLANNED
  ANALYZED --> PLANNED
  PLANNED --> IN_DEV
  IN_DEV --> DEV_VERIFYING
  DEV_VERIFYING --> DEV_BLOCKED
  DEV_BLOCKED --> IN_DEV
  DEV_VERIFYING --> DEV_DONE
  DEV_DONE --> QC_TESTING
  QC_TESTING --> BLOCKED_BY_BUG
  BLOCKED_BY_BUG --> FIXING
  FIXING --> QC_RETESTING
  QC_RETESTING --> QC_TESTING
  QC_TESTING --> QC_DONE
  QC_DONE --> MEMORY_SYNCING
  MEMORY_SYNCING --> DONE
  DONE --> [*]
```

## 6. Deep onboarding

```mermaid
flowchart TD
  ST["Onboarding start"] --> SC["Scan: stacks, components, conventions"]
  SC --> KB["Write knowledge plus test-policy"]
  KB --> IDX["Build memory index"]
  IDX --> CAND["Propose coder candidates"]
  CAND --> AP{"User approval"}
  AP -->|yes| GEN["Agent Factory generates scoped coders"]
  AP -->|no| HOLD["Hold: no generic coders"]
```

## 7. Skill composition

```mermaid
flowchart LR
  A["Agent"] --> RS["required_skills"]
  A --> CS["contextual_skills by stack"]
  A --> OS["optional_skills on trigger"]
  RS --> B["Skill budget plus selection policy"]
  CS --> B
  OS --> B
  B --> EXEC["Agent executes. Skills are knowledge, not agents. R-014"]
```

## 8. Principle flow: evidence and refusal

```mermaid
flowchart TD
  REQ["Request"] --> K{"Enough info and prerequisites? R-021"}
  K -->|missing critical| ASK["Ask or refuse: report the gap. Never invent"]
  K -->|ok| ACT["Act with evidence"]
  ACT --> EV{"Verifiable evidence?"}
  EV -->|no| NOCLAIM["Do NOT claim done"]
  EV -->|yes| OK["Report done with evidence. Karpathy 4"]
```

## 9. Direction gate: idea to approved blueprint

```mermaid
flowchart TD
  IDEA["User idea: chat or ship"] --> DISC["Discovery plus architecture proposal"]
  DISC --> BP["product-blueprint.yaml: scope, architecture, stack, features to AC"]
  BP --> UX{"Has UI?"}
  UX -->|yes| PROTO["UI-UX HTML CSS prototype in docs experience wireframes"]
  UX -->|no| REV{"User reviews and approves?"}
  PROTO --> REV
  REV -->|changes requested| BP
  REV -->|approved| BUILD["Build. Normal chat stops at gates. Ship auto-runs to done"]
```

## 10. Git-flow

```mermaid
flowchart TD
  T["Task"] --> FB["feature branch off develop"]
  FB --> CM["Milestone commits: Conventional, local"]
  CM --> GATE{"Outward action? push, PR, merge, tag"}
  GATE -->|needs user approval R-020-10| OK["User approves"]
  OK --> PR["PR then squash merge to develop"]
  PR --> REL["release branch to main and develop plus tag"]
  REL --> HOT["hotfix off main when needed"]
```

> Folder layout is documented as a text tree in `folder-guide.md` and the workspace layout section of
> `CLAUDE.md` (a tree is clearer than a diagram for directories).
