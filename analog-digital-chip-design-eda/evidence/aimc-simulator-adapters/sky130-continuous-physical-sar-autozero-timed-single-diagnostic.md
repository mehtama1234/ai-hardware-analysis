# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 1, 1, 1]`
- retained logical bits: `[0, 0, 0, 0]`
- final code: `0`
- continuous PMOS/NMOS switch width um: `8.0` / `8.0`
- continuous PMOS bank: `1` parallel device(s)
- bottom diode clamp: `False` (area `1.0`)
- dead-time clamp: `False` (width `1.0` um)
- conversion ground precharge: `False` (2.0 ns)
- top dummy capacitor: `0.5p`
- transient step ps: `20.0`
- conversions measured/required: `1`/`5`
- conversion coverage complete: `False`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[1.230837, 0.8260708, 0.8213899, 0.7107208]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.202705, 0.04898737, 0.02291296, 0.01108077], [0.08419337, 0.7303908, 0.01780183, 0.008745963], [0.01391636, 0.005320721, 1.703419, 0.0006530036], [0.0002753806, -5.897201e-05, -3.216309e-05, 1.799189]]`
- comparator differences V: `[-1.686214, -1.666906, -1.656022, -1.649403]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
