# Platform Completion End-To-End Goal

Start from the [Connected System Map](connected-system-map.html). This goal uses the same contract: object, constraint, design move, evidence, allowed claim, refused claim, and next handoff.

Related architecture roadmap:

- [Platform Roadmap Architecture](platform-roadmap-architecture.md)

## The Meaty Goal

Build a complete evidence workbench that helps a user answer one question:

```text
Can this workload run well on this analog chip, what proof do we have, what breaks, and what must be built or measured next?
```

## End-To-End North Star Goal

Create one highly readable roadmap and proof experience that lets an executive, customer, investor, and engineering team understand the analog chip company from the same source of truth.

The experience should start with the business reason for the company: more AI is moving into machines, sensors, vehicles, robots, industrial systems, and battery-powered devices, where cloud calls are too slow, power is limited, and the system must react locally. It should then explain the company thesis in plain language: analog in-memory compute may help when the workload spends most of its time doing repeated matrix math, but it only becomes a real product if the chip, compiler, runtime, board, calibration flow, and proof package work together.

The page should not read like a technical paper, a pitch deck, or a collection of isolated notes. It should read like a guided decision room. A reader should move from "why this matters now" to "what the chip does" to "where analog helps" to "where digital logic is still required" to "what has been proven" to "what is blocked" to "what we build next." Every section should explain the idea first, then name the technical term only after the reader understands why it matters.

For executives, the goal is fast understanding without hidden assumptions. They should be able to answer: why now, who needs this, what first market is realistic, what proof exists today, what proof is missing, what claims are safe, what claims are not safe, and what funding or partnership would unlock the next proof level.

For engineering teams, the goal is build clarity. They should be able to answer: what must change in silicon, what must change in the compiler, what must change in the runtime, what files the backend must store, what the frontend must show, what tools can be reused, what must be custom-built, what lab data must be imported, and what tests prevent the company from overstating results.

The main artifact should be an interactive HTML roadmap, supported by saved JSON evidence files and a written goal document. The HTML should include diagrams and small animations that reduce confusion rather than decorate the page. The diagrams should show the full path from user workload, to model intake, to analog/digital partitioning, to simulator or compiler evidence, to board and lab results, to final claim boundaries. The animations should teach proof levels: market context is not a measurement, an estimate is not a simulation, a simulation is not a board run, and a board run is not a repeated product claim.

The roadmap must include the concrete product changes needed to make the chip real:

- silicon changes: calibration support, temperature monitors, voltage monitors, tile health checks, fallback behavior, power measurement points, board links, runtime status, and debug traces
- compiler and runtime changes: tiling, bit-slicing, transformer and VLA partitioning, ADC and DAC scheduling, calibration metadata, weight update metadata, runtime package generation, failed-calibration handling, rollback handling, and board command generation
- backend changes: package storage, model summary, simulator imports, compiler reports, board runtime logs, power traces, thermal traces, firmware metadata, task accuracy results, weak-tile lists, correction values, and source notes
- frontend changes: plain-language primer, top blocker board, interactive journey, stack change map, evidence ladder, toolkit map, board proof view, calibration proof view, final verdict, export map, and readiness audit
- proof changes: every claim must point to an artifact that says whether it is source context, estimate, simulator result, compiler result, board measurement, lab measurement, task result, or missing proof

The writing bar is strict. No section should assume the reader already knows terms such as ADC, DAC, MLIR, VLA, calibration, bit-slicing, tile, drift, JTAG, PCIe, or runtime package. If a term appears, the page should explain what it means, why it matters, what can go wrong, and what proof would make it credible. Avoid broad language such as "revolutionary," "seamless," "optimized," "robust," or "production-ready" unless the sentence immediately states the exact measurement or artifact that supports it.

The final outcome should be a review package that can stand on its own after the meeting. A reader should be able to open it later and see the workload, chip target, assumptions, evidence, missing proof, safe claims, blocked claims, next engineering work, and artifact links without needing someone to explain what was meant verbally.

