# Services

Deployable backend services, workers, and gateways live here.

Naming patterns:

- Service: `<project>-<business-capability>-service`
- Worker: `<project>-<business-capability>-worker`
- Gateway: `<project>-<scope>-gateway`

Use bounded-context or business-capability names. Register every component in
`.maestro/registry/components.yaml`.

Internal layout follows the Code Layout Standard (feature-based + layered):
`.maestro/engine/docs/code-layout.md` — `src/modules/<feature>/` (controller/service/repository/dto/types/test) plus `core/` and `shared/`.
