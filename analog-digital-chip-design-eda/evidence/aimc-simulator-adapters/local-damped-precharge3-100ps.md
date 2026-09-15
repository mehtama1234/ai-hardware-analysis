# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[0, 0, 0, 0]`
- retained logical bits: `[1, 1, 1, 1]`
- final code: `15`
- continuous PMOS/NMOS switch width um: `8.0` / `64.0`
- continuous PMOS bank: `8` parallel device(s)
- bottom diode clamp: `False` (area `1.0`)
- dead-time clamp: `False` (width `1.0` um)
- conversion ground precharge: `False` (2.0 ns)
- top dummy capacitor: `0.5p`
- transient step ps: `100.0`
- conversions measured/required: `5`/`5`
- conversion coverage complete: `True`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[0.02985594, -0.7453689, -0.6872649, -0.6597734]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.8, 1.8, 1.8, 1.800004], [0.04743213, 1.805083, 1.803505, 1.802663], [0.01597086, 0.004877686, 1.802511, 1.801866], [0.001568402, 0.003446537, 0.002237637, 1.801339]]`
- comparator differences V: `[-0.8672714, -0.8668145, -0.8659894, -0.864594, 0.8662198, 0.8655656, 0.8655443, 0.8655572, -0.8623232, -0.8653756, -0.8744218, -0.8860851, 0.867268, 0.8670842, 0.8673876, 0.8677367, 0.8636514, 0.8683339, 0.8688913, 0.8689138]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient; fixed-decision diagnostic when enabled; not closed-loop qualification, PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
