# Verification pilot recovery runbook

This runbook applies to the bounded single-pod Kubernetes pilot, where SQLite
and evidence live on the `verification-pilot-artifacts` PVC. It is a recovery
procedure for operators; it does not replace managed database and object
storage controls required for customer production.

## Backup

Pause the worker before taking a filesystem snapshot so no job is writing while
the database and evidence are copied:

```bash
kubectl scale deployment/verification-pilot --replicas=0
kubectl wait --for=delete pod -l app=verification-pilot --timeout=120s
```

Create a snapshot or volume backup using the storage provider's supported
mechanism. The backup must include `/app/.artifacts/jobs.sqlite`, the
`/app/.artifacts/jobs/` tree, collateral, IR, and generated bundles. Record
the snapshot ID, UTC timestamp, image tag, and operator in the change log.

Resume the pilot and verify readiness and queue state:

```bash
kubectl scale deployment/verification-pilot --replicas=1
kubectl rollout status deployment/verification-pilot
kubectl port-forward service/verification-pilot 8080:8080
curl --fail http://127.0.0.1:8080/readyz
```

## Restore

1. Scale the deployment to zero and wait for the pod to terminate.
2. Restore the selected PVC snapshot into a replacement PVC with the same
   access mode and mount path.
3. Validate that `jobs.sqlite` and the job directories are present before
   starting the deployment.
4. Apply the pinned image with `kubectl apply -k deployment/kubernetes` and
   wait for `/readyz` to report `ready`.
5. Check `GET /v1/jobs` for the affected project, inspect one known evidence
   bundle, and confirm its manifest hashes before allowing new submissions.

If the restored queue contains jobs whose worker ownership is stale, the
worker's stale-job recovery path may requeue them. Preserve the original
snapshot and job IDs for audit; never delete a failed or signed-off run while
investigating an incident.

## Incident evidence

Capture the deployment image tag or digest, pod logs from API and worker,
`/healthz` and `/readyz` responses, the affected project and job IDs, and the
signoff receipt or bundle hash. Attach these to the incident record before
rotating credentials or changing the deployment.

For a local pilot rehearsal, verify a snapshot copy and restore inventory with:

```bash
python3 scripts/verify_recovery_snapshot.py /path/to/.artifacts /tmp/pilot-snapshot /tmp/pilot-restored
```

For a combined managed-state rehearsal, use
`deployment/managed_restore_drill.py` with a PostgreSQL DSN and evidence
root. It verifies the four managed tables are queryable and that the evidence
inventory restores byte-for-byte. This is a rehearsal artifact; provider-native
database backup/restore, failover, and disaster-recovery evidence are still
required for customer production.

The command compares every file digest, including `jobs.sqlite`, job evidence,
collateral, and bundles. Managed database/object-storage deployments must run
the equivalent multi-pod restore drill described in the migration plan.

The provider-native PostgreSQL rehearsal uses
`deployment/postgres_backup_restore.py --dsn ... --backup ... --restore-dsn ...`.
It invokes `pg_dump` and `pg_restore` with the password in `PGPASSWORD`, never
in process arguments, and records backup/restore digests. Use a disposable
target database for drills; the helper rejects a restore target that resolves to
the source database, and production restores still require operator review.

Before scheduling a backup, run the compatibility preflight with the same
PostgreSQL client major as the managed server; a mismatch must stop the dump
before it creates a partial artifact.
The policy-validated entry point is
`deployment/run_scheduled_backup.py --dsn ... --output-dir ...`; retain its
timestamped dump and manifest together.

The disposable provider-native rehearsal completed on 2026-09-10 using
PostgreSQL 16 container tools. It restored one project, collateral record, job,
and event into a separate database with all four counts preserved. The host
PostgreSQL 14 client was rejected by the compatibility boundary before the
matching-major rehearsal was run. Evidence is recorded in
`.artifacts/managed-postgres-restore-drill-2026-09-10.json`.

## OIDC key rotation and identity incidents

Before rotating a signing key, publish the new key in the provider JWKS while
the old key remains available. Confirm the service's
`verification_oidc_cached_keys` gauge is nonzero and that a canary token signed
with the new `kid` succeeds. The verifier refreshes its JWKS cache when it sees
an unseen key ID; `verification_oidc_jwks_unknown_kid_total` records that event.

If `VerificationPilotOidcUnknownKey` fires, compare the token issuer, audience,
and `kid` with the provider configuration, then inspect the JWKS endpoint from
the service network. Do not disable bearer validation to clear the alert. If
the cache is empty or the provider is unavailable, stop new sign-offs and
restore provider reachability or roll back the identity configuration through
the normal deployment change process. Preserve the alert, request ID, issuer,
and key ID in the incident record; never record the bearer token itself.

After the old key's provider-defined grace period, remove it from JWKS and run
one canary verification using the retained new key. Key rotation success means
both the canary and the alert-clear transition are recorded; it does not prove
tenant authorization or customer-wide identity availability.
