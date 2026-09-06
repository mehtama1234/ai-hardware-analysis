# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 0, 1, 1]`
- retained logical bits: `[0, 1, 0, 0]`
- final code: `4`
- continuous PMOS/NMOS switch width um: `8.0` / `8.0`
- continuous PMOS bank: `1` parallel device(s)
- dead-time clamp: `False`
- conversion ground precharge: `True` (2.0 ns)
- top dummy capacitor: `0.5p`
- transient step ps: `20.0`
- conversions measured/required: `5`/`5`
- conversion coverage complete: `True`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[0.8585947, 0.4712546, 0.9400211, 0.8164319]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.168374, 0.0504011, 0.02363553, 0.01144636], [0.08422615, 0.7289424, 0.01780697, 0.008748963], [0.003670889, 1.830775, 1.751816, -0.0001489892], [0.0008880578, 1.79649, 3.053461e-05, 1.79931]]`
- comparator differences V: `[-0.873556, -0.8709063, -0.8688929, -0.8661348, -0.8663248, 0.866506, -0.8663982, -0.8666107, -0.8663802, 0.8678416, -0.8651498, 0.8651632, 0.8653845, -0.8715397, -0.869945, -0.868385, 0.8650479, -0.869753, -0.8684225, -0.8673826]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
