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
- cycle DAC values V: `[1.342169, 0.737912, 0.619424, 0.8012114]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.145011e-08, 7.027955e-08, 6.974619e-08], [6.834169e-08, 1.8, 6.834328e-08, 6.834353e-08], [6.834308e-08, 6.834384e-08, 1.8, 6.834408e-08], [6.833698e-08, 6.834157e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655388, -0.8643416, -0.8650823, -0.8653508, -0.8688406, -0.86469, 0.8638999, -0.8659501, -0.8686714, 0.8644052, -0.8665402, -0.8652168, -0.8687501, 0.8659928, 0.8658294, -0.8666056, -0.8676656, 0.8654784, 0.8668793, 0.8658657]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
