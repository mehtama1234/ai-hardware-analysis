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

Run the existing service and durable worker using the deployment instructions.
Open the service's `/workbench/` page for a same-origin UI. The page and its
allowlisted JavaScript assets are public; API requests retain API-key checks.

Choose **Connection**, enter the service origin and any API/project key, and
connect. Credentials are scoped to that origin in tab session storage, never
included in URLs. After connection:

1. Create or select a project.
2. Use **Upload artifact** to choose a text file or paste multiline content.
3. Inspect and ingest its recorded version in **Sources & plan**.
4. Choose **Run verification**, select RTL and checker versions, and queue the run.
5. A durable worker must claim the queued run before it executes.

Regression accepts multiple checker selections. Bounded invariant proof has
explicit signal, expected-value, and bound fields. Tool availability is shown
in the run form. An unavailable tool can still result in a tool failure;
capability-specific admission guidance remains under development.

A separately served static UI requires the service to permit its origin;
the same-origin `/workbench/` path avoids that requirement. The **Connection**
form reports reachability/authentication failures without substituting sample data.

The investigation, exact repair review, retest comparison, bundle download,
and signoff receipt flow are implemented for the open-source pilot. The
walkthrough below describes the supported path; production customers still
need external identity/RBAC, durable production storage, customer-specific EDA
adapters, and representative usability validation. See the implementation
status document for the remaining release gates.
When a live action fails, the inline error includes the service request ID so
an operator can provide an exact trace to support.
Successful run submission displays the same persisted request ID in the queue
confirmation toast.

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

## Pilot recovery checks

If the run list shows `Stale`, use **Refresh** after checking `/readyz`; the
last known run remains reviewable while the service recovers. If it shows
`Unauthorized · reconnect required`, reopen **Connection** and replace the
expired API key in the current tab. A blocked formal run exposes its timeout
reason and cannot be signed off. A comparison marked incomparable requires a
retest with the same checker scope before closure or signoff.
