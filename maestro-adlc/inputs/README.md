# inputs/

This folder stores **user-provided project-level reference documents** that agents should read during
onboarding and task analysis. It is different from `services/`, which contains product source code, and
from `.maestro/work/tasks/<id>/task-input.md`, which stores task-specific input.

## When To Use It

Drop documents here when:

- You are starting a new project and want agents to understand business context before reading code.
- PRD, HLD, LLD, or ADR documents live outside the product source repository.
- You need to provide API contracts, OpenAPI specs, or a domain glossary.
- You want to share runbooks, operations playbooks, or post-mortem references.
- You have diagrams such as PNG, SVG, PDF, or exported Figma material.

The onboarding agent scans this folder and cites source paths into `.maestro/knowledge/project.yaml` and
related component knowledge.

## Structure

```text
inputs/
├── README.md            This file
├── product/             PRDs, business specs, user stories, market analysis
├── architecture/        HLDs, LLDs, ADRs, system diagrams, infrastructure docs
├── api/                 OpenAPI/Swagger specs, Postman collections, API contracts
├── domain/              Domain models, glossary, business rules, data dictionary
├── runbooks/            Operations playbooks, incident response, deployment guides
└── misc/                Uncategorized files
```

Using every subdirectory is optional. If a file does not clearly match a category, place it in `misc/`.

## Supported Formats

| Format | Handling |
| --- | --- |
| `.md`, `.txt` | Read directly, parse headings and content |
| `.yaml`, `.yml`, `.json` | Parse as structured data |
| `.html` | Strip tags and extract text |
| `.pdf` | Read through the available document/read tool, subject to tool page limits |
| `.png`, `.jpg`, `.svg` | Inspect visually when multimodal reading is available |
| `.csv`, `.tsv` | Sample header and first rows |
| Other binary files | Record metadata only: filename, size, and mtime |

## How Agents Use It

**Onboarding agent** when `/onboard` runs:

1. Scan `inputs/` recursively, skipping `.gitkeep` and hidden files.
2. Create entries in `.maestro/registry/inputs.yaml` with `path`, `category`, `summary`, `last_modified`, and `confidence`.
3. Extract key facts such as architecture decisions, API contracts, and business rules into `project.yaml` with `source: inputs/<path>`.
4. Extract component-specific facts into component knowledge when relevant.

**Task Analysis agent:** read `inputs.yaml` first, then open only the files relevant to the task intent.

**Service coders:** read `inputs/api/` and `inputs/domain/` only when the task changes contracts or domain behavior.

## Confidence Ranking

Agents use this heuristic:

```text
high      mtime <= 90 days and the format is structured, such as yaml/json/openapi
medium    mtime <= 365 days and the markdown has clear headings
low       mtime > 365 days, missing metadata, or stored under misc/
```

Memory entries inferred from `inputs/` must cite their source. If source code or code review evidence
later conflicts with `inputs/`, code wins for technical truth and the agent should flag the conflict for
user review.

## Security

- Do not commit credentials, secrets, raw tokens, or private keys in any form. R-013 applies to `inputs/`.
- For confidential material such as NDA contracts or internal-only specs, add manual `.gitignore` rules:

  ```text
  inputs/product/confidential-*.md
  inputs/misc/legal-*
  ```

- Audit `inputs/` before committing to a public repository.

## Relationship To Other Folders

```text
inputs/                    User-provided persistent project-level references
services/<component>/      Product service source, tracked by monorepo or team policy
.maestro/work/tasks/<id>/       Per-task artifacts, including task-input.md
.maestro/knowledge/             Agent-generated distilled memory from the sources above
```

Rules:

- `inputs/` is the source of truth for user-provided knowledge.
- `.maestro/knowledge/` is the distilled agent brain. It does not replace `inputs/`; it cites it.
- When `inputs/` changes, run `/sync-memory --refresh-index` so agents rescan the references.
