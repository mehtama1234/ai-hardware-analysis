# Backend Prototype

This is the first real backend slice for the model-fit workbench.

It imports an ONNX model, extracts the graph, classifies operators against a simple hardware capability profile, estimates analog/digital boundaries, and returns JSON shaped like the frontend mock data.

The current fit engine includes:

- target hardware profiles
- operator placement classification
- grouped model blocks
- ADC/DAC boundary events
- boundary hotspot reporting
- rough latency and energy estimates
- fit score with score reasons
- recommendations based on fallback, unsupported operators, boundary count, and energy target
- modality-aware estimated quantization reports
- selectable calibration profiles with provenance and confidence
- simulated runtime profiling with latency, energy, overhead, trace, bottlenecks, and target pass/fail
- estimated digital baseline comparison for completed inference, not TOPS/W headlines
- deployment package readiness reports with manifest, blockers, safe claim level, and next evidence steps
- evidence gate reports that consolidate passed, estimated, blocked, and missing proof
- measurement evidence contracts for compiler, simulator, board, power, thermal, and task-accuracy artifacts
- plain-language review reports for interview or customer discussion
- downloadable evaluation archives containing the uploaded ONNX and generated analysis artifacts
- persisted package artifacts that can be fetched again by package ID
- persisted model registry that reloads uploaded ONNX model records after backend restart
- persisted project registry that links target context, imported models, and package artifacts
- one-shot project evaluation runs that generate analysis, quantization, runtime, baseline, evidence, review, and package artifacts from the project context
- interview drills with likely questions, strong answer outlines, follow-ups, and overclaim traps
- persisted project run history for comparing evaluation attempts over time
- run comparison reports that show completed-inference deltas across saved evaluations
- editable project settings for rerunning the same model against different target, modality, calibration, and runtime choices
- saved package artifact bundle retrieval for reopening a previous run without recalculating it
- decision reports that turn evidence into a product recommendation: good fit, needs rewrite, needs measurement, or not a fit yet
- rewrite suggestion reports that identify specific operator, boundary, precision, and model-shape changes to try next
- rewrite what-if reports that estimate the effect of proposed changes before editing the real model
- rewrite plan reports that turn selected suggestions into concrete graph, compiler, runtime, and validation steps
- rewrite work orders that convert a plan into owner-facing tasks, gates, and evidence attachments
- adapter registry for local, configured, missing, and planned external tool connections
- connection playbooks that say what each real tool must configure, produce, prove, and not overclaim

## Setup

```bash
cd /home/mehtama1/git-repo/ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture/backend
python3 -m pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload --port 8020
```

## Smoke Test

With the backend running on `127.0.0.1:8020`, run:

```bash
./.venv/bin/python scripts/smoke_end_to_end.py
```

The smoke test imports `../samples/tiny-mlp.onnx`, calls every current product-flow endpoint, runs the one-shot project evaluation endpoint, downloads the evaluation archive, and verifies the required archive files are present.

## APIs

