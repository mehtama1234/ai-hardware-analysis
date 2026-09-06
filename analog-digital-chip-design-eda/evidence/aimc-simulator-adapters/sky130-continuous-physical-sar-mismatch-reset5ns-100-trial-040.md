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
- cycle DAC values V: `[1.344333, 0.7306953, 0.6170692, 0.8018535]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.094954e-08, 6.999149e-08, 6.956518e-08], [6.834081e-08, 1.8, 6.834322e-08, 6.834347e-08], [6.834316e-08, 6.834388e-08, 1.8, 6.834409e-08], [6.833682e-08, 6.834156e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655372, -0.8643163, -0.8650786, -0.8653674, -0.8688462, -0.8645011, 0.8639537, -0.8659584, -0.8686795, 0.8645089, -0.8664126, -0.8650914, -0.8687538, 0.8659559, 0.8659196, -0.8664637, -0.867673, 0.8653927, 0.8668573, 0.8659833]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
