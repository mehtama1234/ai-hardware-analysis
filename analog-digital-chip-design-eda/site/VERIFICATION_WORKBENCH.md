# Verification Workbench

`verification-workbench.html` is the open-source commercial-beta frontend for
the digital verification pilot. It is a static desktop web application with
seeded evidence so the workflow can be reviewed without a running service.

## Run the demo

From the repository root:

```bash
python3 -m http.server 8088 --directory site
```

Open `http://localhost:8088/verification-workbench.html`. The demo exposes a
project selector, collateral/provenance inspector, pipeline and readiness
views, failure evidence, durable-run examples, formal/diagnosis tabs, repair
approval gate, PoV preview, bundle preview, and comparison controls.

## Connect a live pilot service

Use the API origin and project-scoped artifact IDs in the URL:

```text
/verification-workbench.html?api=http://localhost:8080&project=customer_demo&artifact=<rtl-id>&tb=<testbench-id>
```

The page reads project, dashboard, collateral, job, PoV, bundle, comparison,
and signoff endpoints. The job selector supports compile, lint, simulation,
formal preflight, bounded formal proof, and regression. Regression testbench
IDs are supplied as `tbs=id1,id2`; bounded proof parameters may use
`signal`, `expected`, and `sequence`.

The service API key is read from `localStorage` key
`verification_api_key` when present. The frontend does not embed credentials.

## Customer PoV walkthrough

1. Select or create a project.
2. Inspect collateral hashes and ingest a pending artifact.
3. Create a plan or generate review artifacts.
4. Launch compile, lint, simulation, formal, or regression.
5. Monitor the durable job list and inspect a run timeline.
6. Review assertion, waveform, signal-cone, source, log, formal, and
   provenance evidence.
7. Create a review-only repair proposal, then explicitly approve and enqueue
   a retest.
8. Load the PoV report, preview/download its evidence bundle, and compare the
   baseline and retest reports.
9. Sign off only after confirming the exact hash-bound report.

Generated SVA/UVM remains review-only. Bounded formal status is not an
unbounded proof, captured functional markers are not exhaustive coverage, and
simulation evidence is not hardware qualification.
