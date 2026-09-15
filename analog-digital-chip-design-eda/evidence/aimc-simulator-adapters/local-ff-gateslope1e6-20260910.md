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
- cycle DAC values V: `[0.8456171, 0.3183144, 0.5368645, 0.7298746]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.615409, 1.262825e-05, 9.792604e-06, 9.549503e-06], [0.0004518356, 1.615284, -0.0001177884, -9.761789e-05], [3.175936e-05, 1.615406, 1.615409, 2.587889e-06], [5.92222e-05, 1.615397, 1.615404, 1.615406]]`
- comparator differences V: `[-0.732261, -0.7307642, 0.7311458, 0.7318468, -0.733913, 0.7325341, 0.7327849, -0.7329452, -0.7339356, 0.7325878, 0.7330973, 0.7331659, -0.7335346, 0.7330739, 0.7336804, 0.7339657, 0.7338531, -0.7363093, -0.7356137, -0.7353888]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