The platform is not only a frontend page and not only a simulator wrapper. It must become a full workflow:

1. user brings a model, workload, chip target, and success target
2. platform reads the model
3. platform shows what may fit analog compute
4. platform runs or imports proof from simulators, compilers, board tests, power tests, and task tests
5. platform separates estimates from real proof
6. platform shows what is broken or missing
7. platform gives the user the next engineering work
8. platform exports an auditable package for engineering, customer, or investor review

## What Counts As Complete

The platform is complete when a user can start from one workload and finish with a review package that says:

```text
Fit: yes, partial, no, or unknown.
Proof: what was measured, simulated, compiled, estimated, or only source-checked.
Breaks: the exact model, chip, compiler, runtime, sensor, power, task, or update gaps.
Safe claim: what can be said today.
Do not claim: what is not proven yet.
Next work: what must be built, connected, simulated, or measured next.
Archive: complete evidence package for review.
```

## Executive And Engineering Readability Goal

The product page and review package must be readable by two groups at the same time.

Executives, investors, customers, and business leaders should understand the page without knowing analog chip terms. They should be able to see why the company exists, why this market is moving now, what the chip is trying to do, what has been proven, what has not been proven, and what money or engineering work unlocks the next proof level.

Engineers should be able to use the same page as a build map. They should be able to see which frontend panels are needed, which backend artifacts are needed, which external toolkits support each proof step, which compiler changes are required, which board or lab measurements are missing, and which tests prevent the platform from making unsupported claims.

The page must repeatedly answer this question:

```text
Can this workload credibly run on this analog chip,
what proof exists,
what breaks,
and what must be built or measured next?
```

### Readability Principles

Every section must explain the idea before using the technical term heavily. For example, the page should explain that calibration means correcting for real chip behavior before it talks about calibration profiles, weak-tile lists, or drift tables.

Every important claim must include the reason behind it. The page should not only say that we need a hybrid chip. It should explain that analog arrays are good for repeated matrix math, while digital logic is still needed for changing decisions, exact control, model steps such as Softmax and LayerNorm, memory scheduling, and safety behavior.

Every external toolkit must be described by what it gives the user. The page should not lead with tool names. It should lead with the user question, such as "Will analog noise hurt accuracy?" or "Will memory movement erase the speed benefit?" The toolkit name appears after the benefit is clear.

Every roadmap item must say what happens now, what happens later, and what proof is required before stronger claims are allowed. A short phrase such as "add board integration" is not enough. The reader needs to know that board integration means sending a package from a PC to a board, running it, collecting status, collecting timing, collecting power, collecting temperature, checking task accuracy, and tying all of that to the same setup.

The page must avoid vague words and market language that cannot be tested. Do not use words such as revolutionary, unbeatable, flawless, seamless, perfect, or guaranteed unless the sentence immediately explains the exact proof required. Prefer direct wording such as "measured on this board," "estimated only," "simulation result," "blocked until measured," or "not proven yet."

### Executive View

The executive view should be the first usable layer of the page. It should answer these questions in plain language:

1. Why does this company need to exist now?
2. What larger market shift makes local physical AI inference important?
3. Where can analog help, and where should digital compute still be used?
4. What workloads are realistic first targets?
5. What proof exists today?
6. What proof is missing?
7. What would make the company more credible over the next three, twelve, and thirty-six months?
8. What claims are safe to make now?
9. What claims should not be made yet?

The executive view should include a small number of clear visual blocks:

- a plain-language primer that explains the terms before the roadmap uses them
- audience-specific summary bands that explain how an executive should use the page
- a top blocker board that shows what prevents stronger claims today
- a "why now" trend block
- a chip-and-platform story block
- a stack change map that shows what changes in silicon, compiler/runtime, backend, frontend, and proof
- a three-phase roadmap
- an evidence ladder
- a final verdict panel
- a top blocker list
- a readiness audit that checks clarity, reason, evidence level, ownership, action, and audience fit before external sharing

