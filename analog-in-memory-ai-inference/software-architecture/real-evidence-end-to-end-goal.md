# Real Evidence End-To-End Goal

Start from the [Connected System Map](connected-system-map.html). This goal uses the same contract: object, constraint, design move, evidence, allowed claim, refused claim, and next handoff.

## Goal

Build the next version of the analog AI workbench so it does more than organize the idea. It should connect real tools and real measurements into the same path.

The path is:

```text
AI model
-> workload requirements
-> analog/digital split
-> analog simulation
-> digital control logic
-> chip layout flow
-> backend evidence import
-> claim readiness
-> board measurement
-> power measurement
-> final proof package
```

The rule is simple:

```text
Do not claim more than the evidence proves.
```

## What Exists Now

The current system already proves the shape of the workflow.

It can:

- take a model package
- produce hardware placement
- mark analog candidates and digital-required regions
- generate hardware-lab evidence
- run analog evidence scripts
- generate governor traces
- check RTL through Yosys
- prepare OpenLane-ready design packages and routed OpenLane summaries for selected digital controllers
- export evidence from the chip-design lab
- import that evidence into the backend
- show which claims are supported, need review, or remain blocked

The current live package is:

```text
pkg-e931662a01293df2
```

This proves a local model-to-placement-to-lab-to-claim loop.

It does not prove:

- measured board latency
- measured power
- measured energy savings
- calibrated silicon behavior
- analog macro integration
- package reliability
- production readiness

## First-Principles Frame

Analog in-memory compute is useful only if the whole system wins.

The analog core may reduce multiply and memory-movement cost. But that gain can disappear if the system spends too much on:

- digital-to-analog conversion
- analog-to-digital conversion
- moving data between analog and digital regions
- calibration
- retries
- fallback execution
- thermal control
- host overhead
- task accuracy recovery

So the workbench must never ask only:

```text
Can this layer run on analog?
```

It must ask:

```text
Can this workload finish correctly, fast enough, and with less energy after every analog, digital, converter, memory, calibration, and fallback cost is counted?
```

## Build Track 1: Real Analog Simulation

Object:

```text
analog candidate layer or tile
```

Constraint:

```text
analog error, conductance noise, drift, wire drop, ADC/DAC precision, tile size, and calibration assumptions
```

Design move:

```text
run the candidate through AIHWKIT, CrossSim, SPICE-style tests, or another analog model
```

Evidence:

```text
analog_error_simulation.json
tile_operating_point.json
calibration_profile.json
nonideality_sweep.json
```

Allowed claim:

```text
This layer tolerated this simulated analog error under these assumptions.
```

Refused claim:

```text
This chip has measured hardware accuracy.
```

Next handoff:

```text
backend evidence import -> claim readiness -> task accuracy check
```

## Build Track 2: Compiler And Placement

Object:

```text
model graph and operator placement
```

Constraint:

```text
unsupported operators, converter boundaries, tile limits, precision limits, memory movement, fallback cost, and runtime schedule
```

Design move:

```text
lower the model into analog candidates, digital-required regions, boundary crossings, and governor rows
```

Evidence:

```text
hardware-placement.json
backend-hardware-placement-governor-input.csv
compiler-placement.json
```

Allowed claim:

```text
This model has specific regions that are analog candidates and specific regions that must stay digital.
```

Refused claim:

```text
The full model runs on analog hardware.
```

Next handoff:

```text
analog simulation -> digital controller -> RTL checks
```

## Build Track 3: Digital Control Logic

Object:

```text
scheduler, governor, fallback controller, and boundary logic
```

Constraint:

```text
analog uncertainty, timing budget, fallback threshold, tile availability, and error budget
```

Design move:

```text
turn placement and analog evidence into concrete control rules
```

Evidence:

```text
governor trace
RTL test output
Yosys synthesis report
OpenLane package readiness report and routed OpenLane summary where available
```

Allowed claim:

```text
The selected control rule has RTL, synthesis, and bounded exploratory physical-flow evidence.
```

Refused claim:

```text
The chip is physically signed off.
```

Next handoff:

```text
OpenLane run -> layout evidence -> backend import
```

## Build Track 4: Board Runtime Measurement

Object:

```text
one workload running on one board under one package ID
```

Constraint:

```text
latency distribution, firmware version, board revision, repeated runs, runtime window, and host overhead
```

Design move:

```text
collect synchronized runtime traces from a real board or a clearly labeled replay fixture
```

Evidence:

```text
board_runtime.json
```

Measured-ready evidence must include:

- package ID
- workload ID
- board ID
- start timestamp
- end timestamp
- p50 latency
- p95 latency
- repetition count
- host-overhead boundary
- measurement-level provenance

