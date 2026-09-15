# Workbench UX implementation status

2026-09-10: The unified cross-repository product goal now has a concrete
release contract in `UNIFIED_END_TO_END_PRODUCT_GOAL.md`. The public benchmark
validator now enforces five designs, five expected seeded baseline failures,
five passing retests, and an exact release-design list in addition to artifact,
session, summary, and release digest checks. Focused benchmark gates pass.

2026-09-10: Added service-disconnect recovery to the adversarial judge
contract; the fresh packet now covers eight scenarios and its deterministic
browser and service gates pass.

2026-09-10: Commercial handoff verification now semantically validates the
adversarial packet's exact eight scenario IDs and requires its deterministic
gate to pass; digest, handoff, and upload-contract checks pass.

2026-09-10: The full maintained deployment and verification-platform suite
passes `294` tests after the semantic handoff-verifier change; the only output
is the existing Starlette/httpx deprecation warning.

2026-09-10: Added the unified hardware-verification release manifest. It
content-addresses the digital five-design release and AIMC collateral, reports
simulation as proven, preserves physical/measured-hardware claims as
unsupported, and is now generated and uploaded by the commercial CI workflow.

2026-09-10: Added an independent verifier for the unified release artifact.
It checks the self-digest, evidence hashes, qualification status shape, and
physical/measured-hardware claim boundaries; CI and handoff upload validation
now require this verifier.

2026-09-10: The unified-release verifier now reopens and validates both parent
digital and mixed-signal manifests and compares their recorded digests,
preventing a swapped parent manifest from passing the cross-domain gate.

2026-09-10: Added the API-facing agent-proposal boundary. Grounded LLM
proposals are persisted by digest with evidence references and remain
deterministic-only until execution and human approval; the platform contract,
proposal endpoint, and rejection tests pass.

2026-09-10: Exercised the documented public-reference release command sequence
end to end: multi-design pilot, unified release generation and verification,
commercial handoff verification, and upload-contract verification all pass.

2026-09-10: The clean-checkout pilot validator now verifies all five
reference-agent proposal files, their review-required status, and their stable
proposal digests alongside the existing artifact and release checks.

2026-09-10: Added the handoff-upload contract verifier to the documented
operator release sequence; documentation tests, manifest verification, and
the upload-contract check pass.

2026-09-10: Added and exercised the maintained handoff-upload contract
verifier; the full deployment/platform suite now passes `294` tests, and both
the commercial manifest and upload contract verify successfully.

2026-09-10: Wired the CI-produced PostgreSQL restore drill, managed-state
smoke, and adversarial judge packet into the release upload; the local blocked
customer-runtime rehearsal remains explicitly local-only. Handoff tests pass
and the `66`-artifact manifest verifies.

2026-09-10: Added the image-bound release provenance manifest and its writer
to the handoff inventory and CI upload, preserving image digest, source
revision, runtime UID, and gate commands; handoff tests pass and the verified
inventory now contains `66` artifacts.

2026-09-10: Handoff regression now requires both rendered deployment outputs
(`verification-compose-config.yaml` and `verification-production-overlay.yaml`)
to exist before accepting the release; 12 handoff tests and manifest
verification pass.

2026-09-10: Updated deployment release instructions to include the adapter
UX browser gate executed by CI; documentation tests pass and the handoff
manifest was regenerated and verified.

2026-09-10: CI now retains the credential-free rendered Compose configuration
used by deployment validation; the output contains no test secret, is uploaded
and content-addressed, and the verified handoff now contains `64` artifacts.

2026-09-10: Updated the commercial handoff narrative to point directly to
the retained rendered production overlay and its manifest hash; handoff tests
and manifest verification pass.

2026-09-10: CI now retains the rendered customer-production Kubernetes
overlay instead of writing it only to `/tmp`; the persisted YAML passes
semantic preflight, is uploaded, and is content-addressed in the verified
`63`-artifact handoff.

2026-09-10: Refreshed the open-source pilot scorecard after the latest
five-design run; scorecard validation and evidence-digest verification pass,
and the commercial handoff manifest was rebuilt and verified.

2026-09-10: Representative five-design open-source pilot rerun passed with
`5/5` retests, complete artifact integrity, valid session/summary/release
digests, and all seven lifecycle stages; the commercial manifest was rebuilt
and verified against refreshed pilot evidence.

2026-09-10: With stale browser processes cleared, all four local browser gates
passed: full UX, real-service setup, connected handoff, and adapter selector;
the fresh handoff screenshot was rehashed and the `62`-artifact manifest
verified.

2026-09-10: Added the credential-free `deployment/.env.example` reference
configuration to the handoff manifest and CI upload; handoff tests pass and
the verified inventory now contains `62` artifacts.

2026-09-10: Added the Compose and Kustomize source manifests used by
deployment preflight and production rendering to the handoff inventory and CI
upload; handoff tests pass and the verified inventory now contains `61`
artifacts.

2026-09-10: Added pinned runtime requirements and the deployment Dockerfile to
the content-addressed handoff and CI upload, completing service-build-input
provenance; handoff tests pass and the verified inventory now contains `52`
artifacts.

2026-09-10: Added the adversarial judge, readiness reporter, and handoff
manifest builder/verifier to the hashed inventory and CI upload, completing
release-toolchain provenance; handoff tests pass and the verified inventory
now contains `50` artifacts.

2026-09-10: Added the setup and connected-handoff browser harnesses to the
content-addressed manifest and CI upload, alongside their executed gates;
handoff tests pass and the verified inventory now contains `46` artifacts.

2026-09-10: Added the preserved browser handoff screenshot to the manifest
and CI upload, aligning the visual-evidence claim with the shipped bundle;
handoff tests pass and the verified inventory now contains `44` artifacts.

2026-09-10: CI now installs pinned Playwright Chromium and executes the browser,
setup, connected-handoff, and adapter-UX acceptance gates; workflow/requirements
regressions pass and the handoff manifest remains verified.

2026-09-10: Added `scripts/run_adapter_acceptance.py` to the handoff manifest
and release upload beside its acceptance summary, making the reference
adapter matrix reproducible from the bundle; 12 handoff tests pass and the
regenerated manifest verifies with `43` artifacts.

2026-09-10: Enabled `include-hidden-files: true` on the release artifact
upload so the hashed `.github/workflows/verification-pilot.yml` is actually
retained by GitHub Actions; workflow parsing, handoff tests, and manifest
verification pass.

2026-09-10: Re-reviewed the attached adversarial P2 finding: the empty-project
setup-state issue is marked resolved, with live setup labeling and disabled
run submission covered by the handoff gate. Fresh seven-scenario judge output
passed and the `42`-artifact handoff manifest was regenerated and verified.

2026-09-10: Increased the reference adapter acceptance harness budget from
`0.75s` to `1.5s` so healthy subprocesses remain reliable under CI host load;
the three-second timeout case still proves bounded blocking. Five repeated
matrices and 10 adapter-registry tests pass; the handoff manifest was rebuilt
and verified.

2026-09-10: Adapter UX acceptance now bounds Chromium page creation with a
30-second watchdog, converting shared-browser contention into a diagnosable
failure instead of an indefinite CI hang; Python compile and 24 handoff /
adversarial regressions pass.

2026-09-10: Release uploads now include the exact CI workflow already hashed
by the commercial handoff manifest; handoff regression passes and the
regenerated `42`-artifact manifest verifies.

2026-09-10: Handoff regression now reads the generated manifest and asserts
that the exact CI workflow is actually inventoried, closing the gap between
manifest-builder intent and shipped release evidence; 12 handoff tests pass.

2026-09-10: Commercial handoff inventory now content-addresses the exact CI
workflow (`.github/workflows/verification-pilot.yml`) that enforces and
uploads release evidence; focused handoff tests pass and the regenerated
manifest verifies with `42` artifacts.

2026-09-10: Regenerated the content-addressed commercial handoff after the
fresh adversarial packet; the manifest now inventories `41` artifacts and
verifies each file plus the packet self-digest.

2026-09-10: Release-facing browser handoff was rerun successfully after one
transient PoV-load timeout: the complete selected-run, reload, PoV, bundle,
download, signoff, and project-isolation flow passed with no page errors.

2026-09-10: Fixed a release-workflow contract mismatch: CI's runtime-preflight
JSON Schema examples now include the required handoff-relative `schema_path`;
handoff documentation and runtime regression checks pass.

2026-09-10: Full maintained deployment and verification-platform suite passes
`294` tests with one existing Starlette/httpx deprecation warning; the
commercial handoff manifest also verifies after the runtime-preflight
schema-path regression.

2026-09-11: Runtime-preflight staged-contract regression now asserts the
machine-readable schema path as well as schema version and failure stage;
focused runtime, health, and commercial-handoff checks pass (`38` tests),
and the handoff manifest remains content-addressed and verified.

2026-09-11: Promoted the runtime-preflight schema contract to an explicit
verified production checklist control. Regenerated readiness evidence now
reports `118` controls (`110` verified, `8` open); the commercial handoff
manifest was regenerated and verified.

2026-09-11: Runtime-preflight pass and blocked examples now validate against
the checked-in JSON Schema using the installed `jsonschema` validator. Current
maintained coverage is `291` tests (`215` deployment, `76` platform).

2026-09-11: `/v1/contract` now publishes both the runtime-preflight schema
version and its handoff-relative schema path; health/contract regression
coverage passes with the discovery metadata present.

2026-09-11: Deployment README now includes the runtime-preflight JSON Schema
validation step and explicitly documents pass/blocked results as intentional
machine-readable outcomes. Handoff documentation tests and manifest
verification pass after regeneration.

2026-09-11: Added schema-level regression coverage for the versioned
customer-production runtime-preflight contract. Current maintained coverage
is `290` tests (`214` deployment, `76` platform).

2026-09-11: Runtime-preflight pass and blocked outputs now include the
handoff-relative `schema_path`, and the JSON Schema requires it. CLI output,
schema examples, and the commercial manifest were regenerated and verified.

2026-09-11: Added runtime-preflight regression coverage for staged contract
failures; the public entry point now proves it reports `stage: contract`
without exposing connection details. Current maintained coverage is `289`
tests (`213` deployment, `76` platform).

2026-09-11: Customer-production runtime preflight now requires HTTP 200 from
readiness, contract, and Prometheus endpoints before evaluating their bodies.
Non-success responses fail closed; maintained coverage is now `288` tests
(`212` deployment, `76` platform).

2026-09-11: Runtime preflight connection failures now report a safe check
stage (`readyz`, `contract`, `metrics`, or `execution-sandbox`) alongside the
error type, improving operator diagnosis without echoing endpoint URLs,
headers, or credentials. A failed readiness probe was verified to return the
structured stage field.

2026-09-11: Customer-production runtime preflight output now carries the
versioned `verification-customer-production-runtime-v1` schema on pass and all
blocked paths, allowing deployment automation to parse the result without
depending on human-readable text.

2026-09-11: Published the runtime-preflight schema in the authenticated
`/v1/contract` response and added contract regression coverage, completing the
discovery path from integration preflight tooling to the service contract.

2026-09-11: Added the versioned runtime-preflight JSON Schema to the
commercial handoff inventory and documented its pass/blocked contract. Handoff
documentation, manifest generation, and manifest verification pass.

2026-09-11: Pinned `jsonschema==4.23.0` in deployment requirements so clean CI
runners can execute runtime-preflight schema validation without relying on an
ambient package. Handoff and runtime-preflight tests pass.

2026-09-11: Added an explicit CI step that validates pass and blocked runtime
preflight examples against the shipped JSON Schema. Workflow YAML parses and
handoff documentation tests pass.

2026-09-11: CI release uploads now include the runtime-preflight JSON Schema
alongside the commercial manifest, allowing downstream reviewers to validate
the uploaded result without the repository checkout. Workflow parsing and
handoff documentation tests pass.

2026-09-11: Added `scripts/verify_customer_production_runtime.py` itself to
the content-addressed commercial handoff inventory, alongside its schema and
generated results. Handoff and manifest tests pass after regeneration.

2026-09-11: CI release uploads now include both the runtime-preflight verifier
and its JSON Schema, making the validation toolchain reproducible from the
uploaded handoff artifact. Workflow parsing and handoff tests pass.

2026-09-11: Retained a local customer-production runtime rehearsal artifact;
it is schema-valid and explicitly blocked because the reference service is
configured as `pilot`. The artifact is now content-addressed in the commercial
handoff, preserving the real deployment boundary.

2026-09-11: Fixed empty-file adjudication provenance: an explicitly attached
zero-finding LLM review now records its source digest and `finding_count: 0`
instead of being mistaken for no attachment. Full maintained coverage is now
`287` tests (`211` deployment, `76` platform), with the regression included.

2026-09-11: Full maintained validation now passes `286` tests (`210`
deployment, `76` platform) after adding internal adversarial-packet digest
verification. Active handoff counts and commercial-goal evidence were updated
to match the collected suite.

2026-09-11: Independent browser acceptance rerun passes all listed UX,
state-isolation, evidence-boundary, recovery, waveform/source inspection, and
page-error checks. A prior combined sweep was interrupted by stale Chromium
resource contention before test execution; stale processes were cleared and
the standalone gate then passed.

2026-09-11: Fresh adversarial judge rerun passes all seven deterministic
scenarios with no findings; browser/API evidence and the maintained repair and
execution tests remain green. The packet is marked as awaiting external LLM
adjudication, preserving the distinction between deterministic coverage and
independent review.

2026-09-11: Adversarial packets now carry explicit machine-checkable LLM
adjudication metadata, including attached finding-file digest and count when
provided, or an explicit `not_attached` claim boundary otherwise. This makes
external review handoff auditable without treating deterministic preflight as
LLM judgment.

2026-09-11: Hardened adjudication input validation: findings now require
non-empty typed action/evidence arrays and non-empty expected, observed,
trust-risk, and acceptance-test text. Malformed model output fails closed;
ten adversarial-validator tests pass.

2026-09-11: Reconciled the adversarial evaluation contract with the current
browser evidence, leaving representative-user usability and independent LLM
agreement as the only unproven review requirements. Regenerated the changed
judge packet and commercial handoff manifest; manifest verification passes.

2026-09-11: Rendered the customer-production Kubernetes overlay with the
documented `--load-restrictor LoadRestrictionsNone` operator command and ran
the semantic overlay preflight successfully. The rendered configuration
contains no credential material and passes the required managed-state,
identity, backup, isolation, observability, and adapter wiring checks.

2026-09-11: Adversarial judge packets now include a canonical self-digest over
their deterministic results, scenario coverage, evidence references, and LLM
claim boundary. A fresh seven-scenario run passed, its self-digest recomputed
successfully, and the commercial handoff manifest was regenerated and
verified.

2026-09-11: Added maintained regression coverage for canonical packet digest
construction and mutation detection. Eleven adversarial-judge tests now pass;
the handoff manifest was rebuilt and verified after the change.

2026-09-11: Commercial handoff verification now validates the adversarial
judge packet's internal self-digest in addition to its inventory file hash.
Tampering with either the packet bytes or its canonical content is rejected;
the handoff verifier and packet-integrity tests pass.

2026-09-11: Updated the commercial beta handoff instructions to make packet
self-digest and optional external-finding digest checks operator-visible.
Handoff documentation and manifest tests pass after regeneration.

2026-09-10: Replaced string-based panel construction for execution backends,
commercial readiness, and pilot measurement with typed DOM nodes and text
content. This keeps capability and release evidence surfaces safe under the
workbench CSP while preserving their loading, unavailable, and live states.
Validation: `node --check site/verification-workbench.js`, the full browser
gate, and focused adapter-selector acceptance pass with no page errors.

