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
- cycle DAC values V: `[1.290093, 0.6987682, 0.586496, 0.801412]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 1.037442e-06, 1.037431e-06, 1.037429e-06], [1.037409e-06, 1.8, 1.037413e-06, 1.037413e-06], [1.037414e-06, 1.037414e-06, 1.8, 1.037414e-06], [1.037406e-06, 1.037411e-06, 1.8, 1.8]]`
- comparator differences V: `[-0.7324151, -0.7307926, -0.7308002, -0.7311388, -0.734878, -0.731498, 0.7305288, -0.732627, -0.735529, 0.7313983, -0.7329698, -0.7325874, -0.7357194, 0.7321557, 0.7330692, -0.7342314, -0.7347722, 0.731581, 0.7333934, 0.7334556]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
