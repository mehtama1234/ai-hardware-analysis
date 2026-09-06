# Rigorous hybrid inference: active execution plan

Started 2026-09-06 with user authorization. This is the execution plan for the
recovered work across both sibling projects. Earlier research pages retain
historical experiments; their status paragraphs are not acceptance decisions.

## Long-term goal and completion condition

Build and rigorously validate one complete hybrid analog/digital inference
prototype that executes a real, versioned workload, preserves task accuracy,
and quantifies total latency and energy against an equivalent digital baseline.

The proof must connect model and dataset, operator placement, physical analog
computation and conversion, digital support, runtime execution, and task result.
Every result must identify its implementation and measurement boundary. A
repeatable finding that this implementation has no advantage is a valid research
outcome; a simulated advantage is not hardware completion.

Hardware-backed completion requires an actual analog computation path. An FPGA
controller or commercial ADC alone cannot establish analog in-memory inference.
No claim of fabricated custom silicon is allowed without that silicon.

## Project responsibilities

| Project | Responsibilities |
| --- | --- |
| `analog-digital-chip-design-eda` | Circuit design, SPICE, layout/extraction, digital RTL/EDA, compiler execution evidence, circuit-derived operating profiles |
| `analog-in-memory-ai-inference/software-architecture` | Model/data intake, placement and package contracts, simulator adapters, task evaluation, backend evidence intake, user-visible claim readiness |

Reuse the existing cross-project proof, compiler, governor RTL, simulator
adapters, and evidence contracts. Audit their actual coverage before extending
them. Both folders are inside the same Git repository.

## Recovered starting point

These are saved results inspected at recovery, not fresh reruns:

- Git HEAD: `3e873b3`; substantial later work is uncommitted.
- Software: 12 workloads, 91 operators, 321 review commands, 687 planning cycles.
- Guarded runtime: 46 analog-candidate commands retain digital fallback.
- Nominal continuous SAR: 5/5 representative conversions with legal sampled
  bottom plates. This is not full-code, full-waveform, or post-layout signoff.
- Declared 100-trial capacitor stress: 97 measured, 95 full-map/legal passes.
  This is controlled schematic stress, not foundry statistical yield.
- Latest physical sub-block: `sky130_isolated_frontend_active_load_latch`,
  7 NFETs and 4 PFETs, zero reported DRC errors, extracted netlist present.
  Integrated Sky130 transient and full-candidate LVS remain to be established.
- Prior nine-device active-load transient: 30 structural-model cases measured,
  12 classified as regenerated; this does not establish correct small-signal
  polarity or full Sky130-model operation.

The nominal schematic SAR and newest extracted latch are different evidence
objects. Their passing properties cannot be combined into a converter claim.

## Milestones and acceptance gates

### M0 — Recover a reproducible baseline (active)

1. Inventory both folders, Git revision and dirty state; preserve existing work.
2. Record hashes of source and evidence files before regenerating outputs.
3. Record executable paths, versions, simulator environments, and PDK identity.
4. Run existing software and evidence-boundary checks; preserve failures.
5. Separate current candidates, historical experiments, and simplified models.
6. Produce a restart ledger with exact commands, outcomes, and next actions.

Exit: a provenance manifest and fresh check results exist, remaining environment
gaps are explicit, and the restart ledger identifies the next circuit experiment.
A hash manifest detects changes; it is not a backup of the uncommitted files.

### M1 — Freeze workload and engineering acceptance contract

1. Inventory available real models/datasets and select one practical task.
   Keep tiny-MLP and transformer fixtures as regression fixtures, not substitutes
   for a real task. Document licensing, model weights, preprocessing, and hashes.
2. Separate calibration/training data from an untouched evaluation split.
3. Specify task metric, allowed degradation, latency distribution, energy
   boundary, repetition count, and fallback policy before final evaluation.
4. Specify memory technology, array dimensions, signed-weight representation,
   conductance range, programming/update behavior, and bit slicing.
5. Specify converter resolution, usable input/common-mode range, acquisition,
   reset/evaluation timing, throughput, load, and error budget. Resolve how the
   present four-decision prototype relates to higher-resolution architecture.
6. Allocate error and cost budgets across array, converter, digital correction,
   memory traffic, host, calibration, and fallback.

Exit: versioned machine-readable contract with numeric limits and provenance.
Unset targets remain visibly open; thresholds cannot be chosen after seeing
held-out results. Routine engineering choices can proceed within authorized scope.

### M2 — Close the extracted frontend-to-latch decision path

1. Audit the latest eleven-device netlist against intended connectivity, body
   ties, supply isolation, input/output polarity, reset, and evaluation controls.
2. Establish same-candidate DRC and LVS; record tool/deck identity and logs.
3. Build a bounded transient harness using the actual extracted topology and
   Sky130 models; keep simplified structural runs distinctly labeled.
4. Test both signs at realistic frontend amplitudes and common-mode values,
   zero-input behavior, startup states, repeated reset, and swapped inputs.
5. Measure decision polarity, settling time, usable output margin, supply
   current, and kickback into the sampled node. Inspect full relevant waveforms.
6. Compare against the M1 margin budget including offset/noise allowances.

Exit: all declared cases finish and meet the stated decision contract on the
same candidate. Convergence alone, large forced input, or DRC alone is not pass.

