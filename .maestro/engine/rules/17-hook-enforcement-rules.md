# R-017: Hook Enforcement Rules

## Applies to

The tool-adapter hook layer that turns prompt-level rules into hard guardrails. Two parallel
implementations must stay in sync:

```text
Cursor       : .cursor/hooks.json + .cursor/hooks/*.sh
Claude Code  : .claude/settings.json (hooks.PreToolUse) + scripts/hooks/*.py
```

Other adapters (Codex, Copilot, Gemini) rely on the prompt-level rules until they ship a hook runtime.

## Core principle

```text
Hooks are a safety net, not the source of truth. The rules (R-000..R-016) define behavior;
hooks deterministically BLOCK the most damaging violations even if an agent ignores a prompt rule.
A hook must fail closed for source-edit scope and destructive commands.
```

## Rules

```text
R-017-01: The Claude adapter must register three PreToolUse hooks:
          - scope-guard.py      (Write|Edit|MultiEdit|NotebookEdit) — source-edit workflow + coder scope gate (mirrors R-000, R-006).
          - secret-guard.py     (Write|Edit|MultiEdit|NotebookEdit) — block secret material in writes (R-013).
          - destructive-guard.py(Bash)                              — block destructive shell commands (R-011-07).
R-017-02: scope-guard must gate only likely application source. Framework files (.maestro/engine/**, .claude/**, scripts/**, docs, root *.md) must NOT be gated, so framework maintenance is unaffected.
R-017-03: scope-guard must fail closed: missing/invalid active task, missing task-analysis.yaml/context_plan, unapproved architecture review, or a path no active coder allows → block.
R-017-04: destructive-guard must fail closed for rm -rf, force-push to main/master, git reset --hard, git clean -df, kubectl/terraform apply|destroy|delete, DROP TABLE/DATABASE, find -delete, and fork bombs.
R-017-05: A hook block must exit non-zero (exit code 2 for Claude PreToolUse) and write an actionable reason to stderr citing the rule.
R-017-06: Hooks must have no third-party dependencies (no jq, no PyYAML). Pure Python 3.8+ / POSIX shell only, so they run in any adapter environment.
R-017-07: Execution profiles are controlled by env, not by editing hook code:
          - MAESTRO_HOOK_PROFILE = minimal | standard (default) | strict
          - MAESTRO_DISABLED_HOOKS = comma-separated hook ids to disable
          minimal disables scope-guard + secret-guard (destructive-guard stays on).
          strict additionally blocks generic secret-style assignments.
R-017-08: Disabling scope-guard or destructive-guard in a real workspace is a user-approved exception; record it where the approval lives, do not silently ship minimal as default.
R-017-09: Claude and Cursor hooks must enforce equivalent semantics. Changing one adapter's gate requires updating the other (and the architecture-health-check checks for both).
R-017-10: Hooks must never weaken approval gates (R-011) or security rules (R-013); they only ADD enforcement. A passing hook is necessary, not sufficient — agents still follow the full rule set.
R-017-11: Hook changes must keep scripts/architecture-health-check.py green (check_claude_hooks + check_cursor_hooks).
R-017-12: A hook must be safe to fail-open on internal/parse errors of its OWN payload (exit non-2), but must fail-closed on the policy conditions in R-017-03/04. Never let a malformed payload bypass a known-destructive command match.
```

## Profiles

```text
minimal  : destructive-guard only. For trusted framework-maintenance sessions where source gating is noise.
standard : all three active; scope + destructive fail closed; secret-guard blocks high-confidence patterns. DEFAULT.
strict   : standard + secret-guard also blocks generic password/secret/token assignments with a literal value.
```

## Parity matrix

```text
Concern                  Cursor                              Claude Code
source-edit scope gate   .cursor/hooks/check-task-analysis.sh scripts/hooks/scope-guard.py
secret write block       (covered in check-task-analysis)    scripts/hooks/secret-guard.py
destructive command      .cursor/hooks/block-destructive.sh  scripts/hooks/destructive-guard.py
fail-closed required     yes                                 yes
```

## Violation handling

If a hook blocks a legitimate action, do NOT disable the hook inline. Resolve the underlying rule
(create task-analysis, get architecture approval, fix the path scope), or get user approval to lower
`MAESTRO_HOOK_PROFILE` for that session. Destructive commands always require explicit user approval through
Coordinator before being run manually.
