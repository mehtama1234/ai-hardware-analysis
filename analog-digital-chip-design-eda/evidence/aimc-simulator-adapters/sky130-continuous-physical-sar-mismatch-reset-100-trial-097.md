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
- cycle DAC values V: `[1.337569, 0.7344127, 0.6239259, 0.8084002]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.130635e-08, 7.025125e-08, 6.971874e-08], [6.834123e-08, 1.8, 6.834322e-08, 6.834349e-08], [6.834292e-08, 6.834379e-08, 1.8, 6.834404e-08], [6.833658e-08, 6.834143e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655381, -0.8643298, -0.8650902, -0.8653693, -0.8688477, -0.8646091, 0.8637937, -0.866048, -0.8686664, 0.8644518, -0.8665543, -0.865195, -0.8687391, 0.8659793, 0.8658183, -0.8666849, -0.8675898, 0.8654441, 0.8668798, 0.8657922]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
