# /ship

## Purpose

Build to a finished product autonomously. `/ship <idea or what to build>` first proposes a clear
**direction** and gets your approval, then runs the full pipeline
(`blueprint → analysis → plan → dev → verify → QC → fix-loop → done`) in **Safe Autopilot**: after
approval it does not stop at soft gates, self-heals build/test/runtime errors, and hands back a
complete, runnable product.

It is the autonomous counterpart of `/coord`. Use it when you want the system to keep going until the
app is done — but only after you sign off on the direction.

**Direction first (Blueprint gate):** from an idea, autopilot proposes the product scope (MVP vs
production), architecture style (monolith vs microservices), tech stack, features/acceptance criteria,
and tradeoffs, and asks for your explicit approval. It builds only after you approve (R-019-0a..0d).

**Local-only:** everything (install, build, tests, smoke run) happens in your local environment so you
can verify it on your own machine first. Autopilot never deploys or provisions infrastructure —
environment setup/deploy is a separate phase that runs only after you confirm the local result and
ask for it (R-019-00b/00c).

## Responsible agent

coordinator (runs the pipeline under an autonomy grant, R-019)

## Behavior

```text
0. BLUEPRINT GATE (idea/greenfield input) — the one upfront approval (R-019-0a..0d):
   Run discovery + architecture proposal and write product-blueprint.yaml covering: problem/goal/users,
   MVP vs production, monolith vs modular-monolith vs microservices (recommended + why), tech stack
   (language/frontend/backend/DB/libraries + rationale), features → acceptance criteria, non-functional
   targets, assumptions/risks/tradeoffs, out-of-scope (deploy excluded), open questions.
   If the product has a UI, the blueprint MUST also include a UI/UX proposal delivered as a viewable
   static HTML/CSS prototype (docs/experience/wireframes/index.html + per-screen pages + styles.css
   tokens, plus Mermaid flows and specs). The user opens it in a browser and approves BEFORE any UI
   coding (R-019-0a-ui; ui-ux-designer produces it, accessibility-auditor advises).
   Present it and get an EXPLICIT user decision (prefer a structured choice for MVP-vs-prod,
   mono-vs-micro, stack, and UI/UX direction). Revise on changes_requested. Do NOT build until
   status: approved.
1. After approval, record the autonomy grant in .maestro/runtime/workflow-state.yaml.autopilot
   (R-019-01), default max_attempts_per_stage=5, pre_authorized_gates=[R-011-01, R-011-03, R-011-06, R-011-10].
2. Enable tool fullaccess for the run (/access full) so terminal/file calls do not prompt per call.
   The PreToolUse guards (scope/secret/destructive) still run (R-017).
2b. Git (Git-flow, R-020-12): create feature/<task-id>-<slug> off develop and commit milestones LOCALLY
   with conventional messages + attribution line. Never auto-push/PR/merge — those wait for the user.
3. Run the normal pipeline through coordinator; acceptance criteria come from the approved blueprint.
   Soft gates auto-approve and record (R-019-04).
4. After each step, run real verification LOCALLY: build, lint (if configured), tests, and a local
   smoke run of the app when runnable. Record evidence (R-019-07).
5. On any failure, capture the error and loop: route back to coder-leader / bug-router, fix, re-verify
   (R-019-08), up to max_attempts_per_stage (R-019-09).
5b. Real-user QC (R-019-QC1..4): QC acts as a thorough end user — full test plan across UI / API / UX /
   edge / regression, logs every failure as a bug, and loops qc -> dev fix -> re-QC until EVERY test case
   passes and ZERO bugs remain (blocker AND non-blocker), not just zero blockers.
6. Stop and ask the user ONLY on a hard-stop (R-019-05): destructive/prod/irreversible action, a real
   secret/credential is required, scope expansion, policy/state change, or attempts exhausted.
   Provisioning/deploy is never done inside autopilot (R-019-00c).
7. Transition to DONE only when the definition of done holds LOCALLY (R-019-11), then deliver the
   handover (R-019-12): what was built, the exact local run commands, and verification evidence.
8. Offer provisioning/deployment as the explicit next phase — run it only after the user confirms the
   local result and asks for it.
9. On DONE, propose the git integration step (R-020-13): the feature branch name and a ready PR
   title/body; push/open the PR only after the user approves.
```

## Required rules

```text
00-core-rules.md
11-approval-gates.md
12-artifact-contracts.md
13-security-secret-rules.md
17-hook-enforcement-rules.md
19-autonomous-delivery-rules.md
```

## Stop conditions (hand back to user)

```text
Destructive / production / irreversible action required (R-011-07)
A real secret, credential, API key, or token is required (R-013)
Scope expansion beyond the declared acceptance criteria
Workflow policy / state-machine / identity change required
A stage still fails after max_attempts_per_stage (escalate with diagnostics)
```

## Output format

```text
On DONE — deliver the finished product handover:
✅ Built: <summary of the app/feature>
📁 Files: <key changed files>
▶️ Run it: <commands + env to start/use the app>
🧪 Evidence: <build/test/smoke results>
⚠️ Limitations / assumptions: <...>
🔜 Suggested next: <...>

On hard-stop — return needs_user_approval with the exact decision required and current diagnostics.
```
