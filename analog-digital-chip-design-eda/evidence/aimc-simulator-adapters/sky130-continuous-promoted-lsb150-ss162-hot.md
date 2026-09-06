# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
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
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[1.224965, 0.683754, 0.578039, 0.7423475]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.619982, 1.710213e-06, 1.072926e-06, 7.819304e-07], [3.185074e-08, 1.62, 5.160684e-09, 4.227732e-09], [1.651267e-09, 1.789162e-09, 1.62, 1.831911e-09], [1.575558e-09, 1.762645e-09, 1.62, 1.62]]`
- comparator differences V: `[-0.9844869, -0.9814222, -0.9809571, -0.9797708, -0.9845616, -0.9737356, 0.9785496, -0.9786715, -0.9844788, 0.9791925, -0.9786021, 0.9743372, -0.982377, 0.981746, 0.9805404, 0.9755042, -0.97639, 0.9825909, 0.9821679, 0.9806467]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
