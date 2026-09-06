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
- cycle DAC values V: `[1.335062, 0.7437142, 0.6218893, 0.8026835]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.151905e-08, 7.030852e-08, 6.974268e-08], [6.834257e-08, 1.8, 6.834335e-08, 6.834358e-08], [6.8343e-08, 6.83438e-08, 1.8, 6.834406e-08], [6.833699e-08, 6.834151e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655374, -0.8643645, -0.865086, -0.8653446, -0.868845, -0.8648167, 0.8638409, -0.8659709, -0.8686644, 0.864326, -0.8666547, -0.8653294, -0.8687327, 0.8660135, 0.8657391, -0.8667525, -0.8675567, 0.8655395, 0.8668865, 0.8657231]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
