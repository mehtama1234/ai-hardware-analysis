# Kubernetes deployment

This profile runs the API and one durable worker as sidecars in a single pod.
That preserves the pilot's SQLite/PVC single-writer constraint while giving
Kubernetes control over probes, restart, resources, and persistent artifacts.

Build and publish `verification-pilot:latest` to the cluster's image registry,
replace the example Secret value, then apply:

```bash
kubectl apply -f deployment/kubernetes/verification-pilot.yaml
kubectl rollout status deployment/verification-pilot
```

Use a managed database/queue and object storage before scaling beyond one pod;
the SQLite PVC is intentionally a bounded pilot deployment.
