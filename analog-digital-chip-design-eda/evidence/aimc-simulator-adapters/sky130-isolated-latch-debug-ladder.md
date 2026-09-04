# Sky130 Isolated Latch Debug Ladder

- status: `isolated_latch_debug_ladder_ready_after_timeout_failures`
- polarity contract: `converter_positive_input_is_negative_raw_preamp_output_diff`
- best transistor setting: `medium_iso_pair_8ua`
- failed candidate count: `3`
- failed candidate case count: `10`
- measured failed-candidate cases: `0`
- timed-out failed-candidate cases: `9`
- half LSB 12b V: `2.197265625e-04`
- recommended kickback target V: `1.098632813e-04`
- accepted post-layout written: `False`

## First Principle

A timeout is not a circuit measurement. It tells us the combined deck is too hard to judge as one object. The correct response is to split the circuit into smaller objects whose voltages, timing, and state can each be measured.

The polarity contract is already known. The remaining question is where the latch path loses measurability: the preamp, the latch, the clock order, or the coupled kickback. The debug ladder tests those in that order.

## Failed Candidate Pattern

| candidate | measured | timed out | reading |
|---|---:|---:|---|
| `source_follower_input_buffer` | `0` | `4` | combined buffer plus latch fixture did not produce measured signal cases |
| `sampled_internal_decision_capacitor` | `0` | `3` | copy-switch decision-cap fixture was timeout-heavy before kickback could be judged |
| `two_phase_preamp_then_latch` | `0` | `2` | preamp plus delayed latch did not produce measured target-edge cases |

## Debug Ladder

| step | name | question | pass gate | stop if fails |
|---:|---|---|---|---|
| `1` | `preamp_alone_dc_and_transient` | can the preamp or buffer stage settle from the target-edge input without any regenerative latch attached? | both signs produce measurable settled output before latch clock time | fix bias, load, common-mode, or initial condition before reconnecting the latch |
| `2` | `latch_alone_from_measured_preamp_voltages` | can the latch resolve when driven by ideal voltage sources equal to the preamp-alone outputs? | both signs resolve with the polarity contract and full output swing | resize latch or change latch common-mode before adding sampled-node coupling |
| `3` | `clock_timing_ladder` | which copy, preamp, and latch clock order avoids timeout and stale initial conditions? | same topology measures under at least three clock spacings without timeout | separate clock phases further or add explicit precharge/reset nodes |
| `4` | `coupled_kickback_rejoin` | after the pieces work alone, does the coupled circuit keep sampled-node kickback below the line? | kickback <= 2.197265625e-04 V hard line, preferably <= 1.098632813e-04 V | return to isolation mechanism; do not proceed to SAR |
| `5` | `sar_threshold_wrong_code_proxy` | does the measured decision stay correct at the SAR threshold after offset, noise, and kickback budgets are applied? | both signs stay correct under the same budget used by placement and converter acceptance | keep digital fallback; do not create accepted post-layout converter evidence |

## Next Executable Step

write preamp-alone dc/transient fixture before reconnecting the regenerative latch

## Boundary

does not prove a new circuit, SAR bit cycling, noise, offset statistics, extracted layout, DRC/LVS, or accepted post-layout converter evidence
