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

- The scoped test suite passes (`100` tests at the handoff audit).
- Docker image build and live authenticated health/capability smoke pass.
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

1. Replace local SQLite and filesystem evidence with managed database and
   versioned object storage.
2. Integrate enterprise identity, RBAC, tenant isolation, secret rotation,
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
