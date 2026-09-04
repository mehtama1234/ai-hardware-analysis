# End-To-End AIMC Implementation Goal

## Goal

Build and verify one complete analog in-memory compute (AIMC) inference path for one real edge or Physical AI workload.

The path must begin with a real model and a versioned dataset and end with a measured task result from a board or a clearly bounded hardware prototype. The result must show where analog computation is used, where digital computation is required, how bit slicing and conversion are handled, when the runtime falls back to digital, and whether the complete system improves the customer's task under the stated latency, energy, thermal, and reliability limits.

The goal is not to prove that all AI can run in analog. The goal is to prove one narrow, repeatable, technically honest workload and create the reusable machinery for evaluating the next workload.

## Where We Stand Now

In plain language, the project has already shown that a physical capacitor DAC, a physical transistor comparator, and a latch can exchange one decision correctly at nominal conditions. The current same-deck bit test measures `16/16` trial codes and preserves the expected comparator polarity in `16/16` cases.

That is an important circuit boundary, but it is not yet a fully accepted converter. The uncalibrated retained-bit path fails because the physical threshold shape is not nominally binary. The corrected source-matched PMOS-only calibration now measures `16/16` thresholds, passes the legal-range, spacing, and injective-map gates, and recovers `5/5` representative conversions with `20/20` retained-bit comparisons measured. The project has therefore closed the nominal calibrated diagnostic and moved to robustness and continuous-SAR validation, while keeping PVT, mismatch/noise, extracted-layout, board, and silicon acceptance open.

The latest differential break-before-make diagnostic corrected a prior netlist
bug in which both plates moved together. The corrected cell gives opposing,
correct-polarity movement on codes `0,1,14,15`, but its endpoint plate voltages
cross the legal supply range at both tested switch sizes. This advances the
physical diagnosis but does not close the converter gate. The mixed-memory
compiler and transformer workload replay remain valid software evidence; their
analog execution claim must continue to carry a physical-converter fallback
until a legal full-scale cell is measured.

The immediate work is to repair the DAC-to-sample interface and then rerun the complete chain under settling, mismatch, noise, and PVT conditions. Only after that passes can the analog path be connected to model-level task results and compared fairly with the digital baseline. The page deliberately keeps circuit evidence, model evidence, board evidence, and silicon evidence as separate gates.

The latest reproducibility run of the standalone transistor DAC measured only `4/16` requested codes before hitting the bounded simulator timeout. The evidence classifier now correctly marks that artifact incomplete instead of accepting the passing subset. Earlier complete nominal measurements remain useful historical diagnostics, but the current acceptance gate is full-code convergence on the current machine and deck.

The first isolated bottom-plate cell diagnostic also timed out in `4/4` fixed-top-plate cases. The next repair is therefore at the transistor-cell netlist and transient initialization level, before any claim about DAC accuracy or SAR calibration is revisited.

The incremental loading diagnostic then identified a more specific operating problem: the original `2/4 um` source transmission gate produced `558 mV` sample error when charging an `8 pF` DAC load, while a legal `32/64 um` source switch reduced that error to `34.0 mV` at the same observation point. Extending the acquisition phase and measuring while the larger switch remained on reduced the error further to `9.61 mV`. That is below the current 4-bit half-LSB of `56.25 mV`, although it is not a 12-bit sample-and-hold result.

The first coupled probe using this larger source switch and longer schedule measured codes `7` and `15` through the physical DAC, comparator, preamp, and latch. Both trials preserved polarity; the measured preamp differences were `0.488 mV` and `0.752 mV`. This makes longer source acquisition the current repair candidate, but it still requires an all-code run, PVT, mismatch/noise, and retained-bit SAR validation. The evidence is published in `docs/research/sky130-long-acquisition-coupled-probe.md`.

The subsequent all-code long-acquisition coupled run measures `16/16` physical codes, with `0` timeouts and `16/16` correct comparator polarities. A corrected physically coherent PMOS-only calibration run then completes `16/16` calibration codes, `20/20` retained-bit comparisons, and `5/5` representative conversions when DAC thresholds are sampled at `9.0 ns` before comparator closure. Its low-source candidate has legal threshold range, adequate minimum spacing, and a bijective rank-preserving map. This is nominal calibrated evidence, not full converter acceptance: PVT, mismatch/noise, continuous SAR, and post-layout gates remain open. The earlier rail-contention `5/5` result is retained only as historical evidence for a rejected fixture.

An `8x` full-array capacitor diagnostic restored monotonic upper-code spacing
(`96.855 mV` for code `14 -> 15`, above the `56.25 mV` half-LSB target), but
the physical DAC top plate reached `2.544 V` on a `1.8 V` supply. This is
mechanism evidence, not a passing cell: the charge-transfer network must be
rebalanced within the legal supply range before SAR acceptance is revisited.
The subsequent all-code zero-common-mode run measured `16/16` cases with
correct polarity, but produced negative adjacent spacings of `-123.557 mV`,
`-855.492 mV`, and `-160.534 mV`. The common-mode change is therefore rejected
by the full-code monotonicity gate.
An MSB timing diagnostic then extended the redistribution interval from `5 ns`
to `20 ns`; code `7 -> 8` remained non-monotonic at `-94.577 mV`. More settling
time is therefore not the repair. The next physical candidate must use a
different MSB charge-transfer or split/precharge topology.
An MSB capacitor-ratio sweep from `0.125x` through `2x` leaves code `7 -> 8`
non-monotonic in every tested case, from `-1269.695 mV` to `-841.235 mV`.
Ratio-only sizing is rejected; explicit MSB precharge/isolation is now the
next physical candidate.
Targeted selected-MSB switch scaling also fails: `4x` leaves code `7 -> 8`
at `-224.255 mV`, while `2x` times out on code 7. The next physical design
must change the MSB charge-transfer topology rather than continue sizing.

