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
- cycle DAC values V: `[1.338243, 0.7395914, 0.6210566, 0.8061116]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.090218e-08, 6.992942e-08, 6.951378e-08], [6.83411e-08, 1.8, 6.834321e-08, 6.834347e-08], [6.834303e-08, 6.834382e-08, 1.8, 6.834406e-08], [6.833668e-08, 6.834143e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655348, -0.8643551, -0.8650876, -0.8654063, -0.8688414, -0.8647587, 0.8638411, -0.8659913, -0.8686679, 0.864395, -0.8665293, -0.8652544, -0.8687304, 0.8659797, 0.8658886, -0.866515, -0.8674529, 0.8654125, 0.8668587, 0.8660513]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
