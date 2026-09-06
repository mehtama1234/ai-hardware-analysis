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
- cycle DAC values V: `[1.346097, 0.7388405, 0.6182679, 0.7991354]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.173525e-08, 7.04371e-08, 6.986564e-08], [6.834222e-08, 1.8, 6.834334e-08, 6.834357e-08], [6.834312e-08, 6.834386e-08, 1.8, 6.834409e-08], [6.83371e-08, 6.834163e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655396, -0.8643435, -0.8650797, -0.86535, -0.8688435, -0.8647108, 0.8639258, -0.8659213, -0.8686759, 0.8643872, -0.8665324, -0.865228, -0.8687616, 0.865999, 0.8658315, -0.8665823, -0.8677302, 0.8654979, 0.8668797, 0.8658797]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
