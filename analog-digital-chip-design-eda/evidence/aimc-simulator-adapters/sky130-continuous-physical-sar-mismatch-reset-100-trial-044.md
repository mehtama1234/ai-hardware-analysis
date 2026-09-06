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
- cycle DAC values V: `[1.3406, 0.7346261, 0.6252404, 0.8047853]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.125249e-08, 7.02268e-08, 6.965249e-08], [6.834128e-08, 1.8, 6.834322e-08, 6.834352e-08], [6.834287e-08, 6.834377e-08, 1.8, 6.834404e-08], [6.833689e-08, 6.834155e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655386, -0.8643306, -0.8650926, -0.8653337, -0.8688487, -0.8646141, 0.8637598, -0.8660002, -0.8686693, 0.86445, -0.8665763, -0.8650678, -0.8687468, 0.8659796, 0.8658017, -0.8666149, -0.8676385, 0.8654439, 0.8668812, 0.865861]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
