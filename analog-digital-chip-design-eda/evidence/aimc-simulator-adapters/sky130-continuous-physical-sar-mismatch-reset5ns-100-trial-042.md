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
- cycle DAC values V: `[0.4456211, 0.8107932, 0.6892523, 0.6333548]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.082489e-08, 6.988949e-08, 6.947948e-08], [1.8, 1.8, 6.354647e-08, 6.480099e-08], [1.8, 6.791675e-08, 1.8, 6.81472e-08], [1.8, 6.823528e-08, 6.82762e-08, 1.8]]`
- comparator differences V: `[-0.8635222, 0.8611216, 0.862958, 0.8637002, 0.8649928, -0.8659441, -0.8633082, 0.8631705, 0.8646882, -0.8646649, 0.8649098, -0.8653928, 0.8649703, 0.865982, -0.8666908, -0.8647697, 0.8644131, 0.8668177, 0.8650669, -0.8681488]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
