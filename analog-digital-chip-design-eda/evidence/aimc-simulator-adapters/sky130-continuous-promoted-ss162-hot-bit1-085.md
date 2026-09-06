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
- cycle DAC values V: `[1.230597, 0.7287469, 0.5783577, 0.6895635]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.619982, 1.937394e-06, 1.045512e-06, 4.943697e-07], [1.753364e-07, 1.619999, 2.353249e-08, 1.186825e-08], [1.650276e-09, 1.777116e-09, 1.62, 1.845978e-09], [1.612959e-09, 1.764064e-09, 1.62, 1.62]]`
- comparator differences V: `[-0.9844933, -0.9818332, -0.9809678, -0.9787396, -0.9845749, -0.9773512, 0.9785322, -0.9756793, -0.9845024, 0.978143, -0.9799911, 0.9750898, -0.9824354, 0.9815942, 0.9797887, 0.9761481, -0.9766401, 0.9827433, 0.9818909, 0.9807894]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
