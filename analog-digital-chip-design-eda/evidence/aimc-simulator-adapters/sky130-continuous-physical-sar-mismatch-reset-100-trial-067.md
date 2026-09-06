# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[0, 1, 1, 0]`
- retained logical bits: `[1, 0, 0, 1]`
- final code: `9`
- continuous PMOS/NMOS switch width um: `8.0` / `64.0`
- continuous PMOS bank: `8` parallel device(s)
- bottom diode clamp: `False` (area `1.0`)
- dead-time clamp: `False` (width `1.0` um)
- conversion ground precharge: `False` (2.0 ns)
- top dummy capacitor: `0.5p`
- transient step ps: `20.0`
- conversions measured/required: `5`/`5`
- conversion coverage complete: `True`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[0.4433159, 0.8100214, 0.6860023, 0.6316898]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.069058e-08, 6.979231e-08, 6.941656e-08], [1.8, 1.8, 6.368978e-08, 6.487984e-08], [1.8, 6.795751e-08, 1.8, 6.816624e-08], [1.8, 6.823798e-08, 6.82785e-08, 1.8]]`
- comparator differences V: `[-0.8635024, 0.8611253, 0.862958, 0.8636991, 0.8649892, -0.8659387, -0.8631912, 0.8632232, 0.8646754, -0.8646388, 0.8649361, -0.8653288, 0.8647573, 0.8659897, -0.866656, -0.8647678, 0.8644067, 0.8668231, 0.8651125, -0.8681357]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
