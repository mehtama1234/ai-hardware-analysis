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
- cycle DAC values V: `[1.348489, 0.7408823, 0.6218449, 0.8031329]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.179516e-08, 7.047408e-08, 6.989252e-08], [6.834216e-08, 1.8, 6.834332e-08, 6.834356e-08], [6.834299e-08, 6.834381e-08, 1.8, 6.834406e-08], [6.833689e-08, 6.834154e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655402, -0.8643561, -0.8650871, -0.8653862, -0.8688496, -0.8647876, 0.8638215, -0.8659516, -0.8686793, 0.8643563, -0.8665467, -0.8652328, -0.8687635, 0.865995, 0.8658629, -0.8664917, -0.8676739, 0.8654632, 0.8668647, 0.8660482]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
