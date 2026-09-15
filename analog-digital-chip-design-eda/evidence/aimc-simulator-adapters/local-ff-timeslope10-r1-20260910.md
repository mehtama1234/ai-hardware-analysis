# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 0, 0, 1]`
- retained logical bits: `[0, 1, 1, 0]`
- final code: `6`
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
- cycle DAC values V: `[0.8456368, 0.3188493, 0.5374623, 0.7302292]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.615408, 1.309625e-05, 9.940545e-06, 9.669982e-06], [0.0003884987, 1.615303, -9.975783e-05, -8.246528e-05], [3.507191e-05, 1.615405, 1.615409, 1.749809e-06], [6.698059e-05, 1.615394, 1.615403, 1.615404]]`
- comparator differences V: `[-0.730371, -0.7278835, 0.7278886, -0.7284798, -0.7326885, 0.7300714, 0.7303707, -0.7318615, -0.7331342, 0.7306193, 0.7315937, 0.7320261, -0.7329987, 0.7310606, 0.7324434, 0.7333414, 0.7335161, -0.7362468, -0.7355372, -0.7353123]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
