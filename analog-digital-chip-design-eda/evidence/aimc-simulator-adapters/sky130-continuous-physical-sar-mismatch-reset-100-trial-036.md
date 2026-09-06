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
- cycle DAC values V: `[1.340356, 0.7376725, 0.6197861, 0.8014972]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.130097e-08, 7.019247e-08, 6.967699e-08], [6.834152e-08, 1.8, 6.834326e-08, 6.834352e-08], [6.834306e-08, 6.834384e-08, 1.8, 6.834408e-08], [6.833698e-08, 6.834156e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655378, -0.8643422, -0.8650834, -0.8653504, -0.8688486, -0.8646848, 0.8638915, -0.8659542, -0.8686693, 0.8644121, -0.866545, -0.8652015, -0.8687455, 0.8659899, 0.8658284, -0.866606, -0.8676302, 0.8654692, 0.8668791, 0.8658699]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
