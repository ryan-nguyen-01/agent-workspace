# /policy-check

## Purpose

Validate workflow transitions, approval gates, and exception requests.

## Responsible agent

workflow-policy

## Required rules

```text
00-core-rules.md
11-approval-gates.md
12-artifact-contracts.md
13-security-secret-rules.md
```

## Workflow

```text
1. Read current state.
2. Read requested transition or exception.
3. Check required artifacts.
4. Check responsible agent permissions.
5. Check approval gates.
6. Return allow, deny, or needs_user_approval.
```

## Output format

```yaml
policy_decision: "allow|deny|needs_user_approval"
reason: "<reason>"
missing_artifacts: []
required_next_action: "<action>"
```