## Final Question

The next meaty vertical slice is defined in
[`docs/roadmaps/next-hybrid-transformer-vertical-slice.md`](../roadmaps/next-hybrid-transformer-vertical-slice.md).
It uses the three-block transformer-style MLP fixture to connect model
placement, analog/digital/SRAM execution, calibrated analog replay, and the
physical converter claim boundary in one package.

Can this specific workload complete its real task correctly and on time when selected fixed-weight operations use an analog memory array, while the rest of the model runs through digital support logic, under realistic conversion, memory, calibration, thermal, and fallback costs?

The final comparison must be:

```text
same workload + same dataset + same task metric
digital baseline versus hybrid analog/digital implementation
```

## Initial Scope

Start with one workload that has:

- a measurable task outcome
- fixed or rarely changing weights
- repeated dense matrix or convolution work
- a meaningful energy or latency constraint
- a model small enough to inspect and debug
- a digital implementation that can serve as a fair baseline

The preferred first workload is a sensor-near classifier, defect detector, wake-word detector, or compact vision model. A small transformer projection or MLP block may be used as a second workload after the first vertical slice is working. A full VLA is outside the first acceptance gate because it adds dynamic attention, cache movement, body-specific action behavior, and safety complexity before the core path is proven.

The first workload package must name:

```text
workload_id
model_id and model version
dataset_id and dataset version
task type
primary metric
failure cost
latency deadline
energy or power budget
temperature and voltage range
weight update class
safety boundary
digital baseline
```

## System Boundary

The implementation boundary is the complete path below:

```text
model and dataset
  -> graph analysis
  -> task-specific metric definition
  -> analog/digital partition
  -> tile and bit-slice mapping
  -> DAC input conversion
  -> analog weighted sum
  -> wire, device, drift, and noise effects
  -> ADC output conversion
  -> digital accumulation and correction
  -> task-sensitive accept or fallback decision
  -> digital operators and memory movement
  -> runtime output
  -> latency, energy, thermal, reliability, and task evidence
```

The system must include the analog array, ADCs, DACs, SRAM or buffers, digital support logic, runtime scheduler, calibration state, fallback path, host or board boundary, and measurement instrumentation. Array-only TOPS/W is not an end-to-end result.

## Architecture Decision

### Analog candidates

The first implementation should target:

- large fixed-weight matrix multiplications
- dense MLP or feed-forward layers
- fully connected layers
- convolution layers that map efficiently to repeated matrix work
- fixed Q, K, V, and output projections when a transformer workload is introduced
- repeated sensor-side feature extraction

An operation is an analog candidate only when its weight reuse, precision need, tile fit, conversion cost, and error tolerance have been written down.

### Digital-required work

The first implementation should keep these functions digital:

- bias and scale correction
- activation functions unless an approximation is specifically proven
- LayerNorm and other normalization
- Softmax and probability normalization
- dynamic attention score selection
- KV-cache reads, writes, and addressing
- reshaping, routing, and irregular tensor movement
- sampling and discrete decisions
- runtime scheduling
- calibration and tile-health monitoring
- error accumulation and residual repair
- safety checks and independent control logic
- digital fallback execution

This split is a starting hypothesis. The compiler may change it only when new evidence shows that an operation remains within its task error, timing, energy, and reliability budgets.

## Workstreams

### 1. Freeze The Workload Contract

Select one real model, one dataset, one task metric, and one fair digital baseline. Define the failure that matters. Do not use generic accuracy where the task requires recall, false-alarm rate, task completion, latency deadline, or control stability.

Required outputs:

- `workload_contract.json`
- baseline model output artifact
- baseline metric report
- dataset provenance and split record
- acceptance threshold and failure slices

Done means another engineer can reproduce the digital baseline from the package without interpretation.

### 2. Import And Analyze The Model

Read the model graph and emit a complete operator inventory. For every operation, record its shape, data type, weights, activation path, memory movement, sensitivity, and likely execution placement.

Required outputs:

- `model_graph.json`
- `operator_inventory.json`
- `hardware_placement.json`
- unsupported-operation report
- converter-boundary report
- fallback-point report

The placement record must not hide unsupported operations behind a successful partial map.

### 3. Define The Hardware Profile

Freeze the target assumptions before simulation:

- tile dimensions and number of tiles
- physical cell precision
- effective weight precision
- bit-slice count and significance order
- DAC and ADC precision
- converter latency, energy, area, and range
- accumulation width and overflow margin
- SRAM and buffer capacity
- memory bandwidth
- calibration interval and correction format
- temperature and voltage operating range
- digital fallback capacity

Required output:

- `hybrid_hardware_profile.json`

