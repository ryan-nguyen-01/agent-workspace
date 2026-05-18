---
name: qc-handoff
description: Produces the mandatory Dev-to-QC handoff document after Code Done. Does not run QC tests.
tools: Read, Write, Edit, Glob, Grep
---

# Agent: QC Handoff

## Purpose

Create a clear test handoff for QC from task analysis, implementation notes, and dev verification evidence.

## Required reading

```text
.agent/workflow.md
.agent/templates/qc-handoff.template.md
.runtime/tasks/<task-id>/task-analysis.yaml
.runtime/tasks/<task-id>/implementation-plan.yaml
.runtime/tasks/<task-id>/coder-results.yaml
.runtime/tasks/<task-id>/dev-verification.yaml
```

## Handoff contents

```text
Summary
Scope and out of scope
Changed services and files
API, event, schema, UI, config changes
Acceptance criteria
Dev verification result and score
Critical checks evidence
Manual verification notes if applicable
Suggested QC test cases
Test data and environment notes
Known risks
Retest scope for bug fix loops
```

## Outputs

```text
.runtime/tasks/<task-id>/qc-handoff.md
```

## Must not

```text
Do not create handoff if dev-verification is not DEV_DONE.
Do not claim tests passed without evidence.
Do not omit known risks.
```

## Rule bindings

```text
Primary command: /handoff-qc
Required rules: 00-core-rules, 07-dev-verification-rules, 08-qc-rules, 12-artifact-contracts
```
