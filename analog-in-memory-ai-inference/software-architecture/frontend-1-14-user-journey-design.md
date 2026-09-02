# Frontend 1-14 User Journey Design

Start from the [Connected System Map](connected-system-map.html). This journey uses the same contract: object, constraint, design move, evidence, allowed claim, refused claim, and next handoff.

Related completion target:

- [Platform Completion End-To-End Goal](platform-completion-end-to-end-goal.md)

## Main Product Question

The frontend should help a user answer one plain question:

```text
Can this workload run well on this analog chip, what proof do we have, what is broken, and what should we do next?
```

The user journey should not start with tool names. It should start with the user's questions. Tool names appear inside each step as supporting proof providers.

## Display Order

Each frontend step should be displayed in this order:

1. user benefit
2. plain user question
3. journey role
4. current result status
5. toolkits or adapters that support the step
6. what the user gives us
7. what the platform checks
8. what the user sees
9. proof level
10. next action

This means the page can still show toolkit names like AIHWKIT, CrossSim, analog-mlir, SST/Golem, ALPINE, NeuroSim, TxSim, XBTorch, and RxNN. But those names should sit under the reason the user cares.

Example:

```text
User benefit:
The user sees whether normal analog chip behavior may damage accuracy.

Question:
Will analog imperfections hurt the answer?

Tools that help:
AIHWKIT, MemTorch later, local analog-error adapter
```

## Journey Visualization

The frontend should include a simple visual graph of the 14 steps. It should show:

- step number
- journey phase
- step name
- short result
- current status

The graph helps the user understand where they are in the process. It also makes missing work visible without forcing the user to read every card.

The graph should use simple status labels:

- Package loaded
- Result available
- Evidence imported
- Connection checked
- Needs setup

## Result Summary

Above the step cards, the frontend should summarize what the current package has:

- how many steps already have a loaded package or completed result
- how many steps have imported evidence
- how many steps have adapter paths checked
- how many steps still need an adapter, upload, measurement, or manual evidence path

This helps the user quickly answer:

```text
What can I trust now?
What has proof?
What is ready to connect?
What do I need to do next?
```

## Design Rule

Each step should show:

- the user question
- what the user gives us
- what the platform checks
- what tools or adapters help
- what result the user sees
- what proof level the result has
- what can be safely said
- what is still missing
- what the next action is

The page should use simple words. Do not assume the reader knows compilers, analog arrays, ADCs, DACs, MLIR, gem5, or simulator names.

## Step 1: Read The Model

Frontend label:

```text
Model Intake
```

User question:

```text
Can we open and understand the model?
```

What the user gives us:

- model file
- model format
- workload type
- target device or chip profile
- optional dataset

What the platform checks:

- whether the file opens
- input names and shapes
- output names and shapes
- layer list
- operator list
- parameter count
- model size
- unsupported or unknown parts

Tools and adapters:

- ONNX parser
- ONNX Runtime later
- PyTorch parser later
- our model analyzer

Frontend result:

```text
Model loaded.
Inputs found.
Outputs found.
Layers listed.
Unsupported parts flagged.
```

Proof level:

```text
Model parsed evidence
```

Safe claim:

```text
We can inspect this model and begin a fit review.
```

Do not claim:

```text
Do not claim the model runs on the chip just because it loaded.
```

Next action:

```text
Build the analog fit map.
```

## Step 2: Check Analog Fit

Frontend label:

```text
Analog Fit
```

User question:

```text
Which parts can run on analog compute, and which parts cannot?
```

What the user gives us:

- model graph
- chip profile
- supported operator list
- precision assumptions
- memory and array limits

What the platform checks:

- analog candidate layers
- digital-only layers
- unsupported layers
- fallback path
- analog-to-digital handoffs
- data movement risk
- rewrite needs

Tools and adapters:

- our model mapper
- analog-mlir later
- TVM / IREE / MLIR later
- compiler placement adapter

Frontend result:

```text
These layers are analog candidates.
These layers stay digital.
These layers need fallback or rewrite.
```

Proof level:

```text
Local mapping estimate or compiler mapping
```

Safe claim:

```text
This model has analog-friendly regions.
```

Do not claim:

```text
Do not claim full-chip support without compiler mapping and runtime evidence.
```

Next action:

```text
Run compiler mapping or import a compiler placement report.
```

## Step 3: Check Analog Accuracy Risk

Frontend label:

```text
Analog Accuracy Risk
```

User question:

```text
Will analog imperfections hurt the answer?
```

What the user gives us:

- model or selected layers
- chip profile
- calibration profile
- precision assumptions
- task target