The executive view should not require the reader to understand ONNX, MLIR, ADC, DAC, VLA, JTAG, PCIe, or calibration before the page explains those ideas.

The primer should explain at least these ideas in complete sentences:

- workload
- analog in-memory compute
- hybrid chip
- compiler
- ADC and DAC
- calibration
- board proof
- power and thermal proof
- transformer or VLA model
- evidence package

Each primer entry should answer three things: what the term means, why the user should care, and what kind of proof would be needed before the term supports a company claim.

The top blocker board should be near the beginning of the page. It should let an executive see the hard parts before reading the full technical roadmap. It should show:

- the blocker
- why it matters
- the decision it forces
- the proof needed to unlock a stronger claim

At minimum, it should cover full VLA claims, board and power proof, calibration and drift, compiler target, and weight updates.

### Engineering View

The engineering view should sit under the executive view and give the dev team enough detail to build the product. It should answer these questions:

1. What data does the frontend need from the backend?
2. What JSON artifact does each step produce?
3. What adapter runs locally today?
4. What adapter is only a future connection?
5. What proof level does each artifact support?
6. What claim can each artifact unlock?
7. What claim must remain blocked?
8. What compiler changes are required?
9. What board and lab files must be imported?
10. What tests prove that the platform does not overclaim?

The engineering view should include detailed cards for:

- model intake
- analog fit
- analog accuracy risk
- crossbar layout risk
- hardware cost estimate
- compiler mapping
- transformer and VLA split
- full-system runtime
- board runtime
- power and thermal evidence
- task accuracy evidence
- weight update readiness
- sensor path readiness
- final answer and claim boundary

The engineering view should also include audience-specific summary bands that translate the same page into build work. These bands should point engineers toward schemas, adapters, frontend panels, archive entries, validation rules, and tests.

Each card should include complete sentences for:

- what the user is asking
- what the platform checks
- what external toolkit or internal adapter helps
- what data must be collected
- what the result means
- what the result cannot prove
- what the next action is

### Diagrams And Animations

The page should use diagrams to reduce reading load, not to decorate the page.

The main diagram should show the full path:

```text
User workload
  -> model intake
  -> analog and digital fit
  -> toolkit runs or evidence imports
  -> compiler mapping
  -> board and lab proof
  -> normalized evidence package
  -> final answer
  -> next roadmap work
```

The diagram should be interactive in a simple way. As the user scrolls, the current step should be highlighted. When the user opens a step, the diagram should show which upstream evidence feeds that step and which downstream claims depend on it.

The evidence ladder should be visual. It should show that source context, local estimates, simulator results, compiler mapping, system simulation, board runtime, power measurement, task accuracy, and reliability evidence are different proof levels. The animation should make clear that lower proof cannot silently become higher proof.

The page should also include a simple animated claim-flow view. The purpose is not decoration. It should teach the reader that a claim moves from market context, to estimate, to simulator or compiler result, to board and lab result, to repeated task proof. Each level should state what wording is allowed and what wording is still blocked.

The toolkit map should be visual. It should show the user question first, then the toolkit that can help. For example:

```text
Will analog behavior hurt accuracy?
  -> AIHWKIT or local analog accuracy adapter

Will the physical memory grid create errors?
  -> CrossSim or local crossbar layout adapter

Can normal model code become a chip plan?
  -> analog-mlir or our chip compiler target

Does CPU, memory, and runtime overhead erase the gain?
  -> SST/Golem, ALPINE/gem5-X, or local runtime adapter
```

The stack change map should show how each major roadmap item becomes product work across the whole company. It should cover calibration, tiling and bit-slicing, ADC/DAC scheduling, transformer or VLA partitioning, and board integration. For each item, it should show:

