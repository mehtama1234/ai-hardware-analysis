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
- cycle DAC values V: `[1.337899, 0.7348018, 0.6224857, 0.8065138]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.123555e-08, 7.019176e-08, 6.967869e-08], [6.834118e-08, 1.8, 6.834322e-08, 6.834349e-08], [6.834297e-08, 6.834381e-08, 1.8, 6.834405e-08], [6.833667e-08, 6.834146e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655382, -0.8643319, -0.8650879, -0.8653646, -0.8688479, -0.8646187, 0.8638287, -0.8660226, -0.8686666, 0.8644493, -0.866542, -0.8651874, -0.868739, 0.8659793, 0.8658296, -0.8666529, -0.867588, 0.8654426, 0.8668786, 0.8658267]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
