# Production readiness checklist

The current implementation is a verified, open-source pilot deployment. Use
this checklist before calling it customer production.

## Implemented and verified

- [x] API and worker containers build from a trimmed, pinned image.
- [x] API authentication supports environment or mounted secret credentials.
- [x] Durable queue supports retries, cancellation, WAL, and stale-job recovery.
- [x] Async jobs have one owner: the durable worker.
- [x] Job timeouts, backlog limits, CPU, and memory limits are enforced.
- [x] Containers run non-root with health/readiness probes and restart policy.
- [x] Job transitions, logs, manifests, and downloadable evidence are retained.
- [x] CI runs the platform, benchmark, deployment, and image-build gates.
- [x] Customer-project reference adapters cover Icarus compile/simulation, Verilator lint, Yosys preflight, and bounded SAT proof.
- [x] Customer-project runs verify input hashes, emit output manifests, produce triage/closure/PoV reports, and support approved repair retests.

## Required before customer production

- [ ] Replace SQLite with managed PostgreSQL or a managed queue/database.
- [ ] Move evidence bundles to versioned object storage with retention policy.
- [ ] Integrate an enterprise identity provider, RBAC, and project isolation.
- [ ] Execute jobs in isolated per-job workspaces with network and filesystem policy.
- [ ] Add distributed tracing, centralized logs, alerting, and SLO dashboards.
- [ ] Add customer-specific simulator, formal, regression, and artifact adapters beyond the open-source reference backends.
- [ ] Define backup/restore, disaster recovery, key rotation, and incident runbooks.
- [ ] Run a customer pilot with signed proof-of-value metrics and human approval.

The open-source checker remains the evidence-producing reference backend while
those infrastructure integrations are completed.