What the platform checks:

- noise risk
- drift risk
- converter precision risk
- weight programming risk
- sensitive layers
- estimated accuracy drop

Tools and adapters:

- AIHWKIT
- MemTorch later
- local analog-error adapter

Frontend result:

```text
AIHWKIT ran.
Analog error estimate exists.
Estimated accuracy drop is shown.
Sensitive layers are listed when available.
```

Proof level:

```text
Toolkit smoke, analog simulator result, or local estimate
```

Safe claim:

```text
Simulation suggests this analog behavior is low, medium, or high risk.
```

Do not claim:

```text
Do not claim real task accuracy or measured hardware behavior from this alone.
```

Next action:

```text
Run selected model layers through AIHWKIT with task data.
```

## Step 4: Check Crossbar Layout Risk

Frontend label:

```text
Crossbar Layout Risk
```

User question:

```text
Will the physical memory grid change the math?
```

What the user gives us:

- layer weights or model summary
- array size assumptions
- bit slicing assumptions
- ADC range assumptions
- read noise and programming assumptions

What the platform checks:

- wire resistance risk
- voltage drop risk
- read noise
- programming error
- ADC range sensitivity
- array size sensitivity
- whether large layers should be split

Tools and adapters:

- CrossSim

Frontend result:

```text
CrossSim ran.
Crossbar matrix test or layer test result is shown.
Physical layout risk is shown.
```

Proof level:

```text
Crossbar simulator result
```

Safe claim:

```text
Crossbar simulation supports or challenges this layer placement.
```

Do not claim:

```text
Do not claim final chip behavior or measured power from CrossSim alone.
```

Next action:

```text
Run CrossSim on the largest or most sensitive model layer.
```

## Step 5: Estimate Hardware Cost

Frontend label:

```text
Hardware Cost Estimate
```

User question:

```text
How much area, time, and energy might the hardware need?
```

What the user gives us:

- mapped layers
- chip design assumptions
- memory technology assumptions
- array size
- precision
- ADC/DAC assumptions
- power, area, and latency targets

What the platform checks:

- estimated latency
- estimated energy
- estimated area
- ADC/DAC cost
- peripheral circuit cost
- main cost driver
- design tradeoffs

Tools and adapters:

- NeuroSim
- MNSIM later
- local hardware estimator later

Frontend result:

```text
Estimated area is this.
Estimated energy is this.
Estimated latency is this.
Main hardware cost driver is this.
```

Proof level:

```text
Hardware estimate
```

Safe claim:

```text
This chip design direction appears worth testing or needs redesign.
```

Do not claim:

```text
Do not claim measured silicon performance from a hardware estimate.
```

Next action:

```text
Connect NeuroSim and compare estimated hardware cost against targets.
```

## Step 6: Check Compiler Path

Frontend label:

```text
Compiler Mapping
```

User question:

```text
Can this model actually be prepared for the chip?
```

What the user gives us:

- model graph
- chip compiler rules
- supported operators
- fallback rules
- memory limits

What the platform checks:

- extracted layers
- converted layers
- isolated weights
- task graph
- unsupported operators
- runtime graph status
- rewrite needs

Tools and adapters:

- analog-mlir
- TVM
- IREE
- MLIR
- compiler placement adapter

Frontend result:

```text
These layers mapped.
These layers failed.
These weights can be isolated.
These operations need fallback or rewrite.
```

Proof level:

```text
Compiler mapping
```

Safe claim:

```text
These model parts have a compiler path.
```

Do not claim:

```text
Do not claim speed, power, or task accuracy from compiler mapping alone.
```

Next action:

```text
Fix compiler blockers or attach real compiler placement evidence.
```

## Step 7: Check Transformer And VLA Hard Parts

Frontend label:

```text
Transformer And VLA Check
```

User question:

```text
Are attention, Softmax, LayerNorm, or action heads a problem?
```

What the user gives us:

- transformer or VLA-adjacent model
- sequence length
- input modalities
- action outputs
- task target

What the platform checks:

- static projection candidates
- dynamic attention blockers
- Softmax boundary
- LayerNorm boundary
- memory movement
- action head risk
- rewrite options

Tools and adapters:

- our attention partitioner
- analog-mlir later
- custom model analysis

Frontend result:

```text
Static projection layers may fit analog.
Dynamic attention and non-linear parts need digital support or rewrite.
```

Proof level:

```text
Model structure review or compiler partition
```

Safe claim:

```text
This is a partial transformer or VLA fit if only some layers map.
```

Do not claim:

```text
Do not claim full VLA readiness because a few matrix layers look analog-friendly.
```

Next action:

```text
Partition attention and test rewrite options.
```

## Step 8: Check Full-System Behavior

Frontend label:

```text
Full-System Runtime
```

User question:

```text
Does the full CPU, memory, software, and analog accelerator path still work?
```

What the user gives us:

- mapped workload
- CPU assumptions
- memory assumptions
- runtime assumptions
- accelerator dispatch rules
- timing target

What the platform checks:

- analog compute time
- CPU dispatch time
- memory movement
- synchronization
- digital fallback cost
- total simulated runtime

Tools and adapters:

- ALPINE
- SST/Golem
- gem5
- local board-runtime adapter

Frontend result:

```text
Analog compute takes this much time.
CPU and memory overhead take this much time.
Total system time passes or misses the target.
```

Proof level:

```text
System simulation or local runtime estimate
```

Safe claim:

```text
Full-system simulation supports or weakens the workload story.
```

Do not claim:

```text
Do not call system simulation a real board measurement.
```

Next action:

```text
Connect ALPINE, SST/Golem, or real board runtime.
```

## Step 9: Check Real Board Runtime

Frontend label:

```text
Board Runtime
```

User question:

```text
Did it actually run on hardware, and how long did it take?
```

What the user gives us:

- board run
- board ID
- chip ID
- firmware version
- model package
- input data
- runtime logs

What the platform checks:

- measured latency
- per-layer timing
- transfer time
- fallback time
- jitter
- failures
- retries

Tools and adapters:

- board runtime adapter
- firmware logs
- USB/Ethernet/JTAG bridge

Frontend result:

```text
Measured board latency is this.
Failures and retries are listed.
Firmware and board version are recorded.
```

Proof level:

```text
Board runtime evidence
```

Safe claim:

```text
This run supports a measured latency claim for this board, model, and setup.
```

Do not claim:

```text
Do not generalize one board run to production readiness.
```

Next action:

```text
Attach repeated board runs and matching power/task evidence.
```

## Step 10: Check Power And Heat

Frontend label:

```text
Power And Thermal
```

User question:

```text
Did it actually save power, and did it stay cool?
```

What the user gives us:

- power trace
- current monitor data
- voltage rail data
- temperature trace
- measurement setup
- run trigger timestamps

What the platform checks:

- measured energy
- average power
- peak power
- idle power
- temperature rise
- repeated-run heat behavior
- update energy when available

Tools and adapters:

- power meter adapter
- thermal adapter
- onboard current monitor
- Joulescope / Keysight / Otii / oscilloscope later

Frontend result:

```text
Measured energy is this.
Peak power is this.
Temperature rise is this.
Measurement setup is recorded.
```

Proof level:

```text
Power and thermal evidence
```

Safe claim:

```text
This supports an energy or thermal claim only for the measured setup.
```

Do not claim:

```text
Do not claim energy savings without synchronized runtime and task accuracy.
```

Next action:

```text
Import real meter traces and align them with board runtime triggers.
```

## Step 11: Check Task Accuracy

Frontend label:

```text
Task Accuracy
```

User question:

```text
Did the mapped model still solve the user's real task?
```

What the user gives us:

- task dataset
- expected labels or expected outputs
- baseline model result
- candidate model result
- allowed loss
- task metric

What the platform checks:

- baseline metric
- candidate metric
- metric loss
- pass/fail
- failed cases
- tolerance

Tools and adapters:

- task accuracy adapter
- customer dataset
- benchmark dataset
- metric runner

Frontend result:

```text
Baseline result is this.
Candidate result is this.
Allowed loss is this.
Task accuracy passed or failed.
```

Proof level:

```text
Task accuracy evidence
```

Safe claim:

```text
This mapped model passed the selected task metric on this dataset.
```

Do not claim:

```text
Do not claim broad task success from a tiny or synthetic dataset.
```

Next action:

```text
Run customer task data through the mapped candidate model.
```

## Step 12: Check Weight Updates

Frontend label:

```text
Weight Update Readiness
```

User question:

```text
Can the chip update weights after deployment if the workload needs it?
```

What the user gives us:

- update pattern
- update scope
- model layers or adapter layers
- write target
- update frequency
- rollback requirement

What the platform checks:

- fixed-weight only
- occasional update candidate
- adapter update candidate
- adaptive claim blocked
- write latency
- write energy
- write voltage
- endurance
- retention
- post-update accuracy
- rollback

Tools and adapters:

- AIHWKIT update simulation
- TxSim / XBTorch / RxNN later
- board write test
- endurance test
- power measurement

Frontend result:

```text
This workload is fixed-weight ready, update candidate, adapter candidate, or adaptive blocked.
Missing update proof is listed.
```

Proof level:

```text
Update simulation or measured update evidence
```

Safe claim:

```text
This chip supports only the update mode proven by evidence.
```

Do not claim:

```text
Do not claim adaptive Physical AI without write latency, energy, endurance, retention, rollback, and post-update accuracy.
```

Next action:

```text
Run the weight-update measurement harness.
```

## Step 13: Check Sensor Boundary

Frontend label:

```text
Sensor To Model Path
```

User question:

```text
What happens before the model gets input?
```

What the user gives us:

- sensor type
- sample rate
- preprocessing steps
- synchronization rules
- sensor logs
- input quality target

What the platform checks:

- sensor latency
- preprocessing cost
- dropped frames
- synchronization errors
- input quality
- sensor-to-model energy
- sensor-to-output latency

Tools and adapters:

- sensor adapter
- camera/audio/tactile/event preprocessing
- board logs
- latency trace

Frontend result:

```text
Sensor path cost is counted.
Preprocessing and synchronization risks are shown.
```

Proof level:

```text
Sensor boundary evidence
```

Safe claim:

```text
The model timing includes or excludes the sensor path, and the page says which.
```

Do not claim:

```text
Do not claim edge-device latency if sensor and preprocessing time are excluded.
```

Next action:

```text
Attach sensor logs or replay/live sensor traces.
```

## Step 14: Final Answer

Frontend label:

```text
Final Answer
```

User question:

```text
So what can we safely say?
```

What the user gives us:

- all model data
- all toolkit results
- all imported evidence
- all failed runs
- all targets

What the platform checks:

- fit status
- proof strength
- blockers
- safe claims
- do-not-claim list
- next work
- export readiness

Tools and adapters:

- claim engine
- evidence store
- roadmap generator
- archive exporter

Frontend result:

```text
Fit: yes, partial, no, or unknown.
Proof: listed by strength.
Breaks: listed directly.
Safe claim: written plainly.
Next work: ranked.
Export package: ready.
```

Proof level:

```text
Evidence-backed claim summary
```

Safe claim:

```text
Only claims supported by the current evidence are shown as safe.
```

Do not claim:

```text
Anything missing measured or validated evidence remains blocked.
```

Next action:

```text
Export the review package or run the highest-impact missing test.
```

## End-To-End User Journey

1. Model Intake: the user starts a new evaluation and provides the workload, model, target chip, success targets, and optional dataset.
2. Analog Fit: the platform shows which model parts look suitable for analog compute and which parts must stay digital or need fallback.
3. Analog Accuracy Risk: the user runs analog accuracy checks. AIHWKIT and the analog-error adapter support this step.
4. Crossbar Layout Risk: the user runs crossbar layout checks. CrossSim supports this step.
5. Hardware Cost Estimate: the user runs or plans hardware cost estimates. NeuroSim and MNSIM support this step when added.
6. Compiler Mapping: the user runs compiler mapping. analog-mlir, TVM, IREE, MLIR, or the compiler placement adapter support this step.
7. Transformer And VLA Check: the platform checks attention, Softmax, LayerNorm, action heads, and other hard parts so the user does not overclaim from partial matrix-layer fit.
8. Full-System Runtime: the user runs full-system simulation or local runtime estimates. ALPINE, SST/Golem, gem5, and board-runtime adapters support this step.
9. Board Runtime: the user imports real board runtime when hardware exists.
10. Power And Thermal: the user imports power and thermal measurement when lab evidence exists.
11. Task Accuracy: the user imports task accuracy evidence from customer or benchmark data.
12. Weight Update Readiness: the user checks whether the chip can support fixed weights, occasional updates, adapter updates, or frequent local adaptation.
13. Sensor To Model Path: the user checks what happens before the model input when the workload depends on real physical inputs.
14. Final Answer: the frontend generates fit, proof, breaks, safe claim, do-not-claim list, next work, and an export package for engineering review, customer review, investor review, or roadmap planning.

## Frontend Build Plan

First frontend pass:

- add a 14-step journey overview above toolkit result pages
- organize by user question first
- show supporting tools inside each step
- show status from current package evidence where available
- keep toolkit-specific result pages below the journey

Second frontend pass:

- make each step expandable
- show exact artifacts attached to each step
- add per-step run buttons
- add per-step blockers and next actions
- route steps to existing backend endpoints

Third frontend pass:

- add missing backend adapters for NeuroSim, MemTorch, MNSIM, sensor boundary, weight update measurement, and real board/power/task services
- replace smoke tests with model-level and board-level runs as evidence becomes available
