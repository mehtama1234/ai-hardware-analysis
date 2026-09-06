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
- cycle DAC values V: `[1.33712, 0.7364312, 0.6221466, 0.8057853]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.135139e-08, 7.025357e-08, 6.972198e-08], [6.834147e-08, 1.8, 6.834325e-08, 6.834351e-08], [6.834299e-08, 6.834381e-08, 1.8, 6.834406e-08], [6.833672e-08, 6.834146e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655339, -0.8643342, -0.8650837, -0.8653598, -0.8688384, -0.8646462, 0.8638317, -0.8660128, -0.8686734, 0.8644379, -0.8665592, -0.8652166, -0.8687396, 0.865981, 0.8658241, -0.8666723, -0.8675835, 0.8654564, 0.8668708, 0.8658065]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
