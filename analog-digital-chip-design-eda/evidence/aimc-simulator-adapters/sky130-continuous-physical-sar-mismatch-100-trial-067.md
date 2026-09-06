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
- cycle DAC values V: `[1.339093, 0.7408689, 0.6211891, 0.8064001]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.113589e-08, 7.00666e-08, 6.961948e-08], [6.834144e-08, 1.8, 6.834324e-08, 6.834349e-08], [6.834302e-08, 6.834382e-08, 1.8, 6.834406e-08], [6.833667e-08, 6.834142e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655351, -0.864359, -0.8650871, -0.86541, -0.8688421, -0.8647867, 0.8638375, -0.8659954, -0.868669, 0.8643721, -0.866546, -0.8652995, -0.8687351, 0.8659874, 0.8658734, -0.8665535, -0.8674862, 0.865436, 0.8668617, 0.8660191]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