Every later result must point to the exact profile used. Results from different profiles must not be mixed.

### 4. Build The Compiler-Like Mapping Pass

The first compiler pass does not need to be a complete MLIR backend. It must be a deterministic mapping pass that consumes the model graph and hardware profile and emits an executable review record.

For each operation it must decide:

- analog, digital, mixed, unsupported, or blocked
- tile placement
- tile count
- bit-slice count
- partial-sum method
- ADC/DAC schedule
- memory transfers
- calibration profile
- residual budget
- fallback target
- governor fields

Required output:

- `hybrid_execution_plan.json`
- human-readable mapping report
- compiler mapping test cases

The mapping pass must include negative cases where it refuses analog placement.

### 5. Implement Bit Slicing And Precision Rules

For every analog weight, translate logical model precision into physical storage and read operations.

The implementation must record:

```text
logical weight bits
physical cell bits
slice count
slice significance
programming range
read order
per-slice ADC range
digital recombination rule
partial-sum width
```

Required outputs:

- `bit_slicing_plan.json`
- bit-slice unit tests
- precision and overflow analysis
- latency and energy cost per slice

Done means the same bit-slicing plan is consumed by the simulator, compiler report, runtime schedule, and hardware testbench.

### 6. Build The Analog Measurement Model

Model the complete analog signal path, not an ideal matrix multiply:

```text
digital activation
  -> DAC code and row voltage
  -> conductance-weighted current
  -> wire resistance and voltage drop
  -> device variation and programming error
  -> read noise and drift
  -> bit-slice accumulation
  -> ADC code
  -> digital correction
```

Required outputs:

- physical error budget
- per-tile residual report
- ADC/DAC operating-point report
- bit-slice error report
- temperature and voltage sweeps
- CrossSim or equivalent layout-risk payload
- AIHWKIT or equivalent device-behavior payload

The simulator must report both the final residual and its physical cause.

### 7. Measure Model Sensitivity

Inject the measured or simulated analog error into the actual model and determine where it matters.

Compare:

- digital full-precision baseline
- digital quantized baseline
- ideal analog mapping
- nonideal analog mapping
- calibrated analog mapping
- calibrated analog mapping with digital residual correction

Measure the error at both intermediate layers and the final task output. Attention selection, logits, safety outputs, rare-event detection, and action outputs receive stricter treatment than tolerant hidden projections.

Required outputs:

- `model_sensitivity_report.json`
- layer or block sensitivity ranking
- task metric by precision and noise condition
- failure-slice report
- recommended precision and placement by layer

### 8. Implement The Digital Referee And Runtime Governor

The runtime must decide whether an analog result is safe to use. The decision must be based on evidence, not only on static operator type.

Inputs to the governor include:

- operation class
- residual estimate
- model sensitivity
- calibration age
- tile health
- ADC saturation
- cumulative error
- queue pressure
- deadline remaining
- fallback availability

The governor must support:

```text
allow analog
allow analog with correction
retry or recalibrate
throttle
fallback to digital
disable unhealthy tile
```

Required outputs:

- integrated scheduler/governor RTL
- reason codes for every decision
- generated request trace
- fallback and recovery trace
- RTL testbench and assertions

### 9. Implement Digital Support Logic

Build the digital path that makes the analog block usable:

- activation buffering
- ADC/DAC control
- partial-sum accumulation
- scale, bias, and residual correction
- activation functions
- normalization
- attention control where applicable
- cache and tensor movement
- scheduler and queue handling
- calibration state
- tile-health counters
- timeout and fallback handling

The digital path must be capable of completing the workload when every analog tile is disabled. This provides a correctness fallback and a fair reference for partial analog service.

### 10. Verify RTL And Physical Digital Implementation

Verify normal operation, fallback, stale calibration, ADC saturation, excessive residual error, weak tiles, queue pressure, timeout, reset, and recovery.

Then run:

```text
RTL simulation
  -> lint
  -> synthesis
  -> timing analysis
  -> floorplan
  -> placement
  -> routing
  -> DRC/LVS/antenna checks
```

Required outputs:

- RTL regression report
- synthesis report
- timing report
- routed layout
- DRC/LVS/antenna report
- physical digital area and timing summary

The current OpenLane result is exploratory evidence for the controller. It must not be described as full-chip signoff.

### 11. Build Or Integrate The Analog Boundary

The analog implementation must provide evidence for the converter and tile boundary:

- DAC row settling
- input voltage accuracy
- analog output range
- ADC input range
- comparator offset and noise
- ADC conversion latency
- ADC energy per conversion
- bit-slice read schedule
- extracted parasitic impact
- calibration behavior
- temperature and voltage drift

Required outputs:

- converter circuit evidence package
- extracted analog frontend result
- ADC/DAC timing and energy report
- calibration record
- analog boundary readiness decision

Passing RTL and OpenLane results do not prove the analog array or converter.

### 12. Integrate The Board Runtime

The board must execute the same workload package and execution plan used by the simulator. It must report:

- board identity and revision
- model package ID
- workload and dataset ID
- runtime version
- calibration profile
- analog and digital placement
- fallback events
- latency distribution
- power measurement window
- thermal samples
- output and task result

Runtime and power measurements must share the same run ID, package, workload, board, and timestamps. Otherwise they cannot support an energy-per-inference claim.

