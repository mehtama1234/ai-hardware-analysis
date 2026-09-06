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
- cycle DAC values V: `[1.344258, 0.7353283, 0.6176615, 0.8010213]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.140933e-08, 7.025577e-08, 6.975211e-08], [6.834148e-08, 1.8, 6.834327e-08, 6.834352e-08], [6.834314e-08, 6.834387e-08, 1.8, 6.834409e-08], [6.833691e-08, 6.834157e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655366, -0.8643299, -0.8650784, -0.8653604, -0.8688465, -0.8646197, 0.8639401, -0.8659471, -0.8686801, 0.8644485, -0.8664786, -0.8651885, -0.8687567, 0.8659781, 0.8658783, -0.8665484, -0.8676932, 0.8654506, 0.8668649, 0.8659128]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
