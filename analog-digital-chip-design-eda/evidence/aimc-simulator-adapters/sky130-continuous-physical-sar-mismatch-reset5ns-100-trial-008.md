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
- cycle DAC values V: `[1.350094, 0.7304215, 0.6218093, 0.8052602]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.195937e-08, 7.067568e-08, 7.004294e-08], [6.834143e-08, 1.8, 6.834328e-08, 6.834353e-08], [6.834298e-08, 6.834382e-08, 1.8, 6.834406e-08], [6.833666e-08, 6.834154e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655412, -0.8643103, -0.8650823, -0.8653678, -0.8688519, -0.8644928, 0.8638428, -0.8660056, -0.868684, 0.8644964, -0.8664562, -0.8650875, -0.8687728, 0.8659656, 0.8658835, -0.8665407, -0.8678024, 0.8654269, 0.8668649, 0.8659054]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