```text
GET  /health
GET  /targets
GET  /modalities
GET  /runtime-modes
GET  /adapters
GET  /adapters/{adapter_id}/probe
POST /adapters/{adapter_id}/run
POST /deployment-packages/{package_id}/local-evidence
POST /evidence/validate
POST /evidence/import
POST /evidence/import-batch
GET  /evidence/imports
GET  /calibration-profiles
GET  /calibration-profiles/{profile_id}
GET  /project-runs
GET  /project-runs/compare
GET  /project-runs/{run_id}
GET  /projects
POST /projects
GET  /projects/{project_id}
PATCH /projects/{project_id}
GET  /projects/{project_id}/runs
GET  /projects/{project_id}/runs/compare
POST /projects/{project_id}/runs
GET  /models
POST /models/import
GET  /models/{model_id}
GET  /models/{model_id}/graph
POST /models/{model_id}/quantize
POST /models/{model_id}/runtime-profile
POST /models/{model_id}/baseline-comparison
POST /models/{model_id}/deployment-package
POST /models/{model_id}/measurement-evidence
POST /models/{model_id}/evidence-gates
POST /models/{model_id}/review-report
POST /models/{model_id}/decision-report
POST /models/{model_id}/rewrite-suggestions
POST /models/{model_id}/rewrite-what-if
POST /models/{model_id}/rewrite-plan
POST /models/{model_id}/rewrite-work-order
GET  /models/{model_id}/deployment-package/archive
GET  /deployment-packages
GET  /deployment-packages/{package_id}
GET  /deployment-packages/{package_id}/artifacts
GET  /deployment-packages/{package_id}/measurement-evidence
GET  /deployment-packages/{package_id}/workload-fit
GET  /deployment-packages/{package_id}/system-boundary
GET  /deployment-packages/{package_id}/research-guide
GET  /deployment-packages/{package_id}/concept-glossary
GET  /deployment-packages/{package_id}/toolchain-readiness
GET  /deployment-packages/{package_id}/connection-playbook
GET  /deployment-packages/{package_id}/adapter-execution-plan
GET  /deployment-packages/{package_id}/adapter-connection-kit
GET  /deployment-packages/{package_id}/adapter-evidence-templates
GET  /deployment-packages/{package_id}/adapter-connection-self-test
GET  /deployment-packages/{package_id}/adapter-integration-readiness
GET  /deployment-packages/{package_id}/external-connector-contract
GET  /deployment-packages/{package_id}/connector-implementation-guide
GET  /deployment-packages/{package_id}/connector-test-harness
GET  /deployment-packages/{package_id}/connector-acceptance-report
GET  /deployment-packages/{package_id}/connector-backlog
GET  /deployment-packages/{package_id}/connector-delivery-plan
GET  /deployment-packages/{package_id}/connector-risk-register
GET  /deployment-packages/{package_id}/imported-evidence
GET  /deployment-packages/{package_id}/evidence-audit
GET  /deployment-packages/{package_id}/evidence-brief
GET  /deployment-packages/{package_id}/evidence-brief.md
GET  /deployment-packages/{package_id}/interview-brief
GET  /deployment-packages/{package_id}/interview-brief.md
GET  /deployment-packages/{package_id}/interview-drill
GET  /deployment-packages/{package_id}/claim-readiness
GET  /deployment-packages/{package_id}/decision-report
GET  /deployment-packages/{package_id}/rewrite-suggestions
GET  /deployment-packages/{package_id}/rewrite-what-if
GET  /deployment-packages/{package_id}/rewrite-plan
GET  /deployment-packages/{package_id}/rewrite-work-order
GET  /deployment-packages/{package_id}/review-report
GET  /deployment-packages/{package_id}/review-report.md
GET  /deployment-packages/{package_id}/archive
```

Example import:

```bash
curl --data-binary "@model.onnx" "http://localhost:8020/models/import?filename=model.onnx&target_profile=wearable&calibration_profile=proto-audio-0237"
```

Example model registry lookup:

```bash
curl "http://localhost:8020/models"
curl "http://localhost:8020/models/{model_id}"
```

Example project creation:

```bash
curl -X POST "http://localhost:8020/projects?name=Wearable%20Audio&target_profile=wearable&modality=audio_wake_word&calibration_profile=proto-audio-0237&runtime_mode=balanced"
curl "http://localhost:8020/projects"
```

Example project settings update:

```bash
curl -X PATCH "http://localhost:8020/projects/{project_id}?target_profile=camera&modality=vision_classification&calibration_profile=proto-camera-011&runtime_mode=low_latency"
```

Example one-shot project evaluation after importing a model into the project:

```bash
curl -X POST "http://localhost:8020/projects/{project_id}/runs?model_id={model_id}"
```

This returns all generated artifacts in one response and persists the package archive under `.data/packages/{package_id}`. If `model_id` is omitted, the endpoint evaluates the latest model attached to the project.

Example run history lookup:

```bash
curl "http://localhost:8020/project-runs"
curl "http://localhost:8020/project-runs/{run_id}"
curl "http://localhost:8020/projects/{project_id}/runs"
```

Example run comparison:

```bash
curl "http://localhost:8020/project-runs/compare?run_ids={run_id_1},{run_id_2}"
curl "http://localhost:8020/projects/{project_id}/runs/compare"
```

Example adapter status lookup:

```bash
curl "http://localhost:8020/adapters"
```

Example quantization estimate after import:

```bash
curl -X POST "http://localhost:8020/models/{model_id}/quantize?target_profile=wearable&calibration_profile=proto-audio-0237&modality=audio_wake_word"
```

Example simulated runtime profile after import:

```bash
curl -X POST "http://localhost:8020/models/{model_id}/runtime-profile?target_profile=wearable&calibration_profile=proto-audio-0237&modality=audio_wake_word&runtime_mode=balanced"
```

Example estimated digital baseline comparison:

```bash
curl -X POST "http://localhost:8020/models/{model_id}/baseline-comparison?target_profile=wearable&calibration_profile=proto-audio-0237&modality=audio_wake_word&runtime_mode=balanced"
```

Example package-readiness report after import:

```bash
curl -X POST "http://localhost:8020/models/{model_id}/deployment-package?target_profile=wearable&calibration_profile=proto-audio-0237&modality=audio_wake_word&runtime_mode=balanced"
```

Example evidence gate report:

```bash
curl -X POST "http://localhost:8020/models/{model_id}/measurement-evidence?target_profile=wearable&calibration_profile=proto-audio-0237&modality=audio_wake_word&runtime_mode=balanced"
curl -X POST "http://localhost:8020/models/{model_id}/evidence-gates?target_profile=wearable&calibration_profile=proto-audio-0237&modality=audio_wake_word&runtime_mode=balanced"
```

Example evidence validation and attachment:

```bash
curl -X POST "http://localhost:8020/evidence/validate?package_id={package_id}&source_id=compiler_mapping" \
  -H "Content-Type: application/json" \
  --data '{"operator_placements":[],"tiling_plan":[],"memory_plan":{},"unsupported_operators":[],"provenance":{"tool":"compiler","version":"0.1"}}'

curl -X POST "http://localhost:8020/evidence/import?package_id={package_id}&source_id=compiler_mapping" \
  -H "Content-Type: application/json" \
  --data '{"operator_placements":[],"tiling_plan":[],"memory_plan":{},"unsupported_operators":[],"provenance":{"tool":"compiler","version":"0.1"}}'
curl "http://localhost:8020/deployment-packages/{package_id}/imported-evidence"
curl "http://localhost:8020/deployment-packages/{package_id}/claim-readiness"
```

Example batch evidence attachment:

```bash
curl -X POST "http://localhost:8020/evidence/import-batch?package_id={package_id}" \
  -H "Content-Type: application/json" \
  --data '{"items":[{"source_id":"compiler_mapping","payload":{"operator_placements":[],"tiling_plan":[],"memory_plan":{},"unsupported_operators":[],"provenance":{"tool":"compiler","version":"0.1"}}}]}'
```

Example plain-language review report:

```bash
curl -X POST "http://localhost:8020/models/{model_id}/review-report?target_profile=wearable&calibration_profile=proto-audio-0237&modality=audio_wake_word&runtime_mode=balanced"
```

Example decision report:

```bash
curl -X POST "http://localhost:8020/models/{model_id}/decision-report?target_profile=wearable&calibration_profile=proto-audio-0237&modality=audio_wake_word&runtime_mode=balanced"
```

Example rewrite suggestion report:

```bash
curl -X POST "http://localhost:8020/models/{model_id}/rewrite-suggestions?target_profile=wearable&calibration_profile=proto-audio-0237&modality=audio_wake_word&runtime_mode=balanced"
```

Example rewrite what-if:

```bash
curl -X POST "http://localhost:8020/models/{model_id}/rewrite-what-if?target_profile=wearable&calibration_profile=proto-audio-0237&modality=audio_wake_word&runtime_mode=balanced&suggestion_ids={suggestion_id}"
curl "http://localhost:8020/deployment-packages/{package_id}/rewrite-what-if?suggestion_ids={suggestion_id}"
```

Example rewrite plan:

```bash
curl -X POST "http://localhost:8020/models/{model_id}/rewrite-plan?target_profile=wearable&calibration_profile=proto-audio-0237&modality=audio_wake_word&runtime_mode=balanced&suggestion_ids={suggestion_id}"
curl "http://localhost:8020/deployment-packages/{package_id}/rewrite-plan?suggestion_ids={suggestion_id}"
```

Example rewrite work order:

