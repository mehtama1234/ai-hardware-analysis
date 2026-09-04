# Combined AIMC Workbench End-To-End Goal

Build one connected system from the restored product workbench and the newer hardware lab.

The system should answer:

Can this model safely run part of inference on analog in-memory hardware, and what evidence supports that answer?

## Existing Pieces

The old repo already has a real software workbench:

- frontend workbench page
- FastAPI backend
- ONNX model import
- graph analysis
- quantization and runtime estimates
- model, project, run, and package store
- evidence validation and import
- evidence gates
- claim readiness
- adapter registry
- deployment package archives
- strategy, proof, compiler, simulator, benchmark, memory, tapeout, partner, and investor pages

The newer repo has the hardware proof slice:

- analog nonideality measurement stack
- transformer-impact experiment
- model-impact governor request generator
- Verilog governor and scheduler logic
- generated RTL test cases
- RTL simulation checks
- Yosys synthesis reports
- OpenLane prep and successful physical-design result for the pipelined scheduler/governor
- static concept, lab, paper, and research pages

The goal is to stop treating these as two related folders. They should become one workflow.

## Core Principle

Analog in-memory compute is not a faster version of normal digital inference. It changes where the work happens.

In a digital accelerator, the system repeatedly moves numbers from memory into arithmetic units, multiplies them, adds them, rounds the result, and moves the result again. In an analog in-memory tile, the stored weight and the multiply-add operation are partly the same physical object. The weight sits in a device. The input becomes a voltage. The output is a current or charge that must be converted back into a digital number.

That trade is useful only if the saved movement and arithmetic are larger than the new costs:

- converter cost
- noise
- drift
- wire drop
- limited precision
- calibration
- fallback control
- verification burden

So the real question is not "can a transformer run on analog?" The real question is:

Which parts of this model can tolerate this physical error, under this timing and power budget, with this digital controller watching the failure modes?

The whole system should be organized around that question.

## End-To-End Flow

```text
model enters old workbench
  -> backend imports ONNX
  -> backend analyzes operators
  -> placement pass marks analog candidates and digital-only regions
  -> hardware lab estimates analog error for candidate regions
  -> model-impact lab checks whether that error changes important choices
  -> request generator compresses the result into hardware control fields
  -> RTL governor and scheduler decide allow, throttle, reroute, or fallback
  -> synthesis and OpenLane evidence show the controller can become physical logic
  -> evidence exporter emits normalized hardware-lab evidence
  -> old backend imports that evidence into the package
  -> frontend shows the supported claim, blocked claim, and next missing proof
```

## The Argument Each Page Must Help Prove

### 1. The model is the first object

The first object is not a chip. It is the model graph. A model graph tells us where repeated weighted sums happen, where values are normalized, where attention choices are made, where logits are produced, and where control decisions become fragile.

The old backend already imports ONNX and describes operators. The next improvement is to turn that graph summary into placement input. Each operator should receive a simple decision:

- analog candidate
- digital only
- unknown until sensitivity is measured

This decision should not be based on operator names alone. It should be based on what the operator does to the answer. A projection with stable downstream behavior may be a good analog candidate. A small operation near a hard choice may be a bad one.

Current status: the restored backend now builds a package artifact called `hardware_placement`. It derives analog candidates, digital-only regions, converter boundaries, model sensitivity classes, fallback points, and governor fields from the analyzed model graph. The first live package reports 5 operators, 2 analog candidates, 4 converter boundaries, and 3 fallback points.

The hardware lab now imports this artifact through `scripts/import_backend_hardware_placement.py`. That script writes:

- `measurements/backend-hardware-placement.json`
- `measurements/backend-hardware-placement-governor-input.csv`
- `measurements/backend-hardware-placement-governor-input.md`

The model-impact governor generator appends those backend-derived rows to the generated governor requests. The RTL checker now sees both the local transformer sensitivity cases and the backend graph placement cases.

The full cross-repo loop can now be checked with:

```bash
python3 scripts/prove_cross_repo_aimc_loop.py
```

That proof checks backend health, backend placement, lab import, governor generation, RTL trace, evidence export, backend evidence import, and claim readiness in one command.

It also writes the persistent review record:

- `evidence/aimc-hardware-lab/cross-repo-loop-proof.json`
- `evidence/aimc-hardware-lab/cross-repo-loop-proof.md`

That report is the shared anchor for the old pages and the new pages. Any page that says the repos are connected should point back to this proof or to one of the artifacts it names.

