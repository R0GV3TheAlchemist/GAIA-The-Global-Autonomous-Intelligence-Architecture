# GAIA-OS Kubernetes Manifests

> **Tracks:** Issue #265

## Apply order

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/deployment-redis.yaml
kubectl apply -f k8s/deployment-chromadb.yaml
kubectl apply -f k8s/deployment-gaia.yaml
kubectl apply -f k8s/services.yaml
```

Or with kustomize (add a `kustomization.yaml` — future work):

```bash
kubectl apply -k k8s/
```

## Image

Build and push the production image before applying:

```bash
docker build --target prod -t your-registry/gaia-os:latest .
docker push your-registry/gaia-os:latest
```

Then update `deployment-gaia.yaml` → `image: your-registry/gaia-os:latest`.

## Secrets

Never commit secrets to this directory. Create a Kubernetes Secret manually:

```bash
kubectl create secret generic gaia-secrets \
  --namespace gaia \
  --from-env-file=.env
```

Then uncomment the `secretRef` block in `deployment-gaia.yaml`.

## Observability

Prometheus annotations on the GAIA backend Deployment and Service
cause a standard Prometheus Operator or prometheus-community/kube-prometheus-stack
installation to automatically scrape `/metrics` every 30 seconds.

## Scaling

Currently `replicas: 1` for all services. ChromaDB and Redis are
single-instance — scale GAIA backend replicas freely, but keep
ChromaDB and Redis as single-instance until a distributed storage
layer is in place (tracked separately under planetary-scale milestone).
