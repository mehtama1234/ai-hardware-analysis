# Meaty end-to-end goal: commercial verification workbench

## North star

Deliver a production-shaped verification workbench that lets a verification
engineer move from design collateral to an evidence-backed closure decision in
one understandable workflow:

```text
connect project -> ingest collateral -> plan intent -> generate checks
-> execute open-source or customer tools -> triage failures
-> inspect waveform/source evidence -> review bounded repair
-> retest -> compare runs -> measure proof of value -> sign off and export
```

The product earns trust through execution and provenance. An LLM may propose
plans, checks, diagnoses, repairs, and next actions, but it cannot invent a
pass, hide a blocked backend, mutate source without approval, or claim closure
without the required artifacts and tool evidence.

## User outcome

On first use, an engineer can understand what the project is, what is ready,
what is blocked, and what to do next without knowing the platform internals.
During a failure, the engineer can reach the first meaningful divergence,
driving RTL cone, compact trace, diagnosis rationale, and exact source revision
from one investigation view. During review, the engineer can see the proposed
change, its requirement, digest, risk, and test impact before approving it.
After retest, a lead can compare baseline and repaired runs, inspect every
claim, record a named decision, and download an immutable evidence bundle.

## Product contract

The deterministic backend owns typed IR, source and artifact hashes, project
scope, command invocation, worker isolation, timeouts, capability detection,
run state, evidence manifests, policy gates, and audit events. The interface
must make those boundaries visible: sample data is labeled, blocked is distinct
from failed, stale responses cannot replace current project data, and every
error has a request identity that an operator can trace.

The workbench is organized around four destinations:

1. **Project readiness:** collateral, capabilities, requirements, and blockers.
2. **Runs:** queued, running, failed, blocked, cancelled, and completed jobs.
3. **Investigation:** failure clusters, source/dependency cone, waveform or
   counterexample, diagnosis, and next action.
4. **Closure:** repair review, retest comparison, coverage and PoV metrics,
   sign-off receipt, and immutable export.

Each destination preserves context, supports keyboard and screen-reader use,
handles empty/loading/error states, and explains the next useful action.

## Adversarial quality bar

An adversarial LLM judge evaluates captured screenshots, DOM traces, API
responses, and browser actions for first-time engineer, debug engineer, and
verification-lead tasks. Scenarios include wrong-run selection, stale project
responses, missing waveform or coverage, formal timeout, disconnected service,
authorization failure, changed repair digest, narrower retest, and fabricated
sample evidence. Findings are schema-validated, reproduced where actionable,
and retained with the release evidence. Deterministic tests remain the final
gate for security, provenance, state transitions, and artifact integrity.

## Commercial acceptance gates

The open-source pilot gate requires a clean run that ingests a specification
and RTL revision, creates a traceable plan, generates a procedural checker,
executes Icarus/Verilator/Yosys or records a blocked capability, captures
failure evidence, performs logic-aware triage, reviews an exact bounded repair,
retests, compares baseline to retest, and produces a signed bundle. Browser,
setup, handoff, adversarial, scorecard, and full backend tests must pass.

The production gate then adds managed database and object storage, enterprise
identity and RBAC, tenant and per-job isolation, centralized observability,
backup and recovery, secret/key rotation, customer simulator/formal/regression
adapters, CI integration, and a signed pilot on representative collateral.
The pilot reports diagnosis time, review effort, coverage gain, redundant work
avoided, traceability completeness, and invalid or vacuous closure detected.

## Definition of done

Done means a reviewer who did not build the system can reproduce the complete
journey from a versioned project, distinguish evidence from proposals, find
the reason for every blocked or failed result, approve or reject a repair with
an audit trail, verify the retest scope, and validate the exported report and
hashes. It also means the release package states exactly which commercial
gates are implemented and which require customer infrastructure.

## Current starting point and next commercial increment

The open-source pilot vertical slice is implemented and evidence-backed. It
contains the project-scoped service, durable pilot queue, typed collateral and
verification IR, procedural checker generation, compile/lint/formal/simulation
and regression adapters, bounded waveform/source investigation, repair and
retest lineage, comparison and proof-of-value reports, immutable evidence
bundles, sign-off receipts, browser/setup/handoff smoke gates, and the
adversarial judge. The current release evidence is 294 passing tests (218
deployment and 76 platform), 8 adversarial scenarios, a sandbox capability
probe, an adapter acceptance matrix, a managed-state PostgreSQL repository and
restore rehearsal, a digest-bound image runtime artifact, deterministic pilot
scorecard collection with baseline/workbench 95% intervals, and a verified
handoff manifest.

The next meaty goal is **commercial pilot closure**: run this same workflow
against representative customer collateral through a deployed control plane
and close each production boundary with executable evidence. Sequence the work
as follows:

1. Replace the pilot SQLite queue and local evidence store with managed
   PostgreSQL/queue and versioned, retention-controlled object storage.
2. Connect the OIDC verifier to the customer's identity provider, tenant
   directory, operator/reviewer roles, and lifecycle administration.
3. Enforce target-cluster per-job workspace, network, mount, quota, and secret
   policies, then repeat the runtime sandbox probe in that cluster.
4. Wire request correlation, Prometheus, dashboards, alert routing, logs, and
   SLO ownership into the customer's operational system.
5. Implement and acceptance-test customer simulator, formal, regression, and
   artifact adapters using `CUSTOM_ADAPTER_GUIDE.md`.
6. Execute managed backup/restore, disaster-recovery, and key-rotation
   rehearsals using `RECOVERY_RUNBOOK.md`.
7. Run a signed pilot using `PILOT_MEASUREMENT_PLAN.md`, measuring diagnosis
   time, review effort, coverage gain, redundant work avoided, traceability,
   and invalid or vacuous closure detected.

The open-source checker remains the deterministic reference backend throughout
this sequence. No agent may claim production readiness, verification closure,
or customer ROI until the corresponding tool evidence, artifact hashes,
identity/policy checks, and human approval are present. The current readiness
report has 118 controls, 110 verified, and 8 open production gates; those gates
are the remaining definition of done rather than missing product concepts.
