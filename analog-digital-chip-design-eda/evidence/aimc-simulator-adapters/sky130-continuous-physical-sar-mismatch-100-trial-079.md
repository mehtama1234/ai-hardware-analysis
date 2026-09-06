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
- cycle DAC values V: `[1.34762, 0.7323761, 0.623259, 0.8071653]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.107495e-08, 7.009169e-08, 6.961882e-08], [6.834078e-08, 1.8, 6.83432e-08, 6.834347e-08], [6.834293e-08, 6.83438e-08, 1.8, 6.834405e-08], [6.83366e-08, 6.834149e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655401, -0.8643254, -0.8650912, -0.865403, -0.8688489, -0.8645902, 0.8637907, -0.8660063, -0.8686773, 0.8644757, -0.8664502, -0.8650581, -0.8687567, 0.8659562, 0.8659359, -0.8663784, -0.8676199, 0.8653583, 0.8668515, 0.8661276]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
