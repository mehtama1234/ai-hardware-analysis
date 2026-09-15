# Pilot-to-production migration plan

The open-source deployment is intentionally single-pod and SQLite-backed. Move
each boundary below before serving customer production; retain the same API,
job, evidence, and signoff contracts during migration.

## Migration stages

1. **Managed state.** Replace `jobs.sqlite` and local collateral metadata with
   PostgreSQL (transactions, migrations, backups, read replicas) and move
   bundles/collateral to versioned object storage. The provider-neutral
   `deployment/evidence_store.py` contract defines the logical key, immutable
   content, and SHA-256 boundary that the managed implementation must retain.
   The PostgreSQL table and index contract is declared in
   `deployment/managed_state_contract.py`; run it as a DSN/schema preflight
   before implementing or selecting the production provider.
   Apply and verify the contract with
   `deployment/apply_managed_state_migration.py`; retain its schema version and
   migration digest with the deployment release record.
   `deployment/postgres_job_queue.py` is the first managed repository
   implementation and preserves the pilot queue's transactional methods. Keep
   it opt-in until project and collateral repositories cut over together.
   `deployment/postgres_project_store.py` now provides the matching project and
   collateral metadata repositories; collateral bytes remain behind the
   immutable object-key boundary until an object-store provider is selected.
   `S3EvidenceStore` in `deployment/evidence_store.py` is the provider
   implementation seam; configure bucket versioning, object lock, retention,
   encryption, and IAM before selecting it for customer production.
   The authenticated `/v1/storage/controls` endpoint exposes the probe for
   deployment preflight and records the pilot boundary explicitly.
   `deployment/repository_factory.py` selects all three repositories as one
   bundle, preventing the API and worker from mixing SQLite and PostgreSQL.
   The same bundle exposes filesystem evidence in pilot and S3-compatible
   evidence in customer-production; the service should cut evidence writes
   over in the same atomic release as the repository switch.
   Bundle retrieval restores a missing local ZIP from the immutable evidence
   provider before serving a download, providing the first pod-loss
   materialization path. Full artifact materialization and restore drills are
   still required before customer production.
   Individual evidence inspection now restores missing result files and
   waveforms from provider keys before parsing them; complete artifact
   namespace migration and restore drills remain open.
   `S3EvidenceStore.control_probe()` verifies bucket versioning, server-side
   encryption, and a retention lifecycle before production selection.
   `postgres_backup_restore.py` supplies a credential-safe pg_dump/pg_restore
   rehearsal; retain its backup digest and restored-target evidence.
   `scripts/run_managed_state_repository_smoke.py` exercises the selected
   PostgreSQL project, collateral, and durable-queue repositories over a real
   DSN, including enqueue, transactional claim, and terminal finish. CI runs
   this smoke and `managed_restore_drill.py` against an ephemeral PostgreSQL
   16 service before constructing the commercial handoff; customer promotion
   still requires the same checks against managed infrastructure.
   The production configuration also requires `daily-Nd` retention (N>=7) and
   explicit RPO/RTO targets in minutes before readiness can pass.
   `run_scheduled_backup.py` turns those declarations into one timestamped,
   digest-manifested execution; a scheduler and managed retention target must
   invoke it in customer production.
   PostgreSQL collateral uploads now dual-write through that selected evidence
   provider while retaining a local materialization for the open-source
   execution adapters. A later cutover can materialize on demand from the
   object key after customer adapters support remote reads.
   Acceptance: kill and restart
   API/worker processes during a run, then retrieve the same job, event list,
   hashes, and bundle from a second pod.
2. **Identity and authorization.** Map OIDC identities to organization,
   project, reviewer, and operator roles. Enforce project access at every
   metadata, artifact, job, evidence, comparison, bundle, and signoff route.
   Signoff accepts a trusted `X-Identity-Subject` from the identity-aware
   ingress (or an explicit subject in a service-to-service request), and
   `VERIFICATION_REQUIRE_IDENTITY_SUBJECT=true` makes that binding mandatory.
   Acceptance: cross-tenant reads and writes return 403, reviewer approval
   records the identity-provider subject, and audit export contains the
   request ID.
   OIDC operations must retain the old signing key during a provider-defined
   grace period, verify a canary token with the new key, and alert on unknown
   key IDs or an empty JWKS cache; use `deployment/RECOVERY_RUNBOOK.md` for the
   response sequence.
3. **Isolated execution.** Give each job a disposable workspace, least-
   privilege service account, CPU/memory/time quotas, network egress policy,
   and read-only source mounts. Acceptance: a fixture cannot read another
   job's files, contact an unapproved network target, or escape its quota;
   timeout cleanup leaves no live child process.
4. **Operations.** Export request IDs, queue/job latency, tool outcomes,
   evidence completeness, and signoff failures to centralized logs, traces,
   alerts, and SLO dashboards. Acceptance: an injected failed run produces an
   alert with project/job/request IDs and a dashboard can compute queue and
   triage SLOs.
5. **Customer adapters and pilot.** Install licensed simulator/formal/
   coverage/regression adapters through the adapter contract, run the mixed
   failure acceptance fixtures, and execute the signed scorecard against
   representative collateral. Acceptance: the lead reviewer signs the
   scorecard only when every metric links to immutable evidence.

## Rollout controls

Run the open-source pilot and production candidate in parallel for one sample
window. Compare job outcomes, artifact hashes, latency, and signoff receipts;
pause promotion on any mismatch. Keep the pilot PVC snapshot until the
production evidence inventory and restore drill have both passed.
