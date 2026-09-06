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
- cycle DAC values V: `[1.346762, 0.7363175, 0.621707, 0.8050658]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.122997e-08, 7.015359e-08, 6.966992e-08], [6.834115e-08, 1.8, 6.834323e-08, 6.834349e-08], [6.834299e-08, 6.834382e-08, 1.8, 6.834406e-08], [6.833672e-08, 6.83415e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655391, -0.8643401, -0.8650881, -0.8653996, -0.8688482, -0.8646848, 0.863827, -0.8659775, -0.8686768, 0.8644269, -0.8664847, -0.8651512, -0.8687547, 0.8659727, 0.8659131, -0.8664231, -0.8676143, 0.8653999, 0.8668561, 0.8661003]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
