# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[0, 0, 0, 1]`
- retained logical bits: `[1, 1, 1, 0]`
- final code: `14`
- continuous PMOS/NMOS switch width um: `8.0` / `64.0`
- continuous PMOS bank: `8` parallel device(s)
- bottom diode clamp: `True` (area `1.0`)
- dead-time clamp: `False` (width `1.0` um)
- conversion ground precharge: `True` (2.0 ns)
- top dummy capacitor: `0.5p`
- transient step ps: `100.0`
- conversions measured/required: `1`/`5`
- conversion coverage complete: `False`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[0.1414308, -0.05641165, -0.4140346, 1.026727]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.8, -0.2642454, -0.1526073, -0.0750269], [0.9, 0.9104029, 0.02635314, -0.03699323], [6.680915e-07, 2.617001e-07, 0.910403, 1.8], [1.8, 1.8, 1.8, 1.8]]`
- comparator differences V: `[0.8637035, 0.8638859, 0.8635507, -0.8668843]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient; fixed-decision diagnostic when enabled; not closed-loop qualification, PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