```bash
curl -X POST "http://localhost:8020/models/{model_id}/rewrite-work-order?target_profile=wearable&calibration_profile=proto-audio-0237&modality=audio_wake_word&runtime_mode=balanced&suggestion_ids={suggestion_id}"
curl "http://localhost:8020/deployment-packages/{package_id}/rewrite-work-order?suggestion_ids={suggestion_id}"
```

Example evaluation archive download:

```bash
curl -L -o package.zip "http://localhost:8020/models/{model_id}/deployment-package/archive?target_profile=wearable&calibration_profile=proto-audio-0237&modality=audio_wake_word&runtime_mode=balanced"
```

Example saved package retrieval after generating a package report:

```bash
curl "http://localhost:8020/deployment-packages"
curl "http://localhost:8020/deployment-packages/{package_id}"
curl "http://localhost:8020/deployment-packages/{package_id}/artifacts"
curl "http://localhost:8020/deployment-packages/{package_id}/measurement-evidence"
curl "http://localhost:8020/deployment-packages/{package_id}/imported-evidence"
curl "http://localhost:8020/deployment-packages/{package_id}/claim-readiness"
curl "http://localhost:8020/deployment-packages/{package_id}/decision-report"
curl "http://localhost:8020/deployment-packages/{package_id}/rewrite-suggestions"
curl "http://localhost:8020/deployment-packages/{package_id}/rewrite-what-if"
curl "http://localhost:8020/deployment-packages/{package_id}/rewrite-plan"
curl "http://localhost:8020/deployment-packages/{package_id}/rewrite-work-order"
curl -L -o package.zip "http://localhost:8020/deployment-packages/{package_id}/archive"
curl "http://localhost:8020/deployment-packages/{package_id}/review-report.md"
```

Target profiles:

```text
wearable
camera
robotics
```

## Current Scope

This backend does real ONNX graph import when the `onnx` Python package is installed.

It does not yet run real inference, perform real quantization, measure real power, or connect to silicon. Those are later milestones.

The quantization endpoint is estimated and structural. It does not run a calibration dataset yet. It marks sensitive layers, recommends `INT8 protected`, `INT4 candidate`, or `keep digital`, and returns provenance `estimated` with low confidence.

Calibration profiles are representative local records in this prototype. They do not connect to live silicon yet.

The runtime profile endpoint is also simulated. It uses the analyzed layer costs, target constraints, calibration profile, modality-aware quantization policy, and selected runtime mode to produce a normalized profile artifact. The useful product habit is already present: compare energy per completed inference against a fixed latency and energy target. The numbers are not measured hardware results.

The baseline comparison is estimated and low confidence. It compares the simulated analog path with an estimated all-digital path using completed-inference latency and energy. It lists what was counted and excluded so the result is not confused with a vendor headline or measured benchmark.

The workload fit matrix explains why "edge AI" is not one market. It compares the selected model and target against audio wake-word, vision classification, object detection, robotics perception, industrial anomaly, health wearable, and edge LLM use cases. Each row states what gets easier, what gets harder, which task metric matters, and which failure cost should shape validation.

The system boundary report explains the full-system cost around the analog core. It separates analog compute, digital support, fallback work, ADC/DAC conversion, memory movement, host control, and idle energy. It also lists the concrete boundary questions to ask before trusting an efficiency claim.

The research guide turns the analog and in-memory AI paper list into a reading map. It records the theme, first-principles lesson, interview angle, and overclaim guardrail for each record, while marking abstract-only records as design-space context rather than measured product proof.

The concept glossary explains recurring analog and in-memory AI terms in plain language. Each term states what it means, why it matters, and what to watch out for, so the interview and review language stays simple without becoming sloppy.

