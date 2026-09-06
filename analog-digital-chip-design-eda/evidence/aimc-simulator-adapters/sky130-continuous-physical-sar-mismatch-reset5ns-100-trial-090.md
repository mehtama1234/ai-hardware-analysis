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
- cycle DAC values V: `[1.341774, 0.7306227, 0.6175752, 0.8037403]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.089297e-08, 6.996044e-08, 6.95481e-08], [6.834075e-08, 1.8, 6.834321e-08, 6.834346e-08], [6.834314e-08, 6.834388e-08, 1.8, 6.834409e-08], [6.833671e-08, 6.834151e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655356, -0.8643143, -0.8651301, -0.865377, -0.8688438, -0.8644989, 0.8639427, -0.8659841, -0.8686773, 0.8645111, -0.8664201, -0.8651233, -0.8687486, 0.8659547, 0.8659159, -0.8665044, -0.8676311, 0.8653893, 0.8668576, 0.865955]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