2026-09-10: Installed the typed run-list renderer before initial hydration, so
API-controlled job IDs, kinds, statuses, and timestamps cannot briefly pass
through the legacy HTML-string renderer before the setup module loads. Browser
acceptance and workbench contract/runtime tests pass.

2026-09-10: Customer-production runtime preflight now executes standalone with
the local sandbox probe import resolved correctly. Against the local reference
service it returns a structured blocked result because the process is deployed
as `pilot`, which keeps the customer-production gate explicit and prevents a
local rehearsal from being presented as production evidence.

2026-09-10: Added and passed focused adapter-selector browser acceptance: available-only selection, blocked-tool visibility, ephemeral argument input, and no page errors. The check uses the same CI-safe Chromium flags and bounded timeout as the main gate.

2026-09-10: HTTP signoff responses and receipt retrieval now omit absolute report paths while preserving internal digest verification; adapter PoV/signoff tests confirm the public boundary.

2026-09-10: Added negative handoff coverage: blocked customer-adapter executions can produce inspectable PoV evidence but are rejected by the hash-bound signoff route. Maintained release evidence at that increment was `281` tests (`205` deployment, `76` platform); later additions bring the current suite to `285` (`209` deployment, `76` platform).

2026-09-10: Added an HTTP-level customer-adapter handoff test covering `/proof-of-value` and `/signoff`; the returned signoff digest must equal the report digest. Maintained release evidence is now `280` tests (`204` deployment, `76` platform).

2026-09-10: Integrated release validation passes: `279` maintained deployment/platform tests, fresh browser UX gate with no page errors, seven-scenario adversarial judge, and content-addressed handoff manifest verification.

2026-09-10: Adapter PoV generation now persists `adapter_pov` on the durable job record, so the signed report is discoverable through job metadata as well as direct report, evidence, and bundle endpoints.

2026-09-10: Customer-adapter jobs now generate `verification-adapter-pov-v1` reports with a self-digest and can use the existing hash-bound signoff route; blocked adapter executions cannot be signed off. The report is included in bounded evidence inspection and bundles.

2026-09-10: Fresh `verify_workbench_handoff.py` and `verify_workbench_setup.py` runs pass. The end-to-end browser handoff restores a selected run, PoV, immutable bundle, signoff, and project isolation; setup rejects a bad key, creates a project, uploads RTL/checker collateral, queues a bound run, and restores the authenticated session without page errors.

2026-09-10: Fresh adversarial judge rerun passes all seven deterministic scenarios (`gate_passed=true`) after the Chromium launch fix; the judge packet was regenerated and the 35-artifact handoff manifest reverified.

2026-09-10: The browser gate now passes all listed UX scenarios with no page errors after adding `--disable-dev-shm-usage` to Chromium launch arguments; this resolves the prior environment-level page-creation failure.

2026-09-10: Fresh browser-gate verification was attempted and failed before page creation because the installed Chromium closed (`TargetClosedError`). Handoff wording now distinguishes the checked-in gate and preserved screenshots from a fresh local browser pass; deployment/platform evidence remains green.

2026-09-10: Project audit exports now include safe customer adapter identity and argument count for each event, while excluding command arguments; adapter execution, dashboard, evidence, and audit surfaces now share the same bounded metadata boundary.

2026-09-10: Project dashboard terminal-run summaries now include registered adapter identity and argument count while retaining the no-raw-arguments boundary; focused adapter execution and HTTP tests pass.

2026-09-10: The workbench now enforces the published adapter argument limits client-side (64 arguments, 4 KiB each, 64 KiB total) and reports actionable errors before submission; the backend remains the authoritative second enforcement boundary.

2026-09-10: The maintained release suites now collect `279` tests (`203` deployment, `76` verification-platform) after adding argument-boundary coverage. Readiness is `115` controls (`107` verified, `8` open).

2026-09-10: Customer adapter arguments now have explicit limits (64 arguments, 4 KiB each, 64 KiB total), enforced before queueing and again at worker execution; the machine contract publishes these limits. This prevents oversized command payloads from becoming a resource or log attack.

2026-09-10: Adapter execution arguments now use an ephemeral, labeled JSON input in the workbench; URL query arguments are no longer consumed, preventing browser history and proxy logs from becoming an argument channel. The form explicitly directs credentials to the deployment secret manager.

2026-09-10: The workbench now renders a capability-driven selector for available registered adapters, stores only the selected adapter identity in scoped session state, and keeps blocked tools visible with their declared outputs and timeout. The customer-adapter API path remains evidence-bound and secret-safe; handoff artifacts were regenerated and verified.

2026-09-10: Registered customer EDA adapters are now first-class project-scoped `customer-adapter` jobs: availability is checked before queueing, cross-project source artifacts are rejected, execution uses the common bounded runner in both API and durable-worker paths, expected artifacts and provenance are persisted, and pass/fail behavior is covered by service tests. Adapter job, single-job, and list-job responses expose adapter identity and argument count without returning raw arguments, including through HTTP submission, polling, and run-list paths. The machine contract publishes the required fields, preflight guarantees, evidence file, and claim boundary. The maintained deployment and verification-platform suites now target `278` tests (`202` deployment, `76` verification-platform). Readiness remains `114` controls (`106` verified, `8` open); full-repository discovery still encounters an archived recovery fixture with a missing local import, so release evidence remains scoped to the maintained suites.

Active objective: carry out the commercial end-to-end goal in
[`commercial-verification-workbench-goal.md`](commercial-verification-workbench-goal.md):
onboarding through execution, investigation, proposal review, retest, and
evidence handoff using the open-source backend, with adversarial UX validation
and explicit production gates. This file tracks progress and does not narrow
acceptance.

## First implementation increment

- Extracted application JavaScript into `site/verification-workbench.js` for subsequent restructuring.
- Added a prominent sample/connected mode banner. Connected dashboard loading no longer fills missing API fields with demo values; illustrative readiness/metrics are hidden in connected mode.
- Failure selection clears review state and hides unrelated evidence. Returning to the Evidence tab cannot expose the previous failure fixture.
- Run selection clears review state, verifies project identity, and ignores obsolete inspection responses.
- Project changes clear URL artifact/job/proposal parameters and reload the selected context.
- Navigation now moves to the corresponding section with history and focus handling. Narrow screens retain navigation/project controls.
- Fixed dynamic artifact inspection using safe DOM construction and bound row objects. Artifact filters respect the hidden state. Ingest/plan/generate responses can be inspected as JSON.
- Removed guessed report coverage and formal defaults. Sample reports cannot enable signing/downloading a nonexistent live package.
- Marked previous design QA pass as superseded by the behavioral audit.

Validation: `node --check site/verification-workbench.js`; `python3 scripts/verify_workbench_browser.py` (Playwright Chromium, optionally `WORKBENCH_CHROMIUM`); `python3 -m pytest deployment/test_workbench_contract.py -q`. Browser smoke covers selection isolation, Evidence-tab guard, artifact selection/filtering, navigation, sample report guard, mobile navigation, failed-live/no-sample-fallback, and page errors. Contract tests remain only structural checks, not end-to-end evidence.

## Required remaining work

1. Replace the remaining legacy HTML-string paths and split the long page into
   clearer working destinations/three-pane investigation views.
2. Run the usability study with representative verification engineers and
   record measured results in the validated study template.
3. Complete managed database/object storage, enterprise identity/RBAC,
   per-job isolation, centralized observability, recovery/key rotation, and
   customer-specific EDA adapters described by the production migration plan.
4. Run a signed customer pilot and finalize proof-of-value metrics; current
   scorecard and usability templates intentionally remain draft evidence.

## One-hundred-thirty-third implementation increment

Hardened the browser acceptance harness for the workbench CSP. The service
entry point deliberately forbids `unsafe-eval`; the setup and handoff checks
previously used Playwright string-based `wait_for_function` predicates, which
were rejected by that policy. They now wait on concrete DOM attachment, URL,
and text state, so the checks exercise the same browser security posture as a
real deployment without weakening CSP.

Validation: 145 service/platform tests passed; browser smoke, adversarial
judge, deployment preflight, fresh-session setup, and complete report/bundle/
signoff handoff all passed.

## One-hundred-thirtieth implementation increment

Reconciled the roadmap's open-work section with the verified implementation.
Delayed project switching, adversarial adjudication, release packaging, and
operator documentation are now recorded as completed increments; the tracker
focuses on the remaining substantive gates: structured UI decomposition,
representative engineer usability results, enterprise infrastructure and
customer adapters, and a signed measured pilot.

The initial audit screenshot set represents the pre-change HEAD application, recaptured separately from a temporary baseline directory; new verification captures belong in `.artifacts/workbench-browser/`. Do not use baseline captures as evidence of the changed UI.

## Third implementation increment

Added the first run-bound evidence seam. The service now exposes a bounded
`GET /v1/jobs/{id}/evidence` view containing only allowlisted run files,
durable events, artifact identities, capped log text, and waveform presence;
arbitrary filesystem paths are never returned. The worker-to-service test now
executes a real Icarus/VVP simulation with a generated VCD and a functional
coverage marker, verifies terminal events, builds the PoV report, and checks
the evidence endpoint against the exact RTL/checker IDs. The workbench's run
inspector renders that identity, result, output, waveform availability, and
event history. Connected report loading is rebound to the selected terminal
run and chooses the correct regression or simulation report endpoint.

Validation: five workbench tests passed, including real worker execution and
report/evidence generation; both browser scripts pass JavaScript syntax checks.
This increment still does not complete the repair diff, linked retest,
comparison, or human review receipt.

## Fourth implementation increment

Repair proposals now carry a deterministic SHA-256 over the source artifact,
source revision, exact before/after text, rationale, and occurrence count.
The service rejects an approval carrying a changed digest, and retest jobs
persist lineage to the baseline job and both artifact identities. The setup
workbench presents a review form and exact diff, refuses multi-match proposals,
and sends the digest from the displayed proposal when approving. The service
and worker path was exercised end to end with an intentionally failing RTL,
an exact one-occurrence repair, a passing retest, and a comparison proving the
failure resolved. Twelve repair/service tests pass in the focused suite.

The remaining handoff work is a report comparison view that exposes scope and
changed conditions, a readable bundle inventory, explicit reviewer identity and
notes, and a browser-level demonstration of those decisions. The legacy
URL-driven repair handler remains in the source as compatibility code but is
overridden by the setup module in the served application and must be removed
once the new journey is fully covered.

## Fifth implementation increment

Bundle previews now return and render the actual included and missing file
names before download. The workbench signoff action opens a reviewer form,
requires notes, offers an explicit approve/review-required decision, and
records the receipt against the loaded report hash. Comparison rendering shows
baseline/retest IDs, resolution state, coverage delta, claim boundary, and
both report hashes. A real browser handoff check covers selecting a completed
run, loading its run-bound PoV, previewing the bundle, and recording an
approved reviewer decision with no page errors. The service/worker focused
suite and browser handoff check pass.

The complete commercial goal is still active: interruption recovery, richer
comparison scope, accessibility review, adversarial LLM findings and
reproduction, and removal of legacy compatibility handlers remain before the
final acceptance demonstration.

## Sixth implementation increment

The workbench now adds contextual Cancel and Retry actions to queued, running,
and failed run rows. Actions use the authenticated service, preserve the
existing job identity, and report failures inline through the existing status
surface. The worker and synchronous service runner now preserve an execution
adapter's `blocked` result instead of relabeling missing evidence as a design
failure. The fresh-session browser scenario now queues a bound run, reloads,
and cancels it through the UI; the service status is verified as `cancelled`.

## Second implementation increment

Added a same-origin `/workbench/` service entry point with an explicit public asset allowlist; API authentication remains required. Added connection, project creation, multiline/file upload, and run configuration dialogs. API and project keys are scoped to the service origin in tab session storage. Run submission uses actual RTL/checker selections, accepts multiple regression checkers, displays discovered capabilities, and explicitly describes queued-worker semantics. The new forms supersede the legacy prompt/URL-driven setup handlers. A failed run-async request can retry the already-created job instead of creating a duplicate.

Added `deployment/test_workbench_serving.py` to verify public UI/authenticated API separation and reject arbitrary asset paths. Added `scripts/verify_workbench_setup.py` to exercise fresh-session setup against an isolated real service; this validates queue submission, not execution or the full acceptance journey. The worker, investigation, proposal/retest, and signoff integration remain required.

Second-increment validation: four serving/structural tests passed. The real-service browser scenario passed rejected-key recovery, connection, project creation, RTL/checker uploads, exactly one queued run with both artifact identities, authenticated reload, and zero page errors. Screenshot inspection identified a residual sample P0 badge in live mode; it was hidden and added to the browser regression assertions. This evidence does not establish worker execution or downstream review completion.

## Seventh implementation increment

Added the adversarial judge contract at
`docs/evaluations/verification-workbench-adversarial-judge.md`, with separate
first-time engineer, debug engineer, and verification lead roles; wrong-run,
stale-response, missing-waveform, changed-proposal, narrower-retest,
connection-loss, authorization, and missing-coverage traps; and a required
finding schema. The deterministic browser smoke now also checks form-control
names and keyboard focus. It passes alongside the service and handoff suites.

The adversarial document is an evaluation protocol, not a fabricated model
score. The remaining release requirements are executing these delayed/error
scenarios, reproducing model findings, formal timeout UX, and representative
engineer usability validation.

## Tenth implementation increment

The run-scoped evidence view now includes the exact RTL and testbench content,
version, content hash, and bounded source text for the job's artifact IDs.
The investigation screen renders those inputs as inspectable code blocks,
alongside the result, output, waveform availability, and durable events. The
service rejects cross-project artifact lookup while assembling the view. Two
execution evidence tests and the browser handoff test pass after this change.

Current browser verification is green across all three flows: offline trust
and accessibility smoke, fresh connected setup with cancellation, and the
completed run handoff through report, bundle, and signoff. The consolidated
service/workbench suite is 18 passing tests. This is strong vertical-slice
evidence, not completion of the broader commercial objective.

The browser smoke additionally exercises a mocked blocked formal-proof run:
the timeout reason is visible in the evidence view and signoff remains disabled.

## Eighth implementation increment

The workbench preserves the last known run table on transient polling errors
and uses a request identity guard for run inspection. Selecting a run adds its
ID to the address, and reload restores that run's evidence automatically.
The handoff browser test now proves selection, evidence, reload restoration,
report, bundle, and signoff in one connected flow. The browser smoke also
retains the label and focus checks. These changes address interrupted review
continuity; they do not yet cover a deliberately delayed project-switch
response or formal timeout presentation.

## Thirteenth implementation increment

Evidence-tab rendering is now bound to the current selection and uses DOM text
nodes for report-derived diagnosis, solver, counterexample, and claim-boundary
values. The browser adversarial smoke injects an HTML-shaped claim and verifies
that no element is created, while also verifying that missing evidence stays
missing when the user returns to the Evidence tab. Runner, execution, and
workbench checks remain green.

## Ninth implementation increment

Execution evidence now carries a durable job error into the UI. The run view
labels completed design checks, design failures, and execution failures
separately, including timeout reasons and missing evidence. Artifact ingest,
plan, and generation results remain visible after list refresh instead of being
discarded. The focused workbench suite is now 19 passing tests. The remaining
scope is still the delayed project-switch scenario, richer waveform/source
inspection, and formal timeout-specific interaction testing.

## Eleventh implementation increment

The run evidence response now includes bounded RTL and checker source, plus a
parsed VCD summary with signal names, byte size, and an inspectable excerpt.
The investigation view renders these as actual source and waveform details,
with explicit unavailable states. The execution evidence suite verifies the
source hash/content and waveform signal extraction against a real VVP run.

