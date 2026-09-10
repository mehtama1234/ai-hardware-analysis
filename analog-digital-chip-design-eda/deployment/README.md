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

This deployment is a production-shaped pilot foundation. Before a customer
deployment, add external authentication/RBAC, managed PostgreSQL or an
equivalent queue, object storage for evidence, resource quotas and timeouts,
isolated per-job workspaces, log/trace export, and customer-specific EDA
adapters.

See [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md) for the verified gates
and remaining customer-production requirements.
