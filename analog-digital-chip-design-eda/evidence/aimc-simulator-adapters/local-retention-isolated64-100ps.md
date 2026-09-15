# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 0, 0, 1]`
- retained logical bits: `[0, 1, 1, 0]`
- final code: `6`
- continuous PMOS/NMOS switch width um: `8.0` / `64.0`
- continuous PMOS bank: `8` parallel device(s)
- bottom diode clamp: `True` (area `1.0`)
- dead-time clamp: `False` (width `1.0` um)
- conversion ground precharge: `False` (2.0 ns)
- top dummy capacitor: `0.5p`
- transient step ps: `100.0`
- conversions measured/required: `1`/`5`
- conversion coverage complete: `False`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[0.3577437, 0.129962, -0.2040588, 1.237201]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.8, -0.2356499, -0.1794535, -0.1448681], [0.9000003, 0.8834521, 0.01246021, -0.1969845], [5.169781e-07, -1.009048e-07, 0.9052836, 1.8], [1.8, 1.8, 1.8, 1.8]]`
- comparator differences V: `[-0.8626358, 0.8632545, 0.8637292, -0.8687788]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient; fixed-decision diagnostic when enabled; not closed-loop qualification, PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
