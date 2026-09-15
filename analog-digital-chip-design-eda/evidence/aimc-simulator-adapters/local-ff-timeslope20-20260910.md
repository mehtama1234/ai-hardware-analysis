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
- cycle DAC values V: `[1.290192, 0.6988111, 0.5865296, 0.8014443]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 1.037448e-06, 1.037435e-06, 1.037432e-06], [1.037409e-06, 1.8, 1.037413e-06, 1.037413e-06], [1.037414e-06, 1.037414e-06, 1.8, 1.037414e-06], [1.037406e-06, 1.037411e-06, 1.8, 1.8]]`
- comparator differences V: `[-0.7324247, -0.7307606, -0.7307831, -0.7311171, -0.7348783, -0.7314983, 0.7305301, -0.7326272, -0.7355319, 0.7313954, -0.7329909, -0.7326123, -0.7357313, 0.7321724, 0.7330664, -0.7342724, -0.7348334, 0.7316244, 0.7334132, 0.7334576]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
