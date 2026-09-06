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
- cycle DAC values V: `[1.336412, 0.7358073, 0.621416, 0.8058897]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.113698e-08, 7.011491e-08, 6.963076e-08], [6.834118e-08, 1.8, 6.834322e-08, 6.834349e-08], [6.834301e-08, 6.834382e-08, 1.8, 6.834406e-08], [6.83367e-08, 6.834146e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655379, -0.8643363, -0.8650864, -0.8653669, -0.8688464, -0.8646426, 0.863854, -0.866014, -0.8686649, 0.864439, -0.8665434, -0.8652197, -0.8687339, 0.8659817, 0.8658307, -0.8666592, -0.8675577, 0.8654472, 0.8668784, 0.8658236]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
