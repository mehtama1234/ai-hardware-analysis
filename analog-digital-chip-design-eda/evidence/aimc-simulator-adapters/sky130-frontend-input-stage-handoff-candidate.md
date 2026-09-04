# Sky130 Frontend Input-Stage Handoff Candidate

- status: `active_macro_handoff_passed_not_sky130_transistor_or_strict_evidence`
- candidate id: `aimc_readout_candidate_001`
- handoff candidate: `sky130_frontend_input_stage_handoff_candidate`
- run id: `aimc_readout_candidate_001_frontend_input_stage_handoff_candidate_run001`
- source frontend netlist: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/sky130_ultra_sense_capacitive_frontend_extracted.spice`
- generated deck: `labs/analog/analog-in-memory-foundation-model-hardware/spice/sky130_frontend_input_stage_handoff_candidate.sp`
- active gain V/V: `9.201769`
- uses extracted frontend netlist: `True`
- uses active gain macro: `True`
- uses Sky130 transistor input stage: `False`
- case count: `4`
- measured case count: `4`
- sign pass count: `4`
- active output margin pass count: `4`
- loading pass: `True`
- minimum output diff V: `6.206000000e-04`
- same-run strict payload ready: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-frontend-input-stage-handoff-candidate.csv`

## First Principle

A handoff is real only when the output of one block becomes the input of the next block in the same circuit equations. This deck includes the extracted ultra frontend and an active gain element together. The frontend stores and moves charge. The active element turns the resulting signed sense voltage into a larger signed output voltage.

This closes the same-deck handoff at the active-macro level. It still does not close the transistor handoff. The macro uses the measured local input-stage gain, but it does not load the frontend like a real Sky130 input pair, and it does not show transistor operating point, offset, noise, kickback, or latch resolution.

## Acceptance Tests

- A1_bounded_simulator_run: `True`
- A2_sign_handoff: `True`
- A3_active_output_margin: `True`
- A4_loading_check: `True`
- A5_claim_boundary: `True`

## Result

| reset mode | input diff mV | sense diff uV | output diff mV | transfer ratio | sign preserved | margin pass |
|---|---:|---:|---:|---:|---|---|
| `quiet_vcm` | `-0.152971` | `-68.000000` | `-0.620800` | `0.444444` | `True` | `True` |
| `quiet_vcm` | `0.152971` | `68.000000` | `0.620600` | `0.444444` | `True` | `True` |
| `reset_pulse` | `-0.152971` | `-67.000000` | `-0.620800` | `0.437908` | `True` | `True` |
| `reset_pulse` | `0.152971` | `67.000000` | `0.620600` | `0.437908` | `True` | `True` |

## Strict Blockers

- The active input stage is represented by a bounded gain macro, not a Sky130 transistor input-stage netlist.
- The run proves same-deck frontend-to-active-macro handoff, not transistor operating point, offset, noise, or latch resolution.
- There is no SAR loop, DAC switching, full energy integration, DRC/LVS area, or same-run strict converter payload.

## Refused Claim

does not prove Sky130 transistor input-stage handoff, clocked latch behavior, full converter behavior, accepted post-layout evidence, or replacement economics
