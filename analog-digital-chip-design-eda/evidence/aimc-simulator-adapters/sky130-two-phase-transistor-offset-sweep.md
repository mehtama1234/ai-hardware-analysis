# Sky130 Two-Phase Transistor Offset Sweep

- status: `transistor_threshold_sweep_measured_not_noise_or_sar_proof`
- cases: `5`
- measured cases: `5`
- timed-out cases: `0`
- estimated preamp zero crossing mV: `0.0`
- polarity-contract sign passes: `4` of `4`
- preamp sign passes: `4` of `4`

## First-Principles Reading

A fixed offset shifts the input value at which the differential preamp changes sign. Sweeping the signed input and locating that zero crossing turns offset from an assumed number into a circuit-derived threshold. The sweep stops before latch regeneration so the balanced operating point can be measured directly.

This is deterministic offset characterization. It does not include random device mismatch or thermal noise, so it cannot yet support a production 12-bit converter claim.

## Next Gate

Repeat the sweep over process, voltage, and temperature corners, add a transistor noise analysis around the same operating point, and combine the measured threshold distribution with the 12-bit SAR transition test.

## Refused Claim

does not measure random noise, mismatch distributions, process corners, SAR bit cycling, extracted layout, or accepted converter evidence