The placement handoff itself is explained in `backend-hardware-placement-first-principles.md`.

### 2. Placement is a boundary, not a preference

The placement pass draws the line between analog work and digital work. That line creates obligations.

If a layer moves to analog, the system must say where the DAC sits, where the ADC sits, what numeric range is expected, how much residual error is allowed, and where the digital fallback can resume. If those objects are not named, the placement is only a drawing.

The compiler pages should therefore stop at concrete records:

- operator id
- tensor shape
- analog tile candidate
- digital-only reason
- converter boundary
- expected error source
- sensitivity class
- fallback point
- scheduler/governor fields

### 3. The analog tile is a physical measurement chain

An analog matrix multiply is not a clean mathematical multiply. The chain is:

```text
digital input
  -> DAC level
  -> row voltage
  -> device conductance
  -> column current
  -> wire and device error
  -> ADC code
  -> digital correction
```

Every step can change the result. The analog lab therefore should not report only "accuracy." It should report the physical cause of the error: converter quantization, row drop, saturation, drift, programming error, current-range limits, or calibration mismatch.

The evidence is useful when it says: for this operating point, the final residual is this large, and this is why.

### 4. Model sensitivity decides whether the error matters

The same residual can be harmless in one part of the model and harmful in another.

A hidden projection may absorb small noise because later operations smooth it. Attention scores may not absorb it because a small shift can change which token receives weight. Logits may not absorb it because the final choice can flip.

So the model-impact lab is the bridge between physics and model behavior. It should translate analog residual into a model-level statement:

- this location tolerates the current residual
- this location needs lower residual
- this location should stay digital
- this location can use analog only with fallback

### 5. Digital control makes analog usable

The digital controller is not a wrapper around the analog tile. It is the part that makes the analog tile safe to use.

It receives the facts that analog alone does not know: residual budget, sensitivity class, cumulative error, queue pressure, tile health, fallback target, and service deadline. Then it chooses whether to allow analog execution, delay, reroute, throttle, or fall back to digital.

This is why the RTL matters. The controller is the place where the conceptual rule becomes a hardware rule.

### 6. EDA evidence changes the type of claim

A Python result says the idea was simulated. An RTL check says the control rule can be represented as logic. Synthesis says the logic can be lowered into gates in a selected flow. OpenLane says the selected digital block can be placed and routed under the recorded setup.

Those are different kinds of evidence. They should not be collapsed into one word like "validated."

The frontend should show the exact evidence level:

- local simulation
- RTL checked
- synthesized
- OpenLane routed in educational flow
- measured board trace
- measured silicon
- blocked

### 7. The product answer must refuse unsupported claims

The final workbench answer should be useful because it is strict.

It can say: this model slice has a supported local-lab placement and accuracy claim. It can also say: latency needs review because the runtime trace is local, energy needs review because the current power/thermal record is an OpenLane-derived estimate rather than synchronized measured hardware power, and production readiness is blocked because there is no calibrated silicon or signoff evidence.

That refusal is not a weakness. It is the product boundary.

The next proof boundary is measured board and power evidence. `board-and-power-measurement-boundary.md` defines the exact fields needed to upgrade the current local `board_runtime` and `power_thermal` records into synchronized measured evidence. Until those fields exist, the system should keep `C2` and `C3` in needs-review state.

## Development Work

### 0. Seamless Review Spine

Make the pages read in a clear order before adding more machinery.

Done means:

- the old repo has a master review path
- the old repo has a combined workflow page
- the new repo has a bridge page
- the new repo has a combined build goal
- the new repo has an evidence ledger
- the new repo has a cross-repo proof report
- each page states what it consumes and what it produces

## One Meaty End-To-End Goal

Make the old workbench and the new hardware lab read as one system, not two linked notebooks.

The work is done when a reviewer can start from the old frontend, ask whether a model should use analog in-memory compute, follow the answer into the hardware lab, inspect the analog, digital, RTL, synthesis, OpenLane, and evidence records, return to the backend claim-readiness page, and see exactly which claims are supported, which need review, and which are blocked.

The pages should be rewritten around five plain objects:

- model graph: what computation is being moved
- placement boundary: where analog starts and digital resumes
- error source: what physical effect can change the number
- governor rule: what the digital controller does when the error matters
- evidence record: what proof exists and what it does not prove

For each page, add the same four fields:

- consumes: the artifact or decision the page starts from
- produces: the artifact or decision the page emits
- supports: the narrow claim the page can justify
- refuses: the stronger claim the page must not make yet

