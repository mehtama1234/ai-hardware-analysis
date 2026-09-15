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
- cycle DAC values V: `[0.8498224, 0.3202354, 0.5394787, 0.7015475]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.592094, 5.21799e-05, 1.87611e-05, 1.161029e-05], [0.001601146, 1.591585, -0.0004644091, -0.0002952321], [0.0001000801, 1.592119, 1.592137, -1.86531e-05], [0.0001753203, 1.592089, 1.592122, 1.592134]]`
- comparator differences V: `[-0.8657479, -0.8638697, 0.8643659, 0.8648177, -0.8666788, 0.865823, 0.8655387, -0.864586, -0.8667587, 0.8658908, 0.8659679, 0.8648495, -0.8656635, 0.8664264, 0.8667445, 0.8667458, 0.8657251, -0.8686626, -0.8681793, -0.8675341]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
