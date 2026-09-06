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
- cycle DAC values V: `[1.301204, 0.6978597, 0.5847449, 0.7673223]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 1.037424e-06, 1.03742e-06, 1.037418e-06], [1.03741e-06, 1.8, 1.037413e-06, 1.037413e-06], [1.037414e-06, 1.037414e-06, 1.8, 1.037414e-06], [1.037407e-06, 1.037411e-06, 1.8, 1.8]]`
- comparator differences V: `[-0.7324597, -0.7308694, -0.7313289, -0.7317095, -0.7358128, -0.7313294, 0.7311508, -0.7322313, -0.7355403, 0.7314013, -0.7329082, -0.7321668, -0.7356905, 0.7320704, 0.7330752, -0.7335382, -0.7345899, 0.7313659, 0.7332814, 0.7336395]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
