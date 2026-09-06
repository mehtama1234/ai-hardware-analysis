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
- cycle DAC values V: `[1.34917, 0.7357856, 0.6200852, 0.8000831]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.192739e-08, 7.059718e-08, 6.99619e-08], [6.834203e-08, 1.8, 6.834332e-08, 6.834357e-08], [6.834305e-08, 6.834384e-08, 1.8, 6.834408e-08], [6.83366e-08, 6.834129e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655417, -0.8643294, -0.8650793, -0.8653429, -0.8688509, -0.8646302, 0.8638815, -0.8659349, -0.868684, 0.8644342, -0.866511, -0.8651312, -0.8687704, 0.865985, 0.8658498, -0.8665413, -0.8677795, 0.8654728, 0.8668692, 0.8659092]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
