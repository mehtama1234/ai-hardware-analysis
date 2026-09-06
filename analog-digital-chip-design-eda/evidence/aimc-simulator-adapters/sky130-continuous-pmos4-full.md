# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 0, 1, 1]`
- retained logical bits: `[0, 1, 0, 0]`
- final code: `4`
- continuous PMOS/NMOS switch width um: `4.0` / `8.0`
- continuous PMOS bank: `1` parallel device(s)
- bottom diode clamp: `False` (area `1.0`)
- dead-time clamp: `False` (width `1.0` um)
- conversion ground precharge: `False` (2.0 ns)
- top dummy capacitor: `0.5p`
- transient step ps: `20.0`
- conversions measured/required: `5`/`5`
- conversion coverage complete: `True`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[0.8025347, 0.4880791, 1.158702, 1.057066]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[0.600726, 0.03039654, 0.01482042, 0.007320942], [0.04790268, -0.0799086, 0.01106248, 0.005487536], [0.02251409, 1.889732, 1.352767, 0.002024436], [0.009339037, 1.790788, 0.0008232997, 1.707082]]`
- comparator differences V: `[-0.8722027, -0.8690722, -0.8691554, -0.8675335, -0.8663974, 0.8665136, -0.8676594, -0.8684363, 0.8654446, -0.8829046, -0.8764119, -0.8751525, -0.8681585, 0.8701634, 0.8653696, -0.8653888, 0.8713684, -0.8690222, -0.8684889, -0.8683508]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
