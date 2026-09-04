# Sky130 Next Transistor Fixture Work Order

- status: `sky130_next_transistor_fixture_work_order_ready_not_converter_proof`
- recommended next topology: `broaden_differential_dummy_cancellation_candidate`
- known working source: `sky130-sample-switch-hold-mode-ngspice`
- best measured source: `sky130-differential-dummy-candidate-input-sweep`
- best measured hold error V: `6.300000000e-05`
- half LSB 12b V: `2.197265625e-04`
- required reduction x: `0.287`
- remaining margin x: `3.488`
- required cancellation percent: `0.00`
- max allowed differential mismatch mV: `0.2197`
- remaining comparator offset or noise budget mV: `0.1567`
- max passing tested decision uncertainty mV: `0.1530`
- candidate post-layout written: `False`
- accepted post-layout written: `False`

## First Principle

A useful next SPICE run must answer one physical question. Does a concrete transistor circuit keep the decision voltage still enough after the sampling switch turns off?

The target is no longer vague. The differential dummy-cancellation candidate now passes nominal input range and a controlled width-mismatch sweep. The remaining budget for comparator offset or noise is about 0.1567 mV, and the tested offset/noise grid passes up to about 0.1530 mV of combined decision uncertainty. A useful next proof must show that a concrete decision circuit stays inside that budget.

## Acceptance Tests

| test | requirement | why it matters |
|---|---|---|
| `runtime` | each ngspice case finishes inside 180 seconds | a proof fixture has to be repeatable in the bridge, not only possible by hand |
| `low_mid_high_inputs` | keep the input-range and controlled width-mismatch cases passing while adding noise and comparator tolerance | the nominal and simple mismatch gates now pass, so the next risk is whether the margin survives decision noise |
| `comparator_offset_noise_budget` | input-referred comparator offset plus noise should target <= 0.1530 mV in the tested grid and must stay below 0.1567 mV unless the sample-hold error is reduced further | sample-hold error and comparator uncertainty spend the same decision-voltage budget |
| `acquisition_error` | sampled value before turn-off is within half LSB, 2.197265625e-04 V | a hold result is not useful if the capacitor was never charged correctly |
| `hold_error` | decision-voltage movement after turn-off is below 2.197265625e-04 V for every accepted case | this is the direct 12-bit sample-hold target |
| `differential_mismatch` | if differential, unmatched movement stays below 0.2197 mV | common movement can cancel, but mismatch becomes decision error |
| `claim_boundary` | candidate_post_layout_written=false and accepted_post_layout_written=false | transistor schematic evidence is not extracted post-layout converter evidence |

## Build Order

- copy the known-running transmission-gate hold-mode deck exactly
- keep the passing 0.50x differential dummy case as the candidate baseline
- keep the low/mid/high input sweep as the regression gate
- keep the controlled width-mismatch sweep as a regression gate
- add noise and comparator threshold offset before adding SAR behavior
- add supply-energy measurement after the decision-voltage/noise behavior is bounded
- record timeouts as failed fixtures, not as circuit conclusions
- only update break-even or post-layout pages after a strict accepted payload exists

## Refused Claim

does not prove a new circuit, comparator, SAR conversion, extracted layout, DRC/LVS signoff, or accepted replacement economics