The first pass should connect existing pages without inventing new results. The second pass should enrich pages that are still shallow: placement, analog error, model sensitivity, governor control, RTL proof, OpenLane evidence, and backend claim readiness. The third pass should add missing pages only where the chain has a real gap.

### 1. Hardware-Lab Evidence Exporter

Create a script in this repo that reads the current generated artifacts and exports normalized evidence records.

Current status: first version exists at `scripts/export_aimc_hardware_lab_evidence.py`. It currently exports six backend-compatible evidence records: compiler mapping, analog error, local RTL/runtime, local OpenLane-derived power/thermal estimate, task accuracy, and physical flow. Because the governor-request CSV now includes backend-derived placement rows, the exported compiler/runtime evidence carries the first model-graph-to-lab connection.

Inputs:

- analog measurement CSV files
- transformer-impact CSV and Markdown
- model-impact governor request CSV
- RTL checker output
- synthesis summaries
- OpenLane metrics summaries
- project validator and bridge-check result

Outputs:

- JSON evidence records compatible with the old backend import path
- one Markdown evidence ledger for human review

Current exported files:

- `evidence/aimc-hardware-lab/manifest.json`
- `evidence/aimc-hardware-lab/import-batch.json`
- `evidence/aimc-hardware-lab/compiler_mapping.json`
- `evidence/aimc-hardware-lab/analog_error_simulation.json`
- `evidence/aimc-hardware-lab/board_runtime.json`
- `evidence/aimc-hardware-lab/power_thermal.json`
- `evidence/aimc-hardware-lab/task_accuracy.json`
- `evidence/aimc-hardware-lab/physical_flow.json`

Each record should include:

- claim
- status
- source artifact
- command to reproduce
- result summary
- allowed wording
- not allowed wording
- next action

### 2. Old Backend Import Connection

Add a hardware-lab evidence adapter to the old backend.

Current status: live import has been proven through the old FastAPI backend. The backend now exposes `POST /deployment-packages/{package_id}/hardware-lab-evidence`, which reads this repo's exported batch and attaches it to the selected package. The ordinary exported batch has 6 records: compiler mapping, analog error, local runtime, local power/thermal estimate, task accuracy, and physical flow. The backend also imports the strict analog simulator/tool sidecar separately. Package `pkg-e931662a01293df2` now imports with `accepted 6`, `rejected 0`, and `strict_tool_evidence_imported true`.

It should:

- find the evidence export from this sibling repo
- validate every record
- attach records to a deployment package
- recalculate claim readiness
- expose the imported hardware-lab evidence through existing package endpoints
- refresh prior local hardware-lab imports without overwriting stronger non-local evidence

The backend should not treat these records as measured silicon. It should label them as local simulation, RTL verification, synthesis, OpenLane educational-flow evidence, or blocked external evidence.

Current backend behavior after import:

- compiler placement claim: supported
- analog/task accuracy lab claim: supported
- latency claim: needs review because the runtime trace is local RTL simulation, not a board trace
- energy claim: needs review because local power/thermal evidence is attached, but it is an OpenLane-derived estimate rather than synchronized measured hardware power
- production readiness: blocked

### 3. Frontend Hardware Evidence Panel

Add one panel to the old frontend workbench.

Current status: first version exists in `ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture/index.html` as `Hardware lab evidence`.

The frontend also has an `Import Hardware Lab` button. It builds or selects a package, calls the backend hardware-lab import endpoint, reloads the package, and then shows the updated evidence audit, claim readiness, evidence brief, and hardware-lab panel.

It should show:

- analog error evidence
- model-sensitivity evidence
- governor request evidence
- RTL verification evidence
- synthesis evidence
- OpenLane evidence
- allowed claim
- blocked claim
- next missing proof

The panel should be readable without knowing ADC, DAC, RTL, OpenLane, or AIHWKIT in advance. Each term should be tied to the object, constraint, design move, and failure mode.

Current behavior on package `pkg-e931662a01293df2`:

- compiler mapping: local lab / supported
- analog accuracy: local lab / supported
- runtime trace: local lab / needs review
- energy proof: local estimate / needs review
- production: blocked

### 4. Model Graph To Placement Mini-Pass

Connect the old ONNX analyzer to a placement pass.

For each operator, emit:

- operator name
- operator kind
- analog candidate or digital-only
- reason
- required DAC boundary
- required ADC boundary
- expected error source
- model sensitivity class
- fallback point
- scheduler/governor input fields