The toolchain readiness report explains the software support needed around the hardware: model import, quantization, compiler mapping, analog behavior simulation, runtime and board execution, power and thermal measurement, task accuracy validation, profiling/debugging, and customer handoff. It is derived from the adapter registry and measurement evidence contract, so it separates local workflow availability from evidence-backed proof. The adapter execution plan turns the connection playbook into an operating sequence for each adapter: configure, run, normalize, validate preview, import, and archive. The adapter connection kit adds the handoff details for real integration: env vars, raw inputs, raw outputs, normalized artifact fields, and API calls. The adapter evidence templates provide example normalized JSON payloads that external tools can fill before validation and import, plus a claim-impact preview for each artifact type. The adapter connection self-test captures all adapter probe checks in one package artifact so missing dependencies, environment variables, or service health failures are visible before evidence is run. The adapter integration readiness report combines the execution plan, connection kit, evidence templates, and self-test into a short list of ready paths, blockers, and next connection priorities. The external connector contract states what a real compiler, simulator, board service, meter, or accuracy runner must accept and return: health check, run behavior, request shape, response shape, failure behavior, validation endpoint, and import endpoint. The connector implementation guide turns that contract into rollout order, implementation steps, done criteria, and claim boundaries for each connector. The connector test harness lists the probe, run, positive validation, negative validation, import, and failure-safety checks each connector must pass before its evidence can affect claims. The connector acceptance report compares those checks with current probes and imported evidence, so it can say what is accepted, blocked, or still pending without overclaiming that the harness ran. The connector backlog turns blocked and pending acceptance results into owner-facing tasks with priority, command, reason, and done criteria. The connector delivery plan groups those tasks into milestones so teams know the order: unblock probes, produce evidence, harden validation, run failure drills, then refresh claim readiness. The connector risk register lists delivery risks, triggers, mitigations, owners, open tasks, and the evidence needed to control each risk.

The measurement evidence contract states what external artifacts are required before an estimate can become a measured claim. It covers compiler mapping, analog error simulation, board runtime traces, power and thermal measurement, and task accuracy. It can show configured adapters, but a configured adapter is not treated as a measurement result by itself. The evidence import endpoint accepts normalized artifacts and attaches them to a package or run; imported artifacts are what move individual evidence sources from connection state toward claim support.

The claim readiness endpoint recalculates which lab claims are supported from imported evidence. It can support compiler placement, measured latency, measured energy, or accuracy tolerance independently when their required sources are attached and their payload checks pass. Local simulated board and power artifacts move latency and energy claims to `needs review`, not `supported`. A `task-accuracy-report.json` with `pass: false` moves the accuracy claim to `needs review`, not `supported`. Production readiness stays blocked even when lab claims are supported. Sample normalized artifacts for all five required evidence sources are available under `../samples/evidence/`.

Claim readiness also carries evidence details for imported artifacts. For task accuracy this includes dataset ID, metric name, baseline metric, candidate metric, delta, tolerance, pass/fail, and record count. For latency and energy it includes board ID, runtime version, latency, trace count, fallback count, energy, meter, sampling rate, voltage, whether host overhead was counted, and whether the artifact came from local simulation. The frontend renders those fields directly in the claim card so the user can see why a claim is supported or needs review.

Downloaded archives include `workload-fit.json`, `system-boundary.json`, `research-guide.json`, `concept-glossary.json`, `toolchain-readiness.json`, `connection-playbook.json`, `adapter-execution-plan.json`, `adapter-connection-kit.json`, `adapter-evidence-templates.json`, `adapter-connection-self-test.json`, `adapter-integration-readiness.json`, `external-connector-contract.json`, `connector-implementation-guide.json`, `connector-test-harness.json`, `connector-acceptance-report.json`, `connector-backlog.json`, `connector-delivery-plan.json`, `connector-risk-register.json`, `claim-readiness.json`, `evidence-audit.json`, `evidence-brief.json`, `evidence-brief.md`, `interview-brief.json`, `interview-brief.md`, `interview-drill.json`, `imported-evidence/index.json`, every imported evidence record under `imported-evidence/`, `adapter-runs/index.json`, and every saved adapter attempt under `adapter-runs/`. This means the ZIP contains both the generated review artifacts and the external evidence files used to support lab claims, plus adapter-run audit records that do not change claim readiness unless separately imported as validated evidence.

The evidence brief is the short handoff for interview or design review use. It is derived from claim readiness and the evidence audit, so it says what is supported, what needs review, which evidence is local or non-local, what to say clearly, what not to claim, and what evidence is still missing. It also includes a readiness ladder from concept discussion, to package analysis, to evidence-backed lab claims, to measured workload claims, to production readiness. The frontend renders this as a first-class panel after the evidence audit, and the Markdown version remains available as an artifact link.

