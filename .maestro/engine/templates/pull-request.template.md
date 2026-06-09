<!-- Pull Request description (R-020-11). Fill in, keep high-signal, no secrets. -->

## Summary

<!-- What this PR does, in 1–3 sentences. Reference the task id. -->
- Task: <TASK-ID>
- Type: feat | fix | refactor | docs | test | chore
- <one-line summary>

## What changed

<!-- Key changes, grouped. Link files where useful. -->
-

## Why

<!-- The problem/goal and the reasoning behind the approach. -->
-

## Test & QC evidence

<!-- Real evidence, not claims (R-019-10). -->
- Build: <command + result>
- Tests: <suite + pass count>
- Real-user QC: <UI / API / UX / edge — result; link qc-test-results.yaml>
- Open bugs: 0 (all QC bugs fixed, R-019-QC3)

## How to run locally

```bash
# install / build / run / test
```

## Risk & rollout

- Risk: low | medium | high — <why>
- Migrations / breaking changes: <none | details>
- Out of scope: deployment/provisioning (separate phase, R-019-00c)

## Checklist

- [ ] Conventional commits (attribution trailer per `git.commit_attribution`, R-020-05/07)
- [ ] No secrets / .env / large logs committed (R-020-08)
- [ ] Merge target correct (develop for features; main+develop for release/hotfix)
- [ ] Acceptance criteria from the approved blueprint are met
