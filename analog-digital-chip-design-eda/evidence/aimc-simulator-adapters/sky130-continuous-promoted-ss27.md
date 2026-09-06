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
- cycle DAC values V: `[1.362325, 0.7598378, 0.6421001, 0.8253577]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.799997, 2.936793e-07, 1.858063e-07, 1.360872e-07], [3.290079e-09, 1.8, 1.594056e-09, 1.526439e-09], [1.351405e-09, 1.352199e-09, 1.8, 1.352463e-09], [1.344548e-09, 1.349665e-09, 1.8, 1.8]]`
- comparator differences V: `[-1.013128, -1.012419, -1.013439, -1.013643, -1.016334, -1.012537, 1.009604, -1.014048, -1.016235, 1.011264, -1.014396, -1.012772, -1.015934, 1.014247, 1.012768, -1.013668, -1.0145, 1.013728, 1.014746, 1.012445]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
