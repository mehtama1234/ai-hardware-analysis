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
- cycle DAC values V: `[1.251121, 0.6604078, 0.5479678, 0.7630823]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 4.473645e-06, 4.47358e-06, 4.473568e-06], [4.473478e-06, 1.8, 4.47348e-06, 4.47348e-06], [4.473484e-06, 4.473482e-06, 1.8, 4.473482e-06], [4.473476e-06, 4.473479e-06, 1.8, 1.8]]`
- comparator differences V: `[-1.057235, -1.05721, -1.057075, -1.056834, -1.058619, -1.054814, 1.053697, -1.05598, -1.058428, 1.05574, -1.054829, -1.052378, -1.057844, 1.057091, 1.056289, -1.05426, -1.055157, 1.057597, 1.057269, 1.055355]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