The interview brief is a direct explanation guide. It gives a short answer, first-principles framing, safe talking points, questions to ask the company, and things not to overclaim. It is derived from the evidence brief, system boundary, workload fit, and toolchain readiness artifacts.

The interview drill turns that explanation guide into practice. It lists likely interview questions, strong answer outlines, follow-up questions to expect, and what not to overclaim. It keeps the answers tied to package evidence instead of treating analog compute, TOPS/W, edge AI, or prototype silicon as automatic proof.

The connection playbook is the practical wiring checklist for real tools. It covers ONNX Runtime quantization, compiler mapping, analog simulation, dataset accuracy, board runtime, and power or thermal measurement. For each connection it says what to configure, which normalized artifact must be imported, what the artifact can prove, and what not to claim from that connection alone.

The evidence gate report is the conservative review layer. It answers which checks passed, which are estimated, which are blocked, and which are missing. This is the safest place to decide what claim can be made.

The review report turns the artifacts into plain language: what to say clearly, what not to overclaim, what the hard parts are, and what evidence is still needed.

The decision report turns the same evidence into a direct product recommendation. It labels the run as `good fit`, `needs rewrite`, `needs measurement`, or `not a fit yet`, then lists the reasons, next actions, and statements to avoid.

The rewrite suggestion report makes a `needs rewrite` result concrete. It lists which operators, boundaries, or precision-sensitive analog layers to change, why the change should help, what improvement to expect, and how to verify it after rerunning the project.

The rewrite what-if report is a planning estimate. It applies selected rewrite suggestions virtually and reports estimated changes to analog coverage, fallback count, boundary count, latency, energy, and decision. It does not edit ONNX, run a compiler, measure accuracy, or measure board power.

The rewrite plan report turns selected suggestions into concrete actions. It says whether the likely change is an operator replacement, fallback removal, boundary reduction, digital support fusion, precision protection, or model-shape change. It also lists the validation steps and the compiler, simulator, board, and accuracy evidence needed before the estimate can become a claim.

The rewrite work order is the engineering handoff artifact. It lists owner lanes, layer IDs, before state, after target, implementation notes, done criteria, acceptance gates, and evidence attachments. It is still not proof by itself; it tells the team what must be changed and what evidence must be attached after the rerun.

The deployment package endpoint emits a readiness artifact that says what would be included, which blockers remain, and what claim level is safe. It also persists the generated artifacts under `.data/packages/{package_id}`. The archive endpoint bundles that report, the review report, the analyzed model artifacts, and the source ONNX into a ZIP for review. It is not a compiled hardware executable and it does not turn simulated numbers into production proof.

Saved package reports include handoff links for the archive, review report, decision report, rewrite artifacts, measurement evidence, claim readiness, imported evidence, evidence audit, and the local evidence workflow endpoint.

Projects are saved in `.data/projects.json`. Project run records are saved in `.data/runs.json`. Uploaded model records are saved in `.data/models.json`. Package, evidence, review, and archive generation can accept `project_id`; when supplied, the generated artifacts include project ID and project name. The project run endpoint uses the saved project target, modality, calibration profile, and runtime mode, then creates a persisted package from all generated artifacts. Each run points to the model, package, archive, review report, selected profiles, and summary metrics so separate attempts can be compared later. On startup, the store also scans `.data/uploads` and recovers any uploaded `.onnx` files that do not already have a registry entry.

The adapter registry reports which external tool paths are local estimates, installed dependencies, configured services, or not connected yet. It currently checks ONNX, ONNX Runtime, compiler candidates, board runtime environment variables, and power/thermal measurement environment variables. Adapter probes expose the evidence contract for each tool path. Adapter runs currently support ONNX Runtime quantization when the dependency is installed, local compiler-placement generation from analyzer rules, local analog-error generation from calibration profiles, local task-accuracy generation from a dataset file when `dataset_path` is provided, synthetic task-accuracy generation when it is not, local board-runtime trace generation, and local power/thermal report generation. The local evidence adapters attach a scenario-based simulated lab profile to each normalized artifact, covering the assumed device class, workload shape, analog precision, ADC/DAC precision, memory setup, voltage and temperature range, duty cycle, host overhead, and `not_measured_hardware: true`. In the frontend, adapter-produced normalized evidence is validated and previewed before import, using the same claim-readiness projection as pasted JSON artifacts.

