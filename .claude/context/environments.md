# Environment Memory

Do not store real secrets here.

```yaml
environments:
  local:
    enabled: true
    base_url: "http://localhost:3000"
    required_variables: []
  dev:
    enabled: false
    base_url: ""
    required_variables: []
  sit:
    enabled: false
    base_url: ""
    required_variables: []
qc_order:
  - local
  - dev
  - sit
```
