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
- cycle DAC values V: `[1.344314, 0.7359696, 0.6232817, 0.8071858]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.117892e-08, 7.013738e-08, 6.965188e-08], [6.834106e-08, 1.8, 6.834321e-08, 6.834348e-08], [6.834294e-08, 6.83438e-08, 1.8, 6.834405e-08], [6.833662e-08, 6.834146e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655381, -0.864339, -0.8650908, -0.8654025, -0.8688462, -0.8646762, 0.8637885, -0.8660067, -0.8686742, 0.8644327, -0.8665029, -0.8651537, -0.8687458, 0.8659706, 0.8659, -0.866464, -0.867577, 0.8653942, 0.8668576, 0.8660765]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
