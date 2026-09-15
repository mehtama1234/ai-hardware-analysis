# Verification pilot deployment

This is a containerized pilot service with a durable SQLite job queue. It runs
the open-source multi-design checker and stores job metadata, logs, and
evidence under the shared `.artifacts` volume.

The Docker build intentionally excludes historical evidence, lab outputs, and
generated run data; those are runtime artifacts and do not belong in the image.

```bash
cp deployment/.env.example deployment/.env
# set VERIFICATION_SERVICE_API_KEY in deployment/.env
docker compose --env-file deployment/.env -f deployment/docker-compose.yml up --build
```

An open-source Kubernetes profile is available under
`deployment/kubernetes/verification-pilot.yaml` for a single-pod pilot.
Compose passes the deployment-tier contract variables to both API and worker;
review the rendered environment with `docker compose config` before promoting
an override from the pilot tier.

The API is available on port `8080`; Compose reports it healthy only when
`/healthz` responds. Submit work with `POST /v1/jobs`, then
start it with `POST /v1/jobs/{id}/run-async`; the worker claims the queued job
and updates its durable status. Use `/healthz` and `/readyz` for probes;
`/readyz` also reports `storage_provider` and the `evidence-store-v1` contract
plus `identity_mode`/`identity_subject_required`, so a deployment cannot
silently advertise an unimplemented managed backend or permissive signoff
mode.
Integrations can read `/v1/contract` for the versioned workflow, job kinds,
evidence guarantees, claim boundaries, and execution-safety requirements.
The contract advertises `/v1/capabilities`, `/v1/readiness`, and
`/v1/pilot/scorecard`. `/v1/capabilities` reports measured reference tools and
registered customer adapters, including blocked status, expected output paths,
and timeouts. `/v1/readiness` returns only the content-addressed control
summary and open production gates. `/v1/pilot/scorecard` returns metric
summaries, evidence counts, and finalized/draft state without raw pilot
observations. These endpoints require the configured API key and preserve their
claim boundaries in the response.
Registered tools can also run as `customer-adapter` jobs by posting
`{"kind":"customer-adapter","project_id":"…","adapter_name":"…","adapter_args":[]}`
to `/v1/jobs`. The service rejects blocked or unknown registrations before
queueing; the worker executes through the common bounded runner and publishes
`adapter-result.json` with redacted command provenance and expected-artifact
status.
The workbench exposes this action through its capability-driven adapter
selector. Non-secret arguments are entered as an ephemeral JSON array in the
form; credentials must be mounted by the deployment secret manager and are
never supplied through browser URLs.
Use `/metrics` for the pilot counters. Readiness includes a temporary write/delete
probe on the artifact volume, so a pod that cannot persist evidence remains
out of service. Every non-probe endpoint requires the
`X-API-Key` header when an API key is configured.
Every API response includes an `X-Request-ID`; callers may supply one to join
API, worker, and customer support logs for a single operation.
The connected workbench supplies a fresh request ID for each setup/API action.
The managed-state schema can be applied and verified against a PostgreSQL
instance with `python3 -m deployment.apply_managed_state_migration --dsn
postgresql://...`; the command redacts credentials in its result and verifies
all required tables and indexes. It is a migration proof, not the application
provider cutover.
`/metrics/prometheus` also exposes bounded HTTP 2xx/3xx/4xx/5xx counters and
request-ID generation counts plus response-duration sums by class for basic
error-rate and latency monitoring. It also exports readiness and per-adapter
availability gauges for alerting before a run is submitted.
The service also sends a Content-Security-Policy that keeps scripts same-origin
while allowing explicitly configured HTTP/HTTPS API connections.
The default `VERIFICATION_DEPLOYMENT_TIER=pilot` keeps the local reference
backend explicit. Setting `VERIFICATION_DEPLOYMENT_TIER=customer-production`
activates a fail-closed configuration contract: the process must declare a
PostgreSQL URL, object-store provider and bucket, trusted identity subjects,
isolated execution, centralized observability, managed logs and alert routing,
a named SLO owner, a reviewer role claim, and a backup policy before
`/readyz` can report ready. Those declarations do not pretend that provider
implementations or operational drills have been completed; the readiness
response also runs the object-store control probe and stays unready when
versioning, encryption, or retention is missing.
Customer production also requires a non-empty `VERIFICATION_EDA_ADAPTERS`
registry. Each adapter is still reported as available or blocked based on the
executable actually present in the worker image; registration alone cannot
claim a successful customer tool run.
It also requires an identity issuer, audience, and JWKS URL so the trusted
ingress can be bound to a real OIDC provider; a bare subject header is not a
replacement for that deployment configuration.
When `VERIFICATION_REQUIRE_IDENTITY_TOKEN=true`, the API validates bearer
signatures and claims against the configured JWKS before accepting identity
context; the pilot leaves this disabled.
JWKS caches refresh when an unseen key ID appears, allowing planned signing-key
rotation without restarting the service; production still needs provider key
rotation runbooks and monitoring.
Prometheus also exposes bounded JWKS refresh, unknown-key, and cached-key
counters for rotation alerts.
The checked-in `observability/verification-pilot-alert-rules.yaml` provides
provider-neutral Prometheus rules for readiness, API failures, and OIDC key
rotation; route those alerts through the managed incident system in production.
The same rule set includes the dashboard's five-second average-latency SLO;
managed alert routing and escalation remain deployment responsibilities.
The service exports the latest backup timestamp, backup age, and configured RPO;
`VerificationPilotBackupStale` fires when age exceeds twice the RPO.
The policy also alerts when queued work exceeds the default 32-job capacity;
adjust the expression with the deployed queue limit when changing that setting.
Sign-off requests in this tier must also carry the configured reviewer role in
the trusted `X-Identity-Roles` header; the request subject and role are asserted
by the identity-aware ingress rather than accepted from the JSON body.
response still reports an unimplemented evidence provider as unavailable.
For a reproducible local observability rehearsal, start the optional
Prometheus overlay from the repository root:

```bash
docker compose -f deployment/docker-compose.yml \
  -f deployment/observability/docker-compose.observability.yml up --build
```

Prometheus listens on `http://localhost:9090`, scrapes the pilot's
`/metrics/prometheus` endpoint every 15 seconds, and retains data for the
configured `VERIFICATION_PROMETHEUS_RETENTION` period. Import
`observability/verification-pilot-dashboard.json` into Grafana or map its
queries into the managed monitoring system. This overlay is a local/pilot
deployment artifact; durable alert routing, access control, and managed
retention remain customer-production responsibilities.
Project-scoped audit exports are available at
`GET /v1/projects/{project_id}/audit?limit=500`; they contain bounded event
identity and status fields, preserve request IDs, and intentionally omit
filesystem paths and raw logs. Each response includes `export_sha256`, a
canonical digest over the returned entries.

Deployments may additionally set `VERIFICATION_PROJECT_KEYS` to a JSON object
mapping project IDs to scoped keys. Project routes then require
`X-Project-Key` matching the project entry; this is a pilot isolation aid and
does not replace enterprise identity and RBAC.
Deployments may also set `VERIFICATION_PROJECT_SUBJECTS` to a JSON object
mapping project IDs to allowed OIDC subjects. Configured project routes and
job submissions reject subjects outside that allowlist before reading or
executing project data.

For secret-manager mounts, set `VERIFICATION_SERVICE_API_KEY_FILE` to a file
containing the key; it takes precedence over the environment value.

Compose applies default API limits of 1 CPU/512 MB and worker limits of 2
CPUs/2 GB. Adjust these values in `.env` for the host capacity.
The reference runner rejects symlinked workspace outputs after each tool exits;
such runs are marked blocked and cannot publish unsafe evidence.
Set `VERIFICATION_EXECUTION_SANDBOX=isolated` for customer execution. The
Linux namespace backend records its enforcement in provenance; validate the
target runtime with `python3 scripts/verify_execution_sandbox_runtime.py` before
accepting production jobs.

## Release evidence check

Before a controlled pilot handoff, run the backend suites and the three
browser-facing acceptance scripts from the repository root:

```bash
python3 -m pytest verification_platform deployment
python3 scripts/verify_workbench_browser.py
python3 scripts/verify_workbench_setup.py
python3 scripts/verify_workbench_handoff.py
python3 scripts/verify_workbench_adapter_ux.py
python3 scripts/run_workbench_adversarial_judge.py --findings docs/evaluations/verification-workbench-adjudicated-findings.json
python3 benchmarks/multi_design_pilot/ci_gate.py
python3 scripts/build_open_source_pilot_scorecard.py benchmarks/multi_design_pilot/runs/latest .artifacts/open-source-pilot-scorecard.json
python3 scripts/validate_pilot_scorecard.py .artifacts/open-source-pilot-scorecard.json
python3 scripts/verify_pilot_scorecard_evidence.py .artifacts/open-source-pilot-scorecard.json --root .
python3 scripts/report_production_readiness.py --output .artifacts/production-readiness.json
python3 scripts/build_commercial_handoff_manifest.py --root . --readiness .artifacts/production-readiness.json --scorecard .artifacts/open-source-pilot-scorecard.json --recovery .artifacts/recovery-snapshot-verification.json --output .artifacts/commercial-handoff-manifest.json
python3 scripts/verify_commercial_handoff_manifest.py .artifacts/commercial-handoff-manifest.json --root .
python3 scripts/verify_handoff_upload_contract.py .artifacts/commercial-handoff-manifest.json .github/workflows/verification-pilot.yml
python3 scripts/validate_pilot_scorecard.py deployment/pilot-scorecard-template.json
python3 scripts/validate_usability_study.py deployment/pilot-usability-study-template.json
```

After building the image, perform the container smoke gate before publishing
it. The verifier starts the API with a disposable key, checks liveness and
readiness plus the unprivileged UID, then removes the container:

```bash
python3 scripts/verify_verification_image_runtime.py verification-pilot:0.1.0-local
python3 scripts/write_verification_release_manifest.py verification-pilot:0.1.0-local .artifacts/verification-release-manifest.json
python3 scripts/verify_customer_production_runtime.py https://verification.example.com --api-key "$VERIFICATION_SERVICE_API_KEY" --bearer-token "$OIDC_TOKEN" --sandbox-probe
```

The runtime preflight emits the versioned
`verification-customer-production-runtime-v1` result. Validate its output
against `observability/verification-customer-production-runtime.schema.json`
before forwarding it to deployment automation; both pass and blocked results
are intentional machine-readable outcomes.

When validating the nested namespace backend on a Docker host whose default
seccomp profile denies `unshare`, pass the host policy explicitly for the
rehearsal, for example `--sandbox-probe --security-opt seccomp=unconfined`.
This option is deliberately opt-in; customer Kubernetes policy must provide an
approved isolation mechanism and should not inherit an unreviewed local Docker
override.

The manifest records whether the source tree was dirty and caps the changed
path list at 2,000 entries, so reviewers can distinguish a clean commit build
from a local development image without creating an unbounded release artifact.

Retain the generated `.artifacts/workbench-adversarial/judge-packet.json` and
the browser handoff artifacts with the release record.

Example API flow:

```bash
job=$(curl -sS -X POST http://localhost:8080/v1/jobs \
  -H 'Content-Type: application/json' -H "X-API-Key: $VERIFICATION_SERVICE_API_KEY" \
  -d '{"project_id":"customer_demo"}')
id=$(printf '%s' "$job" | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')
curl -sS -X POST "http://localhost:8080/v1/jobs/$id/run-async" \
  -H "X-API-Key: $VERIFICATION_SERVICE_API_KEY"
curl -sS "http://localhost:8080/v1/jobs/$id" \
  -H "X-API-Key: $VERIFICATION_SERVICE_API_KEY"
curl -fS "http://localhost:8080/v1/jobs/$id/bundle/download" \
  -H "X-API-Key: $VERIFICATION_SERVICE_API_KEY" -o verification-$id.zip
```

Customer collateral follows the same durable boundary. Create a project,
upload RTL or a specification, ingest it, generate reviewable artifacts, then
submit an isolated open-source compile job:

```bash
artifact=$(curl -sS -X POST http://localhost:8080/v1/projects/customer_demo/collateral \
  -H 'Content-Type: application/json' -H "X-API-Key: $VERIFICATION_SERVICE_API_KEY" \
  -d '{"name":"counter.sv","kind":"rtl","version":"r7","content":"module counter(input logic clk); endmodule"}')
aid=$(printf '%s' "$artifact" | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')
curl -sS -X POST "http://localhost:8080/v1/projects/customer_demo/collateral/$aid/ingest" -H "X-API-Key: $VERIFICATION_SERVICE_API_KEY"
curl -sS -X POST "http://localhost:8080/v1/projects/customer_demo/collateral/$aid/plan" -H "X-API-Key: $VERIFICATION_SERVICE_API_KEY"
job=$(curl -sS -X POST http://localhost:8080/v1/jobs \
  -H 'Content-Type: application/json' -H "X-API-Key: $VERIFICATION_SERVICE_API_KEY" \
  -d "{\"kind\":\"project-compile\",\"project_id\":\"customer_demo\",\"artifact_id\":\"$aid\"}")
id=$(printf '%s' "$job" | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')
curl -sS -X POST "http://localhost:8080/v1/jobs/$id/run-async" -H "X-API-Key: $VERIFICATION_SERVICE_API_KEY"
```

