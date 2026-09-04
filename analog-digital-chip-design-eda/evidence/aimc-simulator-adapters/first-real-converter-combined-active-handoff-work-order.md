# First Real Converter Combined Active Handoff Work Order

- status: `combined_active_handoff_work_order_ready`
- candidate id: `aimc_readout_candidate_001`
- frontend transfer ratio: `0.437908`
- frontend minimum sense diff V: `6.700000000e-05`
- separate input-stage gain V/V: `9.201769`
- estimated active output diff V: `6.165185271e-04`
- direct proxy status: `frontend_to_input_stage_proxy_timed_out_not_strict_evidence`
- same-run strict payload ready: `False`
- accepted post-layout written: `False`

## First Principle

The signal chain has two jobs. The passive frontend must not lose the sign of the sampled voltage. The active input stage must spend current to make that signed difference larger. The present evidence says the first job works weakly, and the second job works separately. The missing proof is whether the two jobs work when they are connected in one bounded circuit run.

A small-signal estimate is not enough because the active stage is not an invisible calculator. Its input capacitance, bias path, common-mode point, and operating-point solve can change the very voltage it is supposed to amplify. The next object must therefore connect the frontend and input stage directly and measure the handoff.

## New Physical Object

`sky130_frontend_input_stage_handoff_candidate`

one deck that connects the extracted ultra frontend output boundary to a Sky130 active input stage and measures whether the active output keeps sign and becomes large enough for a latch

Minimum contents:
- the extracted ultra frontend capacitance or an equivalent explicit RC network with named sense_p and sense_n nodes
- a Sky130 transistor differential input stage with bounded bias current and load
- explicit common-mode reset or bias path for sense_p and sense_n
- bounded operating-point and transient commands that finish under the local runtime gate
- positive and negative input cases at the comparator-budget edge

## Acceptance Tests

### A1. bounded simulator run

Must show: ngspice returns for every positive and negative case within the timeout bound.

Why: a proof path cannot depend on an unbounded interactive simulator stall.

### A2. sign handoff

Must show: the active output sign matches the original sampled input sign for quiet reset and reset-pulse cases.

Why: gain is useless if the circuit flips the decision.

### A3. active output margin

Must show: minimum active output difference is at least 0.5 mV before the latch.

Why: the latch needs a larger state than the passive frontend's tens of microvolts.

### A4. loading check

Must show: the added input stage does not reduce frontend sense transfer below the current 0.437908 ratio by more than 10 percent.

Why: an amplifier that steals the stored charge can erase the signal it is supposed to enlarge.

### A5. claim boundary

Must show: the result explicitly keeps accepted_post_layout_written false and same_run_strict_payload_ready false.

Why: this is still a handoff block, not the full converter payload.

## Expected Outputs

- `labs/analog/analog-in-memory-foundation-model-hardware/spice/sky130_frontend_input_stage_handoff_candidate.sp`
- `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-frontend-input-stage-handoff-candidate.csv`
- `evidence/aimc-simulator-adapters/sky130-frontend-input-stage-handoff-candidate.json`
- `evidence/aimc-simulator-adapters/sky130-frontend-input-stage-handoff-candidate.md`
- `docs/research/sky130-frontend-input-stage-handoff-candidate.md`

## Done After This Only If

- bounded ngspice run finishes for all cases
- both polarities preserve sign
- active output difference is large enough for the latch target
- the result names remaining latch, SAR, energy, noise, area, DRC/LVS, and same-run payload blockers

## Still Not Done After This

- clocked latch resolution
- comparator offset and noise
- kickback back into the sample nodes
- SAR bit cycling
- full supply-current energy
- DRC/LVS-clean extracted area
- strict accepted post-layout converter evidence

## Refused Claim

does not prove the combined active handoff, full comparator, full converter, accepted post-layout evidence, or replacement economics
