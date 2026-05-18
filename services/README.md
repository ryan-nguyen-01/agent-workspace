# Services

`services/` is a local workspace for cloned application/service repositories.

It is intentionally empty in `agent-workspace` git. Users can run:

```bash
cd services
git clone <service-repo-url> <service-name>
```

Everything cloned here is ignored by git so service source code is not pushed to the agent-workspace repository.

## Where service metadata lives

Do not put agent memory or registries in this folder.

Service metadata belongs in `.runtime/context`:

```text
.runtime/context/service-catalog.yaml   Service inventory and source-code paths
.runtime/context/agent-registry.yaml    Generated service coders and approved scopes
.runtime/context/test-policy.yaml       Per-service test and verification policy
.runtime/context/skill-registry.yaml    Stack-to-skill selection registry
.runtime/context/services/<service>.yaml Per-service brain
```

## Path rule

`service.path` in `.runtime/context/service-catalog.yaml` should point to the cloned repo, normally `services/<service-name>` from the agent-workspace root. Generated coders may write only inside approved `allowed_write_paths`.