The compile result contains the selected top module, tool status, command
provenance, logs, and a content-addressed result artifact. Generated
concurrent SVA and UVM remain explicitly review-only until the target customer
simulator and UVM library are measured by an adapter.

For a behavioral pilot, submit the RTL and testbench as separate collateral
records and use `kind=project-simulation`. The testbench may emit bounded
functional evidence with a line such as
`COVERAGE kind=functional covered=37 total=40`; the worker validates and stores
that result. A failed simulation exposes `diagnosis.json` and
`closure-report.json`. Submit a repair proposal to
`POST /v1/jobs/{job_id}/repair-retest` with `approved=false` for review, then
repeat with explicit approval to create a new RTL artifact and queued retest.
After both jobs are terminal, retrieve
`GET /v1/jobs/{baseline_job_id}/compare/{retest_job_id}` for failure-resolution
and coverage-delta metrics. All reports retain their source artifact IDs and
hashes, and simulation metrics remain separate from formal and hardware claims.

For several tests, submit one durable regression job with the same RTL artifact
and an ordered list of testbench IDs:

```json
{
  "kind": "project-regression",
  "project_id": "customer_demo",
  "artifact_id": "customer_demo-<rtl-digest>",
  "testbench_artifact_ids": ["customer_demo-<smoke-digest>", "customer_demo-<corner-digest>"]
}
```

Retrieve `GET /v1/jobs/{job_id}/regression-proof-of-value` after completion to
see per-case status, aggregate coverage, and links to each isolated case root.

After review, bind the pilot decision to the exact report with
`POST /v1/jobs/{job_id}/signoff`:

```json
{"reviewer":"verification-lead","notes":"metrics reviewed against the run bundle","approved":true}
```

The service writes `pilot-signoff.json` containing the reviewer, timestamp,
decision, and PoV report digest. Bundles created after sign-off include this
record automatically.

Retrieve the receipt independently after a browser reload or incident
recovery with `GET /v1/jobs/{job_id}/signoff`. The response includes
`valid:false` when the stored receipt no longer matches its report digest; an
invalid receipt must not be treated as approval.

For a project-level view, call `GET /v1/projects/{project_id}/dashboard`. The
response combines collateral count, queued/running/terminal job counts,
terminal-job evidence pointers, and all report sign-offs for that project.

The evidence-first browser workbench is available at
`site/verification-workbench.html`. Open it from any static HTTP server to use
the inspectable demo data. To hydrate the project header and metrics from a
running pilot API, provide the API origin, project ID, RTL artifact ID, and
testbench artifact ID as query parameters:

```text
/verification-workbench.html?api=http://localhost:8080&project=customer_demo&artifact=<rtl-id>&tb=<testbench-id>
```

The `Run verification` action submits a durable `project-simulation` job and
starts its worker when those live parameters are present. The repair action is
deliberately review-only in the browser; approval and retest remain explicit
API operations.

The workbench's collateral panel reads
`GET /v1/projects/{project_id}/collateral`, exposes each artifact's kind,
ingestion state, and content hash, and supports client-side filtering so a
reviewer can trace the evidence set before launching a run.

See `site/VERIFICATION_WORKBENCH.md` for the complete demo walkthrough and
live query-parameter contract.

This deployment is a production-shaped pilot foundation. Before a customer
deployment, add external authentication/RBAC, managed PostgreSQL or an
equivalent queue, object storage for evidence, resource quotas and timeouts,
isolated per-job workspaces, log/trace export, and customer-specific EDA
adapters.

See [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md) for the verified gates
and remaining customer-production requirements.

Each HTTP request also emits one structured JSON application log containing its
correlation ID, method, path, status, and duration. Credentials, headers, query
values, and request bodies are intentionally excluded so a centralized log
collector can retain the event safely. Events use the
`verification-http-log-v1` schema identifier.

Before customer promotion, run the packet gate with the finalized scorecard
and signoff receipt:

```bash
python3 scripts/verify_customer_pilot_packet.py \
  --readiness .artifacts/production-readiness.json \
  --scorecard .artifacts/customer-pilot-scorecard.json \
  --signoff path/to/pilot-signoff.json \
  --root .
```
