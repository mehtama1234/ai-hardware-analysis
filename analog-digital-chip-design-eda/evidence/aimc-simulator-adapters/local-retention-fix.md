# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[0, 0, 1, 0]`
- retained logical bits: `[1, 1, 0, 1]`
- final code: `13`
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
- cycle DAC values V: `[0.0910063, 0.1231929, 0.7598593, 0.3432268]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.800003, 1.800001, 2.37268e-07, -0.3532304], [1.81432, 1.800001, 2.414795e-07, -0.3217127], [2.325925, 2.263518, 1.799011, -0.000157513], [1.8, 1.842299, 1.462325, 6.828533e-08]]`
- comparator differences V: `[0.868725, -0.8680016, -0.8687856, 0.8674671, 0.8690762, 0.8690851, -0.8650706, 0.8681741, 0.868919, 0.8691327, 0.8677265, 0.8690327, 0.8702128, 0.8704536, 0.8707108, 0.8709429, 0.8714092, 0.8714922, 0.871539, 0.8715684]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient; fixed-decision diagnostic when enabled; not closed-loop qualification, PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
