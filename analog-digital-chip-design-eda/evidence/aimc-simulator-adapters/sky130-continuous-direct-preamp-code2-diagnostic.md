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
- transient step ps: `20.0`
- conversions measured/required: `1`/`5`
- conversion coverage complete: `False`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[1.462856, 1.926333, 2.153006, 2.229875]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.800001, 1.773406e-07, 1.218709e-07, 9.488831e-08], [1.799999, 1.799998, -9.862493e-08, -1.463073e-08], [1.799644, 1.799822, 1.799911, -9.582897e-06], [1.798197, 1.799115, 1.799561, 1.799782]]`
- comparator differences V: `[0.8798169, 0.9188324, 0.9717115, 0.9937944]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
