---
name: skill-devops-kubernetes
description: Best practices viết Kubernetes manifests: Deployments, Services, ConfigMaps, Secrets, Ingress, HPA, resource limits và Helm charts.
---

# Skill: Kubernetes

## Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-service
  namespace: production
  labels:
    app: my-service
    version: "1.0.0"
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-service
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1         # ✅ Một pod thêm khi rolling
      maxUnavailable: 0   # ✅ Không mất pod nào khi update
  template:
    metadata:
      labels:
        app: my-service
        version: "1.0.0"
    spec:
      serviceAccountName: my-service-sa

      # ✅ Security context
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        fsGroup: 1001

      # ✅ Graceful shutdown
      terminationGracePeriodSeconds: 30

      containers:
        - name: my-service
          image: ghcr.io/myorg/my-service:sha-abc123
          imagePullPolicy: IfNotPresent

          ports:
            - containerPort: 3000
              name: http
              protocol: TCP

          # ✅ Resource limits (ALWAYS set)
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi

          # ✅ Env từ ConfigMap và Secret
          env:
            - name: NODE_ENV
              value: production
            - name: PORT
              value: "3000"
          envFrom:
            - configMapRef:
                name: my-service-config
            - secretRef:
                name: my-service-secrets

          # ✅ Health probes
          livenessProbe:
            httpGet:
              path: /health/live
              port: http
            initialDelaySeconds: 10
            periodSeconds: 15
            failureThreshold: 3

          readinessProbe:
            httpGet:
              path: /health/ready
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
            failureThreshold: 3

          startupProbe:
            httpGet:
              path: /health/live
              port: http
            failureThreshold: 30
            periodSeconds: 5  # Allow 150s to start

          # ✅ Container security
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop: [ALL]

          volumeMounts:
            - name: tmp
              mountPath: /tmp

      volumes:
        - name: tmp
          emptyDir: {}

      affinity:
        # ✅ Spread pods across nodes
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchExpressions:
                    - key: app
                      operator: In
                      values: [my-service]
                topologyKey: kubernetes.io/hostname
```

## Service & Ingress

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
  namespace: production
spec:
  selector:
    app: my-service
  ports:
    - port: 80
      targetPort: http
      name: http
  type: ClusterIP  # ✅ Internal only, expose via Ingress

---
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-service
  namespace: production
  annotations:
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
    - hosts: [api.example.com]
      secretName: my-service-tls
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: my-service
                port:
                  name: http
```

## ConfigMap & Secret

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-service-config
  namespace: production
data:
  DATABASE_HOST: postgres-service
  DATABASE_PORT: "5432"
  REDIS_HOST: redis-service
  LOG_LEVEL: info

---
# k8s/secret.yaml — ✅ Use External Secrets Operator or Sealed Secrets in production
# Never commit raw secrets to git!
apiVersion: v1
kind: Secret
metadata:
  name: my-service-secrets
  namespace: production
type: Opaque
stringData:
  DATABASE_PASSWORD: ""    # Injected by CI/CD or External Secrets
  JWT_SECRET: ""
  REDIS_PASSWORD: ""
```

## HPA (Horizontal Pod Autoscaler)

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-service
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-service
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # ✅ Don't scale down too fast
      policies:
        - type: Pods
          value: 1
          periodSeconds: 60
```

## Helm Chart Structure

```
charts/my-service/
├── Chart.yaml
├── values.yaml          # Default values
├── values.production.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── hpa.yaml
│   ├── configmap.yaml
│   ├── serviceaccount.yaml
│   └── _helpers.tpl    # ✅ Reusable template helpers
```

## Anti-patterns

```yaml
# ❌ Không set resource limits
containers:
  - name: app
    image: myapp:latest  # ❌ Always pin image tag!
# Pod có thể consume unlimited resources → OOM kill other pods

# ❌ imagePullPolicy: Always với :latest (slow, no caching)
# ✅ Pin image digest: image: myapp@sha256:abc...

# ❌ Không có health probes → traffic to unhealthy pods
# ❌ Không có PodDisruptionBudget → all pods down during node drain
# ✅
apiVersion: policy/v1
kind: PodDisruptionBudget
spec:
  minAvailable: 2  # At least 2 pods available during disruption
  selector:
    matchLabels:
      app: my-service

# ❌ Secrets committed to git
# ✅ External Secrets Operator + AWS Secrets Manager/Vault
```
