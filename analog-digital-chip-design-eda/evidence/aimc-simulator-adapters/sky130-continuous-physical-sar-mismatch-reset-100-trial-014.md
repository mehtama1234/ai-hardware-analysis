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
- cycle DAC values V: `[1.33462, 0.733413, 0.6209975, 0.8069046]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.080863e-08, 6.99177e-08, 6.949464e-08], [6.834077e-08, 1.8, 6.834318e-08, 6.834345e-08], [6.834303e-08, 6.834383e-08, 1.8, 6.834406e-08], [6.833663e-08, 6.834144e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655366, -0.8643294, -0.8650864, -0.8653736, -0.8688442, -0.8645855, 0.863864, -0.8660274, -0.8686627, 0.8644741, -0.8665117, -0.8651838, -0.8687259, 0.865969, 0.8658597, -0.8666293, -0.8675095, 0.8654127, 0.8668745, 0.865858]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