- what changes in silicon
- what changes in compiler and runtime
- what changes in the backend
- what the frontend shows
- what proof is needed before stronger claims are allowed

The final verdict should be visually stable and easy to read. It should show fit, proof, broken parts, safe claims, blocked claims, and next work in one place.

The page should include a readiness audit before the final verdict. The audit should catch six failure modes: unexplained terms, missing reasons, unsupported claims, unclear ownership, blocked claims without next steps, and content that serves only executives or only engineers.

### Frontend Acceptance Bar

The frontend is acceptable when an executive can open the page and explain the company story back in simple terms after five minutes.

The frontend is acceptable when an engineer can open the same page and identify the next five build tasks without reading the source code.

The frontend is acceptable when a customer can see whether their workload is a fit, partial fit, not a fit, or unknown.

The frontend is acceptable when an investor can see which claims are measured, which are simulated, which are estimated, and which are only market context.

The frontend is acceptable when every acronym is either avoided, expanded, or explained near where it appears.

The frontend is acceptable when every technical section explains why it matters to the user's decision.

### Backend Acceptance Bar

The backend is acceptable when the frontend can render the fourteen-step journey from backend data rather than hardcoded text.

The backend is acceptable when every step has a saved artifact, proof level, status, limitation, blocked-claim list, and next-action list.

The backend is acceptable when external toolkit output is normalized before it reaches the frontend. Raw logs can be attached for engineers, but the main page must show plain results.

The backend is acceptable when missing evidence remains missing. A simulator result must not unlock a board-power claim. A board runtime result must not unlock task accuracy. A market trend must not unlock chip readiness.

The backend is acceptable when the exported package can be reviewed by an executive, investor, customer technical team, or engineering lead without relying on a meeting transcript.

The exported package should include an audience export map. The same evidence should be organized for executives, customers, investors, and engineering teams. Each export should show what the audience needs, what the package shows, and what the package must not hide.

### Demo Acceptance Bar

The demo is acceptable when the page can be shown live from the local server and the viewer can follow one workload from start to final answer.

The demo should show:

- a presenter script with timed checkpoints, what to say, what to point at, and what decision each checkpoint supports
- a selected workload
- the chip target
- the fourteen-step journey
- which steps have results
- which steps are blocked
- which external tools support each step
- the final answer
- the next engineering work
- the evidence archive
- a review-package export map for executives, customers, investors, and engineering teams

The selected workload and chip target should be shown near the beginning of the page. This panel should state the workload, model shape, chip target, success target, and claim boundary. It should also say clearly when the values are demo assumptions rather than measured product claims.

The demo should not require command-line knowledge from the viewer. Command-line tools may run behind the scenes, but the visible story should stay inside the page.

## Frontend Completion Goal

The frontend must become the user's main operating screen. It should not be a list of toolkit names. It should be a benefit-first journey.

The frontend must support these areas:

### 1. Start A Workload Review

User can create or select a review package.

The screen must ask for:

- model file or existing package
- workload type
- target chip profile
- expected input shape
- expected output type
- success target
- optional dataset
- optional board or lab evidence

User benefit:

```text
The user can start a serious chip-fit review without knowing every backend detail.
```

### 2. Show The 14-Step Journey

The frontend must show the full journey:

1. Model Intake
2. Analog Fit
3. Analog Accuracy Risk
4. Crossbar Layout Risk
5. Hardware Cost Estimate
6. Compiler Mapping
7. Transformer And VLA Check
8. Full-System Runtime
9. Board Runtime
10. Power And Thermal
11. Task Accuracy
12. Weight Update Readiness
13. Sensor To Model Path
14. Final Answer

Each step must show:

- user benefit
- user question
- current status
- supporting toolkit names
- what data is needed
- what the platform checks
- what result exists
- what proof level exists
- what is missing
- next action

User benefit:

```text
The user always knows where they are, what proof exists, and what to do next.
```

