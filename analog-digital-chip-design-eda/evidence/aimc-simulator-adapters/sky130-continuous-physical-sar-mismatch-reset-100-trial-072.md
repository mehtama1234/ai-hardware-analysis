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
- cycle DAC values V: `[1.338378, 0.7397176, 0.6191398, 0.8050215]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.171441e-08, 7.042788e-08, 6.989736e-08], [6.834213e-08, 1.8, 6.834332e-08, 6.834354e-08], [6.834309e-08, 6.834385e-08, 1.8, 6.834407e-08], [6.83367e-08, 6.834144e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655381, -0.864348, -0.8650811, -0.8653834, -0.8688481, -0.8647307, 0.8639061, -0.8660016, -0.8686675, 0.8643777, -0.8665584, -0.8653648, -0.868743, 0.8660013, 0.8658138, -0.8667213, -0.8676258, 0.8655029, 0.8668812, 0.8657483]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