The pass should begin with a tiny transformer-style graph before broad model support.

### 5. AIHWKIT Adapter

Use IBM AIHWKIT as an external tool first.

Do not fork it first.

The adapter should:

- check whether AIHWKIT is installed
- run a tiny model through AIHWKIT when available
- compare AIHWKIT-style analog residuals against the local analog nonideality stack
- export evidence
- skip cleanly with a useful message when AIHWKIT is missing

Current status: AIHWKIT is installed in the optional simulator environment and is part of the executable bridge. The wrapper at `scripts/check_aimc_simulator_adapters.py` imports AIHWKIT, runs a smoke fixture, and writes availability evidence. The bridge also runs small, workload-shaped, tensor-shaped, trained-weight, projection-stack, transformer-MLP, deep transformer-MLP-stack, and attention-shaped payloads. The guarded importer accepts AIHWKIT payloads only when their residual is inside the local positive-claim threshold; the larger current AIHWKIT replays run but are correctly rejected from positive claims when their residual is too high.

Fork or patch AIHWKIT only if the adapter cannot expose the needed per-layer or per-device evidence.

### 6. Crossbar Layout-Risk Adapter

Build a local CrossSim-style layout-risk adapter before depending on a full external CrossSim flow.

It should estimate:

- tile size
- row wire drop
- column current range
- ADC range
- DAC precision
- bit slicing
- saturation risk
- programming and drift risk
- residual risk

The output should feed both the hardware lab and the old backend evidence package.

Current status: CrossSim is installed in the same optional simulator environment and is part of the executable bridge. The wrapper records CrossSim as available in `evidence/aimc-simulator-adapters/simulator-adapter-status.json`. The bridge runs CrossSim across the same fixture family and sends its strict payloads through the guarded importer. Passing CrossSim payloads can support bounded simulator evidence, but they still do not prove board latency, measured energy, analog macro layout, calibrated silicon, or tapeout readiness.

### 7. Integrated Runtime Controller

Generate one trace that combines:

- model placement
- analog residual
- model sensitivity
- tile health
- queue pressure
- cumulative error

The generated Verilog cases should prove:

- fixed projection can use analog
- stressed projection falls back
- attention-score paths fall back
- logits paths fall back
- unhealthy tiles fall back
- overloaded tiles delay or reroute
- accumulated error blocks analog

### 8. Unified Site Review Path

Create an obvious review path across both sites:

1. old workbench combined workflow page
2. old frontend prototype
3. old proof ladder
4. old evidence matrix
5. old compiler and AIHWKIT pages
6. new architecture-to-lab bridge
7. new analog lab page
8. new digital RTL page
9. new EDA/OpenLane page
10. new evidence ledger

## Acceptance Criteria

The combined goal is complete when:

- one sample model enters the old backend
- ONNX graph analysis produces the `hardware_placement` artifact
- placement output drives analog/digital scheduling and generated governor cases
- local analog error and layout risk are generated
- model sensitivity is checked
- governor requests are generated
- RTL simulation checks the generated decisions
- synthesis and OpenLane evidence are linked
- hardware-lab evidence exports as JSON
- old backend imports the evidence
- old frontend shows the imported hardware evidence
- both sites show the same end-to-end story
- one command can rerun the connected proof slice with `scripts/prove_cross_repo_aimc_loop.py`
- the bridge records whether AIHWKIT and CrossSim actually ran or were skipped, without upgrading claims when they were skipped

## Writing Standard For Every Page

Each page should use the same plain structure:

- the concrete object being discussed
- the constraint that makes the object hard
- the design move used to handle the constraint
- the evidence that currently supports the move
- the failure mode that remains
- the next artifact needed to make the claim stronger

Avoid broad words that hide the mechanism. Do not say "optimized," "robust," "efficient," or "validated" unless the page immediately says what was optimized, what failure was resisted, what quantity improved, and what evidence proves it.

Use the shortest accurate term. For example:

- say "ADC bits" instead of "conversion capability"
- say "row voltage drop" instead of "analog degradation"
- say "fallback to digital" instead of "resilience"
- say "OpenLane routed under this setup" instead of "physical design complete"
- say "blocked because measured power is missing" instead of "needs more validation"

## First Claim Boundary

Allowed claim:

This combined system is a working prototype for model-to-evidence analog in-memory AI hardware review. It connects model analysis, analog error simulation, model sensitivity, digital runtime control, RTL verification, synthesis, OpenLane evidence, and claim-readiness reporting.

