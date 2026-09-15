# Hardware handoff after software closeout

The model and numerical path is frozen through the sibling project's
`NON-HARDWARE-CLOSEOUT-2026-09-09.md`. The next work is hardware qualification;
no further model or range-selection changes are needed before a target exists.

## Required converter acceptance

The candidate must use one matching schematic/layout/extraction identity and
the SKY130 model/deck identity recorded with the run. For both input signs at
the declared minimum differential (currently ±0.1529705854 mV) and at ±100 mV,
it must produce the required polarity and at least 0.9 V differential margin at
the declared decision time. Reset, acquisition, regeneration and repeated
history cases must pass; a single-cycle result is insufficient.

The current extracted candidate has clean full-cell DRC and active-transistor
LVS evidence but fails the electrical margin gate. The synthetic
capacitance-balanced, drain-isolated topology passes the four single-cycle
cases, then fails one of eight repeated histories. It is a hypothesis for the
next schematic/layout iteration, not an accepted design.

## Simulation work still valid

Before hardware access, it is valid to implement the isolation topology, create
an actual layout, run extraction/DRC/LVS, and execute the full electrical
qualification matrix. The matrix should include PVT, controlled mismatch or a
clear statement that foundry mismatch models are unavailable, supply/common-mode
variation, input histories, reset recovery, noise/offset, clock feedthrough,
settling, and full converter transfer/sequence behavior. Area, rail energy and
timing must be measured on the same candidate.

The nominal reference DAC evidence remains a component assumption. Its 1 TΩ,
1 MΩ and capacitive loads are not the real array/ADC load. The recovered bank
sequence study covered 23/24 cases before the final 1 pF case timed out; it
must not be called complete settling qualification.

The timeout was a numerical-runtime failure rather than an ngspice nonzero
return: the final deck reached transient output and was terminated by the
wrapper while taking very small steps. The case is retained as an unresolved
stiffness/settling observation. A future rerun may change only solver controls
after recording timestep and integration-method sensitivity; it must not
silently replace the declared waveform or load protocol.

The saved final-bank log contains transient reference times through the deck's
5.42 µs stop time, but no `waveform.txt` was produced and no settling row can
be reconstructed. Reaching the nominal stop time in a log is therefore not
equivalent to a completed, checked waveform.

A bounded solver-sensitivity diagnostic is saved beside the case in
`solver-diagnostic-v2/`. Both altered runs (Gear integration, with and without
100 ps maximum step) also hit a 120-second timeout and produced no waveform.
This strengthens the classification as numerical stiffness or unresolved
convergence cost, but does not establish a circuit settling result. The source
deck hash and both altered deck/log hashes are recorded in the diagnostic
manifest.

## Real-target requirement

The end-to-end claim requires an actual analog-memory target, silicon, or an
equivalent device whose analog array computation is physically exercised. The
digital controller/FPGA and an external ADC can validate control and data
movement, but cannot establish analog in-memory compute. The target plan must
name the array technology, physical dimensions, programming method, converter,
accessible rails/signals, and measurement equipment before execution.

The same frozen GPT-2 projection and data contract must run on digital and
hybrid paths. Measure total task latency and energy, including calibration,
reference switching, array evaluation, conversion, transfers, host overhead,
fallback and warmup. Report distributions and uncertainty, not a single
optimistic sample. A measured lack of benefit is an acceptable conclusion.

## Handoff artifacts

- Software closeout and held-out quality: sibling
  `experiments/gpt2-hybrid-v1/NON-HARDWARE-CLOSEOUT-2026-09-09.md`.
- Joined digital-only decision: sibling
  `experiments/gpt2-hybrid-v1/decisions/20260909-finite-reference-holdout/`.
- Converter physical gate: `evidence/aimc-simulator-adapters/converter-physical-repair-current.json`.
- Repeated-history diagnostic:
  `evidence/aimc-simulator-adapters/recovery-20260909/symmetric-capacitance-diagnostic/`.
- Reference-DAC mapping:
  `evidence/aimc-hardware-lab/switched-reference-ranges/20260909-v1/`.

This document closes the simulation/software handoff boundary while retaining
the overarching hardware-backed goal. It does not authorize fabrication,
external purchases, or analog execution.
