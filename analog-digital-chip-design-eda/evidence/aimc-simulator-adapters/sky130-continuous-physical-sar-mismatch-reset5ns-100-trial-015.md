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
- cycle DAC values V: `[1.335852, 0.741157, 0.6165663, 0.8010367]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.124198e-08, 7.011056e-08, 6.965534e-08], [6.834192e-08, 1.8, 6.83433e-08, 6.834353e-08], [6.834319e-08, 6.834388e-08, 1.8, 6.834409e-08], [6.833693e-08, 6.83415e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655364, -0.8643563, -0.8651777, -0.8653666, -0.8688369, -0.8647574, 0.8639614, -0.8659471, -0.8686727, 0.864378, -0.8665515, -0.8653431, -0.868734, 0.8660023, 0.8658345, -0.8666668, -0.8675438, 0.8654942, 0.8668699, 0.8658162]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
