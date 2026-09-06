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
- cycle DAC values V: `[1.338916, 0.7370281, 0.6208854, 0.8025375]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.112904e-08, 7.00983e-08, 6.960057e-08], [6.834134e-08, 1.8, 6.834324e-08, 6.834351e-08], [6.834303e-08, 6.834383e-08, 1.8, 6.834407e-08], [6.833693e-08, 6.834154e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655384, -0.8643404, -0.8651724, -0.8653493, -0.8688488, -0.8646705, 0.8638661, -0.8659686, -0.8686675, 0.8644227, -0.8665529, -0.8651795, -0.8687409, 0.8659865, 0.8658237, -0.8666143, -0.8675946, 0.8654594, 0.8668784, 0.865865]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