## Twelfth implementation increment

The execution runner now starts tools in their own process group and kills the
whole group on timeout, preventing EDA wrappers from leaving orphaned simulator
processes. Simulation adapters accept and forward the configured timeout, and
blocked adapter results retain a recoverable execution reason in the job and
evidence view. A simple process-group timeout probe passes; an intentionally
infinite VVP scenario is not used as a routine test fixture because some VVP
versions detach child processes, and requires a dedicated sandboxed worker
test before release acceptance.

## Fourteenth implementation increment

The connected handoff now proves project isolation after review completion. A
reviewer can load a run-bound report, preview its bundle, record a signoff, and
switch to a second project; the new project starts with no selected run, no
report, no evidence view, and no artifact inspector state. The browser harness
also covers reload restoration of the original run before the switch. This
closes the cross-project state-leak path in the primary review journey while
leaving delayed in-flight response testing and richer synchronized debug views
as later release work.

Validation: 24 focused service/workbench tests pass; the offline browser smoke,
fresh connected setup flow, and connected handoff/isolation flow pass; both
frontend bundles pass `node --check`. `git diff --check` still reports three
pre-existing trailing-whitespace lines in the unrelated analog measurement CSV.

## Fifteenth implementation increment

Waveform evidence is now an interactive part of the investigation view. A
run's bounded VCD summary exposes captured signals as keyboard-accessible
controls; selecting one shows only the matching records from the bounded
excerpt and clearly states when no transition for that signal was captured.
This keeps the debug action tied to the selected run and avoids presenting a
generic waveform as if it were evidence for another failure. The browser smoke
now exercises signal selection and confirms the selected signal detail renders
without page errors.

## Sixteenth implementation increment

The same run-bound evidence view now exposes bounded RTL source as selectable
line records. Selecting a line opens the artifact inspector with the artifact
name, exact line number, run ID, and content hash. Source content is rendered
through text nodes and capped to a bounded number of lines, preserving the
provenance boundary while giving an engineer a direct signal-to-source debug
step. The browser smoke covers both waveform signal selection and source-line
inspection.

## Seventeenth implementation increment

Run-list refreshes now carry a request generation and re-check the active
project before applying results. An older response is discarded when a newer
refresh has started, so delayed API responses cannot overwrite the current run
table. The browser smoke deliberately returns an older response after a newer
one and confirms that the newest run remains visible.

## Eighteenth implementation increment

Durable execution history is now an actionable review surface. Each recorded
run event is rendered as an accessible control; selecting it opens the exact
event payload with the run identity and an explicit evidence boundary. Empty
histories are stated as missing evidence instead of being represented by an
empty JSON block. Browser smoke covers event inspection alongside waveform and
source inspection.

## Nineteenth implementation increment

The investigation cursor is now durable. Selecting a waveform signal, RTL
source line, or execution event records that position in the selected run's
URL. Reloading the run restores the requested waveform/event context, making a
debug finding shareable and reviewable without relying on browser memory. The
browser smoke verifies URL updates and event-context restoration after reload.

## Twentieth implementation increment

The adversarial evaluation contract is now executable. `scripts/run_workbench_adversarial_judge.py`
runs the browser gate and execution/repair service checks, then emits a
versioned JSON packet containing gate output, seven skeptical scenarios, roles,
action sequences, evidence paths, and an empty findings array reserved for LLM
adjudication. This separates observed evidence from model judgment and avoids
treating a favorable prose summary as an adversarial score.

## Twenty-first implementation increment

The browser adversarial gate now exercises overlapping evidence requests as
well as overlapping run-list refreshes. It starts a delayed request for an old
run, immediately requests a newer run, and verifies that the selected identity
remains the newer run after both responses complete. This validates the
selection-version guard at the actual evidence boundary, not only at the list
rendering boundary.

## Twenty-second implementation increment

The adversarial browser gate now covers the missing-coverage boundary in the
commercial report. A passing run with no functional coverage marker renders
`Not reported` rather than inventing a percentage. This keeps execution
success, formal status, and coverage evidence as separate claims for the
verification lead.

## Twenty-third implementation increment

Baseline/retest comparison now checks scope before making a closure claim. A
repair is allowed to change the RTL artifact, but the testbench stimulus must
remain the same. If a retest uses a different testbench scope, the comparison
returns `scope_comparable: false`, withholds failure resolution and coverage
delta, and states that the results are incomparable. The workbench presents
that boundary directly in the comparison panel, and a focused service test
covers the narrower-scope case.

## Twenty-fourth implementation increment

Polling interruption recovery is now exercised in the browser gate. After a
known run is rendered, the next run-list request is forced to fail; the last
known run remains visible and the pipeline status becomes `Stale`, giving the
reviewer a recoverable refresh path without erasing run identity.

The same gate now forces a 401 after the stale state is visible and verifies
that the known run remains present while the pipeline changes to
`Unauthorized · reconnect required`.

## Twenty-sixth implementation increment

Credential expiry is now treated as recoverable review state. A 401 during
polling preserves the last known run and labels the connection as requiring
reconnection, so the workbench does not silently clear evidence or fall back
to sample metrics.

## Thirtieth implementation increment

The adversarial judge runner now accepts an optional model-produced findings
JSON and validates every finding against the documented severity, role, action,
evidence, trust-risk, and acceptance-test schema before attaching it to the
packet. This keeps provider choice outside the workbench while making an LLM
adjudication reproducible and machine-checkable.

## Twenty-seventh implementation increment

Reviewer receipts are now reloadable evidence. The service exposes a
run-scoped signoff receipt with cryptographic validity, and loading a report
restores the reviewer, timestamp, approval state, and report hash. The
connected handoff proves the receipt survives reload before switching projects;
signoff, serving, and execution tests remain green.

## Twenty-eighth implementation increment

The report loader now distinguishes a valid stored reviewer receipt from a
tampered or invalid one. An invalid receipt is surfaced as `Invalid signoff
receipt`, disables further signoff, and explains that re-review is required.
This prevents a corrupted approval artifact from silently regressing to an
apparently healthy unsigned report.

## Thirty-third implementation increment

The first adjudicated UX finding is now closed in the product. An empty live
project displays `Setup required · upload RTL`, and the primary run action is
disabled until RTL collateral exists. The connected handoff test verifies the
empty-project state after switching away from a reviewed project, and the
finding record documents the evidence and resolution.

## Thirty-fourth implementation increment

The global search control is now functional across failures, durable runs, and
project collateral. It hides non-matching records and reports an explicit
no-match state, while preserving the existing section-specific collateral
filter. Browser smoke covers matching and no-match searches.

## Thirty-fifth implementation increment

Adversarial packets now declare their adjudication state. Packets without model
findings are marked `awaiting_external_llm_adjudication`; packets with validated
findings are marked `findings_attached_for_reproduction`. This makes it
impossible to confuse a deterministic preflight with a completed model score.

## Thirty-sixth implementation increment

Global search is now reapplied whenever run or collateral data is rendered, so
a query entered before a refresh continues to constrain newly arrived records.
The browser gate covers matching and no-match behavior after the data is
present, and the setup bundle passes syntax validation.

The adversarial browser gate now supplies a tampered signoff receipt alongside
an otherwise valid passing report and verifies that the UI displays the
integrity failure and disables signoff.

## Thirty-second implementation increment

The browser gate now covers invalid signoff receipt handling end to end. A
tampered receipt cannot be presented as approval, and the UI disables further
signoff while preserving the report's separate coverage boundary.

## Thirty-first implementation increment

The lead review flow now blocks signoff when a baseline/retest comparison is
scope-incomparable. The comparison panel states the withheld closure claims,
and the signoff control becomes disabled until a comparable retest is
available. Browser and focused comparison/repair tests cover this boundary.

## Twenty-ninth implementation increment

Proof-of-value coverage now carries an explicit `reported` flag. The existing
simulation-execution proxy percentage remains available for internal metrics,
but the workbench displays `Not reported` unless a bounded functional coverage
marker was actually captured. This prevents a passing simulation from being
presented as functional coverage evidence while preserving backwards-compatible
report data.

## Twenty-fifth implementation increment

The connected handoff now proves the immutable bundle download itself. After
loading the run-bound report and previewing its inventory, the browser expects
the ZIP download and verifies the suggested filename contains the exact run ID
before proceeding to reviewer signoff and project isolation.

## Thirty-seventh implementation increment

The live connection status is now announced with an ARIA status region. Stale,
unauthorized, setup-required, and connected states are available to assistive
technology as well as visual users. Browser smoke continues to pass after the
accessibility update.

## Thirty-eighth implementation increment

The operator search path now reapplies its query after refreshed data arrives,
and the stable browser gate covers the user-facing match/no-match behavior.
The implementation retains a separate open requirement for a dedicated
refresh-order browser fixture because the existing mutation-observer harness
made direct DOM injection flaky.

## Thirty-ninth implementation increment

The live run renderer now builds job rows with structured DOM nodes instead of
interpolating service fields into HTML. Job IDs, kinds, statuses, timestamps,
and inspect controls remain available to the existing search, selection, and
contextual retry/cancel flows while untrusted values cannot create markup.
Browser smoke and JavaScript checks pass after the renderer replacement.

## Fortieth implementation increment

The adversarial packet runner now exposes reusable findings-schema validation.
Unit tests cover accepted findings and malformed severity, role, action,
evidence, and required-field output, ensuring model results are rejected before
they enter a review artifact.

## Forty-first implementation increment

Durable reviewer signoff retrieval now has an API-level regression contract in
addition to the browser handoff. The test proves a persisted approval receipt
is reported valid, then detects a tampered proof-of-value digest as invalid;
this protects the integrity boundary independently of browser behavior.

## Forty-second implementation increment

The browser gate now exercises a delayed jobs response crossing a project
navigation boundary. A response for the previous project is discarded after
the URL moves to the new project, while the new project's run remains visible;
this closes the stale cross-project refresh risk in the operator journey.

## Forty-third implementation increment

Sample failure rows now use structured DOM construction with text nodes for
failure IDs, priorities, and metadata. Selection, evidence clearing, and
keyboard-accessible controls are preserved while untrusted fixture values no
longer pass through an HTML template. `node --check` passes; the browser gate
was not rerun because Chromium startup is currently blocked by host resource
contention.

## Forty-fourth implementation increment

The Kubernetes pilot release now pins API and worker containers to an explicit
versioned image tag and includes a Kustomize overlay for changing the registry
and release tag during promotion. Operator instructions use `kubectl apply -k`
and retain the PVC-backed SQLite and evidence state across pod restarts.
`kubectl kustomize` renders both containers, probes, and the persistent volume
claim successfully.

## Forty-fifth implementation increment

Added a Kubernetes manifest preflight test covering immutable image tagging,
shared API/worker image identity, persistent artifact storage, non-root
execution, and health probes. The Kustomize promotion configuration is also
checked for a non-`latest` release tag. The two release tests pass, and PyYAML
is now pinned in the deployment requirements so CI and image builds use the
same parser dependency.

## Forty-sixth implementation increment

Workbench toast notifications now explicitly expose polite, atomic status
semantics and safely stringify messages. This makes queue, retry, evidence,
and signoff outcomes available to assistive technology without changing the
operator flow. JavaScript syntax and diff checks pass.

## Forty-seventh implementation increment

Added `deployment/RECOVERY_RUNBOOK.md` with pause/snapshot/resume backup,
PVC restore validation, stale-job handling, and incident evidence capture for
the SQLite-backed pilot. The production checklist distinguishes this
documented pilot procedure from the still-required managed backup, disaster
recovery, and key-rotation controls.

## Forty-eighth implementation increment

Removed the embedded placeholder API credential from the Kubernetes base
manifest. Operators must create or rotate `verification-pilot-api` out of
band before applying the release, preventing accidental deployment with a
known secret. The manifest preflight asserts that no Secret object or secret
value is shipped in the release; tests and `kubectl kustomize` both pass.

## Forty-ninth implementation increment

The service now emits an `X-Request-ID` on every API response, preserving a
caller-supplied ID or generating a bounded random ID. This gives pilot
operators a correlation handle for tracing queue submission, evidence
retrieval, and signoff calls across API and worker logs. Health tests cover
both supplied and generated IDs.

## Fiftieth implementation increment

Request correlation IDs are now restricted to a safe, bounded character set;
invalid caller values are replaced with a generated ID before the response
header is emitted. This prevents malformed values from crossing into response
headers or log correlation. Health tests cover supplied, generated, and
rejected IDs.

## Fifty-first implementation increment

The request correlation ID now crosses the durable job boundary: API-created
jobs persist the accepted ID in `job.json`, allowing worker execution,
evidence retrieval, and signoff support to join the original customer request.
The persistence regression passes independently of HTTP middleware behavior.

## Fifty-second implementation increment

Durable job transition events now carry the same request correlation ID as the
job record. Exported evidence timelines can therefore be joined to the API
submission without relying on process-local logs. The correlation regression
also verifies the queued event contains the ID.

## Fifty-third implementation increment

Worker-generated running, timeout, and terminal events now preserve the job's
request correlation ID. The worker integration test exercises a real compile
job and verifies every emitted event remains traceable to its originating
request.

## Fifty-fourth implementation increment

Added bounded HTTP response-class counters and request-ID generation counts to
the Prometheus metrics endpoint. The service reports 2xx/3xx/4xx/5xx totals
without URL-cardinality leakage, giving operators a basic error-rate signal
for pilot SLO monitoring. Health/metrics tests pass.

## Fifty-fifth implementation increment

The broader auth/health/worker regression run exposed and fixed a guard
compatibility defect: authentication now safely handles minimal request shims
by deriving method and path defensively, while real ASGI requests retain the
same public-route and credential rules. Auth, health, and worker tests pass
(`9 passed`).

## Fifty-sixth implementation increment

Connected workbench setup requests now send a fresh `X-Request-ID` for each
API action, linking operator interactions to the durable job and event
correlation fields. Workbench contract and serving tests pass (`4 passed`),
and the setup bundle passes JavaScript syntax validation.

## Fifty-seventh implementation increment

Live workbench API failures now include the server's `X-Request-ID` in the
inline error message when available. This gives verification engineers a
support-ready trace handle for authentication, project, queue, and evidence
failures without exposing implementation details. Contract tests and setup
JavaScript syntax validation pass.

## Fifty-eighth implementation increment

Successful live run submission now displays the persisted request correlation
ID in the queue confirmation toast. Operators can capture the trace handle at
the moment work enters the durable queue, complementing the existing error
and event-timeline correlation. Setup JavaScript syntax and diff checks pass.

## Fifty-ninth implementation increment

The workbench contract suite now asserts that setup requests send
`X-Request-ID` and that successful queue confirmations surface the persisted
request identifier. This protects the operator-facing trace path during future
frontend refactors. Contract tests pass (`3 passed`).

## Sixtieth implementation increment

Added `deployment/CUSTOM_ADAPTER_GUIDE.md`, defining how customer simulator,
formal, regression, and artifact adapters use the shared provenance runner,
report blocked tools, preserve expected artifacts and bounded logs, and pass
known pass/fail/timeout/missing-artifact fixtures before handoff. The
production checklist now links this contract instead of leaving adapter
integration as an undefined task. Adapter coverage passes (`1 passed`).

## Sixty-first implementation increment

Adapter regression coverage now includes an otherwise successful command with
a missing expected artifact and a tool that exceeds its timeout. Both are
classified as `blocked` with provenance metadata, matching the customer
adapter contract and preventing false passes. Adapter tests pass (`3 passed`).