### 3. Show A Visual Progress Graph

The frontend must show a visual graph of the journey.

Each node should show:

- step number
- phase
- step name
- short result
- status

Status labels:

- Package loaded
- Result available
- Evidence imported
- Connection checked
- Needs setup
- Blocked

User benefit:

```text
The user can see the whole evaluation at once instead of reading every artifact.
```

### 4. Show Results From Each Step

Each step must show its result in simple words.

Examples:

- Analog Fit: which layers are analog candidates and which stay digital
- AIHWKIT: expected analog accuracy risk
- CrossSim: crossbar layout risk
- analog-mlir: compiler mapping result
- SST/Golem: system timing risk
- ALPINE/gem5-X: full-system runtime risk
- board runtime: measured latency
- power and thermal: measured energy, peak power, and heat
- task accuracy: baseline result, mapped result, pass/fail
- weight update: fixed-weight ready, update candidate, or adaptive blocked

User benefit:

```text
The user sees results as product answers, not raw tool logs.
```

### 5. Show Toolkit Support By Step

Toolkit names must be visible, but they must sit under the user benefit.

Example:

```text
Step: Analog Accuracy Risk
User benefit: know whether analog chip behavior hurts model accuracy
Tools: AIHWKIT, AIHWKIT-Lightning, MemTorch later, local analog-error adapter
Result: analog risk and estimated accuracy impact
```

User benefit:

```text
Investors and technical users can see which proof source supports each claim.
```

### 6. Add Run And Import Actions

Each step should eventually have action buttons.

Examples:

- Run Model Intake
- Run Analog Fit
- Run AIHWKIT
- Run CrossSim
- Run Compiler Mapping
- Run Attention Check
- Run System Runtime
- Import Board Trace
- Import Power Trace
- Import Task Accuracy
- Import Weight Update Evidence
- Import Sensor Path Evidence
- Generate Final Answer
- Export Package

User benefit:

```text
The frontend becomes usable, not just explanatory.
```

### 7. Show Safe Claims And Blocked Claims

The frontend must show:

- what can be said now
- what cannot be said yet
- why a claim is blocked
- which evidence would unblock it

User benefit:

```text
The user avoids making claims that the proof does not support.
```

### 8. Export Review Package

The frontend must let the user export:

- JSON archive
- human-readable summary
- evidence files
- adapter run history
- failed connection history
- safe claim list
- blocked claim list
- next-work list

User benefit:

```text
The user can hand the result to an engineer, customer, investor, or diligence reviewer.
```

## Backend Completion Goal

The backend must become the evidence engine. It should not only store package files. It must normalize every proof source into one reviewable contract.

### 1. Package Store

Backend must store:

- model
- package settings
- chip profile
- workload profile
- 14-step journey state
- artifacts
- adapter runs
- imported evidence
- failed connector attempts
- final claim state

### 2. Model Intake Service

Backend must parse:

- ONNX first
- PyTorch later
- model inputs
- model outputs
- operators
- layer list
- parameter count
- model size
- unsupported parts

Output:

```text
model_intake.json
```

### 3. Analog Fit Service

Backend must produce:

- analog candidate layers
- digital layers
- unsupported layers
- fallback plan
- rewrite plan
- memory movement risk
- analog/digital boundary

Output:

```text
analog_fit.json
```

### 4. Analog Accuracy Service

Backend must support:

- AIHWKIT local run
- AIHWKIT service run later
- AIHWKIT-Lightning service path later
- local analog estimate
- MemTorch later

Output:

```text
analog_accuracy_risk.json
```

### 5. Crossbar Layout Service

Backend must support:

- CrossSim local run
- CrossSim service run later
- crossbar assumptions
- bit slicing
- wire resistance
- read noise
- programming error
- converter range

Output:

```text
crossbar_layout_risk.json
```

### 6. Hardware Cost Service

Backend must support:

- NeuroSim adapter
- MNSIM adapter later
- local rough estimator
- area estimate
- energy estimate
- latency estimate
- memory size estimate
- converter cost estimate

Output:

```text
hardware_cost_estimate.json
```

### 7. Compiler Mapping Service

Backend must support:

- analog-mlir adapter
- TVM / MLIR / IREE adapter later
- local compiler placement estimate
- unsupported operator report
- analog/digital task graph
- weight isolation plan
- runtime graph when available

Output:

```text
compiler_mapping.json
```

### 8. Transformer And VLA Service

Backend must support:

- attention partitioner
- local transformer checker
- static projection mapping
- dynamic attention blockers
- Softmax boundary
- LayerNorm boundary
- action-head boundary
- rewrite candidates

Output:

```text
transformer_vla_check.json
```

### 9. Full-System Runtime Service

Backend must support:

- SST/Golem adapter
- ALPINE/gem5-X adapter
- gem5 path later
- local runtime estimator
- CPU overhead
- memory movement
- dispatch overhead
- synchronization overhead

Output:

```text
full_system_runtime.json
```

### 10. Board Runtime Service

Backend must support:

- local simulated trace for demo
- imported board trace
- real board runtime service later
- firmware version
- test setup
- latency
- jitter
- fallback trace
- failure trace

Output:

```text
board_runtime.json
```

### 11. Power And Thermal Service

Backend must support:

- local simulated power/thermal result for demo
- imported power trace
- imported thermal trace
- power-meter service later
- peak power
- energy per run
- temperature
- thermal warning
- update energy when available

Output:

```text
power_thermal.json
```

### 12. Task Accuracy Service

Backend must support:

- local estimate for demo
- dataset-backed local evaluation
- external metric service later
- baseline metric
- mapped-model metric
- tolerance check
- pass/fail
- sample count

Output:

```text
task_accuracy.json
```

### 13. Weight Update Service

Backend must support:

- fixed-weight classification
- periodic-update classification
- adapter-update classification
- adaptive blocked classification
- update scope
- update frequency
- write latency evidence
- write energy evidence
- endurance evidence
- retention evidence
- recalibration evidence
- rollback evidence

Output:

```text
weight_update_readiness.json
```

### 14. Sensor Boundary Service

Backend must support:

- sensor type
- raw input shape
- preprocessing steps
- timing budget
- buffering
- sync
- analog front-end ownership
- event/tactile/camera/audio path
- whether sensor cost is counted or excluded

Output:

```text
sensor_boundary_readiness.json
```

### 15. Final Answer Service

Backend must combine all results into:

- fit status
- proof list
- broken areas
- missing evidence
- safe claims
- blocked claims
- next engineering actions
- export package

Output:

```text
final_answer.json
review-report.md
package.zip
```

## External Toolkit Completion Goal

Each external toolkit must be connected through an adapter. The product should never depend on raw tool output directly.

Each adapter must provide:

- install/probe status
- run action
- normalized result
- proof level
- tool limitations
- failed run record
- next action

Required adapter families:

### AIHWKIT

AIHWKIT helps answer whether analog behavior may hurt the model's answer. It can test effects such as noisy reads, imperfect weight writing, limited signal conversion, and drift over time. The product should show this as analog accuracy evidence. It should not present this as board speed, board power, or production proof.

### AIHWKIT-Lightning

AIHWKIT-Lightning helps run larger analog simulation sweeps faster. It is useful when the uploaded model or test sweep is too large for slower detailed experiments. The product should show this as faster simulation evidence, not as measured hardware evidence.

### CrossSim

CrossSim helps answer whether the physical memory grid may create errors. It can test risks such as wire resistance, read noise, programming error, bit slicing, and converter range. The product should show this under crossbar layout risk. It should not claim that CrossSim alone proves the final packaged chip.

### analog-mlir

