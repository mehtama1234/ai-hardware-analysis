# Kubernetes deployment

This profile runs the API and one durable worker as sidecars in a single pod.
That preserves the pilot's SQLite/PVC single-writer constraint while giving
Kubernetes control over probes, restart, resources, and persistent artifacts.

Build and publish an immutable image tag to the cluster's image registry,
create the API secret out of band, and set the release tag in the
kustomization:

```bash
kubectl create secret generic verification-pilot-api \
  --from-literal=api-key="$(openssl rand -hex 32)" \
  --dry-run=client -o yaml | kubectl apply -f -
kustomize edit set image verification-pilot=registry.example/verification-pilot:2026.09.10
kubectl apply -k deployment/kubernetes
kubectl rollout status deployment/verification-pilot
```

Before applying a release, run the operator preflight. It validates the
manifest structure, pinned shared image, probes, non-root policy, secret
reference, PVC, egress NetworkPolicy, and required recovery/pilot artifacts; `--render` also checks
that the local cluster tooling can render the overlay:

```bash
python3 scripts/preflight_verification_deployment.py --render
```

The rendered deployment pins both API and worker containers to the same image
digest/tag, while the PVC retains SQLite state and evidence across pod restarts.
The NetworkPolicy permits DNS only; add narrowly scoped egress rules for any
customer adapter endpoint rather than granting unrestricted worker access.
The pod disables service-account token automount and both containers drop all
Linux capabilities and forbid privilege escalation. It also requires the
cluster `RuntimeDefault` seccomp profile and uses read-only container roots;
tool scratch data is confined to the mounted `/tmp` `emptyDir`.
Each container also has an explicit ephemeral-storage request and limit to
prevent tool output from exhausting node disk.
The base manifest contains no credential value; rotate the secret with the same
`kubectl create secret ... | kubectl apply -f -` pattern and restart the
deployment during a controlled maintenance window.

Use a managed database/queue and object storage before scaling beyond one pod;
the SQLite PVC is intentionally a bounded pilot deployment.

The production backup overlay is
`deployment/kubernetes/verification-backup-cronjob.yaml`. It runs the
policy-validated backup entry point hourly with `Forbid` concurrency, bounded
history, retries, a secret-backed database URL, and non-root/read-only
execution. Apply it only after creating the referenced production Secret and
ConfigMap and routing backup output to managed retention storage.
`verification-production-config.example.yaml` lists the required non-secret
ConfigMap keys and the out-of-band database Secret shape. Copy it into the
customer configuration system and replace every example value before applying;
it is intentionally excluded from the base kustomization.
The executable customer-production overlay is
`deployment/kubernetes/production`. It consumes those externally managed
objects, switches the deployment tier, and includes the scheduled-backup
CronJob:

```bash
kubectl kustomize --load-restrictor LoadRestrictionsNone deployment/kubernetes/production \
  | kubectl apply -f -
```
Before applying, run the semantic preflight against the rendered file:

```bash
kubectl kustomize --load-restrictor LoadRestrictionsNone deployment/kubernetes/production \
  >/tmp/verification-production-overlay.yaml
python3 scripts/preflight_customer_production_overlay.py \
  /tmp/verification-production-overlay.yaml
```
