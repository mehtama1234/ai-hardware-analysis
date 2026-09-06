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
- cycle DAC values V: `[1.339949, 0.7389433, 0.6192426, 0.8038108]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.165977e-08, 7.04005e-08, 6.986337e-08], [6.834202e-08, 1.8, 6.834331e-08, 6.834354e-08], [6.834309e-08, 6.834385e-08, 1.8, 6.834408e-08], [6.833678e-08, 6.834148e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655385, -0.8643451, -0.8650815, -0.865373, -0.8688482, -0.8647134, 0.863904, -0.8659853, -0.8686692, 0.8643889, -0.8665496, -0.8653148, -0.8687466, 0.8659981, 0.8658206, -0.8666813, -0.8676451, 0.865494, 0.8668805, 0.8657906]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
