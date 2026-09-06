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
- cycle DAC values V: `[1.334453, 0.7332241, 0.6207003, 0.8065796]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.080003e-08, 6.99122e-08, 6.949062e-08], [6.83408e-08, 1.8, 6.834319e-08, 6.834346e-08], [6.834304e-08, 6.834383e-08, 1.8, 6.834406e-08], [6.833664e-08, 6.834144e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655375, -0.8643249, -0.8650826, -0.8653705, -0.8688384, -0.8645671, 0.8638663, -0.8660231, -0.8686703, 0.8644858, -0.8665023, -0.8651734, -0.8687278, 0.8659627, 0.8658702, -0.8666201, -0.8674995, 0.8654061, 0.8668643, 0.8658662]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