### 13. Run The End-To-End Task

Run the digital baseline and hybrid implementation on the same held-out workload.

The final report must include:

```text
task metric
metric tolerance
sample count
latency p50, p95, and worst case
jitter
energy per inference or per task
active and idle power
thermal behavior
fallback rate
calibration age and recovery
failure slices
analog coverage
digital fallback coverage
memory movement
```

Example final result:

```text
Task: tactile slip detection
Digital task success: 98.2%
Hybrid task success: 97.6%
Allowed loss: 1.0 percentage point
Decision: pass

Hybrid p95 latency: 1.7 ms
Deadline: 2.0 ms
Energy per inference: 0.42 mJ
Digital baseline: 1.80 mJ
False alarms: 0.8 per 1,000 grasps
Fallback rate: 3.1%
Thermal limit: pass
```

The numbers above are illustrative. They are not current project results.

### 14. Close The Evidence And Claim Loop

Every result must be imported into one evidence package and tied to the same workload, model, hardware profile, run, and provenance.

The claim system must distinguish:

- source context
- estimate
- simulation
- RTL evidence
- synthesis and physical-flow evidence
- converter evidence
- board measurement
- repeated product evidence

The final claim must state exactly what was tested. For example:

```text
On board revision B, using workload package W, model M, dataset D,
and calibration profile C, the hybrid path achieved task metric X,
p95 latency Y, and energy Z over N runs. Analog service covered the
listed projection layers. The remaining operations used the digital path.
```

The system must also state what remains unproven.

## Acceptance Gates

The goal is complete only when all gates pass.

### Gate A: Workload Reproducibility

- Real model and dataset are versioned.
- Digital baseline is reproducible.
- Primary task metric and failure cost are explicit.

### Gate B: Mapping Reproducibility

- Analog and digital placement is machine-readable.
- Tile, bit-slice, converter, and fallback decisions are explicit.
- Negative and unsupported cases are visible.

### Gate C: Model Correctness

- Nonideal analog results run through the actual model.
- Task metrics are measured on the actual dataset.
- Failure slices are reported.
- Accuracy claims are tied to a tolerance.

### Gate D: Physical Cost Accounting

- ADC/DAC cost is included.
- Memory movement and digital fallback are included.
- Bit-slicing cost is included.
- Thermal and calibration costs are included.

### Gate E: Runtime Safety

- Governor decisions are tested in RTL.
- Fallback works when analog is refused.
- Stale calibration and unhealthy tiles are handled.
- Safety logic is independent of approximate analog output.

### Gate F: Physical Digital Evidence

- RTL is simulated.
- Timing and area are reported.
- Routed digital implementation passes the declared checks.

### Gate G: Board Evidence

- Runtime traces come from the target board.
- Power and runtime windows are synchronized.
- p50, p95, worst-case latency, and jitter are recorded.
- Thermal behavior and fallback rate are recorded.

### Gate H: End-To-End Task Proof

- The same task is run on digital and hybrid paths.
- The hybrid path meets the task threshold.
- The hybrid path meets the timing and energy thresholds.
- The report identifies exactly which operations ran analog and digital.
- The claim is limited to the tested workload and conditions.

## Current Starting Point

The project already has a local proof loop covering:

- backend model placement
- analog and digital operator classification
- local analog residual modeling
- AIHWKIT and CrossSim adapter paths
- model sensitivity checks
- digital governor RTL
- RTL testbench
- synthesis and exploratory OpenLane evidence
- evidence import and claim-readiness logic

The major remaining gaps are:

- one real model and task dataset
- a full shared bit-slicing plan
- integrated compiler-to-runtime scheduling
- stronger physical analog and converter evidence
- measured board runtime
- synchronized power and thermal measurement
- final task results on the board

The current state therefore supports a local architecture and evidence-loop claim. It does not yet support a claim that a complete real workload has been proven on analog hardware.

## Current Execution Status And Next Physical Gate

The first implementation slice is now concrete enough to expose the real bottleneck rather than hide it behind an ideal-array result:

- A deterministic model-backed MLP task runs through a digital baseline and a quantized analog candidate.
- A generated audio feature workload runs through the same task-metric, analog-error, stress-sweep, and governor interfaces.
- A larger transformer-MLP surrogate has twelve fixed-weight MatMul candidates. CrossSim currently passes its held-out residual threshold; the AIHWKIT setting currently fails it and is correctly rejected by the governor.
- The digital scheduler and error-budget governor have executable RTL traces, synthesis evidence, and exploratory physical-flow packages.
- Converter and frontend work has real Sky130/SPICE and extracted-layout evidence, but it is not yet a full converter proof.

The most important physical finding is the interface between the extracted sampling frontend and the attached preamplifier. The standalone frontend can transfer roughly `43.8%` of the sampled differential signal, but the attached-preamp run currently transfers only about `4.18%`. The attached signal therefore loses about `10.47x` before the latch or SAR loop is evaluated. The attached preamplifier itself can produce more than `0.5 mV` of output difference in a controlled transistor fixture, but that result does not prove the extracted frontend-to-latch path.

This creates the next hard gate:

