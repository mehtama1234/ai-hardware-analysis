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
- cycle DAC values V: `[1.337437, 0.7457316, 0.6253624, 0.8065785]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.161723e-08, 7.036928e-08, 6.978594e-08], [6.834255e-08, 1.8, 6.834333e-08, 6.834358e-08], [6.834288e-08, 6.834376e-08, 1.8, 6.834404e-08], [6.833679e-08, 6.834143e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655339, -0.864377, -0.8650931, -0.8653805, -0.8688409, -0.8648887, 0.86373, -0.8659999, -0.8686693, 0.8642921, -0.8666676, -0.8653327, -0.8687341, 0.8660092, 0.8657752, -0.8666696, -0.867489, 0.8654986, 0.8668741, 0.8659207]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
