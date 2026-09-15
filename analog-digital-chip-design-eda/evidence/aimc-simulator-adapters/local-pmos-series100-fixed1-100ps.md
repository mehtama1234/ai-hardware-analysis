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
- conversions measured/required: `1`/`5`
- conversion coverage complete: `False`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[0.3768765, -0.1404235, -0.4635482, -0.3679524]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[0.5863025, 1.822662, 1.815125, 1.811341], [0.02230224, 0.6979667, 1.822122, 1.804914], [0.0001822404, 6.775254e-05, 1.798707, 3.586753e-05], [0.01245566, 0.00460086, 1.803689, 0.798203]]`
- comparator differences V: `[-0.849652, 0.8523067, 0.8593328, 0.8621719]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient; fixed-decision diagnostic when enabled; not closed-loop qualification, PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