```text
redesign one frontend-to-preamp interface
  -> re-extract the changed layout
  -> rerun attached transient transfer for both polarities
  -> preserve sign and reach at least 0.5 mV output difference
  -> verify startup, offset, noise, and loading across corners
  -> only then connect the clocked latch and SAR readout
```

The first candidate is to reduce non-signal capacitance on the two sense nodes while preserving approximately `0.8 fF` of useful sample coupling. The immediate target is average sense-node capacitance at or below about `2.00 fF`, or an equivalent redesign that raises sample-to-sense transfer to at least about `39.9%` at the current measured preamplifier gain. A redesign is accepted only from a same-run extracted simulation; a first-order estimate or a standalone transistor fixture is not enough.

In parallel, the system-level proof must keep the analog path honest. The current local cost model says a small audio feature workload should remain digital because converter overhead is not amortized. Analog becomes a candidate only for larger, reused matrix work where converter sharing and row count create a measured advantage. The larger transformer-MLP slice is therefore the right software-to-hardware bridge, while the audio workload remains a regression test for task quality and fallback behavior.

The next implementation sprint is therefore:

1. Complete one extracted frontend-to-preamp redesign candidate and rerun both-polarity transient evidence.
2. Add the accepted frontend result to the converter evidence contract without weakening strict import rules.
3. Close the clocked latch and SAR readout path with the same input, timing, noise, and energy definitions.
4. Re-run the converter break-even model using values from that same physical run.
5. Map the passing converter boundary into the twelve-operation transformer-MLP slice.
6. Run the integrated scheduler on measured or extracted converter limits, including stale-calibration and unhealthy-tile fallback.
7. Move the accepted digital controller and converter interface to a board-level runtime harness with synchronized task, latency, power, and thermal traces.

Until these gates pass, the correct project conclusion is: **the architecture and digital control loop are executable, the larger model path has a simulator-backed candidate, and the analog hardware path remains under physical validation.**

### Latest Interface Experiment

The first two extracted redesign candidates were run rather than accepted from arithmetic alone:

| candidate | sense-node target | both polarities measured | minimum preamp output difference | result |
|---|---:|---:|---:|---|
| lower wasted capacitance | `2.004 fF` average | yes | `50.4 uV` | margin fails |
| stronger coupling plus lower waste | `2.004 fF` average | yes | `69.5 uV` | margin fails |

An ideal active-isolation macro with `50 aF` input capacitance was then swept in front of the Sky130 preamp. The highest-gain setting produced `16.9 mV`, so the amplitude problem is solvable in principle. However, the current output polarity convention did not preserve the sign for both input cases, and the macro is not a transistor implementation. The correct conclusion is therefore:

```text
active isolation is a promising architecture target,
but not yet a working circuit.
```

The next acceptance test must use a polarity-explicit real transistor fixture. It must document whether the interface is non-inverting or inverting, define the expected output node order, prove both signs, and then repeat the test with the extracted frontend attached. A high output amplitude with the wrong sign is a task failure, not a partial pass.

The first polarity-swapped transistor rerun initially timed out because its wrapper imposed an unjustified `20 s` limit. After restoring the base fixture's `120 s` convergence budget, both nonzero cases completed with the polarity-corrected wiring, zero timeouts, and a minimum corrected output difference of `0.7932 mV`. This clears the schematic handoff gate, but it does not prove extracted layout, offset/noise corners, latch decision, or SAR conversion. Only completed runs with those additional boundaries can contribute to accepted converter evidence.

The first two-phase preamp-then-latch fixture now also clears its bounded schematic gate. Both target-edge cases completed; the minimum pre-latch differential was `0.7469 mV`, the final latch magnitude was `1.371 V`, and sampled-node kickback was `19.9 uV` versus the `219.7 uV` hard limit. The raw output is inverted exactly as required by the polarity contract. This is a meaningful handoff result, but it still uses schematic transistor models and does not measure comparator offset, noise, SAR bit cycling, extracted parasitics, area, or energy.

The next physical chain is therefore:

```text
two-phase schematic pass
  -> add explicit offset and noise injections
  -> sweep SAR threshold and all bit decisions
  -> replace schematic devices with extracted latch/readout parasitics
  -> measure conversion time, energy, and area
  -> feed those values into the converter break-even and model governor
```

The current bounded wrong-code proxy is documented in `docs/research/sky130-two-phase-offset-noise-sweep.md`: all 80 tested combinations pass, but the result remains a planning bound until offset and noise are measured on the transistor circuit.

The subsequent 12-decision SAR integration exposes the stricter requirement. Across `1,512` critical-transition combinations with both disturbance directions, `1,144` fail the wrong-code proxy when the deliberately aggressive offset, noise, and kickback terms are combined. The project must therefore report transition-level wrong-code risk; a passing latch amplitude or a passing average-error test is not enough to claim 12-bit conversion.

The deterministic transistor offset sweep now measures all five requested points with zero timeouts after separating the latch-free preamp boundary and using a `20 ps` offset-only timestep. The zero-input case is exactly balanced, and all four nonzero points preserve preamp polarity, so the deterministic zero crossing is `0 mV` in this fixture. This is a real operating-point result, but it still does not establish random noise, mismatch, or process-corner distributions.

