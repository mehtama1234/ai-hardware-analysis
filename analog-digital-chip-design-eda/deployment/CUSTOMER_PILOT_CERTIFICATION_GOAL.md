# Customer Pilot Certification Lab

## Meaty end-to-end goal

Build a provider-free, production-shaped pilot environment that proves a semiconductor customer can onboard a verification project, connect approved EDA adapters, execute a bounded verification workflow, review AI-generated proposals, approve a copy-only repair, retest at identical scope, measure workflow value, recover from interruption, and export evidence that another operator can replay.

The lab uses synthetic customer projects and public RTL. It does not require proprietary EDA licenses, customer infrastructure, hardware, or an external LLM API. A deterministic reference agent stands in for an LLM while preserving the typed proposal, evidence, source-revision, and human-review boundary.

## Customer journey to certify

```text
create isolated customer workspace
  -> upload specification, RTL, testbench, register map, and coverage export
  -> validate collateral and build retrieval/typed verification IR
  -> select and certify open-source adapters
  -> plan checks and execute baseline regression
  -> capture logs, waveform/formal output, coverage, and provenance
  -> cluster failures and trace dependency cones
  -> produce reviewable diagnosis and next-test proposals
  -> approve a repair against an immutable source revision
  -> run the repair only in a copy at the same test scope
  -> compare artifacts and coverage with explicit claim boundaries
  -> record pilot metrics and reviewer sign-off
  -> recover/replay the complete evidence bundle from an archive
```

## Product surfaces

The browser must make the journey legible: project and collateral setup, adapter readiness, run state, failure evidence, proposal review, repair approval, retest comparison, scorecard, and downloadable handoff. The API and CLI must expose the same operations with stable schemas and deterministic errors. A customer adapter must be declarative, versioned, capability-checked, and unable to bypass evidence or approval policy.

## Certification matrix

Use at least three synthetic customer projects with different collateral shapes and at least four adapters: Icarus, Verilator, Yosys, and SymbiYosys (or an explicitly recorded unavailable state). Exercise successful, failed, timeout, missing-artifact, malformed-collateral, and blocked-tool paths.

Every project must demonstrate:

- tenant/project isolation and safe path handling;
- immutable collateral and source-revision digests;
- typed plan and generated-check artifacts;
- baseline failure evidence and dependency-aware triage;
- review-required diagnosis and next-test proposals;
- human approval before repair application;
- copy-only repair with original-source preservation;
- identical-scope retest and coverage comparison;
- honest `blocked` status when an adapter or artifact is unavailable;
- durable session, artifact, scorecard, and archive-replay evidence.

## Proof-of-value measures

Collect matched baseline/workbench measurements for triage latency, reproduction time, manual actions, evidence completeness, useful diagnosis fraction, coverage gain, repair success, and avoided redundant regression work. Report sample sizes, exact run scopes, tool versions, source revisions, and claim boundaries. These are workflow pilot metrics; they do not establish exhaustive functional coverage, formal completeness, silicon correctness, or customer ROI.

## Definition of done

The goal is complete when a clean checkout can run one command that:

1. provisions the three synthetic projects;
2. validates collateral and adapter contracts;
3. executes baseline and approved-repair workflows;
4. exercises failure, timeout, missing-artifact, and recovery cases;
5. verifies browser, API, and CLI acceptance;
6. generates scorecards and content-addressed evidence bundles;
7. rejects cross-project, stale-digest, changed-scope, and unreviewed-repair attacks;
8. builds and verifies a source-only release archive; and
9. replays that archive in a temporary directory with no external dependency.

The final handoff must include the certification matrix, pilot scorecards, adversarial findings, adapter manifests, recovery evidence, archive digest, release commands, and a clear list of production gates that remain customer- or infrastructure-dependent.

## Handoff status

The existing 11-design open-source closure lab is the verification engine for this goal. Its current evidence includes 11 unique fault classes, 11 passing copy-only retests, diagnosis and next-test proposals, taxonomy and identical-scope validation, archive verification, and archive replay. The provider-free synthetic-customer onboarding and adapter-certification slice is now also executable and passed through the complete bounded gate; no current artifact should be interpreted as enterprise deployment or silicon sign-off.

The current certification slice is executable with `python3 scripts/run_customer_pilot_certification.py`. It provisions three isolated synthetic projects, registers seven adapter definitions (six available on the reference host and SymbiYosys explicitly blocked when unavailable), ingests specification and RTL collateral, creates one typed plan and review-only generated artifacts per project, runs three evidence-producing synthetic adapter jobs, and exercises timeout and missing-artifact paths as explicit `blocked` outcomes. Each project then runs a failed simulation baseline, rejects a stale repair digest, records an approved copy-only repair, passes an identical-scope retest, writes a comparison proof-of-value report, and records a valid human-review sign-off. The durable packet is `.artifacts/customer-pilot-certification.json`.

The current acceptance evidence also includes a live browser handoff run (`python3 scripts/verify_workbench_handoff.py`) covering reload persistence, evidence and bundle inspection, sign-off, and project-switch isolation. The adversarial judge packet covers eight browser/API scenarios, including timeout, missing coverage, invalid sign-off, waveform/source inspection, disconnect recovery, and auth expiry; its deterministic gate is passed. These checks certify the reference workbench behavior and synthetic pilot path, while customer-specific tool installation, collateral, identity, and production infrastructure remain open gates.

The complete bounded command is `python3 scripts/run_customer_pilot_certification_gate.py`. It regenerates the synthetic certification packet and scorecard, validates recovery evidence, runs the browser and adversarial gates, executes the restart/recovery flight, rebuilds and replays the public archive, and verifies the commercial handoff manifest. The latest local result is `gate=passed` with three certified synthetic runs and 24 scorecard observations. Customer-specific infrastructure, identity, adapters, and signed production measurements remain open gates.
