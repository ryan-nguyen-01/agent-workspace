# R-020: Git Workflow (Git-flow)

## Applies to

Coordinator, Coder Leader, Service Coders, QC Runner, Dev Verification, Memory Update.

## Purpose

Maestro uses a **Git-flow** branching model so every task is built on an isolated branch, committed in
reviewable milestones, and integrated through merges/PRs — never by editing shared branches directly.
Local commits are free; anything that leaves the machine (push, PR, merge to shared branches, tags) is
outward-facing and requires explicit user approval.

## Branching model (Git-flow)

```text
R-020-01: Long-lived branches:
  main     production-ready, protected, tagged releases only. Never commit or merge directly by hand.
  develop  integration branch; features merge here first.
R-020-02: Supporting branches:
  feature/<task-id>-<slug>   off develop, merges back to develop. One task = one feature branch.
  release/<version>          off develop, merges to main AND develop, tagged on main.
  hotfix/<id>-<slug>         off main, merges to main AND develop (urgent production fix).
R-020-03: Never commit directly to main or develop. All work lands through a branch + merge/PR.
R-020-04: Branch names are kebab-case and carry the task id when there is one (feature/TASK-...-login).
```

## Commit policy

```text
R-020-05: Conventional Commits: <type>(<scope>): <imperative summary>. Types: feat, fix, docs, refactor,
  test, chore, perf, build, ci. Subject <= 72 chars, imperative mood, no trailing period.
R-020-06: Commit in meaningful milestones, not one giant blob: a logical unit, after dev-verification
  passes, and after QC fixes. Each commit should build. Body explains WHY when not obvious.
R-020-07: Commit attribution is configurable via `.maestro/project.yaml.git.commit_attribution`.
  When false (default) write plain commits with NO `Co-Authored-By` / agent-attribution trailer.
  When true, append the configured `git.attribution_trailer`. Respect the project setting; do not add
  an attribution trailer the user has turned off.
R-020-08: Never commit secrets, credentials, .env values, raw tokens, or large logs/binaries (R-013).
  Respect .gitignore; runtime/session state is already ignored. Stage only files relevant to the task.
R-020-09: If the directory is not a git repo, ask the user before running `git init`. Do not commit
  pre-existing unrelated changes you did not make — surface them instead.
```

## Outward-facing git (explicit user approval — gated)

```text
R-020-10: These leave the local machine or rewrite shared history and require explicit user approval
  (treat as R-011-07 destructive/outward; the destructive-guard hook also blocks the dangerous ones):
    - git push (any remote), opening or merging a PR
    - merging into main or develop
    - creating/pushing tags or a GitHub release
    - force push, history rewrite (rebase -i, reset --hard on shared, filter-branch), deleting a
      remote branch, push to main
R-020-11: PRs use .maestro/engine/templates/pull-request.template.md. The PR body states what changed,
  why, test/QC evidence, and how to run it locally. Default merge into develop is squash unless the
  user sets otherwise; release/hotfix follow Git-flow (merge to main + develop, tag).
```

## Autopilot git (R-019)

```text
R-020-12: Under an active autopilot grant, git is LOCAL-ONLY automatic:
  - At run start, create feature/<task-id>-<slug> off develop (create develop off main if missing,
    after confirming with the user when the repo already exists).
  - Commit locally at each milestone (R-020-06) with conventional messages (attribution per git.commit_attribution).
  - NEVER auto-push, auto-open/merge PRs, or merge into develop/main. Those stay user-gated (R-020-10).
R-020-13: On DONE, the handover (R-019-12) proposes the integration step for the user: the branch name,
  a ready PR title/body (from the template), and the suggested merge target (develop). Pushing/opening
  the PR runs only after the user approves.
```

## Required artifact

```text
.maestro/engine/templates/pull-request.template.md   (PR description)
```

## Violation handling

Stop and ask the coordinator to request user approval for any outward-facing git action (R-020-10).
Destructive git commands are additionally blocked by the destructive-guard hook (R-011-07, R-017).
