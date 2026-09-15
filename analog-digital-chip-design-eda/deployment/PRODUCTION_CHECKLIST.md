# Production readiness checklist

The current implementation is a verified, open-source pilot deployment. Use
this checklist before calling it customer production.

## Implemented and verified

- [x] API and worker containers build from a trimmed image with a pinned base-image digest.
- [x] Built image runtime smoke verifies `/healthz`, `/readyz`, and UID 10001 before publication.
- [x] API authentication supports environment or mounted secret credentials.
- [x] Durable queue supports retries, cancellation, WAL, and stale-job recovery.
- [x] Async jobs have one owner: the durable worker.
- [x] Job timeouts, backlog limits, CPU, and memory limits are enforced.
- [x] Reference tool execution applies POSIX CPU-time and per-file-size limits and records those limits in provenance metadata.
- [x] Containers run non-root with health/readiness probes, artifact-volume write readiness, and restart policy.
- [x] Job transitions, logs, manifests, and downloadable evidence are retained.
- [x] Project-scoped bounded audit export preserves event identity, request correlation, and safe adapter identity/count without raw paths/logs or command arguments, redacts path-like error text, and includes a canonical export digest.
- [x] CI runs the platform, benchmark, deployment, and image-build gates.
- [x] Customer-project reference adapters cover Icarus compile/simulation, Verilator lint, Yosys preflight, and bounded SAT proof.
- [x] Customer-project runs verify input hashes, emit output manifests, produce triage/closure/PoV reports, and support approved repair retests.
- [x] Workbench browser gate covers evidence isolation, stale responses, interruption recovery, missing evidence, invalid receipts, and reviewer handoff.
- [x] Evidence bundles download with run identity; signoff receipts are hash-bound and reloadable, while HTTP responses omit absolute report paths.
- [x] Pilot API responses and durable events carry bounded request correlation IDs; Prometheus exposes bounded HTTP response-class and duration signals.
- [x] API and workbench responses include a same-origin Content-Security-Policy with explicit API connect origins.
- [x] Authenticated `/v1/contract` publishes the versioned workflow, job kinds, evidence guarantees, and claim boundaries for integrations.
- [x] `/v1/contract` publishes execution-safety guarantees and the remaining per-job isolation requirements for integration preflight.
- [x] `/v1/contract` publishes managed-state, observability-ownership, identity, and customer-adapter requirements for deployment automation.
- [x] Kubernetes profile disables service-account tokens, drops capabilities, forbids privilege escalation, requires RuntimeDefault seccomp, and uses read-only container roots.
- [x] Kubernetes egress policy defaults to DNS-only; customer adapter endpoints require explicit deployment rules.
- [x] Evidence-store and customer-adapter contracts reject unsafe paths and expose provider/tool availability before execution.
- [x] Reference adapter acceptance matrix exercises pass, fail, timeout, and missing-artifact outcomes with bounded provenance.
- [x] Evidence objects are immutable by logical key: differing bytes and symlink targets are rejected before persistence.
- [x] S3-compatible immutable evidence provider contract is implemented and tested with an injected client; bucket versioning, object lock, retention, encryption, and IAM remain deployment gates.
- [x] Completed job outputs and logs are published through the selected evidence provider with logical object keys and SHA-256 metadata while retaining local execution materializations.
- [x] Evidence bundle retrieval can materialize a missing local ZIP from the selected immutable provider and verify its digest before download.
- [x] Evidence inspection can materialize missing result files and waveforms from provider storage before rendering bounded forensic context.
- [x] S3 provider control probe reports versioning, encryption, lifecycle retention, and a positive default object-lock retention period separately from object-write success.
- [x] Customer-production readiness enforces the storage-control probe instead of trusting declarations alone.
- [x] Customer-production configuration validates a measurable backup retention policy and bounded DR RPO/RTO targets.
- [x] Backup policy parser validates a five-field schedule and PostgreSQL client/server major compatibility before dump execution.
- [x] Disposable PostgreSQL repository smoke exercises project, collateral, and durable queue round trips with transactional claim/finish semantics.
- [x] Policy-validated scheduled backup entry point emits timestamped dump and atomic digest manifest artifacts.
- [x] Scheduled backup runner can publish the dump to the configured immutable evidence provider and record its logical object key and digest.
- [x] Kubernetes production backup overlay defines non-overlap, retries, bounded history, secret-backed DSN, and least-privilege execution.
- [x] A separate Kubernetes production overlay consumes external ConfigMap/Secret objects, enables customer-production settings, and renders successfully with the explicit load restriction override.
- [x] Semantic customer-production overlay preflight verifies production tier, OIDC enforcement, external ConfigMap/Secret references, and backup CronJob wiring without accepting credential material.
- [x] Semantic overlay preflight verifies every readiness-critical identity, isolation, observability, and DR variable is present in the rendered API environment.
- [x] Post-apply runtime smoke script checks managed readiness, platform contract, and required safety/DR metrics without emitting credentials.
- [x] Customer-production mode fails closed unless managed state, object storage, trusted identity, isolated execution, observability, and backup declarations are present; declarations remain separate from provider implementation evidence.
- [x] Customer-production configuration requires an explicit reviewer role claim for sign-off; sign-off rejects requests whose trusted ingress roles do not include it.
- [x] Customer-production configuration requires explicit identity issuer, audience, and JWKS settings before readiness can pass; the pilot remains API-key based.
- [x] OIDC verifier validates bearer signature, issuer, audience, subject, key ID, and reviewer roles against cached JWKS; token enforcement is customer-production configurable.
- [x] Optional project-to-identity subject mapping rejects cross-tenant project reads and job submissions before execution.
- [x] Customer-production readiness requires a non-empty project-to-identity mapping instead of allowing token-valid users to access every project.
- [x] Customer-production mutating routes require the configured operator role, so token-valid readers cannot create or execute verification work.
- [x] OIDC JWKS resolution refreshes on rotated key IDs and production configuration rejects non-HTTPS JWKS endpoints.
- [x] API middleware integration test proves validated bearer claims become the route's subject/role context and missing tokens are rejected.
- [x] Customer-production identity configuration requires HTTPS issuer and JWKS endpoints.
- [x] Customer-production readiness requires explicit disposable-workspace and deny-by-default network-policy declarations.
- [x] Reference runner audits completed workspaces for symlink escape artifacts and blocks unsafe evidence publication.
- [x] Reference runner can enforce Linux user/PID/mount/network namespaces in isolated mode and records the enforced backend in provenance.
- [x] Credential-free runtime probe verifies namespace creation and an empty isolated network route table; target-cluster policy validation remains required.
- [x] Image runtime smoke accepts explicit host security-policy options and records sandbox success; default Docker seccomp remains fail-closed when it denies namespace creation.
- [x] Image runtime smoke emits JSON evidence with image identity, security options, sandbox result, and claim boundary for handoff.
- [x] OIDC JWKS refresh and unknown-key counters are exported through bounded Prometheus metrics for rotation monitoring.
- [x] Provider-neutral Prometheus alert rules cover readiness loss, API 5xx errors, and OIDC key rotation/empty-key failures.
- [x] Observability alerts include a bounded queue-backlog threshold aligned to the pilot's maximum queued-job setting.
- [x] Queue capacity is exported as a metric and the backlog alert compares against live configured capacity rather than a hard-coded threshold.
- [x] Prometheus alert rules cover the dashboard's latency SLO in addition to readiness, errors, backlog, adapters, and identity rotation.
- [x] Backup freshness and declared RPO are exported as metrics with a stale-backup alert.
- [x] Customer-production configuration requires explicit managed logs, alert-routing, and named SLO-owner declarations; endpoint wiring remains visible in the deployment overlay.
- [x] Customer-production readiness requires a non-empty customer EDA adapter registry; adapter availability remains measured separately from declaration.
- [x] Registered-adapter preflight emits digest-bound available/blocked status; correctness and customer-tool acceptance remain deployment-specific.
- [x] Registered adapters carry validated workspace-relative expected artifacts and bounded execution timeouts that resolve into the common adapter contract.
- [x] Workbench capability view exposes adapter availability, expected outputs, timeout limits, and an available-only run selector with an explicit blocked state before execution.
- [x] Browser acceptance verifies the adapter selector, blocked-tool visibility, ephemeral non-secret argument input, and no page errors.
- [x] Commercial handoff inventory content-addresses the shipped workbench UI and its browser acceptance gate alongside deployment controls.
- [x] Commercial handoff inventory includes the eight-scenario adversarial judge packet with its deterministic gate and claim boundary.
- [x] Adversarial judge runner bounds each deterministic gate and emits a structured timeout packet before failing closed.
- [x] HTTP request logs emit structured request ID, method, path, status, and duration fields without headers, query values, bodies, or credentials; centralized shipping remains a deployment gate.
- [x] Adapter job and evidence responses expose registered adapter identity and argument count while withholding raw adapter arguments.
- [x] Customer adapter arguments enforce bounded count, per-argument bytes, and total payload bytes before queueing and again in the worker.
- [x] Customer-adapter jobs produce a self-digested PoV report, persist its evidence pointer on the durable job, and can be reviewed and hash-bound by the existing signoff flow; blocked executions produce evidence but cannot be signed off.
- [x] HTTP dispatch exceptions also emit a correlated 500 structured log before re-raising, preserving failure visibility for centralized collectors.
- [x] HTTP dispatch exceptions increment the 5xx response counter and duration so error-rate dashboards include unhandled failures.
- [x] Per-job execution enforces a total workspace byte quota in addition to CPU and per-file limits; quota breaches block evidence publication.
- [x] Customer-production configuration requires explicit positive workspace and per-file byte quotas instead of silently relying on runner defaults.
- [x] Customer-production configuration rejects a per-file byte quota larger than the total workspace quota.
- [x] Docker Compose and the customer-production Kubernetes overlay wire both byte-quota settings through to API and worker containers; overlay preflight passes.
- [x] Structured HTTP logs carry a versioned schema identifier for stable centralized parsing.
- [x] The versioned HTTP-log JSON Schema is included in the handoff inventory for downstream collector validation.
- [x] The `/v1/contract` response publishes the request-log schema path for integration discovery.
- [x] Customer-production runtime preflight emits a versioned result and ships a JSON Schema for pass/blocked output validation.
- [x] The `/v1/contract` response publishes the `/v1/capabilities` endpoint used to discover registered execution backends.
- [x] Authenticated `/v1/readiness` exposes bounded checklist counts, open controls, self-digest, and claim boundary without serving raw report files.
- [x] Authenticated `/v1/pilot/scorecard` exposes bounded PoV metric summaries and evidence counts without raw observations.
- [x] Scorecard summary normalizes malformed sample metadata and fails closed on schema errors without promoting draft evidence.
- [x] HTTP regression verifies `/v1/pilot/scorecard` returns the bounded summary used by integrations and omits raw observations.
- [x] Registered customer adapters are first-class project-scoped `customer-adapter` jobs with preflight availability checks, bounded execution, expected-artifact enforcement, and persisted provenance.
- [x] Workbench capability, readiness, and scorecard requests use bounded client-side timeouts and render actionable unavailable states.
- [x] Commercial handoff inventory content-addresses the operator deployment README for the runtime capability, readiness, and scorecard surfaces.
- [x] Commercial handoff inventory includes the usability-study plan and structured template for measuring first-time, debug, and lead workflows.
- [x] Commercial handoff inventory includes the scorecard schema and evidence validators used to reproduce PoV acceptance.
- [x] Workbench renders draft versus finalized pilot scorecard state and bounded metric summaries without inventing baseline or ROI evidence.
- [x] Workbench renders the bounded commercial-readiness summary and open controls, with explicit sample/live claim boundaries.
- [x] Browser acceptance covers connected readiness rendering from `/v1/readiness`, including open controls and blocked production state.
- [x] Readiness reports carry a self-digest that the customer-pilot packet gate recomputes before promotion.
- [x] Customer-pilot promotion requires the readiness report's `pilot_controls_verified` flag to be a true boolean.
- [x] Deterministic pilot scorecard collection enforces matched samples, category coverage, blocked/timeout sampling, metric computation, and evidence hashes before human review.
- [x] Finalized scorecards require valid 95% confidence intervals for both baseline and workbench values for every metric in addition to point estimates, evidence, and lead receipt.
- [x] Pilot observation intake rejects unsupported categories, non-finite or negative timings, and non-boolean review labels before aggregation.
- [x] A credential-free OIDC key-rotation drill proves old-key acceptance, overlap with a new key, and rejection after retirement; customer IdP availability and RBAC lifecycle remain deployment gates.
- [x] A single customer-pilot packet verifier fails closed unless readiness, finalized scorecard evidence, and a signoff receipt agree.
- [x] Customer-pilot promotion receipts require an authenticated reviewer subject in addition to approval and digest binding.
- [x] Customer-pilot promotion validates readiness counts and open-control state instead of trusting a standalone ready flag.
- [x] Customer-pilot promotion rejects empty zero-control readiness reports.
- [x] Customer-pilot promotion verifies the readiness report's checklist path and SHA-256 digest before accepting its counts.

## Required before customer production

- [ ] Replace SQLite with managed PostgreSQL or a managed queue/database.
- [ ] Move evidence bundles to versioned object storage with retention policy.
- [ ] Deploy the OIDC verifier behind the customer's enterprise identity provider, tenant directory, and administrative RBAC lifecycle.
- [ ] Execute jobs in isolated per-job workspaces with network and filesystem policy.
- [ ] Connect request correlation, Prometheus signals, dashboards, and alert rules to centralized production logs, managed alert routing, and SLO ownership.
- [ ] Add and validate customer-specific simulator, formal, regression, and artifact adapters beyond the open-source reference backends; use `deployment/CUSTOM_ADAPTER_GUIDE.md` for the contract.
- [ ] Complete managed backup/restore, disaster recovery, and key rotation; pilot recovery and incident procedures are documented in `deployment/RECOVERY_RUNBOOK.md`.
- [ ] Run a customer pilot with signed proof-of-value metrics and human approval; use `deployment/PILOT_MEASUREMENT_PLAN.md`.

The open-source checker remains the evidence-producing reference backend while
those infrastructure integrations are completed.
Use `deployment/PRODUCTION_MIGRATION_PLAN.md` to sequence the migration and
define acceptance evidence for each production boundary.
