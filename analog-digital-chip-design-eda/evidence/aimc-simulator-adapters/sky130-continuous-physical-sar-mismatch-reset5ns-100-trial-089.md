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
- cycle DAC values V: `[1.343841, 0.7369281, 0.6179987, 0.8003563]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.145223e-08, 7.027517e-08, 6.975648e-08], [6.83417e-08, 1.8, 6.834329e-08, 6.834353e-08], [6.834313e-08, 6.834386e-08, 1.8, 6.834409e-08], [6.833699e-08, 6.834158e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655366, -0.8643358, -0.8650788, -0.8653534, -0.8688461, -0.8646613, 0.8639324, -0.8659381, -0.86868, 0.8644275, -0.8665054, -0.8652047, -0.8687559, 0.8659846, 0.8658601, -0.8665686, -0.8676904, 0.8654675, 0.8668673, 0.8658958]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