Not allowed claim:

This is not a production analog foundation-model chip. It does not yet prove calibrated silicon, real board runtime, measured power, real thermal behavior, full CrossSim or AIHWKIT agreement, signoff-grade physical verification, or tapeout readiness.

## Meaty End-To-End Program Goal

The next program goal is to take a portfolio of representative AI workloads
through one common model-to-chip workflow and produce an evidence-backed answer
for each one:

```text
model and dataset
  -> digital reference and task metric
  -> graph analysis and operator sensitivity
  -> analog/digital/SRAM placement
  -> tile, bit-slice, converter, and calibration plan
  -> workload-shaped analog error replay
  -> compiled execution schedule
  -> physical converter and source-interface validation
  -> guarded runtime with digital fallback
  -> PVT, mismatch, noise, settling, and thermal analysis
  -> extracted/layout or board evidence
  -> end-to-end accuracy, latency, energy, and reliability comparison
```

The program is complete only when the same compiler, runtime contract, evidence
schema, and claim gates are used across the workload portfolio. A workload may
pass the software and simulator gates while remaining physically blocked. That
must be visible in the report; a simulator pass must never silently become a
chip claim.

The machine-readable tracking record is
`evidence/aimc-hardware-lab/end-to-end-workload-portfolio.json`. It is the
authoritative index for workload IDs, current proof level, source evidence, and
the next required proof.

### Workload Portfolio

The following portfolio is the scope to implement and test. It deliberately
starts with controlled fixtures, then moves toward task workloads and more
difficult transformer behavior.

| stage | workload | computation exercised | current state | next proof |
| --- | --- | --- | --- | --- |
| 1 | `tiny-mlp-task-v1` | small fixed-weight MLP and classification path | task/governor evidence, shared compiler package, and guarded fallback trace exist | replace the fixture task with a versioned external or captured dataset and rerun task-level digital-versus-hybrid accounting after SAR closure |
| 1 | `projection-stack-v1` | repeated dense fixed-weight projections | CrossSim and AIHWKIT adapter evidence exists; CrossSim is connected to the shared target schedule and guarded runtime | add measured converter cost and physical compatibility after the SAR gate |
| 1 | `wake-nonwake-audio-v1` | edge audio classifier with repeated inference and a real task metric | generated-audio rehearsal reaches F1 `1.0`; compiler selects digital because converter overhead is not amortized | use versioned external or captured audio, then compare digital and hybrid latency/energy |
| 2 | `transformer-mlp-block-v1` | gate/up/down/output projections, nonlinear mix, and residual add | calibrated CrossSim replay passes with relative L2 about `4.94e-8`; shared compiler and guarded fallback trace exist | enable analog only after SAR closure, then measure task metric and system cost against the digital baseline |
| 2 | `attention-block-v1` | static Q/K/V/output projections plus dynamic scores, Softmax, and value mixing | calibrated CrossSim replay passes with relative L2 about `4.18e-8`; dynamic attention remains digital/SRAM and the shared schedule is generated | quantify projection-to-digital attention traffic, then test analog projection enablement after SAR closure |
| 2 | `deep-transformer-mlp-stack-v1` | three repeated transformer-style MLP blocks and 12 fixed-weight MatMuls | calibrated CrossSim replay passes with relative L2 about `6.7e-8`; shared compiler, runtime estimate, and fallback trace exist | close physical converter compatibility and full hybrid execution comparison |
| 3 | `compact-vision-or-defect-v1` | convolution or im2col-like repeated matrix work with task-level classification/detection | imported intake placement package exists; no real image dataset or task result yet | select a versioned model/dataset and prove whether analog reuse offsets converter cost |
| 3 | `wearable-keyword-v1` | always-on wearable keyword detection with feature extraction and a compact classifier | imported intake placement package exists; no real audio dataset or task result yet | freeze captured keyword data, false-accept/false-reject metric, and sensor-to-model accounting |
| 3 | `smart-camera-inspection-v1` | camera preprocessing plus compact vision/defect classification | imported intake placement package exists; no real image dataset or task result yet | freeze an image dataset and compare preprocessing, SRAM traffic, and analog reuse |
| 3 | `small-language-model-serving-v1` | token projections, MLP, attention, normalization, KV-cache movement, and logits | synthetic next-token rehearsal passes at `0.9375` versus `1.0` baseline; normalized policy replay and shared compiler trace exist | replace the synthetic rehearsal with a real token dataset and end-to-end KV-cache serving trace with digital attention boundaries |
| 4 | `robot-sensor-policy-v1` | sensor preprocessing, transformer policy inference, and deterministic control handoff | imported intake placement package exists; control readiness is not accepted | freeze sensor logs, control/jitter safety metric, and the model-to-controller boundary |
| 4 | `vla-or-physical-ai-v1` | perception, transformer policy, and action/control path | imported intake placement package exists; no task or control-safety result yet | attempt only after the preceding workload classes pass physical, runtime, and safety gates |

