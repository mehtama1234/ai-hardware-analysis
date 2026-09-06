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
- cycle DAC values V: `[1.201347, 0.6780404, 0.5757952, 0.7869856]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.619972, 2.49843e-06, 1.570718e-06, 1.570718e-06], [3.150054e-08, 1.62, 5.13434e-09, 5.13434e-09], [1.659443e-09, 1.792231e-09, 1.62, 1.819695e-09], [1.568353e-09, 1.759359e-09, 1.62, 1.62]]`
- comparator differences V: `[-0.9844601, -0.9813516, -0.9809086, -0.9804472, -0.9845246, -0.973275, 0.9786094, -0.9798868, -0.9843777, 0.9792451, -0.9781704, -0.9767208, -0.9820803, 0.9817537, 0.980634, -0.9767316, -0.9752356, 0.9826015, 0.9821951, 0.9798329]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