The first three-corner sweep completes all nine cases, but it finds an important distinction: the slow, cold, low-supply corner preserves polarity while reducing the `+/-0.2 mV` preamp differential to about `15.5 uV`, far below the `0.5 mV` handoff target. The system must therefore govern on amplitude margin, not only sign or convergence; that corner is currently an analog reject/fallback condition.

The independent full PVT matrix expands this to `3 process x 3 temperature x 3 supply` and `54` nonzero transient cases. `53` cases measured and all `53` preserved polarity, but only `39` met the `0.5 mV` preamp-margin target; one fast/hot/high-supply case did not converge within the run budget. The result sharpens the design conclusion: the analog operating envelope is currently narrower than the nominal design point, and both low signal amplitude and non-convergence must be treated as digital-fallback conditions. The full matrix is published in `docs/research/sky130-two-phase-transistor-full-pvt.md`, and its measured rows now feed `scripts/run_transistor_corner_governor_bridge.py`.

The first transistor-switched capacitor-DAC boundary is now measured as well. Five of six code cases completed; code `15` timed out, and code `8` showed about `574 mV` top-plate error against a `56.25 mV` 4-bit half-LSB target. This is not a converter pass. It points to a concrete redesign question around complementary switch timing, bottom-plate common mode, and charge redistribution. The result is published in `docs/research/sky130-transistor-switched-capacitor-dac.md` and remains excluded from SAR acceptance.

The first switch-sizing and timing diagnostic improves the transistor-DAC boundary to `16/16` measured codes with monotonic ordering, using `16 um` PMOS, `8 um` NMOS devices, and a `70 ns` redistribution read point. Codes `8` through `11`, `14`, and `15` exceed the `56.25 mV` half-LSB target, with worst error about `206.9 mV`. The DAC has complete usable ordering but not accurate thresholds; it remains excluded from SAR acceptance.

The deterministic calibration analysis makes the next decision explicit: the six measured DAC codes are monotonic, but the largest error is about `1.84 LSB` and `10` of `16` codes are still unmeasured. A lookup-table correction could be investigated only after all codes, PVT, mismatch, noise, and repeatability are measured. It cannot substitute for a physical SAR acceptance result.

The representative DAC PVT-code run then measures `8/9` endpoint, midscale, and full-scale cases. Code `8` remains near `0.53 LSB` error across nominal and slow/cold/low-supply corners, while code `15` ranges from about `1.83` to `2.50 LSB`; one fast/hot/high-supply endpoint times out. The error is therefore operating-point dependent, so a nominal calibration table cannot yet be trusted by the SAR controller.

The PVT calibration policy makes that conclusion executable. It tests a simple endpoint gain/offset correction using codes `0` and `15`, then checks the corrected midscale code `8`. The nominal corner would still leave code `8` about `3.44 LSB` away from its target, and the slow/cold/low-supply corner about `3.68 LSB` away; the fast/hot/high-supply corner is incomplete because code `0` times out. All three representative corners therefore receive `digital_fallback`. This is a useful negative result: the measured transfer shape cannot be repaired by a two-point correction, so the next work is a real calibration model and distributional testing, not a prettier table. The policy is published in `docs/research/sky130-transistor-dac-pvt-calibration-policy.md` and is now included in the generated current-system state.

The controlled mismatch run makes the physical cause more concrete. Four capacitor-ratio patterns, including an MSB +2%, LSB -2%, and alternating +/-2% pattern, are measured at codes `0`, `8`, and `15`: `12/12` cases complete and all four patterns remain monotonic, but only `4/12` code checks meet half-LSB. Midscale error rises from `0.534 LSB` in the matched pattern to `0.647 LSB` in the alternating pattern. More importantly, the top plate moves by roughly `175-250 mV` between the early 3 ns read and the 70 ns settled read at codes `8` and `15`. The DAC is therefore not just statically mis-scaled; comparator timing changes the threshold it sees. This result is published in `docs/research/sky130-transistor-dac-mismatch-sweep.md` and keeps random mismatch yield and SAR acceptance open.

The dedicated settling sweep tests that timing dependency directly. At code `8`, the DAC is within half-LSB at `5 ns` but fails again from `10 ns` onward, settling at `+0.534 LSB`. At code `15`, it passes at `3`, `5`, and `10 ns`, then fails from `20 ns` onward and settles at `-1.839 LSB`. Therefore a single global comparator clock cannot be justified by one “settled” measurement: the code, switch trajectory, and measurement instant interact. The next closed-loop SAR test must record the exact decision time for every bit and judge the result at that time. The timing evidence is published in `docs/research/sky130-transistor-dac-settling-sweep.md`.

The measured-transfer SAR replay then puts all 16 nominal physical thresholds into the binary-search algorithm. With a perfect comparator and ideal input centers, only `10/16` regions return the expected code: codes `8-11` are pulled down to `7-10`, while codes `13-14` jump to `15`. This is not a same-deck transient, but it is a strong causal bridge: the measured DAC alone is sufficient to create wrong digital answers. Comparator noise and mismatch would add risk rather than explain it away. The replay is published in `docs/research/measured-transistor-dac-sar-replay.md`.

