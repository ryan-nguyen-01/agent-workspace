# Applications

Deployable user-facing applications live here.

Naming pattern: `<project>-<channel>-app`, for example `nova-web-app` or `nova-admin-app`.
Register every application in `.maestro/registry/components.yaml`.

Internal layout follows the Code Layout Standard (feature-based + layered):
`.maestro/engine/docs/code-layout.md` — `src/features/<feature>/` (components/hooks/api/types/test) plus `src/shared/`, routes in `app/` or `pages/`.
