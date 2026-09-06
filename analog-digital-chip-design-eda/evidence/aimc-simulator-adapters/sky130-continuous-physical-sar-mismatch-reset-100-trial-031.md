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
- cycle DAC values V: `[1.337286, 0.7366187, 0.6224423, 0.8061098]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.134949e-08, 7.025236e-08, 6.972111e-08], [6.834142e-08, 1.8, 6.834324e-08, 6.834351e-08], [6.834298e-08, 6.834381e-08, 1.8, 6.834406e-08], [6.833671e-08, 6.834146e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655372, -0.864338, -0.8650876, -0.8653627, -0.8688474, -0.864661, 0.8638294, -0.8660172, -0.8686662, 0.864425, -0.8665657, -0.865227, -0.8687379, 0.8659869, 0.8658113, -0.8666813, -0.8675813, 0.8654622, 0.8668805, 0.8657977]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
