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
- all conversions correct: `True`
- measured: `True`
- cycle DAC values V: `[1.371635, 0.7461419, 0.6265173, 0.7545193]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 6.990015e-08, 6.931624e-08, 6.880147e-08], [6.83409e-08, 1.8, 6.834312e-08, 6.83437e-08], [6.834278e-08, 6.834373e-08, 1.8, 6.834411e-08], [6.833808e-08, 6.834197e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655556, -0.8643993, -0.8651024, -0.8649027, -0.8688692, -0.8649036, 0.8636915, -0.8652098, -0.8687, 0.8643315, -0.8667185, -0.8636528, -0.868795, 0.8659876, 0.8657683, -0.8651508, -0.8678375, 0.8654123, 0.8668709, 0.8665452]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
