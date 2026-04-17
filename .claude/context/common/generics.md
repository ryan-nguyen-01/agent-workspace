# Common Reusable Patterns

Status: needs onboarding.

Record reusable helpers, cross-service patterns, and existing shared utilities here after onboarding or memory updates. Do not paste large source files.

## Reusable asset index

Onboarding and memory-update agents should keep this file as a human-readable index of reusable project assets. Do not paste large source files. Record only the path, purpose, when to reuse, and evidence.

### Utilities

```yaml
utilities:
  - name: ""
    path: ""
    purpose: ""
    when_to_reuse: []
    used_by: []
    evidence: []
    confidence: "low|medium|high"
```

### Shared components and base abstractions

```yaml
shared_components: []
base_classes: []
hooks: []
middleware: []
validators: []
mappers_serializers: []
error_handling: []
logging: []
auth_helpers: []
db_transaction_helpers: []
event_queue_helpers: []
payment_helpers: []
notification_helpers: []
test_helpers: []
```

### Reuse rule

Before creating any new helper, wrapper, mapper, validator, repository abstraction, API client, transaction helper, event helper, or test utility, service coders must check this file and the relevant service brain.
