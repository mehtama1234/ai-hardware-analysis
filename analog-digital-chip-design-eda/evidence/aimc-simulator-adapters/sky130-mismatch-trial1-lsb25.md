# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
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
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[1.244393, 0.8196926, 0.6112469, 0.8820004]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 9.935405e-08, 8.226748e-08, 8.638755e-08], [6.897536e-08, 1.8, 6.843312e-08, 6.846074e-08], [6.834349e-08, 6.834389e-08, 1.8, 6.834405e-08], [6.83348e-08, 6.833955e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8654778, -0.8646883, -0.8650629, -0.8659772, -0.8687583, -0.8660685, 0.8640284, -0.8668456, -0.8685747, -0.8635033, 0.8653518, -0.8641716, -0.8683411, 0.8661949, 0.8644846, -0.86858, -0.8662426, 0.8664211, 0.8667958, -0.8674336]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
