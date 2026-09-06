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
- cycle DAC values V: `[1.346265, 0.7333831, 0.6176368, 0.8021768]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.143772e-08, 7.028349e-08, 6.978593e-08], [6.83413e-08, 1.8, 6.834326e-08, 6.83435e-08], [6.834313e-08, 6.834387e-08, 1.8, 6.834409e-08], [6.83368e-08, 6.834155e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655389, -0.8643247, -0.8650795, -0.8653725, -0.8688437, -0.8645836, 0.8639408, -0.8659627, -0.8686755, 0.8644609, -0.8664511, -0.8651778, -0.8687604, 0.8659768, 0.8658912, -0.8665308, -0.8677235, 0.8654393, 0.8668722, 0.8659247]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