## Sixty-second implementation increment

Ran the complete deployment service suite and the full provenance/adapter
suite after the tracing, Kubernetes, and customer-adapter changes. All
deployment tests pass (`58 passed`) and all verification-platform tests pass
(`66 passed`), with only the existing Starlette/httpx deprecation warning.

## Sixty-third implementation increment

Added `deployment/PILOT_MEASUREMENT_PLAN.md`, a customer scorecard defining
triage latency, root-cause usefulness, reproduction time, evidence completeness,
manual effort, and closure integrity with explicit evidence sources and
acceptance targets. It also requires mixed failure sampling, independent
reviewer labels, immutable run/request/hash links, and explicit claim
boundaries. The production checklist now links the scorecard for pilot
execution.

## Sixty-fourth implementation increment

The full Playwright browser gate now runs cleanly after the frontend tracing
changes. It covers search/no-match, selection and evidence isolation, stale
responses across project changes, blocked formal timeout, missing coverage,
invalid receipts, waveform/source/event inspection, interruption recovery, and
auth expiry with no page errors.

## Sixty-fifth implementation increment

The real-service browser handoff passes after the latest changes. It exercises
connected setup, a queued and completed run, run-bound evidence, reload
restoration, proof-of-value loading, immutable bundle preview/download,
reviewer signoff and receipt restoration, and project-switch isolation with no
page errors.

## Sixty-sixth implementation increment

The consolidated adversarial preflight passes with the adjudicated findings
packet attached. It executes the browser gate plus repair/execution evidence
tests across seven failure and recovery scenarios, validates the findings
schema, and writes a reproducible packet at
`.artifacts/workbench-adversarial/judge-packet.json`.

## Sixty-seventh implementation increment

The fresh-session setup flow passes against an isolated real service after the
latest changes. It rejects a bad key, connects with tab-scoped credentials,
creates a project, uploads RTL and testbench collateral, queues one bound run,
and reloads the authenticated session with no page errors.

## Sixty-eighth implementation increment

Revalidated the complete connected handoff after request-ID propagation into
the setup UI. The real service still supports run selection, evidence and
context reload, PoV loading, immutable bundle download, reviewer signoff and
receipt restoration, and project isolation without page errors.

## Sixty-ninth implementation increment

The consolidated browser evidence set is green: offline UX smoke, fresh
real-service setup, and the connected run-to-signoff handoff all pass in the
same validation cycle. This confirms the latest tracing and deployment changes
preserve onboarding, execution, investigation, evidence export, approval, and
project isolation across the three operator entry paths.

## Seventieth implementation increment

Updated the UX review's status header to reflect current evidence: the
open-source pilot vertical slice is implemented and verified across browser,
service, worker, adversarial, and handoff gates, while enterprise integrations
and representative-user validation remain open. This prevents the product
brief from misrepresenting the implementation state.

## Seventy-first implementation increment

Updated `deployment/COMMERCIAL_BETA_HANDOFF.md` to replace its stale “100
tests” and unqualified image-smoke claim with current evidence: 58 deployment
tests, 66 verification-platform tests, green browser/setup/handoff/adversarial
gates, and successful Kubernetes rendering. The handoff now distinguishes CI
image validation from a registry push and avoids overstating local production
deployment.

## Seventy-second implementation increment

Added handoff-document regression checks for current evidence counts,
Playwright/adversarial gate references, and explicit managed-production
boundaries. The checklist test also requires links to the recovery runbook,
customer adapter guide, and pilot measurement plan, preventing documentation
drift from silently weakening the release decision. The new checks pass
(`2 passed`).

## Seventy-third implementation increment

Linked the commercial beta handoff, recovery runbook, customer adapter guide,
and pilot measurement plan from the repository's primary README. The pilot's
verified scope and remaining production gates are now reachable from the first
deployment instructions rather than hidden in deployment subdirectories.

## Seventy-fourth implementation increment

Added a documentation-integrity test ensuring the root README continues to
link the commercial handoff, recovery runbook, customer adapter guide, and
pilot measurement plan. The handoff-document suite now passes (`3 passed`).

## Seventy-fifth implementation increment

Added a release-evidence sequence to `deployment/README.md` covering backend
tests, browser smoke, fresh setup, connected handoff, and adversarial packet
generation. A documentation test now guards all four acceptance script links;
the handoff-document suite passes (`4 passed`).

## Seventy-sixth implementation increment

Re-ran the documented adversarial release gate against the current worktree.
The gate passed with seven scenarios and wrote a fresh reproducible judge
packet at `.artifacts/workbench-adversarial/judge-packet.json`.

## Seventy-seventh implementation increment

Added `deployment/pilot-scorecard-template.json`, a versioned structured
scorecard for baseline/workbench metric values, evidence links, independent
reviewer labels, lead receipt, and claim boundaries. A contract test validates
all six required metrics and traceability fields; the handoff-document suite
passes (`5 passed`).

## Seventy-eighth implementation increment

Added `deployment/pilot_scorecard.py` with validation rules for finalized pilot
scorecards: all six metrics, at least 20 sampled failures, baseline/workbench
values, evidence links, a lead reviewer, and a SHA-256 receipt are required.
Template and finalized-scorecard tests pass (`6 passed`), preventing an
incomplete measurement artifact from being presented as commercial proof.

## Seventy-ninth implementation increment

The pilot measurement plan now documents the scorecard validation command and
distinguishes structural validation from lead approval and evidence-bundle
verification. Handoff-document tests guard that instruction; the suite passes
(`6 passed`).

## Eightieth implementation increment

Added `scripts/validate_pilot_scorecard.py`, a supported CLI with readable
errors and exit codes for draft versus finalized scorecard validation. The
documented command now works from the repository root; a draft template passes
and the same template correctly fails finalized validation until pilot
evidence and review are populated.

## Eighty-first implementation increment

Added process-level tests for the scorecard CLI. The documented command now
has verified exit behavior: draft templates return success with a validation
message, while incomplete finalized templates return failure with readable
errors. Handoff-document tests pass (`7 passed`).

## Eighty-second implementation increment

Refreshed the commercial handoff's deployment-suite count after the new
scorecard CLI and documentation tests. The current deployment suite is
`65 passed` and the verification-platform suite remains `66 passed`; the
handoff regression now enforces the updated count.

## Eighty-third implementation increment

Added scorecard validation to the documented release-evidence sequence and
guarded the command in the handoff documentation test. The README sequence
now covers platform gates and measurement-artifact validation together; the
new documentation assertion passes directly.

## Eighty-fourth implementation increment

Re-ran the complete handoff-document suite after host contention cleared. All
seven documentation and scorecard contract tests pass, confirming the release
sequence, commercial evidence counts, artifact links, and CLI validation
instructions remain synchronized.

## Eighty-fifth implementation increment

Refined the production checklist to mark pilot-level request correlation and
bounded Prometheus response counters as implemented, while keeping centralized
logs, alerting, and SLO dashboards as the open production gate. Documentation
tests pass (`7 passed`), preventing the checklist from overstating observability
readiness.

## Eighty-sixth implementation increment

The auth observability regression exposed and fixed a middleware-ordering gap:
early 401 responses now carry the same sanitized `X-Request-ID` as successful
responses. Health/auth tests cover supplied, generated, invalid, and rejected
request IDs and pass (`3 passed`).

## Eighty-seventh implementation increment

The complete deployment suite remains green after the authentication
middleware correction: `65 passed` with only the existing Starlette/httpx
deprecation warning. This confirms protected routes, job lifecycle, worker,
Kubernetes, handoff, and scorecard contracts remain intact.

## Eighty-eighth implementation increment

Added `deployment/PRODUCTION_MIGRATION_PLAN.md`, sequencing the pilot-to-
production transition across managed state, identity/RBAC, isolated execution,
operations, and customer adapters/pilot measurement. Each stage has concrete
acceptance evidence and rollout controls; the production checklist and
handoff-document tests now link the plan. Documentation tests pass (`7 passed`).

## Eighty-ninth implementation increment

Added migration-plan contract coverage requiring managed state,
identity/authorization, isolated execution, operations, customer adapters,
acceptance evidence, and rollout controls to remain documented. The
handoff-document suite passes (`8 passed`).

## Ninetieth implementation increment

Refreshed the commercial handoff count after adding the migration-plan
contract: the deployment suite now passes `66 passed`, while the
verification-platform suite remains at `66 passed`. The handoff regression was
updated to enforce the current deployment count.

## Ninety-first implementation increment

Ran the combined backend acceptance suites in one cycle: deployment and
verification-platform tests pass together (`132 passed`) with only the known
Starlette/httpx deprecation warning. This is the current full-backend baseline
for the commercial pilot artifact.

## Ninety-second implementation increment

Project-scoped authorization failures now also return the sanitized
`X-Request-ID`. Health coverage exercises both global-key 401 and project-key
403 responses, confirming every authentication failure class remains
traceable. The health suite passes (`3 passed`).

## Ninety-third implementation increment

The combined deployment and verification-platform baseline remains green after
the project-key authorization fix: `132 passed` with only the known
Starlette/httpx deprecation warning.

## Ninety-fourth implementation increment

Made the commercial beta handoff self-contained with direct links to the
recovery runbook, customer adapter guide, pilot measurement plan, scorecard
template, and production migration plan. Handoff-document tests now verify all
five links; the suite passes (`8 passed`).

## Ninety-fifth implementation increment

Strengthened the commercial handoff contract so its operational links are
evidence-bounded: the recovery runbook, customer adapter guide, pilot
measurement plan, scorecard template, and production migration plan must each
exist on disk as well as appear in the handoff. The handoff suite passes
(`8 passed`), preventing a documentation-only release from pointing at a
missing artifact.

## Ninety-sixth implementation increment

Replaced the previous UX scope with the commercial verification workbench goal
in `commercial-verification-workbench-goal.md`. The goal now treats the
engineer journey, deterministic evidence boundary, adversarial LLM judging,
and production migration gates as one acceptance contract. The browser
acceptance run still passes all delayed-refresh, project-isolation,
authorization, evidence, and sign-off scenarios with no page errors; the
current result remains an open-source pilot gate rather than enterprise
production completion.

## Ninety-ninth implementation increment

Added a measured usability validation gate for the commercial workbench:
`USABILITY_STUDY_PLAN.md` defines five representative engineer tasks and
evidence handling, while `pilot-usability-study-template.json` and
`validate_usability_study.py` reject finalized claims without observed task
results, at least three participants, aggregate measurements, a lead reviewer,
and an evidence-bundle SHA-256. The handoff and release sequence link this
gate. Draft validation and handoff tests pass (`10 passed`).

## One-hundredth implementation increment

Revalidated the commercial pilot gates from the current worktree: the combined
backend suite passes (`136 passed` with the known Starlette/httpx warning), the
browser smoke has no page errors, the fresh-service setup passes, the complete
connected handoff passes after a serial rerun, the adversarial judge reports
`gate_passed: true` across seven scenarios, and the Kubernetes release
preflight renders successfully. The one initial handoff timeout occurred only
when multiple local browser services were started concurrently; the same
handoff verifier passes when run serially.

## One-hundred-first implementation increment

Built the actual release image from `deployment/Dockerfile` as
`verification-pilot:0.1.0-local` and extended the operator preflight with an
optional `--image` check. The combined render-and-image preflight passes,
proving that the pinned API/worker package can be rendered and is present in
the local container runtime; release publication to a customer registry
remains an explicit deployment action.

## Ninety-seventh implementation increment

Added a safe analysis renderer at the workbench boundary. Diagnosis,
counterexample, solver, closure, and claim-boundary values are now rebuilt as
text nodes after the legacy tab handler, and evidence rows retain keyboard
activation and run-bound inspection. JavaScript syntax, browser acceptance,
and focused contract suites pass (`11 passed` across the two pytest suites),
with no page errors in the browser run.

## Ninety-eighth implementation increment

Added `scripts/preflight_verification_deployment.py` as an operator-facing
release gate. It validates the Kubernetes pilot's API/worker image parity and
pinning, probes, secret reference, non-root policy, PVC, and required recovery,
adapter, measurement, scorecard, and migration artifacts; `--render` invokes
`kubectl kustomize` as an additional cluster-tool check. The deployment
preflight passes with rendering enabled, and its contract suite passes
(`12 passed`).

## One-hundred-second implementation increment

Ran the built `verification-pilot:0.1.0-local` image as a disposable API
container. `/healthz` returned the expected service response, startup logs
were clean, and `docker exec ... id -u` returned `10001`, confirming the
runtime is unprivileged. The deployment README and production checklist now
carry this runtime smoke gate, and handoff documentation tests enforce its
presence.

## One-hundred-third implementation increment

Added `scripts/verify_verification_image_runtime.py` to make the image smoke
gate repeatable. It starts a uniquely named disposable container, waits for a
200 response from `/healthz`, verifies UID `10001`, and stops the container in
a `finally` path even when the check fails. The verifier passes against
`verification-pilot:0.1.0-local`, and deployment documentation now uses this
single command.

## One-hundred-fifth implementation increment

Pinned the Dockerfile's `python:3.11-slim` base to its verified SHA-256
digest, closing the mutable-base-image gap in the production checklist. The
image rebuilt successfully as `verification-pilot:0.1.0-pinned`, the runtime
smoke passed against it, and the Kubernetes manifest suite now asserts the
base-image digest contract.

## One-hundred-fourth implementation increment

Extended `.github/workflows/verification-pilot.yml` with the commercial
release gates: deployment preflight, scorecard and usability-template
validation, adversarial workbench adjudication, and disposable image runtime
smoke after the Docker build. The workflow YAML parses successfully, and the
image smoke verifier passes against the CI-tagged image locally. Registry
publication and customer-specific infrastructure remain outside this local
workflow by design.

## One-hundred-sixth implementation increment

Expanded the disposable image verifier to require both liveness (`/healthz`)
and readiness (`/readyz`) before accepting the container, then verify UID
`10001` and clean up. The pinned image passes the stronger gate; deployment
documentation, checklist language, and handoff tests now describe readiness as
well as liveness.

## One-hundred-eighth implementation increment

Added `scripts/write_verification_release_manifest.py` to capture the built
image ID/repository digest, source revision, base-image pin state, runtime
user, and exact acceptance-gate commands in one release artifact. Generated a
manifest for `verification-pilot:0.1.0-pinned` successfully and documented the
command beside the runtime smoke, making package provenance portable with the
commercial handoff.

## One-hundred-ninth implementation increment

Hardened the release manifest generator to locate the Dockerfile's `FROM`
declaration structurally instead of relying on line position. The manifest now
records the exact base-image declaration and expected numeric runtime UID
(`10001`) in addition to the inspected image ID and digest. Regenerated the
pinned-image manifest successfully and verified both fields.

## One-hundred-seventh implementation increment

