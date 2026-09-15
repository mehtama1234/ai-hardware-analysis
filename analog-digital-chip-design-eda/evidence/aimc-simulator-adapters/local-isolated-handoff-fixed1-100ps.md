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
- cycle DAC values V: `[0.3856177, -0.1376045, -0.4659547, -0.3694302]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[0.6037901, 1.823234, 1.815505, 1.811625], [0.0228407, 0.7174473, 1.82233, 1.805026], [0.0001844065, 6.869711e-05, 1.798869, 3.638465e-05], [0.01273668, 0.00469889, 1.803767, 0.8200045]]`
- comparator differences V: `[-0.8632216, 0.864265, 0.8637924, 0.8640081]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient; fixed-decision diagnostic when enabled; not closed-loop qualification, PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
