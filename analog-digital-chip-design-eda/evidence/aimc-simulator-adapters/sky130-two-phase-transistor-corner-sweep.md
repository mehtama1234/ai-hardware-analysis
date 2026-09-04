# Sky130 Two-Phase Transistor Corner Sweep

- status: `transistor_corner_sweep_measured_not_noise_or_mismatch_proof`
- cases: `9`
- measured cases: `9`
- timed-out cases: `0`
- nonzero polarity passes: `6` of `6`
- zero-input cases measured: `3`
- nonzero preamp margin passes: `4` of `6`
- preamp margin target V: `5.000000000e-04`
- minimum nonzero preamp magnitude V: `1.550000000e-05`

## First-Principles Reading

The nominal zero crossing is not enough. Process, supply, and temperature change transistor current, gain, headroom, and the sampled operating point. This sweep checks sign, convergence, and useful preamp amplitude at three deliberately separated corners.

The slow, cold, low-supply corner preserves polarity but collapses amplitude. A sign-only pass would therefore allow a corner that cannot reliably drive the latch.

## Next Gate

Expand to the declared corner matrix, redesign or digitally derate the low-supply corner, add device mismatch and small-signal noise, then carry the measured input-referred uncertainty into the 12-bit transition test.

## Refused Claim

does not prove random noise, mismatch distributions, full PVT coverage, SAR bit cycling, extracted layout, or accepted converter evidence