Added conservative browser security headers at the service boundary:
`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, strict referrer
policy, and a permissions policy disabling camera, microphone, and location.
The headers apply to API and workbench responses without changing the
same-origin workflow. Health/header coverage passes (`4 passed`), and the
combined backend suite remains green (`138 passed`).

## One-hundred-fourteenth implementation increment

Extended the browser acceptance flow to exercise the connected Reports
`Export audit` action against a mocked project audit response and verify the
downloaded filename is project-scoped (`verification-audit-coverage.json`).
This proves the audit endpoint is reachable through the lead's UX, not only
through direct API tests; the browser gate passes with no page errors.

## One-hundred-eighteenth implementation increment

Improved the Reports audit UX with a live status line showing exported entry
count, truncation state, and the leading digest characters. The browser flow
now verifies both the project-scoped filename and visible `1 entries` status
after export, preserving an immediately reviewable handoff signal with no
page errors.

## One-hundred-eleventh implementation increment

Auth-path testing exposed and fixed a middleware-ordering gap: early global-key
401 and project-key 403 responses now receive the same conservative security
headers as successful responses. Rejection-path assertions pass, and the
combined backend suite remains green (`138 passed` with the known dependency
warning).

## One-hundred-twelfth implementation increment

Added authenticated project-scoped audit export at
`GET /v1/projects/{project_id}/audit`. It returns a bounded, stable event
stream with job/project identity, status, timestamps, executor/reason, and
request IDs while omitting filesystem paths and raw logs. Audit export tests
pass within the service suite (`12 passed`), and the combined backend baseline
remains green (`139 passed`).

## One-hundred-seventy-third implementation increment

Extended `/v1/contract` with discoverable handoff-manifest builder and
verifier paths. Authorized customer tooling can now find the commands needed
to assemble and independently validate the complete commercial pilot package
from the same contract endpoint.

Validation: complete service/platform suite passes (`172 passed`).

## One-hundred-seventy-second implementation increment

Closed the commercial handoff integrity loop. The handoff manifest now carries
its own canonical SHA-256, and `verify_commercial_handoff_manifest.py`
recomputes that digest plus every inventoried artifact digest and path. CI and
release instructions run the verifier before upload, making exported handoff
packages independently auditable.

Validation: manifest tamper/path tests pass; the current 12-artifact manifest
verifies successfully.

## One-hundred-seventy-first implementation increment

Added a content-addressed commercial handoff manifest that inventories the
production checklist, migration/recovery/adapter/measurement artifacts,
observability specification, pilot ledger, readiness report, scorecard, and
recovery record. CI builds and uploads it after release provenance; the
manifest explicitly reports `customer_production_ready: false` while gates
remain open.

Validation: handoff-manifest contract test passes; the current manifest hashes
12 artifacts and records the eight open production controls.

## One-hundred-seventieth implementation increment

Added a canonical `scorecard_sha256` self-digest to generated pilot
scorecards. Validation recomputes the digest over the complete scorecard
payload, so edits to metrics, evidence references, or claim boundaries are
detected even when referenced files remain unchanged.

Validation: scorecard generation, tamper detection, handoff, and validator
tests pass; the regenerated draft scorecard validates.

## One-hundred-sixty-ninth implementation increment

Bounded the machine-readable readiness report to the exact checklist contents
with a `checklist_sha256` field. A handoff can now verify that its open/closed
control counts were generated from the intended checklist revision rather
than an untracked local edit.

Validation: readiness-report and handoff tests pass; the regenerated report
contains the checklist digest. (`jq` was unavailable locally, so inspection
used the generator and validator outputs.)

## One-hundred-sixty-eighth implementation increment

Linked the production readiness report generator from `/v1/contract`, giving
authorized customer tooling a discoverable path to the current release-gate
summary in addition to workflow, evidence, storage, and observability
contracts.

Validation: complete service/platform suite passes (`171 passed`).

## One-hundred-sixty-seventh implementation increment

Added `scripts/report_production_readiness.py`, which converts the production
checklist into a machine-readable report with verified/open control counts and
an explicit `customer_production_ready` boolean. CI now generates and uploads
the report with release evidence, preventing a pilot handoff from obscuring
the eight remaining enterprise gates.

Validation: readiness-report contract test passes; the current report records
20 verified controls, 8 open controls, and `customer_production_ready: false`.

## One-hundred-sixty-sixth implementation increment

Bounded Kubernetes ephemeral storage for both API and worker containers with
explicit requests and limits. This prevents noisy customer tools or temporary
artifacts from exhausting node disk; deployment preflight and manifest tests
now enforce the limits alongside CPU and memory constraints.

Validation: Kubernetes manifest and release-preflight tests pass; rendered
deployment preflight passes.

## One-hundred-sixty-fifth implementation increment

Linked the observability dashboard specification from the machine-readable
`/v1/contract` response. Authorized integrations can now discover the exact
dashboard and alert artifact alongside workflow and evidence contracts. A
test-placement regression was corrected so readiness fields and contract
fields remain distinct.

Validation: complete service/platform suite passes (`170 passed`).

## One-hundred-sixty-fourth implementation increment

Extended the observability dashboard specification with actionable Prometheus
alerts for readiness loss, sustained HTTP 5xx responses, high average
latency, and blocked EDA adapters. Alert expressions use only metrics emitted
by the service and include explicit duration and severity fields.

Validation: observability schema, handoff, and release-preflight tests pass.

## One-hundred-sixty-third implementation increment

Added a versioned observability dashboard specification covering service
readiness, queue depth, HTTP errors, average request latency, and EDA adapter
availability. The queries match the metrics the service actually exports and
the dashboard states its operational claim boundary. Deployment preflight and
commercial handoff now require the artifact.

Validation: dashboard schema, handoff, and release-preflight tests pass.

## One-hundred-sixty-second implementation increment

Made recovery evidence durable in CI. The snapshot verifier now accepts
`--output` and writes a JSON record containing source/restored file counts,
inventory digests, and match status; CI uploads it with the scorecard and
release manifest. Recovery is therefore inspectable after the workflow ends,
not only visible in transient logs.

Validation: recovery CLI, workflow documentation, and recovery tests pass;
the current record reports matching inventories and digests.

## One-hundred-sixty-first implementation increment

Added the recovery snapshot rehearsal to CI immediately after the
multi-design pilot. Every release now copies the generated evidence tree,
restores it into a clean root, and compares file inventories and SHA-256
digests before continuing to packaging and deployment gates.

Validation: pilot execution, recovery rehearsal, and workflow documentation
tests pass; the current rehearsal matched all four pilot evidence files.

## One-hundred-sixtieth implementation increment

Added `scripts/verify_recovery_snapshot.py`, a deterministic pilot recovery
rehearsal that copies the artifact root into a snapshot and restored root,
then compares every file digest, including SQLite, job evidence, collateral,
and bundles. The recovery runbook now includes the command and clearly
separates this local rehearsal from the required managed multi-pod drill.

Validation: recovery snapshot contract test passes with matching inventories
and content digests.

## One-hundred-fifty-ninth implementation increment

Reconciled the production checklist with the authenticated platform contract:
the versioned workflow, job kinds, evidence guarantees, and claim boundaries
are now an explicit verified release item rather than an undocumented API
detail.

Validation: handoff documentation and API health/contract tests pass (`20
passed`).

## One-hundred-fifty-eighth implementation increment

Added HTTP-level authorization coverage for `/v1/contract`. The contract is
available to authorized integrations with its version and claim boundaries,
while unauthenticated requests receive 401 and responses remain non-cacheable.

Validation: complete service/platform suite passes (`168 passed`) with the
existing dependency deprecation warning only.

## One-hundred-fifty-seventh implementation increment

Extended Prometheus output with readiness and per-adapter availability gauges.
Operators can now alert on an unready service or a blocked configured
simulator/formal adapter before users submit verification work, while adapter
labels remain bounded to the validated name/kind contract.

Validation: health metrics tests pass with an unavailable adapter and a ready
service, alongside the existing request, duration, and queue metrics.

## One-hundred-fifty-sixth implementation increment

Connected run setup now fetches and displays the service contract version
(`verification-platform-contract-v1`) beside tool and customer-adapter
capabilities. The engineer sees API compatibility before selecting immutable
inputs or queuing work; contract discovery failures keep setup in its existing
recoverable error state.

Validation: JavaScript syntax and the real-service setup journey pass with
contract-version and adapter-capability assertions.

## One-hundred-fifty-fifth implementation increment

Added the authenticated `/v1/contract` endpoint. Integrations can now
discover the versioned workflow, supported job kinds, evidence guarantees,
storage contract, and explicit claim boundaries without scraping UI or prose.
This gives customer adapters and future managed services a stable discovery
surface while preserving the open-source pilot semantics.

Validation: platform contract and complete service/platform tests pass
(`166 passed`).

## One-hundred-fifty-fourth implementation increment

Readiness now reports identity enforcement mode: `api-key-pilot` or
`oidc-subject-required`, plus a boolean `identity_subject_required`. Operators
can therefore detect whether the deployment is using the intended enterprise
signoff boundary before sending it traffic.

Validation: health/readiness tests cover both modes; rendered deployment
preflight remains green.

## One-hundred-fifty-third implementation increment

Added enforcement coverage for identity-bound signoff. When
`VERIFICATION_REQUIRE_IDENTITY_SUBJECT=true`, approval without a trusted
identity subject returns 403; a receipt carrying the subject verifies and
retains it. This tests the production ingress contract while leaving the
open-source pilot's default behavior unchanged.

Validation: verification-service and signoff tests pass, including missing-
subject rejection and subject-bound receipt integrity.

## One-hundred-fifty-second implementation increment

Extended hash-bound signoff receipts with an optional identity-provider
subject. Identity-aware ingress can supply `X-Identity-Subject`, and
production deployments can set `VERIFICATION_REQUIRE_IDENTITY_SUBJECT=true`
to reject approvals without that trusted binding. The pilot default remains
backward compatible, while the migration plan now names the exact enforcement
boundary.

Validation: signoff and verification-service tests pass, including receipt
integrity with a reviewer subject.

## One-hundred-fifty-first implementation increment

Expanded connected run setup capability text to include each customer
adapter's kind and non-secret engine version alongside its available/blocked
state. This lets an engineer identify the intended simulator/formal/coverage
backend and detect an incompatible version before queuing work.

Validation: JavaScript syntax and the real-service setup journey pass with the
adapter identity, kind, version, and availability visible.

## One-hundred-fiftieth implementation increment

Readiness now validates customer adapter configuration in addition to the
evidence-store provider. Malformed `VERIFICATION_EDA_ADAPTERS` configuration
reports `adapter_config: invalid` and makes `/readyz` return `not-ready`,
matching the capabilities endpoint instead of allowing a misconfigured pod to
receive traffic.

Validation: health tests and rendered deployment preflight pass.

## One-hundred-forty-ninth implementation increment

Reconciled the production checklist with the implemented deployment controls:
service-account suppression, capability dropping, privilege and seccomp
hardening, read-only roots, DNS-only egress, provider contracts, and adapter
availability discovery are now explicit verified items. Enterprise state,
identity, isolation, operations, recovery, customer adapters, and signed pilot
requirements remain unchecked as required.

## One-hundred-forty-eighth implementation increment

Removed the unexplained numeric AI confidence claim from the sample diagnosis
surface. The workbench now labels the result `Assessment: review required`,
which matches the evidence-first human review boundary. Browser smoke asserts
the wording alongside the existing sample/live separation checks.

Validation: JavaScript syntax and browser acceptance passed with no page
errors.

## One-hundred-forty-seventh implementation increment

Added `Cache-Control: no-store` to service responses so authenticated
verification evidence, audit exports, bundles, and signoff data cannot be
retained by browser or intermediary caches. Health, authorization, and audit
route tests enforce the header.

Validation: focused health and verification-service tests pass (`20 passed`),
with the existing dependency deprecation warning only.

## One-hundred-forty-sixth implementation increment

Made API and worker container roots read-only in the Kubernetes profile and
provided an explicit `/tmp` `emptyDir` for tool scratch data. Preflight and
manifest tests enforce both mounts and the read-only setting, while durable
evidence remains on the dedicated artifact volume.

Validation: Kubernetes manifest and release-preflight tests pass; rendered
deployment preflight passes.

## One-hundred-forty-fifth implementation increment

Required the Kubernetes `RuntimeDefault` seccomp profile for the verification
pod. The security context, deployment preflight, and manifest tests now enforce
the runtime sandbox alongside non-root execution, capability dropping, and
privilege-escalation prevention.

Validation: Kubernetes manifest and release-preflight tests pass; rendered
deployment preflight passes.

## One-hundred-forty-fourth implementation increment

Hardened the Kubernetes pod security profile: service-account token
automounting is disabled, both API and worker containers forbid privilege
escalation, and all Linux capabilities are dropped. Deployment preflight and
manifest tests enforce these controls so a release cannot silently regress to
the container runtime defaults.

Validation: Kubernetes manifest and release-preflight tests pass; rendered
deployment preflight passes.

## One-hundred-forty-third implementation increment

Added a Kubernetes egress NetworkPolicy for the pilot deployment. API and
worker pods are default-denied for outbound traffic except cluster DNS;
customer adapter endpoints must be opened with a deployment-specific narrow
rule. Deployment preflight now requires the policy, and the Kubernetes tests
assert its DNS-only ports.

Validation: Kubernetes manifest and release-preflight tests pass; rendered
deployment preflight passes.

## One-hundred-forty-second implementation increment

Closed the scorecard evidence loop with
`scripts/verify_pilot_scorecard_evidence.py`. It validates every referenced
file path and recomputes its SHA-256, rejecting traversal, missing files, and
tampered content. CI and the release-evidence instructions now run this
check after generating the open-source draft scorecard.

Validation: tamper and path-boundary tests pass, and the current generated
scorecard verifies against the multi-design pilot ledger.

## One-hundred-forty-first implementation increment

Bound the generated open-source pilot scorecard to the exact evidence files:
the scorecard now carries SHA-256 digests for the pilot summary, session
ledger, and release manifest. The validator checks digest shape, while the
generator leaves unsupported human metrics empty. A changed ledger therefore
cannot be mistaken for the scorecard that was reviewed.

Validation: scorecard generator, validator, and handoff documentation tests
pass; the regenerated draft artifact validates successfully.

## One-hundred-fortieth implementation increment

Added scorecard regeneration to the release workflow. CI now runs the
multi-design pilot, builds `.artifacts/open-source-pilot-scorecard.json` from
its current ledger, validates the scorecard, and uploads it with release
provenance. This keeps the open-source proof-of-value artifact reproducible
and prevents draft metrics from being mistaken for a signed customer study.

Validation: the workflow documentation test, pilot scorecard test, pilot
execution, and scorecard validator all passed.

## One-hundred-thirty-ninth implementation increment

Added `scripts/build_open_source_pilot_scorecard.py`, which derives a draft
proof-of-value scorecard from the multi-design pilot ledger and summary. It
populates only metrics directly supported by immutable evidence
(evidence-completeness and closure-integrity) and leaves latency, usefulness,
reproduction, and manual-effort fields empty until a human baseline study is
run. The generated artifact is validated by the existing scorecard contract
and explicitly states its claim boundary.

Validation: generated `.artifacts/open-source-pilot-scorecard.json` passes
scorecard validation; the generator contract test passes.

## One-hundred-thirty-eighth implementation increment

Connected run setup now presents registered customer EDA adapters alongside
the open-source tool capabilities, including an explicit `available` or
`blocked` state before submission. The real-service setup check registers a
pilot adapter, verifies it is visible to the engineer, and still queues a run
with immutable RTL/checker identities.

Validation: JavaScript syntax and the real-service setup journey passed with
no page errors.

## One-hundred-thirty-seventh implementation increment

Added a validated customer EDA adapter registry. Deployments can declare
non-secret adapter metadata through `VERIFICATION_EDA_ADAPTERS`; the
capabilities endpoint reports each executable as available or blocked, while
malformed configuration returns an explicit service-unavailable error. The
registry does not accept credentials or filesystem executable paths.

Validation: adapter registry and capability health tests pass, including
available/blocked discovery, duplicate and unsafe configuration rejection, and
the empty-registry pilot default.

## One-hundred-thirty-sixth implementation increment

Readiness now reports the active evidence-store provider and
`evidence-store-v1` contract. The pilot advertises `filesystem-pilot`; an
unimplemented managed provider is explicitly reported as not-ready instead
of appearing healthy. This gives deployment probes an authoritative signal
for the storage migration boundary.

Validation: focused health and evidence-store tests passed; the complete
service/platform suite is green with `154 passed` and one existing dependency
deprecation warning.

## One-hundred-thirty-fifth implementation increment

Defined and tested the provider-neutral evidence storage boundary in
`deployment/evidence_store.py`. The pilot filesystem implementation now has
the same logical-key, immutable-content, and SHA-256 semantics required of a
future managed object-store provider; traversal, absolute paths, duplicate
separators, and backslash keys are rejected. This advances the production
migration seam without claiming that managed PostgreSQL or object storage is
already deployed.

Validation: eight evidence-store contract tests passed, including idempotent
writes, content hashing, retrieval, existence, and path-boundary rejection.

## One-hundred-thirty-first implementation increment

Strengthened `/readyz` to verify artifact persistence, not only queue access:
it performs a temporary write/delete probe on the configured evidence volume
and reports `storage: ready` or `unavailable`. Kubernetes therefore keeps a
pod out of service when it cannot persist verification evidence. Health
coverage passes (`5 passed`) and the combined backend suite remains green
(`144 passed`).

## One-hundred-thirty-second implementation increment

Added the negative readiness contract: when the configured artifact parent is
not writable, `/readyz` reports `status: not-ready` and `storage: unavailable`.
Health/readiness tests now pass (`6 passed`), and the full combined backend
suite remains green (`145 passed`).

## One-hundred-twenty-ninth implementation increment

Revalidated the current commercial pilot release serially after the audit,
CSP, adapter, provenance, and CI changes: the combined backend suite passes
(`144 passed` with the known dependency warning), the browser smoke has no
page errors, the adversarial judge reports `gate_passed: true` across seven
scenarios, and the Kubernetes deployment preflight renders successfully.

## One-hundred-twenty-eighth implementation increment

Added HTTP-level authorization coverage for project audit export. A valid API
key plus scoped project key returns the digest-bearing audit payload, while a
wrong project key returns `403` with the supplied request ID. The service test
suite passes (`13 passed`) and the combined backend baseline remains green
(`144 passed`).

## One-hundred-twenty-seventh implementation increment

Made release provenance explicit in the commercial handoff. It now names the
CI artifact `verification-pilot-release-provenance` and describes its image
digest, source revision/dirty state, base-image pin, runtime UID, and gate
commands. Handoff-document tests pass (`8 passed`), preventing a reviewer from
mistaking an untracked local image for the released package.

## One-hundred-twenty-fifth implementation increment

Added a same-origin Content-Security-Policy to API and workbench responses,
with explicit HTTP/HTTPS connect origins for configured service APIs,
`frame-ancestors 'none'`, and self-only scripts. Successful and rejected auth
responses both carry the policy; health/header tests pass (`4 passed`), the
browser smoke has no page errors, and the combined backend suite remains green
(`142 passed`).

## One-hundred-twenty-sixth implementation increment

Extended browser-policy coverage to the served workbench HTML itself. The
service test now verifies a successful `/workbench/verification-workbench.html`
response carries self-only scripts, frame denial, and the CSP; the health
suite passes (`5 passed`) and browser acceptance remains free of page errors.

## One-hundred-twenty-third implementation increment

Made clean-source provenance an actual CI gate. After generating the release
manifest, the workflow now fails if `source_tree_dirty` is true and uploads the
manifest only after that assertion passes. Workflow parsing and handoff
contract tests pass (`8 passed`), preventing a locally modified tree from
being presented as a clean commercial release.

## One-hundred-twenty-first implementation increment

Added provenance command redaction for common secret-bearing adapter flags and
`KEY=value` forms. The subprocess still receives the original arguments, while
stored `ToolRun` commands replace secret values with `[REDACTED]`. Adapter and
runner tests pass (`11 passed`), and the full combined backend suite remains
green (`142 passed`). The customer adapter guide documents the redaction
boundary and secret-manager recommendation.

## One-hundred-twenty-fourth implementation increment

Hardened the project audit export redaction boundary: path-like substrings in
adapter reasons are replaced with `[PATH]` and reason text is capped at 500
characters, while raw path fields remain excluded. Regression coverage proves
the sensitive path is removed; the combined backend suite passes (`142
passed`).

## One-hundred-twenty-second implementation increment

Release provenance now records `source_tree_dirty`, a bounded list of changed
paths, and a truncation flag in addition to the commit revision. This prevents
an image containing local edits from being mistaken for a clean commit build
while keeping the manifest bounded; generation succeeds against the pinned
image and the deployment README documents the behavior.

## One-hundred-seventeenth implementation increment

Added a canonical `export_sha256` to every bounded project audit response. The
digest covers exactly the returned entries, allowing exported audit JSON to be
verified after transfer; tests confirm it is 64 hex characters and changes
when the audit content changes. The service suite passes (`12 passed`) and the
combined backend baseline remains green (`139 passed`).

## One-hundred-sixteenth implementation increment

Completed the Prometheus latency contract with explicit request-duration
counts alongside duration sums for each bounded HTTP response class. Operators
can now compute average latency without inferring denominators from a separate
counter; health/metrics coverage and the combined backend suite remain green
(`139 passed`).

## One-hundred-thirteenth implementation increment

Carried project audit export into the Reports UX. Connected projects now get
an `Export audit` action that requests the bounded project endpoint and
downloads JSON named for the project; sample mode explains that a connected
project is required. The first DOM insertion exposed a hydration-order issue,
which was corrected by appending to the resolved report-action container. Node
syntax, browser acceptance, and service/handoff tests pass with no page errors.

## One-hundred-tenth implementation increment

Closed the CI provenance loop: the verification-pilot workflow now generates
the release manifest after image smoke and uploads it as the
`verification-pilot-release-provenance` artifact. The workflow parse check and
handoff documentation suite pass (`8 passed`), and a local pinned-image run
wrote a non-empty `.artifacts/verification-release-manifest.json`.

## One-hundred-nineteenth implementation increment

Closed an adapter workspace-escape gap. `run_command()` now validates every
expected artifact as a non-empty relative path contained within the run root
before launching a customer tool; absolute and traversal paths are rejected.
Adapter and runner regressions pass (`9 passed`), and the combined backend
suite remains green (`140 passed`). The customer adapter guide documents this
containment contract.

## One-hundred-twentieth implementation increment

Bounded customer-tool logs at the common runner boundary. Standard output and
error are capped at 2 MiB per stream with explicit truncation metadata in the
`ToolRun`; timeout and normal completion paths use the same limit. Noisy-tool
and adapter regressions pass (`10 passed`), and the combined backend suite
remains green (`141 passed`). The customer adapter guide now states the bound.

## One-hundred-fifteenth implementation increment

Added bounded Prometheus request-duration sums by response class alongside the
existing response counters and request-ID generation metric. This gives the
operator a latency signal for SLO work while retaining low-cardinality labels;
health coverage asserts the new exposition and the combined backend suite
remains green (`139 passed`).

## One-hundred-thirty-fourth implementation increment

Added a persistent current-context strip to the workbench. Project identity,
selected run, evidence freshness, and the next useful action stay visible as
the engineer moves between overview, sources, runs, investigation, coverage,
and reports. The strip is responsive and uses live URL/state values, so it
cannot imply that sample evidence belongs to a connected project.

Validation: JavaScript syntax checks and browser smoke passed, including the
sample-mode context assertions and existing stale-response, evidence, mobile,
recovery, and authorization scenarios.

## Cross-cutting commercial-goal verification

The accumulated open-source workbench now passes a full integration gate:
`git diff --check`, the combined backend and deployment suite (`172 passed`),
browser acceptance (including stale-response, project-isolation, recovery,
waveform/source inspection, audit export, and malicious-rendering cases), the
seven-scenario adversarial LLM judge, and Kubernetes deployment preflight.
This establishes a reproducible, reviewable beta baseline for the end-to-end
verification workflow. Enterprise production readiness still requires the
managed infrastructure, identity/RBAC, isolation, centralized observability,
recovery/key-rotation, real EDA adapters, and signed customer pilot gates
listed above.

## Structured run-list rendering

The durable run list now renders job IDs, kinds, statuses, and timestamps with
DOM text nodes and typed attributes. This removes the remaining unsafe run-list
HTML interpolation path while preserving empty-state, bounded-list, and
selection behavior. JavaScript syntax validation and browser acceptance pass
after the change.

## Project-key enforcement for job APIs

Project-key enforcement now covers filtered job listings and every persisted
job endpoint. The API middleware resolves a job's stored project owner before
dispatch, preventing a caller with another project's key from reading or
mutating a run by guessing its ID. Regression coverage exercises both allowed
and denied listing/detail requests; the combined suite passes (`173 passed`).

Job submission now enforces the same project key when the project ID arrives in
the JSON body of `POST /v1/jobs`. The request middleware carries the scoped
header into the body-bound route, while direct deterministic service calls
remain usable for pilot tests. HTTP regression coverage verifies that the
owner key can submit work and another project's key receives `403`.

## Trusted reviewer identity on HTTP signoff

HTTP signoff now treats `X-Identity-Subject` as the authoritative reviewer
identity whenever identity enforcement is enabled. A body-supplied
`reviewer_subject` cannot spoof that identity; missing headers receive `403`,
and signed receipts retain the trusted subject. Regression coverage exercises
spoofed, missing, and trusted HTTP signoff requests.

When `VERIFICATION_REQUIRE_IDENTITY_SUBJECT=true`, project creation now also
requires a trusted `X-Identity-Subject`. This prevents API-key-only callers
from creating tenant projects in the identity-enforced deployment profile,
while direct pilot service calls and the default API-key profile remain
compatible. The full backend/deployment suite passes (`174 passed`).

## Deployable pilot observability overlay

Added `deployment/observability/prometheus.yml` and an optional Compose
overlay that scrapes the service's `/metrics/prometheus` contract with bounded
retention. The deployment README now gives the reproducible startup command
and links the dashboard specification to the scrape target. Configuration and
handoff tests pass, and the full backend/deployment suite passes (`175
passed`). Managed alert routing, access control, and retention remain open
customer-production gates.

The Kubernetes release preflight now requires the Prometheus scrape
configuration and Compose observability overlay alongside the dashboard
contract. `preflight_verification_deployment.py --render` and the release
preflight/observability tests pass, so the pilot handoff cannot omit the
operational monitoring artifacts.

The CI workflow now runs `docker compose config --quiet` against the same
observability overlay with a disposable API key. The overlay was validated as
an executable Compose configuration, and handoff tests assert that this check
remains present.

## Hardened per-job workspaces

Before API or worker execution, each job workspace is now created with owner
only permissions (`0700`) and symlink roots are rejected. This strengthens the
open-source isolation boundary for simulator, formal, and adapter artifacts;
the regression test verifies both the mode and symlink rejection. The full
backend/deployment suite passes (`176 passed`).

The common adapter runner now applies the same workspace boundary to direct
customer-tool invocations: arbitrary run roots are owner-only (`0700`) and
symlinked roots are rejected before `Popen`. Runner, worker, and service
regressions cover the guard; the full suite passes (`177 passed`).

Worker exception handling now persists a bounded, path-redacted error and a
durable `worker_exception` event before finishing a job as failed. This keeps
adapter/workspace failures explainable to the workbench and audit export while
preventing host-path leakage. Worker regression coverage and the full suite
pass (`178 passed`).

Comparison requests now authenticate both persisted job owners. A baseline and
retest from different projects are rejected before comparison data is read,
closing a multi-run tenant-isolation edge. Regression coverage verifies the
cross-project denial and the full suite remains green (`178 passed`).

Project discovery is now scoped as well. With `VERIFICATION_PROJECT_KEYS`
configured, `GET /v1/projects` requires a valid project key and returns only
the projects mapped to that key, preventing project-ID enumeration through the
connection flow. Isolation regression coverage includes discovery, submission,
job access, and comparison.

Cancellation now performs the durable queue compare-and-set before changing
the JSON job record. A worker claim therefore wins cleanly, returning `409` to
the cancellation request; the API cannot overwrite a running job as cancelled.
The race regression and full backend/deployment suite pass (`179 passed`).

## Rendered UX audit: failed-project recovery

A current Playwright capture exposed stale sample identity in the breadcrumb
after an unauthorized live-project response. The recovery path now replaces
that breadcrumb with the requested project ID, keeping the header, context
strip, and connection state consistent. The accepted screenshot and findings
are recorded in `docs/evaluations/verification-workbench-ux-audit-2026-09-10.md`;
browser acceptance remains green.

The same rendered audit found that a live project with no uploaded RTL left
the primary run button looking enabled even though execution was blocked. A
disabled-action style now communicates the unavailable state, and the accepted
connected-empty-project screenshot is included in the UX audit artifact.

The adversarial judge, browser acceptance suite, and Kubernetes deployment
preflight were rerun after the isolation and worker-boundary changes. All
three pass together, covering rendering, recovery, project scoping, and
deployment contract behavior in the current beta evidence.

The full pilot handoff chain was rerun: recovery matched all four files, the
evidence-backed scorecard validated, production readiness reported 20 verified
and 8 open controls, and the 12-artifact commercial handoff manifest verified
its own digests. It correctly records `customer_production_ready: false` until
the managed infrastructure and signed pilot gates are closed.

Live project discovery and dashboard hydration now send bounded request
correlation IDs from the workbench. This makes the first customer-facing
connection failures traceable to service logs without exposing credentials;
the remaining direct artifact/report calls inherit the same contract through
the setup workflow.

Customer-production configuration now fails closed at readiness. The new
provider-neutral contract requires managed PostgreSQL state, object storage,
trusted identity subjects, isolated execution, centralized observability, and
backup declarations when `VERIFICATION_DEPLOYMENT_TIER=customer-production`.
Tests prove both rejection of an incomplete declaration and the separate
failure of a declared but unimplemented object-store provider. This turns the
production migration checklist into an executable safety boundary while
preserving the local pilot tier.

The production-configuration increment leaves the full deployment and
verification-platform suites green at `181 passed` (111 deployment, 70
verification-platform).

CI now generates the execution-sandbox probe and reference adapter acceptance
summary before building and verifying the commercial handoff manifest, and
uploads both artifacts with release provenance. This prevents a clean checkout
from claiming a handoff whose required evidence was never produced.

Post-apply runtime smoke can now accept `--sandbox-probe`; when enabled it
requires the live namespace capability result in addition to readiness,
contract, and Prometheus checks. The negative validation path is covered, and
the full-suite evidence target is now `234` tests (`160` deployment, `74`
verification-platform).

An executable Kubernetes customer-production overlay now consumes externally
managed ConfigMap and Secret objects, enables the production tier and OIDC /
object-store settings, and includes the backup CronJob. Its rendered output
was verified with `kubectl kustomize --load-restrictor LoadRestrictionsNone`;
the pilot base remains unchanged. Applying real managed resources is still a
deployment gate.

The Kubernetes deployment now includes a non-secret production configuration
example covering identity, reviewer role, object storage, observability, DR,
and execution-isolation declarations, plus the out-of-band database Secret
shape. It is intentionally excluded from the base pilot kustomization. The
full-suite evidence is `218` tests (146 deployment, 72 verification-platform).

The machine-readable `/v1/contract` now publishes execution-safety guarantees
and explicitly names the remaining per-job namespace and read-only source-mount
requirements. Integrations can preflight these boundaries before submitting
work; customer deployment still must provide and verify those controls.

The reference runner now audits the completed workspace for symlink entries
and marks the run blocked when one is present, preventing unsafe links from
being hashed or published as evidence. This complements owner-only workspace
permissions and process limits; true per-job namespaces and read-only source
mounts remain deployment gates. Current evidence is `217` tests (145
deployment, 72 verification-platform).

Customer-production configuration now requires explicit `disposable`
workspaces and `deny-by-default` execution network policy declarations. The
Kubernetes profile carries these settings alongside its DNS-only egress policy,
making the intended isolation boundary reviewable before a production overlay
is selected. Actual per-job namespaces and source-mount enforcement remain
deployment gates; current evidence is `216` tests (145 deployment, 71
verification-platform).

Backup freshness is now observable: the service exports the last successful
backup timestamp, current age, and declared RPO, while the alert policy fires
when age exceeds twice the RPO. The dashboard includes matching age and RPO
panels. Provider-native backup scheduling and managed alert routing remain
production gates; current evidence is `216` tests (145 deployment, 71
verification-platform).

The Prometheus rule set now also includes the dashboard's five-second average
latency SLO, keeping alert coverage aligned across readiness, errors, backlog,
adapters, and identity rotation. Focused observability checks pass; managed
alert routing and escalation remain deployment operations gates.

Queue monitoring now exports `verification_queue_capacity` and compares queued
work against that live configured gauge in both the alert rule and dashboard.
This removes fixed-threshold drift when deployments change
`VERIFICATION_MAX_QUEUED_JOBS`; the current handoff evidence target is `215`
tests (144 deployment, 71 verification-platform).

Provider-neutral Prometheus alert rules now ship with the observability
overlay. They cover readiness loss, sustained HTTP 5xx responses, unknown OIDC
signing keys, and an empty JWKS cache, with runbook references where relevant.
The full-suite evidence target is `215` tests (144 deployment, 71
verification-platform); managed alert routing and on-call ownership remain
production operations gates.

The observability alert policy now includes a sustained queue-backlog alert at
the default 32-job capacity, aligned with the dashboard threshold and the
service's configured queue limit. Focused observability checks pass; managed
alert routing and per-deployment threshold templating remain operational work.

The observability dashboard now includes OIDC JWKS refresh, unknown-key, and
cached-signing-key panels aligned with the alert rules and Prometheus export.
This makes key-rotation behavior visible to an operator during a pilot
rehearsal; managed dashboard access, retention, and alert routing remain
production operations gates.

Customer-production identity configuration now requires both issuer and JWKS
endpoints to use HTTPS, closing the last transport ambiguity in the OIDC
contract. Readiness regression coverage passes; the full-suite evidence target
is `214` tests (143 deployment, 71 verification-platform).

An API-level integration test now proves that a validated bearer token supplies
the subject and roles consumed by project routes, while requests without the
required token are rejected before route execution. The full-suite evidence
target is now `213` tests (142 deployment, 71 verification-platform).

OIDC verification now requires an HTTPS JWKS endpoint in customer-production
configuration and refreshes the cached key set when a new signing key ID is
encountered. Rotation and transport validation are covered by regression tests;
provider key-rotation runbooks and alerting remain operational gates. The next
full-suite evidence target is `212` tests (141 deployment, 71
verification-platform).

Project-to-identity subject allowlists are now enforced at the HTTP project
boundary and job-submission boundary, rejecting cross-tenant reads and runs
before execution. Compose and the environment template expose the mapping for
pilot rehearsal. The next full-suite evidence target is `209` tests (138
deployment, 71 verification-platform); an external tenant directory and
administrative RBAC lifecycle remain production gates.

The deployment contract is now wired through Compose and `.env.example` for
both API and worker, with a handoff test checking the required tier, storage,
and sandbox variables. `docker compose config --quiet` passes with a
disposable pilot key, so the promotion path is inspectable before any runtime
is started.

The evidence-store reference now enforces its immutable-object promise: a
logical key accepts identical bytes idempotently, rejects changed bytes even
with `overwrite=true`, and rejects symlink targets. This protects report and
signoff digests in the pilot and gives a managed object-store implementation a
precise integrity behavior to preserve.

The managed-state contract tests and route metadata bring the current full
suite to `188 passed` (118 deployment, 70 verification-platform). The
commercial handoff count is updated to this collected total.

The migration runner was exercised against a disposable PostgreSQL 16
instance. It applied all six statements, verified all four tables and both
indexes, emitted a redacted DSN, and returned `verified: true`. The instance
was removed after the proof; application cutover and backup/restore evidence
remain open production gates.

The migration runner regression brings the current full suite to `189 passed`
(119 deployment, 70 verification-platform), and the handoff count now matches
that collected total.

The first real managed repository, `deployment/postgres_job_queue.py`, now
implements the durable queue contract with PostgreSQL transactions,
`FOR UPDATE SKIP LOCKED` claims, stale-job recovery, and compare-and-set
terminal transitions. It is intentionally opt-in until project and collateral
repositories move together, avoiding a split API/worker backend. A surface
regression confirms parity with the pilot queue methods.

The queue was exercised against disposable PostgreSQL 16 at runtime: a
project was seeded, one job was claimed and finished, a second was cancelled,
and the final durable counts matched `passed=1, cancelled=1`. The disposable
database was removed after the proof. The complete suites now pass at `190`
tests (120 deployment, 70 verification-platform).

Project and collateral repository implementations now share the managed
PostgreSQL schema with the queue. They preserve project creation/list/get,
content-addressed collateral metadata, local object-key compatibility, and
immutability checks while remaining opt-in until the service can switch all
repositories atomically. Surface tests confirm parity with the pilot APIs.

The integrity regression leaves the complete suites green at `182 passed`
(112 deployment, 70 verification-platform), with the commercial handoff
counts updated to match the collected tests.

The managed-state migration now has an executable schema contract in
`deployment/managed_state_contract.py`. It validates PostgreSQL DSNs without
leaking credentials and emits the project, collateral, job, event, foreign
key, and queue-index statements needed to preserve the pilot's durable
semantics. This is a migration preflight, not a claim that PostgreSQL is
already wired into the service; provider implementation and restart/restore
evidence remain open.

The shared repository path was exercised against disposable PostgreSQL 16:
project creation/listing, collateral add/get/list, queue claim, and terminal
completion all succeeded in one database. The database was removed after the
proof. The complete suites now pass at `191` tests (121 deployment, 70
verification-platform), and the handoff count matches that collected total.

The evidence boundary now includes an S3-compatible `S3EvidenceStore` with
conditional first-write semantics, idempotent identical writes, digest-based
conflict rejection, and injected-client tests. It is ready as a provider seam;
bucket versioning, retention, encryption, IAM, and service-wide object-store
cutover remain explicit production gates.

Evidence bundles now cross the provider boundary. `get_bundle` creates a
stable local ZIP for download, stores the exact bytes through the atomic
filesystem/S3 evidence provider, and returns a logical object key plus
`bundle_sha256`. Existing bundle requests reuse the ZIP, preserving immutable
idempotency. Execution, repair, full backend, and browser suites pass after
the change; service-wide artifact writes and managed bucket operations remain
open production work.

Evidence inspection now materializes missing result files and waveforms from
provider keys before parsing bounded forensic context. A regression deletes a
simulation result locally and verifies transparent recovery through the API;
the full backend and browser suites remain green. Full artifact namespace
migration, remote-only downloads, and managed restore drills remain open.

Completed run outputs and logs now publish through `_publish_job_artifacts` in
both API and worker execution. Job metadata records each logical provider key,
byte count, and SHA-256 while local files remain available for current
downloads and adapters. The browser and full backend suites pass after this
user-visible evidence change; remote materialization and managed retention are
still open.

The S3 provider regression brings the complete suites to `193 passed` (123
deployment, 70 verification-platform), and the commercial handoff count is
updated to match.

The atomic `repository_factory.py` is now integrated into the service and
worker. With the customer-production tier and managed declarations set, both
processes resolve one PostgreSQL-backed queue/project/collateral bundle; with
the pilot tier they resolve the existing SQLite bundle. A disposable
PostgreSQL 16 runtime proof exercised the production factory end to end, and
the full suites now pass at `192` tests (122 deployment, 70
verification-platform). The factory remains opt-in until object storage and
the remaining production providers are implemented.

PostgreSQL collateral uploads now dual-write through the selected evidence
provider while retaining an execution materialization. Returned records keep
the managed `object_key` and compatible local `path` separately. A disposable
PostgreSQL 16 proof verified the project, collateral, managed write, and path
contract together; the complete suites now pass at `194` tests (124
deployment, 70 verification-platform).

The S3 evidence provider now exposes `control_probe()`, independently
checking bucket versioning, server-side encryption, and retention lifecycle.
The injected-client regression passes, and readiness/handoff artifacts were
refreshed. Actual cloud bucket policy and IAM evidence remain customer
deployment gates.

The managed evidence control probe now requires object-lock/WORM enablement in
addition to versioning, encryption, and lifecycle retention, and reports the
result explicitly. The injected-provider test covers the complete control
contract; provider-specific IAM and retention policy deployment remain open.

The latest end-to-end release rehearsal also passed browser UX smoke,
real-service setup, reviewer handoff/reload/project-switch flow, and all seven
adversarial judge scenarios with no page errors. These checks cover the user
journey from authenticated setup through evidence review and sign-off; they do
not substitute for a signed customer pilot.

The deployment package now includes a post-apply runtime smoke gate that checks
managed readiness, the versioned execution-safety contract, and backup/queue
metrics through the live endpoint while suppressing credentials in its output.
The complete suite is `223` tests (151 deployment, 72 verification-platform).

The semantic customer-production preflight now has negative tests for missing
Deployment/CronJob wiring and credential-bearing renders. The production
backup CronJob's database Secret reference was also corrected to match the
out-of-band Secret shape. The complete suite is now `221` tests (149
deployment, 72 verification-platform).

The production overlay semantic preflight now checks the complete readiness
variable set, including issuer/audience/JWKS, reviewer role, isolation policy,
observability endpoint, backup policy, and DR targets. A rendered overlay with
any missing wiring fails before cluster apply; the real external resources and
values remain deployment gates.

The current deployment promotion checks now pass together: base Compose
configuration, observability Compose configuration, production Kustomize
render, and semantic customer-production preflight all returned success. This
confirms the release artifacts compose cleanly before any external cluster,
database, object store, or identity credentials are supplied.

CI now runs `preflight_customer_production_overlay.py` after rendering the
production Kustomize overlay. The semantic gate verifies customer-production
tier, bearer-token enforcement, external ConfigMap/Secret references, backup
wiring, and absence of credential material, closing the gap between YAML
assembly and a reviewable promotion artifact.

The combined managed restore drill was exercised against disposable PostgreSQL
16 plus a temporary evidence tree. It verified live project/job table access
and byte-for-byte evidence snapshot restoration, emitted a redacted DSN, and
returned `verified: true`; the disposable database and files were removed.
Provider-native database backup/failover evidence remains open. The full suite
now passes at `196` tests (126 deployment, 70 verification-platform).

The credential-safe PostgreSQL backup helper is implemented and tested for
password isolation. A native runtime attempt correctly failed closed because
the host `pg_dump` 14 client was older than the PostgreSQL 16 server; the
production backup gate remains open until matching-version dump/restore tools
are used. The full suite now passes at `197` tests (127 deployment, 70
verification-platform).

The authenticated `/v1/storage/controls` endpoint now exposes the evidence
provider control probe. Pilot responses explicitly state that local storage
has no managed versioning, encryption, or retention policy; object-store mode
returns the live S3-compatible probe. Full backend and deployment preflight
checks pass at `195` tests (125 deployment, 70 verification-platform).

Customer-production readiness now executes the object-store control probe and
requires it to pass before reporting `ready`; environment declarations alone
cannot bypass missing versioning, encryption, or retention. Pilot readiness
continues to report its local-storage claim boundary explicitly.

Customer-production configuration now validates a measurable DR contract:
`daily-Nd` retention with at least seven days and explicit RPO/RTO targets
bounded to 1..1440 minutes. Missing or malformed targets keep readiness
unready. The full suites pass at `198` tests (128 deployment, 70
verification-platform).

The matching PostgreSQL 16 client path was then exercised inside the running
PostgreSQL 16 container: a source database with project/job rows was dumped,
restored into a separate target database, and both rows were verified before
both temporary databases were dropped. The host-side helper still correctly
rejects mismatched client/server versions; provider-native backup evidence is
now proven for the matching-tool path, while production scheduling, retention,
and failover policy remain open.

`run_scheduled_backup.py` now turns the validated DR policy into one concrete
operation: policy and client/server compatibility preflight, timestamped
custom-format dump, and atomic SHA-256 manifest publication. Targeted tests
pass; a scheduler, managed retention target, and production failover process
still need deployment integration.

The Kubernetes production overlay now schedules the policy-validated backup
hourly with `Forbid` concurrency, bounded history, retries, secret-backed DSN,
and non-root/read-only execution. YAML tests and deployment preflight pass;
managed retention routing and failover orchestration remain open. The full
suite is green at `202` tests (132 deployment, 70 verification-platform).

The scheduled-backup increment brings the complete suite to `201` tests (131
deployment, 70 verification-platform), with the commercial handoff count
updated to match.

The backup policy module now validates a five-field cron schedule and checks
PostgreSQL client/server major compatibility before dump execution. The full
suites pass at `200` tests (130 deployment, 70 verification-platform), and
the handoff count matches the collected total.

The scheduled backup runner now optionally publishes each custom-format dump
to the configured immutable evidence provider under a logical `backups/` key,
recording the provider object key and SHA-256 alongside the local manifest.
The production Kubernetes overlay passes the managed evidence bucket into the
runner. The full suite passes at `203` tests (133 deployment, 70
verification-platform); provider-native retention, key rotation, and failover
operations remain deployment gates.

The reference execution runner now applies POSIX child CPU-time and
per-file-size limits in addition to process-group timeout cleanup, and records
the applied limits in the provenance ledger. Targeted runner and handoff tests
pass; the complete suite is now `204` tests (133 deployment, 71
verification-platform). Container-per-job namespaces, network policy, and
tenant-level execution isolation remain production deployment gates.

The identity boundary now includes an explicit configured reviewer role. In
identity-required mode, HTTP sign-off accepts only a trusted subject whose
`X-Identity-Roles` assertion contains `VERIFICATION_REVIEWER_ROLE`; customer
production readiness fails closed when that role is undeclared. The focused
identity and readiness tests pass, and the handoff evidence is now `205` tests
(134 deployment, 71 verification-platform). Full IdP token validation,
tenant-directory mapping, and role administration remain deployment gates.

Customer-production readiness now also requires explicit OIDC issuer,
audience, and JWKS URL declarations. This keeps the trusted ingress subject
and role contract tied to a named identity provider configuration instead of
allowing a bare header to imply enterprise authentication. Health and
identity tests pass; JWT verification, key rotation, and tenant-directory
integration remain deployment work.

Compose and the deployment environment template now expose the reviewer role
and OIDC issuer, audience, and JWKS settings required by the customer-
production contract for both API and worker containers. The configuration
surface is tested so a production promotion has one consistent source of
identity declarations; actual token validation and managed identity lifecycle
remain open gates.

The platform now includes an executable OIDC verifier with cached JWKS key
resolution, allowed asymmetric algorithms, issuer and audience validation, and
role extraction. Customer-production can require bearer-token validation before
routes consume identity context. Focused OIDC tests pass; tenant-directory
mapping, key-rotation operations, and provider-specific ingress rollout remain
open. The next full-suite evidence target is `208` tests (137 deployment, 71
verification-platform).

The customer-production Kubernetes overlay rendered to five objects
(Deployment, Service, PersistentVolumeClaim, NetworkPolicy, and backup
CronJob) with the explicit load-restriction override, and CI now runs that
render. The current complete suite is `218` tests (146 deployment, 72
verification-platform); real managed resources and secret injection remain
deployment gates.
### 2026-09-10 — Object-lock retention readiness is measurable

The managed evidence control probe now requires both object-lock/WORM enablement
and a positive provider-reported default retention duration. It exposes the
effective duration as `object_lock_retention_days`, so readiness cannot be
reported for a bucket that has WORM enabled but no actual default retention.
The injected-provider regression covers the 35-day case. This strengthens the
customer-production evidence gate; provider-specific IAM and deployment of the
retention policy remain operational gates.

The negative path is also covered: an object-lock-enabled bucket with no
default retention is reported not ready. The complete suite is now `224`
tests (`152` deployment, `72` verification-platform).

The managed repository cutover now has an atomic-selection regression: a
customer-production bundle must select PostgreSQL queue, project, and
collateral repositories together with the S3 evidence provider and pass the
same migration flag to each. Incomplete production configuration is rejected
before any managed repository is constructed. The focused checks pass, and
the full-suite evidence target is now `226` tests (`154` deployment, `72`
verification-platform).

The PostgreSQL restore helper now rejects a restore target that resolves to the
source database, even when credentials differ, preventing a recovery drill
from destructively restoring over live state. Disposable-target and rejection
paths are covered by regression tests; the full-suite evidence target is now
`228` tests (`156` deployment, `72` verification-platform).

The first provider-native disposable PostgreSQL restore rehearsal also ran
successfully. PostgreSQL 16 migration, dump, restore into a separate database,
and four-table row-count verification all passed. A mismatched host PostgreSQL
14 client was rejected before the rehearsal, confirming the compatibility
preflight. The digest-bound result is included in the commercial handoff
manifest; managed provider retention, replication, and failover remain open.

Scheduled-backup regression coverage now proves a PostgreSQL client/server
compatibility failure stops before `pg_dump` creates any output. This protects
the production backup boundary from partial or incompatible dumps; the full
suite target is now `229` tests (`157` deployment, `72` verification-platform).

The runner now has an opt-in Linux namespace backend for customer execution:
isolated mode launches tools in private user, PID, mount, and network
namespaces and records the enforced backend in provenance. Smoke execution and
invalid-mode fail-closed paths are covered. Deployment-specific read-only
source mounts, quotas, and policy wiring remain open; the full-suite target is
now `231` tests (`157` deployment, `74` verification-platform).

The production image and CI runner now install `util-linux`, making the
`unshare` namespace backend an explicit image dependency instead of an
accidental host capability. Kubernetes and customer runtime policy validation
still remain required because namespace support must be confirmed by the target
cluster.

The credential-free runtime probe now emits digestable JSON evidence for the
namespace backend and verifies an empty isolated network route table. The
production handoff includes this probe alongside the managed restore result;
target-cluster security policy and mount/quotas validation remain open.

Customer-production configuration now fails closed unless a non-empty
`VERIFICATION_PROJECT_SUBJECTS` mapping is supplied. The production ConfigMap
example and overlay wire that mapping into the API, preventing valid OIDC
tokens from becoming global project access. Enterprise tenant-directory and
RBAC lifecycle integration remains an operational gate.

Readiness regression coverage now proves this mapping requirement directly,
including a fully declared customer-production configuration with the mapping
omitted. The full-suite evidence target is now `235` tests (`161` deployment,
`74` verification-platform).

The runtime probe is now a digest-bound handoff artifact, and the deployment
documentation test requires its presence. The full-suite evidence target is
now `232` tests (`158` deployment, `74` verification-platform).

The executable reference adapter matrix now covers pass, explicit tool
failure, timeout, and missing expected artifact cases. Every case retains the
common bounded provenance record, and the passing summary is included in the
commercial handoff manifest. Customer-specific licensed adapter validation
remains open.

The handoff/documentation gate now requires the adapter acceptance summary;
the full-suite evidence target is `233` tests (`159` deployment, `74`
verification-platform).

Customer-production mutation routes now require the configured operator role
after trusted OIDC and project-subject checks. This prevents token-valid
readers from creating collateral, planning or generating artifacts, proposing
repairs, submitting or executing jobs, and cancelling queued work. The full
suite evidence target is now `237` tests (`163` deployment, `74`
verification-platform); enterprise role lifecycle integration remains an open
deployment gate.

The commercial handoff manifest now inventories the complete observability
profile (Prometheus scrape configuration, alert rules, dashboard, and compose
profile) rather than only the dashboard. This makes the pilot's operational
signals reproducible while managed routing, centralized logs, and SLO ownership
remain deployment-specific gates.

Customer-production readiness now fails closed unless managed logs,
alert-routing, and a named SLO owner are declared in addition to the telemetry
endpoint. The Kubernetes production example and semantic overlay preflight wire
and verify all three values; actual customer-managed routing and ownership
remain part of the production deployment gate.

Customer-production readiness now requires a non-empty customer EDA adapter
registry. The overlay carries the registry as non-secret configuration and
preflight verifies its presence; executable availability and pass/fail
acceptance remain measured adapter evidence rather than configuration claims.

The container build context was tightened to exclude bulky evidence, lab,
documentation, and generated binary artifacts while retaining runtime scripts
and benchmark entry points. The image build reaches dependency installation
and application assembly; local Docker layer export remains an environment
issue, so cluster image loading is still unverified here.

Image runtime smoke now supports `--sandbox-probe` and runs the namespace
capability check inside the built container. CI enables this flag and the
release provenance manifest records the stronger command, preventing an image
that only passes HTTP/UID checks from being published without isolation support.

Generated `.artifacts/` output is now ignored by the project-local `.gitignore`.
This keeps release provenance clean after CI creates evidence while retaining
the files for handoff hashing and artifact upload.

The versioned `/v1/contract` now includes structured customer-production
requirements: exact environment variables, runtime evidence obligations, and a
claim boundary. Deployment automation can consume this schema directly while
provider implementation and signed pilot evidence remain separate gates.

A disposable PostgreSQL repository smoke now exercises the managed project,
collateral, and durable-queue classes over TCP, including transactional claim
and finish behavior, and emits digest-bound evidence. It strengthens the
managed-state boundary without claiming HA, managed availability, credentials,
backup, or customer production readiness.

CI now provisions a PostgreSQL 16 service, applies the managed schema, runs the
repository smoke, and executes the managed restore drill before building the
commercial handoff. The open-source job still keeps credentials ephemeral and
does not promote this service rehearsal to customer-production readiness.

The versioned `/v1/contract` now publishes the customer-production boundary
requirements for managed state, retained object storage, enterprise identity,
operational ownership, and customer adapter registration. Integrations can
preflight against one machine-readable contract instead of inferring gates
from readiness error strings.

The local `verification-pilot-ci` image tag was found to predate the sandbox
probe and fails the in-image runtime check; rebuilding reaches application
assembly but stalls during local Docker layer export. The runtime smoke now
includes container probe error detail, and target-image rebuild/export plus
cluster execution remain an explicit deployment gate.

The deterministic pilot scorecard collector now computes all six workflow-value
metrics from matched baseline/workbench observations. It requires at least 20
samples spanning simulation, lint, formal, and regression, including three
blocked or timeout cases, and hashes both input sets. Human labels and lead
approval remain required before a scorecard can be finalized.

The collector now adds deterministic 95% uncertainty intervals: bootstrap
intervals for continuous medians and Wilson intervals for fractions. This keeps
the commercial pilot from presenting point estimates without sample uncertainty.

Image runtime acceptance now has a digest-bound JSON handoff artifact. It
records liveness, readiness, UID, selected Docker security options, and sandbox
result; a permissive local seccomp rehearsal cannot substitute for target
cluster isolation policy.

Pilot observation intake now rejects unsupported categories, negative or
non-finite timings, and non-boolean review labels before aggregation. The full
suite evidence target is now `272` tests (`196` deployment, `76`
verification-platform).

Finalized pilot scorecards now require uncertainty intervals for both sides of
each comparison: the collector emits deterministic 95% bootstrap intervals for
median baseline/workbench timings and Wilson intervals for baseline/workbench
fractions, while validation rejects missing, malformed, or inverted intervals.

The release package now includes a credential-free OIDC key-rotation drill that
rehearses old-key acceptance, overlap with a new signing key, forced JWKS
refresh, and rejection after retirement. The artifact records its explicit
boundary: customer identity-provider availability, tenant mapping, and RBAC
lifecycle still require deployment evidence.

Confidence-interval validation now rejects NaN, infinity, booleans, and inverted
bounds, so malformed uncertainty cannot satisfy finalized pilot acceptance.

The customer-pilot packet gate now combines readiness, finalized scorecard
validation, evidence-digest verification, and signoff receipt verification in a
single fail-closed command. It is a promotion control, not a substitute for
customer infrastructure or signed business outcomes.

Signoff verification now supports the scorecard's `scorecard_sha256` digest in
addition to report and comparison digests. The packet gate requires the receipt
to be approved and bound to the exact scorecard path, and has both rejection and
successful synthetic promotion tests.

Customer promotion now also requires the receipt's authenticated
`reviewer_subject`; a display name alone cannot satisfy the identity boundary.

The packet gate now cross-checks readiness counts and `open_controls`, rejecting
inconsistent reports even when their standalone ready flag is true.

Readiness promotion now also verifies the reported checklist path is contained
inside the packet root and that its SHA-256 matches the current checklist.

Structured request logging now covers downstream dispatch exceptions as
correlated 500 events before re-raising, so failed requests cannot disappear
from centralized observability solely because they raised an exception.

Unhandled dispatch exceptions now also increment the 5xx response counter and
duration, keeping Prometheus error-rate signals aligned with structured logs.

The execution runner now measures total job-workspace bytes and blocks runs that
exceed `VERIFICATION_JOB_MAX_WORKSPACE_BYTES`, complementing CPU and per-file
limits and recording both measured and configured quota values in provenance.

Customer-production readiness now requires positive declarations for both total
workspace and per-file byte quotas, so the isolation policy cannot omit the
limits enforced by the runner.

The byte-quota settings are now wired through the example environment, Docker
Compose, and both API/worker containers in the production Kubernetes overlay;
compose validation and semantic overlay preflight pass.

The `verification-http-log-v1` JSON Schema is now versioned and included in the
handoff inventory, giving customer log pipelines a machine-readable contract.

The platform contract now exposes the request-log schema path directly, so
integrations can discover the observability format through `/v1/contract`.

Readiness reports now carry `readiness_sha256`; the packet gate recomputes it in
addition to checking the referenced checklist digest, preventing coherent but
edited readiness fields from being promoted.

The packet gate also requires `pilot_controls_verified` to be an explicit true
boolean, keeping readiness semantics from being inferred from counts alone.

Registered-adapter preflight now emits digest-bound availability evidence and
keeps unavailable customer tools explicitly blocked; adapter behavior and
licensed-tool acceptance remain separate deployment gates.

Customer-production byte-quota validation now rejects configurations where the
per-file limit exceeds the total workspace limit, with a focused health test;
the complete deployment/platform suite remains green at `272` tests (`196`
deployment, `76` verification-platform).

That quota relationship is now represented as an explicit verified checklist
control. The regenerated readiness report has `96` controls (`88` verified,
`8` open), and the commercial handoff manifest was rebuilt and verified against
the updated checklist and readiness digests.

The workbench now renders registered execution backends in both sample and live
mode, including available/blocked status, expected output paths, and timeout
limits. The service capabilities response publishes the same contract, and the
browser smoke gate asserts the sample capability state without page errors.
Readiness records this as a verified UX/integration control: `97` controls,
`89` verified, and `8` open.

The commercial handoff manifest now also content-addresses the shipped
workbench HTML/JavaScript and its browser acceptance script, closing the gap
between backend evidence and the reviewed interface. This adds one verified
checklist control; the regenerated package has `98` controls (`90` verified,
`8` open) and `28` content-addressed artifacts.

The adversarial judge packet is now also content-addressed in the commercial
handoff. It records the seven scenarios, deterministic browser/service gate,
LLM review instruction, and claim boundary; the regenerated readiness package
has `100` controls (`92` verified, `8` open) and `29` artifacts.

The adversarial runner now bounds both deterministic subprocesses and writes a
terminal structured packet when either gate times out. A one-second timeout
rehearsal produced a failed packet and exit code 1; no indefinite process was
left running. Readiness records this as a verified control: `101` controls,
`93` verified, and `8` open.

Authenticated `/v1/readiness` now exposes the bounded readiness summary and
claim boundary at runtime, while withholding raw report files. Its contract
entry and regression test close the distinction between liveness and commercial
readiness; the current checklist is `102` controls (`94` verified, `8` open).

The workbench now renders that readiness summary in the connected and sample
experiences, including open controls and an explicit claim boundary. Browser
smoke covers the sample boundary and the live failure path; readiness is now
`103` controls (`95` verified, `8` open).

The browser gate now also mocks a connected `/v1/readiness` response and proves
that the UI renders its verified count, open production controls, blocked state,
and adapter capability without page errors. Readiness records this as a
verified live UX control: `104` controls (`96` verified, `8` open).

The service now exposes `/v1/pilot/scorecard`, a bounded summary of pilot
windows, metric values/intervals, evidence counts, finalization state, and
claim boundary. Raw observations are withheld; a schema-focused health test
proves the boundary. The current checklist is `105` controls (`97` verified,
`8` open).

The workbench now renders a pilot-measurement panel with draft/finalized state,
bounded metric summaries, and an explicit no-ROI claim for the sample scorecard.
A direct browser page smoke confirms the panel renders; the larger Playwright
scenario harness is currently timing out in the local environment after the
additional panel and therefore has not been promoted as fresh full-gate
evidence. Readiness is `106` controls (`98` verified, `8` open).

Scorecard summary parsing now normalizes non-numeric sample metadata and treats
non-object review metadata as draft state; schema errors still fail closed.
Focused health coverage passes, and readiness records the control at `107`
controls (`99` verified, `8` open).

The machine-readable platform contract now advertises `/v1/capabilities`,
closing the integration discovery loop between deployment metadata and the
workbench capability panel. Contract regression coverage passes; readiness is
now `99` controls (`91` verified, `8` open).

Capability, readiness, and scorecard fetches in the workbench now use an
AbortController timeout and render an actionable unavailable state when the
service stalls. A direct page smoke reached the new panels; the larger local
Playwright process became unresponsive and was terminated, so no fresh full
browser-gate claim is made. Readiness is now `108` controls (`100` verified,
`8` open).

The deployment README now documents `/v1/capabilities`, `/v1/readiness`, and
`/v1/pilot/scorecard`, including authentication and claim boundaries. The README
is content-addressed in the handoff manifest; readiness is now `109` controls
(`101` verified, `8` open).

The commercial handoff now also content-addresses `USABILITY_STUDY_PLAN.md` and
`pilot-usability-study-template.json`, preserving the human-workflow evidence
needed for first-time, debug, and verification-lead pilot evaluation. Readiness
is now `110` controls (`102` verified, `8` open).

The handoff now includes `validate_pilot_scorecard.py` and
`verify_pilot_scorecard_evidence.py`; both documented commands pass against the
current draft scorecard. This makes the scorecard acceptance procedure
reproducible from the handoff itself. Readiness is now `111` controls (`103`
verified, `8` open).

The authenticated HTTP route for `/v1/pilot/scorecard` now has regression
coverage proving the bounded payload used by integrations omits raw
observations. Readiness is now `112` controls (`104` verified, `8` open).
