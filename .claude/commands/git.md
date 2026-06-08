# /git

## Purpose

Run the Maestro Git-flow workflow: branch, commit, sync, and PR with the right policy. Local commits
are automatic/free; anything outward-facing (push, PR, merge to shared branches, tags) needs explicit
user approval. Full contract: `.maestro/engine/rules/20-git-workflow-rules.md`.

## Responsible agent

coordinator

## Subcommands

```text
/git status                 Show branch, staged/unstaged, ahead/behind, and suggested next git action.
/git branch <task-id>       Create feature/<task-id>-<slug> off develop (create develop off main if
                            missing, after confirming when the repo already exists). R-020-01/02.
/git commit                 Commit staged work as a milestone: Conventional Commit + attribution line
                            (R-020-05/06/07). Refuses secrets/large logs (R-020-08).
/git sync                   Pull/rebase the current branch onto its base (develop) to stay current.
/git pr                     Prepare a PR from pull-request.template.md (title/body/target). Pushing and
                            opening the PR run only after explicit user approval (R-020-10).
/git release <version>      Git-flow release: release/<version> off develop, merge to main+develop, tag.
                            Outward + production -> always user-approved.
/git hotfix <id>            Git-flow hotfix: hotfix/<id> off main, merge to main+develop. User-approved.
```

## Behavior

```text
1. Read 20-git-workflow-rules.md and the current repo state (branch, status, remote).
2. Never commit directly to main or develop; always use a branch (R-020-03).
3. Commit at milestones with conventional messages + Co-Authored-By line; never commit secrets.
4. STOP and ask the user before any outward-facing action (push, PR, merge, tag, force push, history
   rewrite) — these are gated (R-020-10); destructive ones are also blocked by the destructive-guard hook.
5. For autopilot runs, git stays local-only automatic: branch + milestone commits; push/PR/merge wait
   for the user (R-020-12/13).
```

## Required rules

```text
00-core-rules.md
11-approval-gates.md
13-security-secret-rules.md
17-hook-enforcement-rules.md
20-git-workflow-rules.md
```

## Stop conditions (hand back to user)

```text
Push to any remote, opening/merging a PR, merging into main or develop
Creating/pushing a tag or release
Force push, history rewrite, or deleting a remote branch
Not a git repo (ask before git init)
Pre-existing unrelated changes detected (surface, do not commit)
```

## Output format

```text
✅ Git: <action taken>
🌿 Branch: <current> (base: <develop|main>)
📦 Commit: <type(scope): summary> | none
🔜 Next (needs your approval): <push / PR / merge target>, or: nothing pending
```
