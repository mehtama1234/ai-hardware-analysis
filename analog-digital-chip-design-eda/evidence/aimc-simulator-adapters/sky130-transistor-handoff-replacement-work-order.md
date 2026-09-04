# Sky130 Transistor Handoff Replacement Work Order

- status: `transistor_handoff_replacement_work_order_ready`
- candidate id: `aimc_readout_candidate_001`
- replacement object: `sky130_frontend_transistor_input_stage_handoff_candidate`
- active-macro status: `active_macro_handoff_passed_not_sky130_transistor_or_strict_evidence`
- macro minimum output diff V: `6.206000000e-04`
- macro sign pass count: `4` of `4`
- direct transistor proxy status: `frontend_to_input_stage_proxy_timed_out_not_strict_evidence`
- direct transistor timed-out case count: `4` of `4`
- same-run strict payload ready: `False`
- accepted post-layout written: `False`

## First Principle

The macro proof says the signal chain is mathematically possible. The transistor replacement must show the same thing physically: the real input devices must sense the frontend voltage without stealing too much charge, must bias into a solvable operating point, and must create enough output difference for the latch.

A voltage gain macro can show that the sign and size of the signal are enough in equations. A transistor replacement must show that real devices can do the same job while adding capacitance, needing bias current, and forcing ngspice to find a physical operating point.

## Replacement Object

`sky130_frontend_transistor_input_stage_handoff_candidate`

replace the active gain macro with a Sky130 transistor differential input stage while preserving the same frontend input cases and acceptance tests

Must keep from the macro run:
- same extracted ultra frontend netlist
- same positive and negative comparator-budget input cases
- same quiet-reset and reset-pulse cases
- same sign-handoff check
- same 0.5 mV minimum active-output margin
- same explicit false accepted_post_layout_written flag

Must replace:
- bounded gain macro
- ideal output without input capacitance
- macro gain imported from separate evidence

Must add:
- Sky130 nfet or complementary input devices connected directly to sense_p and sense_n
- finite input capacitance that loads the extracted frontend
- explicit bias current or reset path that lets ngspice solve without unbounded model startup
- measured output polarity and gain from the same deck
- runtime-bound failure reporting for each case

## Acceptance Tests

- T1. every case returns from ngspice inside the runtime bound
- T2. measured sign matches the original sampled input sign in all four cases
- T3. minimum active output difference is at least 0.5 mV
- T4. sample-to-sense transfer after transistor loading stays within 10 percent of the macro handoff run
- T5. report states uses_sky130_transistor_input_stage=true, uses_active_gain_macro=false, same_run_strict_payload_ready=false, accepted_post_layout_written=false

## Expected Outputs

- `labs/analog/analog-in-memory-foundation-model-hardware/spice/sky130_frontend_transistor_input_stage_handoff_candidate.sp`
- `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-frontend-transistor-input-stage-handoff-candidate.csv`
- `evidence/aimc-simulator-adapters/sky130-frontend-transistor-input-stage-handoff-candidate.json`
- `evidence/aimc-simulator-adapters/sky130-frontend-transistor-input-stage-handoff-candidate.md`
- `docs/research/sky130-frontend-transistor-input-stage-handoff-candidate.md`

## Still Not Done After Replacement

- clocked latch resolution
- kickback into the sampled frontend
- comparator offset and noise
- SAR bit cycling
- DAC switching
- full converter energy
- DRC/LVS-clean extracted area
- same-run strict converter payload

## Refused Claim

does not prove the transistor handoff, latch, SAR, full converter, accepted post-layout evidence, or replacement economics