Allowed claim:

```text
This workload ran on this board with this measured latency distribution.
```

Refused claim:

```text
The product meets latency across customers, boards, and environments.
```

Next handoff:

```text
power measurement -> task result -> claim readiness
```

## Build Track 5: Power And Thermal Measurement

Object:

```text
power and temperature during the same runtime window
```

Constraint:

```text
rail selection, meter setup, integration window, peak power, average power, temperature, and host overhead
```

Design move:

```text
tie meter samples to the same package, workload, board, and runtime trace
```

Evidence:

```text
power_thermal.json
```

Measured-ready evidence must include:

- package ID
- workload ID
- board ID
- runtime trace ID
- integration start timestamp
- integration end timestamp
- average power
- peak power
- meter setup
- host-overhead boundary

Allowed claim:

```text
This board used this measured power during this workload run.
```

Refused claim:

```text
The chip has measured power savings against every digital baseline.
```

Next handoff:

```text
digital baseline comparison -> task accuracy -> final proof package
```

## Build Track 6: Final Proof Package

Object:

```text
one review package for one workload, model, target, evidence set, and claim report
```

Constraint:

```text
each claim must name the evidence that supports it, and each missing proof must stay visible
```

Design move:

```text
export a package that a customer, investor, engineer, or founder can read without guessing what was proven
```

Evidence:

```text
manifest.json
hardware-placement.json
analog evidence
RTL and OpenLane evidence
board runtime evidence
power evidence
task accuracy evidence
claim-readiness report
```

Allowed claim:

```text
This package proves exactly the claims listed in the claim-readiness report.
```

Refused claim:

```text
Any claim not backed by the package evidence.
```

## Definition Of Done

This goal is done when:

- the frontend shows one clear path from model to claim readiness
- the backend imports analog, compiler, RTL, OpenLane, board, power, and task evidence without mixing proof levels
- analog simulator evidence has a readiness gate that separates local toy evidence from CrossSim, AIHWKIT, SPICE, or calibrated simulator evidence
- the frontend custom evidence panel lets a user choose ordinary evidence, strict simulator/tool evidence, or strict measured board/power evidence before validation and import
- AIHWKIT or CrossSim-style analog evidence can be attached to a package
- digital RTL and OpenLane evidence can be attached to a package
- board runtime evidence can pass a measured-readiness gate only when it contains real board provenance
- power evidence can pass a measured-readiness gate only when it contains real meter provenance
- the final package says what is proven, what needs review, and what remains blocked
- all pages keep the same object, constraint, evidence, and claim-boundary flow
- page-contract, backend, measured-evidence, and cross-repo bridge checks pass together

## Seamless Page-Flow Goal

The HTML and markdown pages are part of the system, not side notes. They should read as one review path.

The reader should be able to start at:

```text
connected-system-map.html
```

and move through:

```text
master-review-path.html
-> combined-system-end-to-end-workflow.html
-> real-evidence-end-to-end-goal.html
-> current-proof-ledger.html
-> index.html
-> hardware-lab evidence pages
```

without having to guess how one page connects to the next.

Each important page should answer the same seven questions:

- What object is this page about?
- What physical, mathematical, software, or measurement constraint matters here?
- What design move does the system make?
- What evidence exists now?
- What claim is allowed from that evidence?
- What stronger claim is still refused?
- What artifact or page receives the next handoff?

This is the writing standard:

```text
plain first-principles explanation
-> concrete artifact
-> proof level
-> allowed claim
-> refused claim
-> next work
```

The page set is acceptable only when a new reader can explain the full workflow in simple words:

```text
The model is split.
Analog handles the parts where physical error is tolerable.
Digital logic controls the parts where exact decisions, routing, fallback, and interfaces matter.
The lab checks analog error, RTL behavior, synthesis, OpenLane readiness, and routed OpenLane exploratory results for selected digital controllers.
The backend imports the evidence and blocks claims that are stronger than the proof.
Measured board runtime and measured power are still separate gates.
```

The page set is not done if:

- pages repeat the same idea without naming the next artifact
- pages use words like validated, ready, optimized, or proven without saying the exact evidence level
- local simulation looks like measured board evidence
- OpenLane readiness or routed exploratory evidence looks like full-chip signoff
- analog simulator evidence looks like calibrated silicon
- frontend/backend work looks disconnected from the lab evidence
- the reader cannot tell what to do next after finishing a page

The review pass should improve existing pages before adding new ones. Add a new page only when it removes confusion from the review path.

Final outcome:

```text
A serious analog AI chip workbench that shows what the chip idea can prove today, what it cannot prove yet, and exactly what evidence is needed next.
```