### M3 — Close continuous converter operation

1. Integrate the qualified decision circuit with sample/hold, DAC, and SAR control.
2. Align bit order, clear/retain polarity, calibration, valid/error, and timeout
   semantics across transistor deck, control model, and compiler interface.
3. Sweep the full supported input range and all codes, code boundaries, input
   histories, saturation, repeated conversion, and reset recovery.
4. Measure monotonicity, missing codes, INL/DNL, acquisition/decision timing,
   and rail excursions throughout operation, not only at chosen sample times.
5. Keep calibration fitting and conversion validation separate.

Exit: complete declared transfer/sequence coverage meets M1 on one candidate,
with raw waveforms, measurements, and failure handling available for replay.

### M4 — Qualify robustness and extracted physical implementation

1. Freeze matching schematic/layout identities and extraction settings.
2. Run parasitic transient checks and compare with the matching schematic.
3. Cover process/voltage/temperature and controlled component variation;
   separately establish whether statistically valid foundry mismatch models
   are available before making yield claims.
4. Probe comparator offset/noise, jitter, supply noise, leakage, metastability,
   drift and calibration sensitivity under the declared operating envelope.
5. Report seeds, attempted/completed/pass counts, failures and timeouts,
   worst cases, uncertainty, and numerical timestep/tolerance sensitivity.
6. Bind area, energy, and timing to the same candidate and operating condition.

Exit: declared qualification matrix passes or the supported operating envelope
is explicitly revised and revalidated. Synthetic stress is never renamed yield.

### M5 — Propagate circuit behavior into a real task

1. Export circuit-derived transfer/error/timing profiles with fit uncertainty
   and validity ranges; avoid double-counting ADC effects in simulators.
2. Configure CrossSim and AIHWKIT with explicit array/device assumptions.
3. Check small shared numerical cases against digital and circuit references;
   explain adapter differences instead of selecting the best reported result.
4. Run one frozen task on held-out data with nominal and stressed profiles.
5. Count accuracy, clipping, calibration cost, fallback rate, and data movement.

Exit: task limits pass with reproducible circuit-linked simulation. This remains
simulation until hardware measurements exist; tiny residuals alone are insufficient.

### M6 — Implement the real execution boundary

1. Audit existing RTL, Yosys/OpenLane evidence and review bytecode interpreter.
2. Specify target instructions/registers, SRAM transfers, synchronization,
   conversion handshake, calibration loading, and error recovery.
3. Implement the controller/runtime bridge and test against an independent
   functional reference, including invalid inputs, timeout, and fallback.
4. Verify synthesis/timing for the chosen digital target and correlate traces
   with the software schedule; planning cycles remain estimates until measured.

Exit: a complete workload execution trace crosses the defined target boundary.
FPGA/emulated control validation is explicitly distinguished from analog execution.

### M7 — Hardware-backed task and cost comparison

1. Inventory accessible hardware and measurement equipment. Prepare a concrete
   implementation, acquisition/fabrication plan, cost and expected proof scope
   before seeking any necessary purchase or fabrication authorization.
2. Execute the same model/data/task on digital and hybrid implementations.
3. Synchronize runtime and power traces; define measured rails, host overhead,
   idle subtraction, warmup, repetitions, calibration, and thermal conditions.
4. Report accuracy, latency distributions, energy per task, fallback frequency,
   uncertainty, and the full accounting boundary.

Exit: repeatable hardware-backed comparison with a defensible advantage or
documented no-advantage result. A custom-converter claim requires that converter;
a substituted component changes the claim and must be recorded.

### M8 — Publish reproducible evidence and conclusion

Package source revisions, tool/PDK setup, data/model identities, contracts,
raw measurements, scripts, derived reports, negative results, and limitations.
Verify rerun instructions and backend evidence intake against the final package.
Update the user-facing workbench from that package rather than manual claims.

Exit: a reviewer can trace every conclusion back to a named run and reproduce
the supported checks. Final status states what is measured and what remains open.

## Execution rules

- Work proceeds M0 → M1 → M2 → M3 → M4 → M5 → M6 → M7 → M8;
  software preparation can overlap physical work without promoting its claims.
- Every experiment declares candidate, hypothesis, controlled change, expected
  discriminator, timeout, output location, and acceptance criteria before running.
- Use unique run directories. Never overwrite the sole evidence for a recovered
  candidate; do not launch unbounded sweeps before validating a small case.
- All declared trials count. Missing measurements cannot be treated as passes.
- Keep schematic, extracted, simplified-model, board, and silicon evidence separate.
- Existing user work is preserved. Purchases, fabrication, external deployment,
  and messages to others require the applicable explicit authorization.
- Update the restart ledger after meaningful progress. Passing documentation
  checks does not complete a circuit or the long-term goal.

## Next bounded work package

The user requested a project-level reset after excessive sub-block iteration.
See the [current checkpoint](hybrid-inference-project-checkpoint.md): resolve
hardware feasibility and remaining M1 system requirements first. Hardware
planning moves forward now; this does not promote M7 completion or change the
original goal. Bound further converter work to an export audit and matched
transient of the latest DRC/LVS-passing revision before reassessing integration.
Do not automatically resume open-ended latch optimization.
