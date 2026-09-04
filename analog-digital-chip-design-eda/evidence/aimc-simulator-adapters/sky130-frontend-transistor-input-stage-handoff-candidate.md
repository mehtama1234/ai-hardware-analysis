# Sky130 Frontend Transistor Input-Stage Handoff Candidate

- status: `transistor_handoff_failed_or_timed_out`
- candidate id: `aimc_readout_candidate_001`
- handoff candidate: `sky130_frontend_transistor_input_stage_handoff_candidate`
- run id: `aimc_readout_candidate_001_frontend_transistor_input_stage_handoff_candidate_run001`
- source frontend netlist: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/sky130_ultra_sense_capacitive_frontend_extracted.spice`
- generated deck: `labs/analog/analog-in-memory-foundation-model-hardware/spice/sky130_frontend_transistor_input_stage_handoff_candidate.sp`
- uses extracted frontend netlist: `True`
- uses active gain macro: `False`
- uses Sky130 transistor input stage: `True`
- case count: `4`
- measured case count: `0`
- timed-out case count: `4`
- sign pass count: `0`
- active output margin pass count: `0`
- loading pass: `False`
- minimum output diff V: `0.000000000e+00`
- same-run strict payload ready: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-frontend-transistor-input-stage-handoff-candidate.csv`

## First Principle

The active-macro handoff proved that the equations can carry the extracted frontend signal into a gain block. This run replaces that macro with real Sky130 nfet input devices. That matters because transistor gates add capacitance, transistor current needs a bias point, and the output is now produced by device equations instead of an ideal gain statement.

This is a stronger handoff than the macro run if it passes. It still stops before the latch. A comparator is not only an input pair. It must regenerate, settle before the bit deadline, avoid kicking charge back into the sample, and survive offset and noise.

## Acceptance Tests

- T1_bounded_simulator_run: `False`
- T2_sign_handoff: `False`
- T3_active_output_margin: `False`
- T4_loading_check: `False`
- T5_claim_boundary: `True`

## Result

| reset mode | input diff mV | sense diff uV | gate diff uV | output diff mV | transfer ratio | sign preserved | margin pass |
|---|---:|---:|---:|---:|---:|---|---|
| `quiet_vcm` | `-0.152971` | failed | failed | failed | failed | `False` | `False` |
| `quiet_vcm` | `0.152971` | failed | failed | failed | failed | `False` | `False` |
| `reset_pulse` | `-0.152971` | failed | failed | failed | failed | `False` | `False` |
| `reset_pulse` | `0.152971` | failed | failed | failed | failed | `False` | `False` |

## Strict Blockers

- This is a transistor input-stage handoff, not a clocked latch or SAR conversion.
- The input stage is schematic-level Sky130 devices connected to an extracted frontend; the combined active block is not DRC/LVS-clean extracted layout.
- There is no comparator offset/noise sweep, kickback test, full converter energy integration, DAC switching, SAR bit cycling, area signoff, or same-run strict converter payload.

## Refused Claim

does not prove clocked latch behavior, SAR conversion, full converter behavior, accepted post-layout evidence, or replacement economics
