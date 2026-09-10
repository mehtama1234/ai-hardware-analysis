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

The API is available on port `8080`; Compose reports it healthy only when
`/healthz` responds. Submit work with `POST /v1/jobs`, then
start it with `POST /v1/jobs/{id}/run-async`; the worker claims the queued job
and updates its durable status. Use `/healthz` and `/readyz` for probes and
`/metrics` for the pilot counters. Every non-probe endpoint requires the
`X-API-Key` header when an API key is configured.

Deployments may additionally set `VERIFICATION_PROJECT_KEYS` to a JSON object
mapping project IDs to scoped keys. Project routes then require
`X-Project-Key` matching the project entry; this is a pilot isolation aid and
does not replace enterprise identity and RBAC.

For secret-manager mounts, set `VERIFICATION_SERVICE_API_KEY_FILE` to a file
containing the key; it takes precedence over the environment value.

Compose applies default API limits of 1 CPU/512 MB and worker limits of 2
CPUs/2 GB. Adjust these values in `.env` for the host capacity.

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
