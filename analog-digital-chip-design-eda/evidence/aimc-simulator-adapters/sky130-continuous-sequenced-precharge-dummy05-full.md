# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[0, 1, 1, 1]`
- retained logical bits: `[1, 0, 0, 0]`
- final code: `8`
- continuous PMOS/NMOS switch width um: `8.0` / `8.0`
- continuous PMOS bank: `1` parallel device(s)
- bottom diode clamp: `False` (area `1.0`)
- dead-time clamp: `False` (width `1.0` um)
- conversion ground precharge: `False` (2.0 ns)
- top dummy capacitor: `0.5p`
- transient step ps: `20.0`
- conversions measured/required: `5`/`5`
- conversion coverage complete: `True`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[0.6130728, 1.40033, 1.118798, 1.028332]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.153437, 0.04533521, 0.02146017, 0.01044282], [2.00764, 1.417074, 0.006320998, 0.002881735], [1.773272, 0.02938965, 1.58948, 0.004940607], [1.783935, 0.003477875, 0.001235742, 1.787878]]`
- comparator differences V: `[-0.8694377, -0.8652196, 0.8657504, 0.8662936, 0.8652144, -0.8716887, -0.8712179, -0.8702588, -0.8659401, 0.8689888, 0.8652696, -0.8652369, 0.8659571, -0.8699518, -0.8689981, -0.8678693, 0.8661304, -0.8692311, -0.8683235, -0.8674265]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
