# Software Architecture For Analog In-Memory AI Hardware

This folder designs the software layer around an analog in-memory AI inference chip.

The active goal shared with the EDA workbench is the
[rigorous hybrid inference execution plan](../../analog-digital-chip-design-eda/docs/roadmaps/rigorous-hybrid-inference-execution-plan.md).
Its [restart ledger](../../analog-digital-chip-design-eda/docs/roadmaps/rigorous-hybrid-inference-restart-ledger.md)
records recovered evidence and the next implementation steps.

The first thing to do is not build a dashboard. The first thing is define the path from a trained model to a measured inference result on the target device.

```text
trained model
  -> import and validate
  -> quantize for hardware
  -> map operators across analog and digital paths
  -> calibrate against real chip behavior
  -> package for runtime
  -> run inference
  -> measure accuracy, latency, energy, and reliability
```

That path is the product. The frontend and backend should exist to make that path clear, repeatable, measurable, and debuggable.

## What We Should Do First

Start with the model onboarding workflow.

A customer will arrive with a model and a target device constraint. They need to know:

- whether their model can run on the chip
- which parts run on the analog core
- which parts stay digital
- what quantization does to accuracy
- how much conversion, memory movement, and fallback cost exists
- whether the result meets latency, energy, and reliability targets

So the first product milestone should be:

```text
Upload or register a model -> analyze operator support -> produce a hardware-fit report
```

This is useful even before full hardware deployment because it tells the customer whether their workload fits the architecture.

## Documents

- [connected-system-map.html](connected-system-map.html): start-here system map that explains the complete object flow from model graph to analog/digital placement, RTL/OpenLane evidence, backend import, claim readiness, and measured-board upgrade path.
- [analog-digital-execution-plan.html](analog-digital-execution-plan.html): ordered build plan that turns the goal into batches, artifacts, strict evidence gates, allowed claims, and blocked claims.
- [current-proof-ledger.html](current-proof-ledger.html): short browser-readable state ledger that separates current proof, local/simulated evidence, strict template proof, measured gaps, and blocked production claims.
- [page-contract-audit.html](page-contract-audit.html): audit page and verification command for the full visible HTML/markdown review surface against the shared object/constraint/evidence/claim contract.
- [master-review-path.html](master-review-path.html): start-here reading path across the frontend/backend workbench, proof pages, strategy pages, and hardware-lab evidence.
- [combined-system-end-to-end-workflow.html](combined-system-end-to-end-workflow.html): unified review path connecting the frontend/backend workbench, strategy pages, and the newer analog/digital/EDA hardware lab.
- [real-evidence-end-to-end-goal.html](real-evidence-end-to-end-goal.html): browser-readable next meaty goal for connecting real analog simulator output, compiler placement, RTL/OpenLane evidence, board runtime, power measurement, and final proof packages.
- [real-evidence-end-to-end-goal.md](real-evidence-end-to-end-goal.md): markdown source for the same goal.