Set `ANALOG_AI_REPLAY_FIXTURE_MODE=1` before starting the backend to exercise the external-connector shape without a real board or meter service. In that mode, the board runtime and power/thermal probes report a ready replay fixture path, and their adapter runs write raw `external-replay-request.json` and `external-replay-response.json` files alongside the normalized artifact. This is useful for testing connector handoff, validation, import, archive, and failure-safety workflow before lab hardware exists. It is not measured evidence; replay payloads keep `not_measured_hardware: true` and should stay in needs-review territory for measured claims.

The connector acceptance report has a separate `replay accepted` state. That state means the request shape, response shape, normalized artifact, validation, import, and archive flow worked through replay fixtures. It does not mean the external board runtime service, power meter service, or hardware measurement path is accepted. Real external acceptance still requires non-replay output with raw references, versions, target settings, and measured or simulator provenance.

Packages also include `connector-acceptance-drills.json`. That artifact runs two safety checks against imported evidence: remove a required field and confirm validation rejects it, then simulate a failed connector run and confirm no evidence is imported or upgraded. The acceptance report consumes those drill results so negative validation and failure-safety cases can move from pending to passed.

When `ANALOG_AI_COMPILER_API_URL`, `ANALOG_AI_ERROR_SIM_URL`, `ANALOG_AI_ACCURACY_API_URL`, `ANALOG_AI_BOARD_API_URL`, or `ANALOG_AI_POWER_METER_URL` is set, the matching adapter run posts to `{url}/run` before falling back to local simulation. The service may return either `{ "normalized_evidence_payload": { ... } }`, `{ "payload": { ... } }`, or the normalized artifact directly. The backend writes `external-service-request.json` and `external-service-response.json` next to the normalized artifact, then validates and imports the normalized payload through the same evidence path. If the service is configured but fails, or if it returns JSON that does not match the normalized evidence contract, the adapter run is blocked instead of silently substituting local simulation. The blocked run links to `external-service-request.json`, any saved `external-service-response.json`, and `external-service-failure.json` so the failed evidence path can be audited.

Dataset-backed task accuracy expects a `.json`, `.jsonl`, or `.csv` file with expected labels plus baseline and candidate predictions. The sample file is `../samples/datasets/wake-word-mini.json`. The runner produces the same normalized `task-accuracy-report.json` evidence contract, but with provenance tied to the dataset records instead of only a synthetic estimate.

The frontend `Run Local Evidence` action calls the runnable local adapters for compiler mapping, analog error, task accuracy, board runtime, and power/thermal evidence, imports their normalized artifacts into the current package, then refreshes claim readiness. Re-running it refreshes previous local-generated artifacts instead of appending duplicates. If non-local evidence already exists for a source, the local refresh skips that source by default so stronger evidence is not overwritten. This is a workflow shortcut. It does not turn local simulated evidence into measured hardware proof.

The frontend also has a custom evidence import panel for normalized JSON artifacts. It provides source-specific templates, can load a local `.json` evidence file into the editor, calls `POST /evidence/validate` to run backend validation and preview before/after claim readiness, posts to `POST /evidence/import` for the selected source, and refreshes the package evidence panels. This is the practical path for pasting a compiler report, board trace, power report, analog simulation result, or task accuracy result produced outside the local adapters.

The backend validates evidence in two places: validation preview and import. Both paths use the same checks for required fields plus basic structure: lists for traces and placements, objects for provenance and setup, numeric latency, energy, accuracy, and tolerance fields, and boolean pass flags. The validation endpoint returns errors and a package preview without saving anything. For valid artifacts it appends a temporary in-memory record, recalculates claim readiness, and reports what would move, what would remain blocked, and what quality warnings would remain. Bad artifacts are rejected before they can change claim readiness.

The evidence audit endpoint groups imported artifacts by required source and shows total imports, local-generated imports, non-local imports, the latest active artifact, claim status, and local refresh behavior. It is the fastest way to see why local refresh will replace or skip a source.

Generated archives include `adapter-registry.json`, so a reviewer can tell whether the package was produced from local estimates, configured external tools, or measured hardware connections.
