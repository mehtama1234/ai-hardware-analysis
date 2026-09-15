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
- cycle DAC values V: `[1.28356, 0.6921033, 0.5783453, 0.7937107]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 1.037438e-06, 1.037429e-06, 1.037427e-06], [1.03741e-06, 1.8, 1.037413e-06, 1.037413e-06], [1.037414e-06, 1.037414e-06, 1.8, 1.037414e-06], [1.037406e-06, 1.037411e-06, 1.8, 1.8]]`
- comparator differences V: `[-0.732441, -0.7308138, -0.7312917, -0.7318885, -0.7357908, -0.7314017, 0.7311599, -0.7325786, -0.7355104, 0.7314039, -0.732829, -0.7324306, -0.7356117, 0.7320798, 0.7330769, -0.7340346, -0.7345337, 0.7314285, 0.7333169, 0.7335074]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