The saved package flow now includes a `hardware_placement` artifact at `/deployment-packages/{package_id}/hardware-placement`. It translates the analyzed ONNX graph into analog candidates, digital-only regions, converter boundaries, sensitivity classes, fallback points, and governor fields. It is also persisted as `hardware-placement.json` inside the saved package directory and exported package zip. The frontend includes an `Import Hardware Lab` action that calls `/deployment-packages/{package_id}/hardware-lab-evidence` and imports the sibling `analog-digital-chip-design-eda` evidence batch into the selected package.
- [index.html](index.html): static frontend prototype for the model-fit workbench.
- [strategy-synthesis-and-next-pages.html](strategy-synthesis-and-next-pages.html): start-here synthesis that ties the strategy pages together and explains the remaining product gaps.
- [six-gap-end-to-end-goal.html](six-gap-end-to-end-goal.html): meaty end-to-end goal for customer intake, evidence matrix, timing budget, memory decision, benchmark suite, and simulator calibration.
- [customer-workload-intake-plan.html](customer-workload-intake-plan.html): concrete intake plan for collecting model, task, sensor, timing, power, update, environment, and safety inputs.
- [evidence-matrix-plan.html](evidence-matrix-plan.html): claim-to-evidence rulebook that says which proof is required before each claim is allowed.
- [timing-latency-budget-plan.html](timing-latency-budget-plan.html): full-loop timing plan for sensor, analog compute, ADC/DAC, digital support, safety override, and output paths.
- [memory-technology-decision-plan.html](memory-technology-decision-plan.html): memory/update decision plan for fixed-weight, periodic-update, adapter-update, and adaptive-blocked claims.
- [benchmark-suite-plan.html](benchmark-suite-plan.html): benchmark plan for strong-fit, partial-fit, and bad-fit Physical AI workloads.
- [hybrid-benchmarking-practical-pipeline.html](hybrid-benchmarking-practical-pipeline.html): practical seven-step pipeline for benchmarking a hybrid analog-plus-digital system end to end.
- [analog-vs-digital-validation-process.html](analog-vs-digital-validation-process.html): detailed side-by-side comparison of analog IMC proof steps against mature digital semiconductor validation processes.
- [simulator-calibration-plan.html](simulator-calibration-plan.html): plan for turning guessed analog assumptions into calibrated simulator profiles.
- [partner-ecosystem-variations.html](partner-ecosystem-variations.html): partner strategy variations by market wedge, partner type, stage, and named example players to evaluate.
- [investor-narrative-variations.html](investor-narrative-variations.html): investor story variations by audience, stage, and proof level.
- [proof-ladder-step-by-step.html](proof-ladder-step-by-step.html): plain-language 14-step proof ladder for answering whether a workload can run well.
- [physical-ai-opportunity-roadmap-digital-twins.html](physical-ai-opportunity-roadmap-digital-twins.html): Physical AI opportunity map and digital-twin ecosystem explainer.
- [physical-ai-robot-learning-implications.html](physical-ai-robot-learning-implications.html): robot-learning implications for sim-to-real, recovery, safety, tactile sensing, and compiler/chip requirements.
- [simulation-as-compiler-hat-plan.html](simulation-as-compiler-hat-plan.html): simulation-as-compiler and hardware-aware-training explainer.
- [aihwkit-tool-stack-plan.html](aihwkit-tool-stack-plan.html): AIHWKIT and analog simulation tool-stack explainer.
- [analog-mlir-to-silicon-compiler-plan.html](analog-mlir-to-silicon-compiler-plan.html): analog-mlir-to-real-silicon compiler plan.
- [hardware-tapeout-risk-roadmap.html](hardware-tapeout-risk-roadmap.html): hardware tape-out risk roadmap for chiplets, thermal, noise, memory, ADC, and pruning decisions.
- [company-roadmap-end-to-end.html](company-roadmap-end-to-end.html): full browser roadmap combining chip, software, proof, claims, and workbench context.
- [end-to-end-goal.md](end-to-end-goal.md): full build goal, milestones, and acceptance criteria.
- [architecture.md](architecture.md): detailed frontend and backend design.
- [frontend-design.md](frontend-design.md): concrete model-fit workbench layout and screens.
- [modality-quantization-spec.md](modality-quantization-spec.md): modality-aware quantization requirements.
- [external-tool-integration-spec.md](external-tool-integration-spec.md): phased plan for compiler, simulator, analog, digital, and hardware connections.
- [physical-ai-domain-map-spec.md](physical-ai-domain-map-spec.md): Physical AI domain map that connects mobility, ambient hardware, industrial systems, infrastructure, agriculture, defense/aerospace, sensory hardware, and robotics/VLA systems back to edge inference evidence.
- [physical-ai-readiness-implementation-spec.md](physical-ai-readiness-implementation-spec.md): concrete backend artifacts, frontend panels, archive files, and smoke tests needed to implement Physical AI and VLA-era readiness.
- [current-state-audit.md](current-state-audit.md): short status audit that says what is implemented, what is simulated, what remains missing, and what the next real external-evidence step should be.
- [source-check-register.md](source-check-register.md): source-checked company, product, and research examples with allowed-use and do-not-claim boundaries.

## Prototype Data

The frontend currently uses local mock backend responses under [mock-api](mock-api):

- `wearable-keyword.json`
- `smart-camera.json`
- `robot-sensor.json`

These files model the API payloads that a real backend would later return for fit summary, operator placement, boundary mapping, quantization, calibration, profiling, and recommendations.

## Real ONNX Backend Prototype

The first backend slice lives under [backend](backend).

Run it with the project-local virtual environment:

```bash
cd /home/mehtama1/git-repo/ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture/backend
./.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8025
```

The frontend can import a real `.onnx` file through that backend. A tiny sample model is available at:

```text
samples/tiny-mlp.onnx
```

Run the backend smoke test after the API is running:

```bash
cd /home/mehtama1/git-repo/ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture/backend
./.venv/bin/python scripts/smoke_end_to_end.py
```

Run the measured-evidence boundary check when editing claim readiness or evidence import code:

```bash
cd /home/mehtama1/git-repo/ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture/backend
./.venv/bin/python scripts/check_measured_evidence_readiness.py
```

That check proves the current local `board_runtime` and `power_thermal` artifacts remain structurally importable but are not measured-ready, while properly shaped measured board and meter payloads are accepted by the stricter measured-evidence gate.

