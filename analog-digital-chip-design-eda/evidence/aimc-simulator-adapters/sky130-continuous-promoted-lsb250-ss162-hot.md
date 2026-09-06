# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 0, 1, 1]`
- retained logical bits: `[0, 1, 0, 0]`
- final code: `4`
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
- cycle DAC values V: `[1.17953, 0.6728865, 0.8769504, 0.9276581]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.619958, 3.436762e-06, 2.164907e-06, 2.782713e-06], [3.107229e-08, 1.62, 5.099451e-09, 6.104304e-09], [1.052774e-09, 1.62, 1.62, 1.69784e-09], [-1.375512e-10, 1.62, 1.582417e-09, 1.62]]`
- comparator differences V: `[-0.9844347, -0.9812905, -0.9808664, -0.9810172, -0.9844876, 0.9734894, -0.9814958, -0.9823136, -0.9842139, 0.9793075, -0.9776494, -0.9789375, -0.981767, 0.981762, 0.9807163, -0.9790293, 0.9754751, -0.9825432, -0.982003, -0.9823729]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
