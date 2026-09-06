# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 1, 0, 1]`
- retained logical bits: `[0, 0, 1, 0]`
- final code: `2`
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
- cycle DAC values V: `[0.6711081, 0.2377562, 0.2368333, 0.357588]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.263329, 0.0461903, 0.02149355, 0.01036782], [0.08419925, 0.7301684, 0.01780341, 0.008746792], [0.01396769, 0.005354152, 1.702957, 0.0006572472], [0.0001883161, -0.0001405092, 1.80051, 1.799303]]`
- comparator differences V: `[-0.8670518, 0.8668703, -0.867549, -0.8673107, -0.869061, -0.8647969, 0.8651717, -0.8650546, -0.8684843, 0.8659133, -0.8667558, -0.8651048, -0.8650616, 0.8689284, 0.8651472, -0.8656924, -0.8651975, 0.8689038, 0.8651295, -0.8657232]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
