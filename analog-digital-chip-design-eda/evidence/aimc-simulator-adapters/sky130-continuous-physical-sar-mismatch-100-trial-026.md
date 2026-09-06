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
- cycle DAC values V: `[1.346128, 0.7385583, 0.6210819, 0.8027854]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.118538e-08, 7.010813e-08, 6.962561e-08], [6.834132e-08, 1.8, 6.834324e-08, 6.83435e-08], [6.834301e-08, 6.834382e-08, 1.8, 6.834407e-08], [6.83369e-08, 6.834155e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655394, -0.8643498, -0.865087, -0.8653839, -0.8688476, -0.8647364, 0.8638408, -0.8659463, -0.8686762, 0.8643999, -0.8665097, -0.8651613, -0.8687534, 0.8659801, 0.8658987, -0.8664212, -0.8675999, 0.8654179, 0.8668584, 0.8661032]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