analog-mlir helps answer whether parts of a normal model can be turned into an analog execution plan. It gives us useful compiler ideas such as layer extraction, analog conversion, static weight isolation, and simulation-oriented lowering. The product should show this under compiler mapping. It should also make clear that our real chip still needs a chip-specific compiler target.

### SST/Golem

SST/Golem helps answer whether CPU-to-accelerator communication, memory movement, dispatch timing, and synchronization may slow the system down. The product should show this under full-system runtime simulation. It should not present this as a real board measurement.

### ALPINE/gem5-X

ALPINE/gem5-X helps answer fuller computer-system questions. It can model CPU behavior, memory behavior, operating-system effects, and accelerator calls in one simulated setup. The product should show this as system simulation evidence. It should not present this as measured energy, measured heat, or production readiness.

### NeuroSim

NeuroSim helps estimate hardware cost before silicon exists. It can support early estimates for area, latency, energy, and memory needs. The product should show this as a planning estimate and keep it separate from measured silicon results.

### MNSIM

MNSIM can support additional early hardware architecture and cost estimates. The product should use it as another planning input when useful. It should not let MNSIM estimates replace compiler mapping, board runtime, or measured power evidence.

### TxSim

TxSim helps explore training and weight-update behavior under crossbar-style assumptions. The product should use it when the question is about update noise, training behavior, or write behavior in simulation. It should not claim endurance or retention unless those are measured.

### XBTorch

XBTorch helps test PyTorch models with crossbar behavior such as drift, programming risk, and imperfect writes. The product should use it for analog accuracy risk and weight-update readiness when its assumptions match the target chip. It should still label the result as simulation unless backed by hardware.

### RxNN

RxNN helps explore memristor-style behavior and larger resistive-crossbar models. The product should use it when the chip memory looks closer to that class of device. It should not replace board calibration, write endurance, or retention proof.

### Attention Partitioner

The attention partitioner helps answer which transformer or VLA parts can be analog candidates and which parts should stay digital. It should separate static projection layers from changing attention scores, Softmax, LayerNorm, action timing, and safety logic. The product should show this under transformer and VLA check.

### Board Runtime Adapter

The board runtime adapter helps answer whether the package actually ran on hardware or a prototype setup. It should collect pass or fail, latency, jitter, firmware version, board setup, and failure traces. The product should show this as board runtime evidence only for the exact setup tested.

### Power And Thermal Adapter

The power and thermal adapter helps answer how much energy the run used and how hot the board or chip became. It should collect power rails, energy per run, peak power, temperature traces, and thermal warnings. The product should show this as measured power and thermal evidence only when the trace is tied to the same package and board run.

### Task Accuracy Adapter

The task accuracy adapter helps answer whether the mapped or hardware-run model still solves the user's real task. It should compare the baseline model result with the mapped or measured result using the task metric that matters. The product should show this as task evidence and should not infer it from speed, power, or compiler success.

## Evidence Contract

Every result must declare its proof level.

Proof levels:

1. source-checked context
2. local estimate
3. toolkit smoke result
4. simulator output
5. compiler mapping
6. system simulation
7. board runtime
8. power and thermal measurement
9. task accuracy result
10. repeated reliability/update evidence

The claim engine must never treat a lower level as a higher level.

Example:

```text
AIHWKIT output can support analog-risk discussion.
It cannot prove board power.

CrossSim output can support crossbar-risk discussion.
It cannot prove production silicon behavior.

Board runtime can support latency claims.
It cannot prove task accuracy unless task accuracy was also measured.
```

## Build Phases

### Phase 1: Complete The Demo Frontend

Deliver:

- 14-step visual journey
- benefit-first cards
- current evidence status
- toolkit support by step
- per-step result preview
- per-step next action
- final answer preview

Done when:

```text
A user can open the page, select a package, understand the whole journey, see what proof exists, and know what to run next.
```

### Phase 2: Add Per-Step Actions

Deliver:

- run buttons for steps with local adapters
- import buttons for evidence files
- disabled buttons with clear missing setup for unavailable tools
- per-step result drawer
- per-step missing-evidence drawer

Done when:

```text
A user can operate the workflow from the frontend instead of reading static cards.
```

### Phase 3: Normalize Backend Artifacts

Deliver:

- one JSON artifact per step
- a demo review package folder that contains the fourteen artifact files before live adapters exist
- a manifest that lists every artifact and warns when the package is demo evidence rather than measured silicon proof
- a package schema document that explains required manifest fields, artifact fields, alignment rules, and claim rules in plain language
- a readable package index that renders the manifest and artifacts for executives and engineers without requiring them to open raw JSON
- a standalone executive brief that states the current answer, safe claims, blocked claims, top blockers, and next proof milestone
- a standalone engineering work queue that turns each artifact into concrete backend, frontend, compiler, runtime, lab, and test work
- a backend endpoint that validates and returns the demo package as one reviewable contract
- a repeatable archive builder that packages the readable index, briefs, schema, manifest, journey JSON, and all fourteen artifacts
- one API endpoint per step
- consistent status model
- consistent evidence model
- common claim-boundary fields: what the artifact supports and what the artifact does not prove
- consistent next-action model
- package archive includes all 14 step artifacts
- package archive is checked by the smoke test so missing files fail the build

Done when:

```text
The frontend can render every step from backend data, not hardcoded text.
```

The frontend should also load the demo review package when it is available. If the backend is running, the page should read the validated package endpoint. If only the static server is running, the page should read the static manifest and fourteen artifact files. The journey detail panel should show artifact status, artifact source, missing evidence, and next work from those records.

The page should show a package-level summary near the top of the reading path. That summary should say where the package came from, how many artifacts loaded, what proof warning applies, and what review rule controls the claims. This lets an executive see the evidence state before opening the detailed journey.

Verification command:

```bash
backend/.venv/bin/python backend/scripts/smoke_roadmap_demo_package.py
backend/.venv/bin/python backend/scripts/smoke_readability_contract.py
```

The package smoke test must validate both sides of the demo contract. It should verify the manifest and artifact files, and it should also verify that `roadmap-journey-demo.json` points to the same artifact filenames, titles, and proof levels.

### Phase 4: Connect Real Toolkit Runs

Deliver:

- AIHWKIT local model-level run
- CrossSim local model-level run
- NeuroSim adapter
- analog-mlir adapter with clear dependency handling
- SST/Golem adapter with clear dependency handling
- ALPINE/gem5-X adapter with clear dependency handling
- task accuracy local dataset runner
- board/power import contracts

Done when:

```text
At least one real or imported result can support each major proof area.
```

### Phase 5: Build The Final Claim Engine

Deliver:

- safe claim generator
- blocked claim generator
- do-not-claim list
- evidence-to-claim rules
- next-work ranking
- review report
- export package

Done when:

```text
The platform can produce one plain final answer with proof, gaps, and next work.
```

## Immediate Next Implementation Work

The next concrete build items are:

1. Move the 14-step journey data out of static HTML and into a backend endpoint.
2. Add a backend `roadmap_journey` artifact that summarizes status for all 14 steps.
3. Add per-step frontend drawers for result, proof, missing evidence, tools, and next action.
4. Add run buttons for existing local adapters: AIHWKIT, CrossSim, local evidence, board runtime, power/thermal, task accuracy, and compiler estimate.
5. Add import buttons for board runtime, power/thermal, task accuracy, weight update, and sensor path evidence.
6. Add final-answer panel that directly answers the central question.
7. Add archive persistence for the 14-step journey state.
8. Add smoke tests proving blocked steps do not become safe claims.

## The One-Sentence Product Target

```text
The platform lets a user move from a model and analog chip target to a clear, evidence-backed answer about fit, proof, failures, safe claims, and next engineering work.
```
