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
- cycle DAC values V: `[1.34065, 0.7378586, 0.622807, 0.8074152]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.106681e-08, 7.00534e-08, 6.959565e-08], [6.83411e-08, 1.8, 6.834321e-08, 6.834347e-08], [6.834296e-08, 6.83438e-08, 1.8, 6.834405e-08], [6.833662e-08, 6.834143e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655361, -0.8643472, -0.8650902, -0.8654055, -0.8688433, -0.8647197, 0.8637994, -0.8660096, -0.8686697, 0.8644127, -0.8665259, -0.8652113, -0.8687391, 0.8659758, 0.8658873, -0.8665095, -0.8675067, 0.8654053, 0.8668593, 0.8660505]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
