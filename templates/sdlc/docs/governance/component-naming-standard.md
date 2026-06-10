# Component Naming Standard

Use `kebab-case` and the product key configured in `.maestro/project.yaml`.

```text
Application:   <project>-<channel>-app
Service:       <project>-<business-capability>-service
Worker:        <project>-<business-capability>-worker
Gateway:       <project>-<scope>-gateway
Package:       <project>-<capability>
Design system: <project>-design-system
```

Use business capabilities and bounded contexts. Do not encode language, framework, team name, or sequence
number in component names. A component id remains stable when its path moves or its repository is extracted.