The fixture workloads are not substitutes for real task validation. They isolate
mapping, calibration, and error propagation so the hardware contract can be
debugged. The audio, vision, and language workloads establish whether the same
architecture has useful end-to-end behavior under realistic data and metrics.

### Remaining Work Packages

1. **Close the physical converter path.** The selected low-source PMOS-only
   candidate now passes nominal `16/16` threshold calibration, legal range,
   spacing, injective mapping, and `5/5` representative calibrated SAR
   conversions. The remaining work is same-topology PVT, mismatch/noise,
   settling, continuous multicycle SAR, extraction, and post-layout evidence;
   the analog path remains guarded until those gates pass.

2. **Freeze the hardware contract.** Record tile dimensions, cell and slice
   precision, DAC/ADC ranges, accumulation width, SRAM capacity and bandwidth,
   calibration interval, voltage/temperature range, and fallback capacity in a
   versioned hardware profile. The current contract is
   `educational-hybrid-tile-v1`; every workload result and the shared portfolio
   acceptance contract must name that profile.

3. **Make one compiler output authoritative.** Every operator must have exactly
   one placement, tile mapping, bit-slice rule, converter crossing, SRAM move,
   calibration profile, sensitivity budget, and fallback destination. Include
   negative tests where the compiler refuses analog placement.

4. **Run the portfolio through common evidence gates.** For each workload,
   generate the digital baseline, model-level hybrid comparison, runtime trace,
   converter assumptions, analog residual report, and claim boundary. Keep
   simulator, RTL, synthesis, extracted/layout, board, and silicon evidence as
   separate levels. Validate the portfolio manifest with
   `python3 scripts/validate_aimc_workload_portfolio.py` before accepting a
   new workload or changing its proof status.
   The reproducible software-side vertical-slice regression is available as
   `python3 scripts/run_aimc_end_to_end_regression.py`; it runs the transformer
   schedule, model-backed task check, governor, guarded runtime, report build,
   and both validators in one recorded run.

5. **Close physical robustness.** For the selected converter and analog tile,
   measure settling, PVT, mismatch, noise, drift, supply variation, legal
   common-mode range, and calibration age. The analog path is enabled only when
   the governor can prove the current workload and tile remain inside their
   task-sensitive error budgets.

6. **Measure system economics.** Compare the same workload and dataset on the
   same target using digital-only and hybrid execution. Report end-to-end
   latency, energy per inference, power, thermal behavior, SRAM traffic,
   converter crossings, analog utilization, fallback rate, and task metric.
   Array-only TOPS/W is not an acceptance result.

7. **Upgrade to board and silicon evidence.** Tie measurements to a board,
   firmware, package, workload, model, dataset, and synchronized runtime/power
   trace. Keep production readiness blocked until calibrated silicon, reliability,
   thermal, packaging, and signoff evidence exist.

### Program-Level Acceptance Criteria

The program earns an end-to-end pass only when:

- at least one real task workload and its digital baseline are reproducible;
- all staged fixture workloads use the same compiler/runtime/evidence schema;
- the compiler can select analog, digital, mixed, or fallback execution per
  operator for defensible reasons;
- the physical converter passes full-code, full-range, calibrated SAR tests;
- analog error is evaluated at the model output and task metric, not only at a
  circuit node;
- PVT, mismatch, noise, settling, calibration-age, and thermal gates are
  recorded for the enabled analog path;
- digital-only and hybrid runs use the same model, data, metric, and target
  accounting rules;
- a measured board result exists before making latency, energy, or thermal
  claims about hardware; and
- every report states the strongest supported claim and the next blocked claim.

The immediate target is therefore not "run a large language model on analog."
It is: **close one physically valid converter, compile the transformer and edge
workload portfolio through the same mixed-memory runtime, and demonstrate one
fair task-level digital-versus-hybrid comparison with measured system costs.**
