# Commercial beta handoff

## Product boundary

The current product is an evidence-backed digital verification pilot. It takes
project collateral through structured ingestion, planning, generation, open
source tool execution, failure analysis, repair review, retest, regression
measurement, and human sign-off.

The deterministic service owns source hashes, schemas, tool commands, worker
execution, artifact manifests, job state, and evidence bundles. Generated
assertions, UVM scaffolds, diagnoses, repairs, and closure decisions remain
reviewable proposals unless a measured tool result and explicit human approval
support them.

## Verified customer workflow

```text
project and collateral
  -> IR ingestion and retrieval
  -> conservative verification plan
  -> SVA/procedural/UVM artifacts
  -> Icarus compile or simulation
  -> Verilator lint
  -> Yosys preflight or bounded SAT proof
  -> waveform/formal triage and closure
  -> exact-match repair review
  -> approved retest and regression comparison
  -> PoV report, dashboard, bundle, and reviewer sign-off
```

The reference deployment supports project-scoped durable jobs, idempotent
submission, input and output SHA-256 checks, per-case regression roots,
downloadable evidence, and measured backend availability through
`GET /v1/capabilities`.

## Acceptance evidence

- The deployment suite passes (`218` tests) and the verification-platform suite
  passes (`76` tests), for `294` combined tests; focused auth/health/worker
  checks and adapter checks are included in those runs.
- The Playwright gate passes offline UX smoke, fresh real-service setup,
  connected handoff, and the eight-scenario adversarial preflight with no page
  errors. Chromium is launched with the CI-safe `--disable-dev-shm-usage`
  flag; `.artifacts/workbench-browser/handoff-signed.png` and the judge packet
  are included in the handoff.
- The adversarial judge packet carries a canonical `packet_sha256`; commercial
  handoff verification checks both that internal digest and the packet's outer
  inventory hash. If an external LLM finding file is attached, its digest and
  finding count are recorded under `llm_adjudication` for reproduction.
- The runtime preflight result contract is shipped as
  `observability/verification-customer-production-runtime.schema.json` and
  covers both successful and fail-closed staged results.
- `.artifacts/customer-production-runtime-preflight.json` records the local
  runtime rehearsal; it is intentionally blocked because the reference
  service runs in `pilot` tier, not customer-production.
- Focused adapter-selector browser acceptance passes available-only selection,
  blocked-tool visibility, ephemeral argument input, and no page errors.
- Kubernetes manifest preflight and `kubectl kustomize` rendering pass; image
  build remains a CI/deployment gate rather than a claim of a local registry
  push. The exact rendered output is retained as
  `.artifacts/verification-production-overlay.yaml` and hash-checked in the
  handoff manifest.
- The handoff inventory includes the Prometheus scrape configuration, alert
  rules, and observability compose profile alongside the dashboard; routing to
  customer-managed logs and alert ownership remains an open production gate.
- The handoff includes the versioned `verification-http-log-v1` JSON Schema for
  centralized request-log parsing.
- A disposable PostgreSQL 16 provider-native restore rehearsal preserves all
  four managed table classes; its digest-bound evidence is included in the
  handoff manifest.
- A disposable PostgreSQL repository smoke exercises project, collateral, and
  durable-queue round trips with transactional claim/finish semantics; its
  digest-bound evidence is included in the handoff manifest.
- The reference adapter acceptance matrix passes explicit success, failure,
  timeout, and missing-artifact cases; the summary is digest-bound in the
  handoff manifest, and `scripts/run_adapter_acceptance.py` is included so the
  matrix can be reproduced from the release bundle.
- The reference adapter preflight confirms the open-source simulator/formal
  executables are available and records their digest-bound statuses; customer
  adapter correctness and licensing remain separate gates.
- CI publishes `verification-pilot-release-provenance`, containing the image
  ID/digest, source revision and dirty-tree state, pinned base-image
  declaration, runtime UID, and acceptance-gate commands.
