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
- cycle DAC values V: `[1.341572, 0.7392307, 0.6168683, 0.7997073]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.147564e-08, 7.026556e-08, 6.975948e-08], [6.834191e-08, 1.8, 6.834331e-08, 6.834354e-08], [6.834317e-08, 6.834388e-08, 1.8, 6.834409e-08], [6.833702e-08, 6.834157e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.865535, -0.8643452, -0.865077, -0.8653562, -0.8688434, -0.8647144, 0.863956, -0.8659289, -0.8686781, 0.8643989, -0.8665238, -0.8652694, -0.8687506, 0.8659922, 0.8658494, -0.8666015, -0.8676544, 0.8654862, 0.8668686, 0.8658695]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