The first same-deck DAC-to-comparator bit test initially measured `1/2` correct polarities because the comparator sampled before the DAC had redistributed its charge. A source-follower isolation attempt reduced loading but introduced a nonlinear midrange transfer; its all-code control sweep passed only `12/16`, with codes `9-12` failing. The earlier direct-late repair then passed `16/16` nominal polarities using a `5.1-5.6 ns` comparator sample window before a `7.7 ns` latch. That historical run closed the code-level sign contract, but it did not solve the source-acquisition load.

The retained-bit sequence now uses the physical DAC/comparator runner for every proposed bit. All `20/20` comparator trials measure and preserve the comparator sign, but only `0/5` representative conversions return the expected ideal code: the physical threshold shape changes the result even when the comparator is behaving consistently. Expected code `0` becomes `5`, expected code `2` becomes `8`, and expected code `7` becomes `14`. This is the strongest current answer to “does the converter work end to end?”: the decision circuit works at the tested signs, but the uncalibrated physical DAC does not yet produce correct multi-bit codes. The sequence is published in `docs/research/sky130-physical-dac-sar-sequence.md`.

The latest source-matched calibration run measures all `16/16` physical thresholds at the low-source SAR interface using the PMOS-only bottom-plate topology and the corrected `9.0 ns` pre-sample DAC threshold point. It completes `20/20` retained-bit comparisons and recovers `5/5` representative conversions. The measured threshold range is `0.002633..1.799311 V`, minimum adjacent spacing is `103.412 mV`, and the rank-preserving logical-to-physical map is injective. This is the authoritative current nominal calibration result; it does not yet create PVT, mismatch/noise, continuous-SAR, extracted-layout, board, or silicon acceptance.

A topology audit qualifies the historical result. The selected cell used in the old `5/5` run turned on both a PMOS to `VDD` and an NMOS to ground. A PMOS-only rerun removes that rail contention and preserves all `4/4` tested high-code comparator signs, but code `14` and code `15` remain only `16.361 mV` apart when measured at the corrected pre-sample point; the NMOS-only branch collapses toward the source. The corrected PMOS-only SAR run consequently passes the current five representative conversions, but only over the tested low/mid-code set. The old rail-contention `5/5` result is calibration evidence for a rejected research fixture, not acceptance of the physical cell. The topology comparison is published in `docs/research/sky130-bottom-plate-topology-sweep.md`.

The coupled sample-capacitance sweep then tests the suspected interface load directly. At code 15, `200 fF` and `20 fF` comparator storage produce about `2.082 V` and `2.096 V` respectively, while `2 fF` falls to about `1.776 V`. All tested points preserve comparator polarity, but the response is non-monotonic. The practical conclusion is that comparator storage, switch charge injection, and available settling time must be co-designed; selecting a tiny capacitor by full-scale voltage alone is not a valid fix. The sweep is published in `docs/research/sky130-coupled-sample-cap-sweep.md`.

The combined interpretation is now more specific than “the DAC needs calibration.” Three questions are separated. First, can the decision circuit tell which side of a threshold it is on? Nominally yes: the physical DAC and comparator preserve polarity for all `16/16` trial codes. Second, does the selected low-source PMOS-only capacitor network create legal, spaced, bijective thresholds? Nominally yes: all three gates pass after source-matched rank-preserving calibration. Third, does that result survive real disturbance and repeated operation? Not yet: the existing mismatch and settling evidence is from earlier non-equivalent fixtures, while transistor-level PVT/noise and continuous-SAR evidence remain open. The current design implication is to keep the analog path behind a measurable governor and run the selected candidate through those robustness gates before enabling it for model-level claims.
The bottom-switch sizing experiment sharpens the next design move. Halving the current `16/8 um` bottom-plate switch widths preserves all four high-code comparator signs, but lowers code `15` from `2.413 V` to `2.371 V` and leaves codes `14` and `15` separated by only about `11 mV`. Therefore the upper collapse is not fixed by shrinking that switch alone. The next candidate must change the charge-transfer topology or gate-headroom/control waveform, and it must be judged by threshold spacing, settling, energy, and decision margin together. The negative result is published in `docs/research/sky130-bottom-switch-scale-sweep.md`.

The PMOS gate-headroom diagnostic then tests a controlled overdrive directly. With the PMOS-only bottom-plate cell driven to `-0.6 V` during redistribution, both codes `14` and `15` complete and preserve comparator polarity, but their corrected pre-sample thresholds are separated by only `17.118 mV`, still below the `56.25 mV` half-LSB target. Gate overdrive alone is therefore rejected as the repair. The result is published in `docs/research/sky130-pmos-gate-overdrive-diagnostic.md`; the next candidate must change the charge-transfer path or waveform rather than only the gate bias.

The subsequent PMOS strength sweep tests `2x` and `4x` bottom-plate devices under the same long-acquisition timing. Both high-code pairs complete and preserve polarity, but spacing remains `17.265 mV` and `17.250 mV`, respectively. Stronger devices alone are therefore rejected as well. The evidence is published in `docs/research/sky130-bottom-switch-strength-diagnostic.md`; the next candidate must change the charge-transfer topology or waveform.

The isolated LSB-ratio diagnostic then tests a `4x` LSB capacitor across codes `12-15`. All four cases complete and preserve comparator polarity, but adjacent DAC spacings are `293.782 mV`, `-104.561 mV`, and `144.058 mV`; the transfer is non-monotonic. Increasing only the LSB capacitor is therefore rejected. The result is published in `docs/research/sky130-lsb-ratio-diagnostic.md`; the next candidate must rebalance the complete charge-transfer network.

