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
- cycle DAC values V: `[1.347412, 0.7349801, 0.621125, 0.8066654]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.132217e-08, 7.021364e-08, 6.97379e-08], [6.83411e-08, 1.8, 6.834323e-08, 6.834348e-08], [6.834301e-08, 6.834383e-08, 1.8, 6.834406e-08], [6.833658e-08, 6.834146e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655398, -0.8643343, -0.8650868, -0.8654169, -0.8688487, -0.8646533, 0.8638419, -0.8659989, -0.8686776, 0.8644412, -0.8664551, -0.8651787, -0.868758, 0.8659688, 0.8659305, -0.86643, -0.8676316, 0.8653915, 0.8668533, 0.8660938]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
