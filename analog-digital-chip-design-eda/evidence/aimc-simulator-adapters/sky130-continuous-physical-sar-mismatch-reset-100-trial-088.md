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
- cycle DAC values V: `[1.347637, 0.7303922, 0.6229816, 0.8066242]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.173417e-08, 7.054238e-08, 6.993712e-08], [6.834122e-08, 1.8, 6.834325e-08, 6.834351e-08], [6.834294e-08, 6.834381e-08, 1.8, 6.834405e-08], [6.833661e-08, 6.834151e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655477, -0.8643125, -0.865088, -0.8653693, -0.8688449, -0.8645073, 0.8638188, -0.8660241, -0.8686769, 0.8644906, -0.8664783, -0.8650892, -0.8687662, 0.865969, 0.8658669, -0.8665677, -0.867759, 0.8654241, 0.8668754, 0.8658876]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
