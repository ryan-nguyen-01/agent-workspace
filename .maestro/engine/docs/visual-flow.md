# Visual Workflow

Flow diagrams for Maestro, written in **Mermaid** (text) so both humans and AI agents can read and
update them. They render in GitHub, Kiro, VS Code, and most Markdown viewers. These reflect the current
architecture (Direction gate, prerequisites, decomposition, real-user QC, Git-flow).

## 1. System overview

```mermaid
flowchart TD
  U["User — command OR natural language"] --> C["Coordinator (single entrypoint)"]
  C --> CL{"Classify: target_scope, execution_mode"}
  CL -->|framework maintenance| FM["Targeted edits + lightweight evidence"]
  CL -->|idea / greenfield product| DG["Direction gate: Blueprint approval"]
  CL -->|approved spec / ticket| TA["Task Analysis"]
  DG -->|approved| TA
  TA --> SA["Solution Architect (when needed)"]
  SA --> PL["Coder Leader: decompose + assign"]
  PL --> CO["Service / built-in coders"]
  CO --> DV["Dev Verification"]
  DV --> QC["QC Runner (full test cases)"]
  QC -->|bug| BR["Bug Router"] --> CO
  QC -->|pass, 0 bugs| MEM["Memory Update"] --> DONE["DONE"]
  C -. reads .-> KB[("Knowledge / Registry / Rules")]
```

## 2. Bootstrap — onboarding and coder creation

```mermaid
flowchart TD
  S["Request"] --> Q{"Project Brain present & fresh?"}
  Q -->|"no / stale (product work)"| ON["Onboarding: scan project"]
  ON --> AF["Agent Factory: propose coders"]
  AF -->|"user approval (R-011-01)"| RC["Coders ready"]
  Q -->|yes| RC
  Q -->|framework maintenance| FM["Skip onboarding"]
```

## 3. Task execution — full pipeline

```mermaid
flowchart TD
  I["Idea or task"] --> DG{"Idea / greenfield?"}
  DG -->|yes| BP["Blueprint gate: scope, architecture, stack, UI/UX prototype → user approves (R-019-0a)"]
  DG -->|approved spec| TA
  BP -->|approved| TA["Task Analysis: acceptance criteria + decompose (R-022)"]
  TA --> PR{"Prerequisites present & sufficient? (R-021)"}
  PR -->|"missing / insufficient"| ASK["Refuse: report missing docs to user (no guessing)"]
  PR -->|ok| ARC["Architecture review (when required)"]
  ARC --> PLAN["Coder Leader: small tasks + context_bundle"]
  PLAN --> CODE["Coders build per Code Layout"]
  CODE --> DV{"Dev Verification ≥80% + critical checks"}
  DV -->|fail| CODE
  DV -->|Code Done| HO["QC Handoff"]
  HO --> QC["QC Runner: full test cases per AC/endpoint/screen"]
  QC -->|bug| BUG["Bug Router"] --> CODE
  QC -->|"every case pass, 0 open bugs"| MEM["Memory Update"] --> DONE["DONE (local)"]
```

## 4. QC and bug routing

```mermaid
flowchart TD
  HO["QC Handoff"] --> QC["QC Runner: derive full test cases (R-022-08) — per AC positive+negative; per endpoint success/validation/auth/error; per screen each state"]
  QC --> R{"Result"}
  R -->|blocker bug| SB["Stop immediately"] --> BR["Bug Router"]
  R -->|non-blocker bug| BR
  BR --> FIX["Dev fix"] --> RT["Re-QC: bug scope + regression"]
  RT --> R
  R -->|"every case pass + zero open bugs (any severity)"| QD["QC_DONE"]
```

## 5. State machine

```mermaid
stateDiagram-v2
  [*] --> NEW
  NEW --> NEED_ONBOARDING
  NEED_ONBOARDING --> ONBOARDED
  ONBOARDED --> AGENTS_READY
  AGENTS_READY --> READY_FOR_ANALYSIS
  READY_FOR_ANALYSIS --> ANALYZED
  ANALYZED --> ARCHITECTURE_REVIEWING
  ARCHITECTURE_REVIEWING --> PLANNED
  ANALYZED --> PLANNED
  PLANNED --> IN_DEV
  IN_DEV --> DEV_VERIFYING
  DEV_VERIFYING --> DEV_BLOCKED
  DEV_BLOCKED --> IN_DEV
  DEV_VERIFYING --> DEV_DONE
  DEV_DONE --> QC_READY
  QC_READY --> QC_TESTING
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
  ST["Onboarding start"] --> SC["Scan repo: stacks, components, conventions"]
  SC --> KB["Write knowledge: project.yaml, components, conventions, test-policy"]
  KB --> IDX["Build memory index"]
  IDX --> CAND["Propose coder candidates"]
  CAND --> AP{"User approval"}
  AP -->|yes| GEN["Agent Factory generates scoped coders"]
  AP -->|no| HOLD["Hold — no generic coders created"]
```

## 7. Skill composition

```mermaid
flowchart LR
  A["Agent"] --> RS["required_skills"]
  A --> CS["contextual_skills (by stack)"]
  A --> OS["optional_skills (on trigger)"]
  RS --> B["Skill budget + selection policy"]
  CS --> B
  OS --> B
  B --> EXEC["Agent executes with composed skills"]
  EXEC -. "skills are knowledge, not agents (R-014)" .-> EXEC
```

## 8. Principle flow — evidence & refusal

```mermaid
flowchart TD
  REQ["Request"] --> K{"Enough info & prerequisites? (R-021)"}
  K -->|"missing critical"| ASK["Ask / refuse: report the gap — never invent"]
  K -->|ok| ACT["Act with evidence"]
  ACT --> EV{"Verifiable evidence?"}
  EV -->|no| NOCLAIM["Do NOT claim done"]
  EV -->|yes| OK["Report done with evidence (Karpathy #4)"]
```

## 9. Direction gate (idea → approved blueprint)

```mermaid
flowchart TD
  IDEA["User idea (chat or /ship)"] --> DISC["Discovery + architecture proposal"]
  DISC --> BP["product-blueprint.yaml: scope (MVP/prod), architecture (mono/micro), tech stack, features→AC"]
  BP --> UX{"Has UI?"}
  UX -->|yes| PROTO["UI/UX HTML/CSS prototype (docs/experience/wireframes)"]
  UX -->|no| REV{"User reviews & approves?"}
  PROTO --> REV
  REV -->|changes requested| BP
  REV -->|approved| BUILD["Build (normal chat: stop at gates · /ship: auto-run to done)"]
```

## 10. Git-flow

```mermaid
flowchart TD
  T["Task"] --> FB["feature branch off develop"]
  FB --> CM["Milestone commits (Conventional, local) — attribution per git.commit_attribution"]
  CM --> GATE{"Outward action? push / PR / merge / tag"}
  GATE -->|"needs user approval (R-020-10)"| OK["User approves"]
  OK --> PR["PR → squash merge → develop"]
  PR --> REL["release branch → main + develop + tag"]
  REL --> HOT["hotfix off main when needed"]
```

> Folder layout is documented as a text tree in `folder-guide.md` and the workspace layout section of
> `CLAUDE.md` (a tree is clearer than a diagram for directories).
