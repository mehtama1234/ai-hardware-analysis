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
- cycle DAC values V: `[1.338008, 0.7416017, 0.6220538, 0.8033711]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.176338e-08, 7.047436e-08, 6.986791e-08], [6.834243e-08, 1.8, 6.834334e-08, 6.834358e-08], [6.834299e-08, 6.834381e-08, 1.8, 6.834406e-08], [6.833692e-08, 6.834151e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655381, -0.8643552, -0.865086, -0.8653509, -0.8688479, -0.8647719, 0.8638378, -0.8659802, -0.8686674, 0.8643525, -0.8666251, -0.8652994, -0.8687421, 0.8660182, 0.8657611, -0.8667262, -0.8676117, 0.8655186, 0.8668852, 0.8657462]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
