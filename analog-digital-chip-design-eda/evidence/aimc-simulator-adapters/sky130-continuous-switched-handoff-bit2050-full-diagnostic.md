# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 1, 0, 0]`
- retained logical bits: `[0, 0, 1, 1]`
- final code: `3`
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
- cycle DAC values V: `[1.37303, 0.8714089, 0.5021916, 0.6338341]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.14116e-08, 6.897817e-08, 6.897817e-08], [6.88712e-08, 1.8, 6.837777e-08, 6.837777e-08], [6.834731e-08, 6.83458e-08, 1.8, 6.834468e-08], [6.834243e-08, 6.834337e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655571, -0.8650959, -0.8647705, -0.8649526, -0.8688706, -0.8666949, 0.8648392, 0.8632605, -0.8687045, -0.8647792, 0.8648524, 0.8654969, -0.8688008, 0.8661596, 0.8657588, -0.8652172, -0.8678639, 0.866487, 0.8668864, 0.8665304]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
