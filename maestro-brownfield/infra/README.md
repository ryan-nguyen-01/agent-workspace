# Infrastructure

Infrastructure source lives here: environments, Terraform, Kubernetes, deployment configuration,
pipelines, and platform observability.

Do not hide infrastructure inside an application or service directory when it is shared across the product.

Layout per the Code Layout Standard: `.maestro/engine/docs/code-layout.md` — `docker/`, `ci/`, `deploy/` (deploy used only in the post-DONE deploy phase, R-019-00c).