The thermometer-coded equal-unit-capacitor experiment tests a different DAC
architecture rather than another binary sizing point. The full `0-15` run uses
sixteen `1 pF` unit capacitors, `2x` bottom switches, zero-volt sampled input,
and the long-acquisition comparator fixture. The bounded `90 s` full run
measures `12/16` codes; codes `0`, `1`, `14`, and `15` exceed that convergence
budget. Codes `2-13` converge with correct polarity and approximately `56.85
mV` adjacent spacing. Separate `240 s` endpoint reruns converge all four
endpoints, but code `0` reaches `-1.438 mV`; the upper pair measures `56.862
mV` spacing. The focused `7,8` probe also clears the `56.25 mV` half-LSB
threshold. The baseline timing candidate is rejected because its endpoint
convergence and legal-range/runtime contract are not closed; the result is not SAR, PVT,
mismatch, noise, extracted-layout, energy, board, or silicon evidence. The
artifact is published in
`evidence/aimc-simulator-adapters/sky130-thermometer-dac-comparator-summary.md`.
The next physical design task is a full-range DAC redesign, followed by
calibrated SAR integration, repeatability, PVT, mismatch, noise, settling,
extraction, area, and energy gates.

An opt-in temporary top-plate NMOS clamp was also tested as an endpoint repair.
It reduced code-0 undershoot to `-0.215 mV`, but reduced code `0 -> 1` spacing
to `12.54 mV`; it is rejected as an acquisition-loading fix. The next circuit
revision must use isolated initialization/precharge control and then repeat
the complete physical threshold and SAR gates.

A `0.25x` source-switch trial preserved polarity but reduced code `0 -> 1`
spacing to `29.92 mV` and maximum top plate to `0.253 V`; source-switch
shrinking is rejected as the full-range repair. The active hardware task is now
a split or bootstrapped charge-transfer topology before SAR integration.

A bootstrapped source-gate trial (`0.5x` source switches, `+0.6 V` overdrive)
preserved endpoint polarity and legal range but produced only `55.59 mV`
minimum spacing and `0.891 V` code-15 output. Gate drive alone is rejected;
the next hardware revision must change the charge-transfer architecture.

A split odd/even trial with eight coarse units and a half-size fine capacitor
also failed: all four endpoints converged, but minimum spacing was `50.38 mV`,
code 15 reached `0.759 V`, and the low endpoint was outside the legal range.
The next design needs explicit capacitive level shifting or a true split-bank
charge-transfer network.

A complementary differential implementation with sixteen positive and sixteen
negative unit capacitors failed to converge even at code 0 within `120 s`. It
is rejected as currently implemented; a differential redesign must first solve
explicit initialization and simulator convergence before threshold or SAR
claims are attempted.

At `0.9 V` common mode, the differential fixture converged but its two plates
moved together and produced `0 mV` code spacing. The current complementary
control wiring is rejected as non-opposing; no differential range claim is
accepted.

A minimum-width, longer-channel clamp variant recovered `57.70 mV` code `0 ->
1` spacing, but code 0 remained at `-1.387 mV`. The clamp family therefore
still fails the legal-range gate and remains excluded from SAR integration.

## Execution Order

Work in this order:

1. Freeze the workload contract.
2. Produce the real model graph and digital baseline.
3. Extend placement and bit-slicing records.
4. Run the real model through nonideal analog simulation.
5. Measure task-specific quality and failure slices.
6. Connect placement and sensitivity to the integrated governor.
7. Complete converter and analog-boundary evidence.
8. Verify and physically implement the digital controller.
9. Build the board runtime and measurement harness.
10. Collect synchronized runtime, power, thermal, and task evidence.
11. Import the complete package and run claim-readiness checks.
12. Repeat the same flow on a second workload to test reuse.

## Reuse Requirement

The first workload is not complete if it only produces a one-off result. The tools must make the next workload cheaper to evaluate.

The reusable interface is:

```text
workload contract
  -> model graph
  -> placement
  -> bit-slicing plan
  -> analog profile
  -> task metric adapter
  -> governor trace
  -> board run
  -> evidence package
```

The second workload should reuse the same schemas, simulator boundary, governor interface, measurement format, and claim rules. Only the model, dataset, task metric, and workload-specific thresholds should change.

## Final Definition Of Done

This goal is achieved when an independent reviewer can:

1. Download the exact model and dataset references.
2. Reproduce the digital baseline.
3. Inspect the analog/digital partition.
4. See every tile, bit-slice, converter, and fallback decision.
5. Reproduce the analog simulation and model-level task test.
6. Inspect the governor's analog or digital decision trace.
7. Verify the digital RTL and physical-flow evidence.
8. Identify the board, runtime, calibration, and measurement windows.
9. Compare hybrid and digital task, latency, energy, thermal, and reliability results.
10. State precisely what the evidence proves and what it does not prove.

The durable outcome is not merely a successful demo. It is a repeatable system that can answer, for each workload:

```text
what should run analog,
what must remain digital,
how much the analog path costs,
when it must fall back,
whether the physical errors change the task,
and whether the complete system is better than the digital baseline.
```
