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
- cycle DAC values V: `[1.34284, 0.7379107, 0.6167612, 0.800679]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.153448e-08, 7.030826e-08, 6.980317e-08], [6.834183e-08, 1.8, 6.83433e-08, 6.834353e-08], [6.834317e-08, 6.834388e-08, 1.8, 6.834409e-08], [6.833692e-08, 6.834155e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655358, -0.8643394, -0.8650727, -0.8653661, -0.8688447, -0.864684, 0.8639588, -0.8659422, -0.8686793, 0.8644142, -0.8665016, -0.8652684, -0.8687532, 0.8659886, 0.8658628, -0.8665953, -0.8676787, 0.8654785, 0.8668672, 0.8658718]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
