# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_nominal_map_passed`
- expected code: `2`
- comparator clear flags: `[1, 1, 0, 1]`
- retained logical bits: `[0, 0, 1, 0]`
- final code: `2`
- continuous PMOS/NMOS switch width um: `8.0` / `64.0`
- continuous PMOS bank: `8` parallel device(s)
- bottom diode clamp: `False` (area `1.0`)
- dead-time clamp: `False` (width `1.0` um)
- conversion ground precharge: `False` (2.0 ns)
- top dummy capacitor: `0.5p`
- transient step ps: `20.0`
- conversions measured/required: `5`/`5`
- conversion coverage complete: `True`
- all conversions correct: `True`
- measured: `True`
- cycle DAC values V: `[1.343203, 0.7349472, 0.6141027, 0.7976977]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.082631e-08, 6.987023e-08, 6.948092e-08], [6.834097e-08, 1.8, 6.834323e-08, 6.834348e-08], [6.834326e-08, 6.834392e-08, 1.8, 6.834411e-08], [6.833707e-08, 6.834162e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655392, -0.8643338, -0.8650748, -0.865359, -0.868841, -0.8646223, 0.8640116, -0.8659003, -0.8686715, 0.8644534, -0.8664347, -0.865167, -0.8687492, 0.8659754, 0.8659132, -0.8664598, -0.8676462, 0.8654289, 0.8668684, 0.8659912]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
