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
- cycle DAC values V: `[1.345924, 0.7386457, 0.6179621, 0.798799]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.179849e-08, 7.047614e-08, 6.989402e-08], [6.834222e-08, 1.8, 6.834334e-08, 6.834357e-08], [6.834313e-08, 6.834386e-08, 1.8, 6.834409e-08], [6.833712e-08, 6.834163e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655376, -0.8643434, -0.865078, -0.8653472, -0.8688481, -0.8647011, 0.863933, -0.8659167, -0.8686818, 0.8644006, -0.8665256, -0.8652176, -0.8687624, 0.8659932, 0.8658436, -0.8665726, -0.8677283, 0.8654924, 0.8668698, 0.8658881]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
