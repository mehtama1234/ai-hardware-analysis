# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
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
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[1.268337, 0.8296417, 0.6138506, 0.8360516]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 8.960628e-08, 7.783385e-08, 7.783385e-08], [6.897316e-08, 1.8, 6.843222e-08, 6.843222e-08], [6.834338e-08, 6.834384e-08, 1.8, 6.834407e-08], [6.833607e-08, 6.834018e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.865488, -0.864769, -0.865065, -0.8656965, -0.8687815, -0.8661997, 0.863972, -0.8663682, -0.8686029, -0.863785, 0.8653506, 0.8637833, -0.8684837, 0.8661911, 0.8645304, -0.8683317, -0.8666562, 0.8664362, 0.8667614, -0.8666898]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