Run the tool-evidence readiness check when editing analog simulator import rules:

```bash
cd /home/mehtama1/git-repo/ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture/backend
./.venv/bin/python scripts/check_tool_evidence_readiness.py
```

That check proves the current local analog artifact remains useful local evidence but is not yet detailed enough for the strict tool-evidence import path, while a properly shaped CrossSim/AIHWKIT-style payload is accepted by the analog simulator gate.

Run the strict evidence API check when editing frontend import modes or backend evidence endpoints:

```bash
cd /home/mehtama1/git-repo/ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture/backend
./.venv/bin/python scripts/check_strict_evidence_api.py
```

That check starts the FastAPI app on a temporary local port, copies the demo package into a temporary store, and proves the browser-facing strict endpoints accept calibrated simulator and measured payloads while rejecting local analog evidence from the strict simulator import path.

The strict tool-evidence API path is:

```text
POST /evidence/validate-tool?source_id=analog_error_simulation
POST /evidence/import-tool?source_id=analog_error_simulation
```

Use ordinary `/evidence/import` for local educational analog evidence. Use `/evidence/import-tool` only when the payload names a real analog simulator or calibrated analog evidence source, visible calibration profile, ADC/DAC assumptions, voltage/temperature boundary, and passing accuracy impact.

A strict simulator template is available at:

```text
review-package-demo/import-templates/analog-simulator-tool-evidence.template.json
```

Strict measured templates are available at:

```text
review-package-demo/import-templates/measured-board-runtime.template.json
review-package-demo/import-templates/measured-power-thermal.template.json
```

Run the page-contract audit when editing the HTML or markdown review path:

```bash
cd /home/mehtama1/git-repo/ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture
python3 scripts/check_page_contracts.py
```

That check keeps the writing aligned around the same object, constraint, evidence, and claim-boundary contract. It also catches stale local links, stale open/partial audit labels, and unsafe production or silicon claims that are not clearly framed as blocked.

The smoke test imports the sample ONNX model, runs quantization, runtime profiling, digital baseline comparison, package readiness, local evidence adapter generation, evidence imports, evidence gates, review report generation, runs the one-shot project evaluation flow, updates project settings, verifies run-history retrieval, verifies run comparison, and verifies the ZIP archive contents.

The frontend currently targets the restored local backend at:

```text
http://127.0.0.1:8025
```

The first hardware-lab evidence package created from the newer chip-design repo is:

```text
pkg-e931662a01293df2
```

Load that saved package from the frontend registry to review the Hardware Lab Evidence panel.

Projects are saved in `.data/projects.json`. Project evaluation runs are saved in `.data/runs.json`. Uploaded model records are saved in `.data/models.json`. Generated package reports and archives are saved under the backend `.data/packages/{package_id}` directory and can be fetched again through the project, model, and package retrieval APIs. The project evaluation flow uses the saved project context to generate analysis, quantization, runtime, baseline, workload-fit, system-boundary, Physical AI map, VLA readiness, weight-update readiness, calibration/drift readiness, control-boundary, sensor-boundary, source-check register, research-guide, concept-glossary, toolchain-readiness, compiler-ecosystem readiness, connection-playbook, adapter-execution-plan, adapter-connection-kit, adapter-evidence-templates, adapter-connection-self-test, adapter-integration-readiness, external-connector-contract, connector-implementation-guide, connector-test-harness, connector-acceptance-report, connector-backlog, connector-delivery-plan, connector-risk-register, measurement-evidence, evidence-gate, review, decision, rewrite, what-if, rewrite-plan, rewrite-work-order, and package artifacts in one backend call. Project settings can be updated, so the same model can be rerun against different target, modality, calibration, and runtime choices. The frontend shows saved runs, compares recent attempts by completed-inference metrics, fit, and evidence status, lets the user select saved projects, models, packages, and runs to resume earlier work, shows a focused run detail panel with artifact links and change notes, renders a workload fit matrix across audio, vision, detection, robotics, industrial, health, and edge LLM use cases, renders a system boundary report for analog compute, digital support, fallback work, ADC/DAC conversion, memory movement, host control, and idle energy, renders Physical AI readiness panels for domain fit, VLA/transformer fit, weight updates, calibration and drift, control handoff, sensor-to-tensor boundaries, compiler ecosystem, and guarded source-checked examples, renders a research guide for analog and in-memory AI papers, renders a concept glossary for plain-language interview terms, renders a toolchain readiness report for model import, quantization, compiler mapping, analog simulation, board runtime, measurement, accuracy validation, profiling, and customer handoff, renders a connection playbook for wiring real compiler, simulator, board, power, and accuracy tools, renders an adapter execution plan for configure/run/normalize/validate/import/archive steps, renders an adapter connection kit for env vars, raw inputs, raw outputs, normalized artifact fields, and API calls, renders adapter evidence templates for the JSON payloads external tools should emit, renders a connection self-test for adapter probes and missing service configuration, renders adapter integration readiness for ready paths, blockers, and next connection priorities, renders the external connector contract for request, response, health, failure, validation, and import behavior, renders a connector implementation guide for rollout order, implementation steps, done criteria, and claim boundaries, renders a connector test harness for probe, run, validation, import, and failure-safety checks, renders a connector acceptance report for current passed, blocked, and pending connector status, renders a connector backlog for owner-facing tasks that close acceptance gaps, renders a connector delivery plan for milestone order and owner gates, renders a connector risk register for delivery risks, triggers, mitigations, and evidence needed, renders an interview brief with first-principles framing and questions to ask, renders an interview drill with likely questions and answer outlines, renders a decision report that says whether the run is a good fit, needs rewrite, needs measurement, or is not a fit yet, lists concrete rewrite suggestions for operator, boundary, precision, and model-shape changes, runs low-confidence what-if estimates before the user changes the real model, builds a rewrite plan with graph, compiler, runtime, validation, and evidence steps, builds a work order with owners, done criteria, gates, and evidence attachments, shows which compiler, simulator, board, power, thermal, and accuracy artifacts are still required before measured claims are allowed, probes adapter connections and evidence contracts from the UI, can run each local evidence adapter one at a time, can run all local evidence adapters through the `Run Local Evidence` button, imports generated evidence into the current package, recalculates which lab claims are supported, blocked, or need review, and exposes an evidence brief that says what to say clearly, what not to claim, and what evidence is still missing while keeping production readiness blocked.

