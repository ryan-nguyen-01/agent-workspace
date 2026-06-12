# Conventions Memory

Status: needs onboarding.

Onboarding should populate coding, testing, API, logging, error-handling, and folder conventions discovered from the repository.

Default folder architecture: the Code Layout Standard (feature-based + layered) at `.maestro/engine/docs/code-layout.md`. Use it for greenfield components; when an existing repo already differs, record the repo's actual layout here and follow that.

## Deep coding conventions

Onboarding should populate this file with project-specific coding flow, not generic best practices.

```yaml
folder_structure: []
naming_rules: []
layering_rules: []
api_patterns: []
validation_patterns: []
error_handling_patterns: []
logging_patterns: []
transaction_patterns: []
async_job_patterns: []
migration_patterns: []
testing_patterns: []
configuration_patterns: []
anti_patterns: []
```

Each convention should include:

```yaml
- rule: ""
  applies_to: []
  evidence_paths: []
  reuse_or_follow_instruction: ""
  confidence: "low|medium|high"
```
