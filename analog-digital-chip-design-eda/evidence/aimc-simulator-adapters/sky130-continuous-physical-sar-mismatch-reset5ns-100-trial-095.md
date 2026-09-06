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
- cycle DAC values V: `[1.340181, 0.7336288, 0.6214117, 0.8048387]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.120277e-08, 7.016996e-08, 6.966327e-08], [6.83411e-08, 1.8, 6.834322e-08, 6.834349e-08], [6.834301e-08, 6.834382e-08, 1.8, 6.834406e-08], [6.833675e-08, 6.83415e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655339, -0.8643242, -0.8650829, -0.8653581, -0.8688418, -0.8645773, 0.8638501, -0.8659999, -0.8686763, 0.864473, -0.8665102, -0.8651386, -0.8687467, 0.8659437, 0.8658582, -0.8665947, -0.8676236, 0.8654275, 0.8668666, 0.8658784]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