The adapter panel includes an accuracy dataset path field. When `accuracy.local-task-check` runs, the frontend passes that path as `dataset_path`, so the backend can produce dataset-backed task-accuracy evidence instead of only synthetic accuracy evidence. The run card then shows dataset ID, record count, baseline metric, candidate metric, delta, tolerance, and pass/fail. Adapter run cards also preview the normalized evidence through the same backend validation endpoint used by custom JSON import, so adapter-produced artifacts show before/after claim impact before they are saved.

Local adapter runs now attach a simulated lab profile to their evidence. The profile says which scenario was assumed, such as wearable, smart camera, robot, industrial sensor, or small edge LLM. It records the assumed analog precision, ADC/DAC precision, memory setup, voltage and temperature range, duty cycle, host overhead, and whether the evidence is measured hardware. Today these profiles make the local workflow closer to a real lab handoff because the assumptions are explicit and repeatable. They still do not replace a real compiler, circuit simulator, board trace, power meter, thermal setup, or task dataset.

For connector practice without lab hardware, start the backend with `ANALOG_AI_REPLAY_FIXTURE_MODE=1`. Board runtime and power/thermal adapter probes then behave like a configured replay path, and adapter runs write `external-replay-request.json` plus `external-replay-response.json` beside the normalized evidence. This tests the same handoff pattern a real board service or meter service would use: raw request, raw response, normalized artifact, validation, import, and claim review. It remains a replay fixture, so the UI and payloads keep `not_measured_hardware: true`.

The connector acceptance panel now separates `replay accepted` from true external acceptance. Replay accepted is useful because it proves the workflow shape works end to end. It is not proof that a board, meter, compiler, or lab setup exists.

Current vendor, product, and roadmap examples are tracked in [source-check-register.md](source-check-register.md). The frontend should keep examples conceptual until a source-checked record has an official source, checked date, allowed use, and do-not-claim boundary.

The frontend also includes a custom evidence import panel. Select a source such as `analog_error_simulation`, `board_runtime`, `power_thermal`, or `task_accuracy`, choose ordinary evidence, strict simulator/tool evidence, or strict measured board/power evidence, start from the source-specific JSON template or load a `.json` evidence file, edit the normalized artifact if needed, and validate it before import. Validation calls the backend, checks the same schema and structural rules used by import, then recalculates claim readiness in memory to show before/after status, still-missing evidence, and quality warnings without saving the artifact. Strict simulator/tool mode calls `/evidence/validate-tool` and `/evidence/import-tool`; strict measured mode calls `/evidence/validate-measured` and `/evidence/import-measured`. Import then saves the artifact and refreshes claim readiness, measurement evidence, evidence audit, and evidence brief panels.

The current static frontend is being served in this workspace from:

```text
http://127.0.0.1:8024/analog-in-memory-ai-inference/software-architecture/
```
