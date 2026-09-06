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
- cycle DAC values V: `[1.336735, 0.7375149, 0.6158724, 0.8000829]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.083694e-08, 6.987877e-08, 6.947937e-08], [6.834115e-08, 1.8, 6.834323e-08, 6.834348e-08], [6.834321e-08, 6.834389e-08, 1.8, 6.83441e-08], [6.833697e-08, 6.834154e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655313, -0.8643419, -0.8650727, -0.8653591, -0.8688378, -0.8646758, 0.8639764, -0.8659339, -0.868673, 0.864434, -0.8664963, -0.8652371, -0.8687326, 0.8659789, 0.8658763, -0.8665697, -0.8675322, 0.8654451, 0.8668639, 0.8659106]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
