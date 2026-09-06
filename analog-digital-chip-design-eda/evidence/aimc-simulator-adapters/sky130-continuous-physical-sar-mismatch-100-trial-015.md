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
- cycle DAC values V: `[1.338392, 0.7433719, 0.6203666, 0.8052757]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.123994e-08, 7.010931e-08, 6.965441e-08], [6.834182e-08, 1.8, 6.834328e-08, 6.834351e-08], [6.834305e-08, 6.834383e-08, 1.8, 6.834407e-08], [6.833673e-08, 6.834142e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655338, -0.864369, -0.8650854, -0.8654082, -0.8688414, -0.8648402, 0.8638558, -0.86598, -0.8686687, 0.8643353, -0.8665695, -0.8653526, -0.8687337, 0.8659973, 0.8658562, -0.8665843, -0.8674807, 0.8654628, 0.8668643, 0.8659951]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