- The release bundle includes the browser acceptance harnesses
  `scripts/verify_workbench_browser.py`, `scripts/verify_workbench_setup.py`,
  and `scripts/verify_workbench_handoff.py` used by CI.
- The release-toolchain provenance also includes the adversarial judge,
  readiness reporter, and handoff manifest builder/verifier used to produce
  and validate this package.
- The image-bound `verification-release-manifest.json` and its writer are
  included, preserving the image digest, source revision, runtime UID, and
  release-gate commands.
- The pinned runtime requirements and deployment `Dockerfile` are included so
  the service build inputs can be reproduced alongside the CI workflow; the
  credential-free `deployment/.env.example` captures the reference defaults.
- The Compose and Kustomize source manifests used by deployment preflight and
  production rendering are included in the handoff inventory.
- The credential-free rendered Compose configuration is retained as
  `.artifacts/verification-compose-config.yaml` for direct inspection.
- CI also publishes `verification-image-runtime.json`, binding the current
  image digest to liveness, readiness, UID, and sandbox results. A local
  `seccomp=unconfined` rehearsal is labeled as such; target-cluster isolation
  policy remains a separate production gate.
- The handoff manifest content-addresses `.github/workflows/verification-pilot.yml`
  so reviewers can verify the exact CI gate and upload contract used to produce
  the release evidence.
- The handoff includes a credential-free OIDC key-rotation drill proving old-key
  acceptance, overlap with a new key, and rejection after retirement. Customer
  IdP availability, tenant mapping, and administrative RBAC remain deployment
  gates.
- `project-simulation` captures VCD, structured failure, diagnosis, closure,
  coverage, PoV, and artifact-manifest evidence.
- `project-formal-proof` records proven, counterexample, and unknown outcomes;
  counterexamples enter the common triage IR.
- Approved repairs create a new content-addressed artifact and enqueue a
  retest; the original source remains unchanged.
- `project-regression` executes multiple testbenches and aggregates case
  status and captured coverage.
- PoV reports can be compared, downloaded, surfaced in a project dashboard,
  and signed by a named reviewer against the exact report digest.

## Production gates before a customer deployment

The next controlled-pilot objective is specified in the [Customer Pilot Certification Lab goal](CUSTOMER_PILOT_CERTIFICATION_GOAL.md). It turns the existing open-source closure lab into a synthetic-customer onboarding and adapter-certification rehearsal before any customer infrastructure is required.

1. Replace local SQLite and filesystem evidence with managed database and
   versioned object storage.
2. Deploy the OIDC verifier with the customer's enterprise identity provider,
   tenant directory, RBAC lifecycle, secret rotation,
   audit export, and customer retention policies.
3. Enforce isolated per-job network/filesystem policy and add tracing,
   centralized logs, alerts, SLOs, backup, restore, and incident runbooks.
4. Add adapters for the customer’s simulator, formal engine, regression
   database, coverage database, and CI system.
5. Run a signed pilot on representative customer collateral with baseline
   measurements for diagnosis time, review effort, coverage gain, and avoided
   regression work.

The open-source backend is ready for controlled technical pilots. These gates
are infrastructure and customer-integration work; they are not claims that
the current local pilot is enterprise production.

## Operational artifacts

- [Recovery runbook](RECOVERY_RUNBOOK.md)
- [Customer adapter guide](CUSTOM_ADAPTER_GUIDE.md)
- [Pilot measurement plan](PILOT_MEASUREMENT_PLAN.md)
- [Pilot scorecard template](pilot-scorecard-template.json)
- [Usability study plan](USABILITY_STUDY_PLAN.md)
- [Pilot usability study template](pilot-usability-study-template.json)
- [Pilot-to-production migration plan](PRODUCTION_MIGRATION_PLAN.md)
- [Observability dashboard specification](observability/verification-pilot-dashboard.json)
