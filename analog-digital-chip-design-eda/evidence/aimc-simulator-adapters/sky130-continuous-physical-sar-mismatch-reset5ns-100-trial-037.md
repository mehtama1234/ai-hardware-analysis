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
- cycle DAC values V: `[1.341634, 0.7375426, 0.6184362, 0.80107]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.140174e-08, 7.024464e-08, 6.973195e-08], [6.834167e-08, 1.8, 6.834328e-08, 6.834352e-08], [6.834311e-08, 6.834386e-08, 1.8, 6.834408e-08], [6.833695e-08, 6.834156e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655343, -0.8643388, -0.8650795, -0.8653545, -0.8688436, -0.8646758, 0.8639225, -0.865948, -0.8686781, 0.8644216, -0.866522, -0.8652229, -0.8687485, 0.8659861, 0.8658502, -0.866596, -0.8676544, 0.8654697, 0.8668683, 0.8658746]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
