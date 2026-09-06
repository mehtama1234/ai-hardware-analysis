# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 0, 1, 1]`
- retained logical bits: `[0, 1, 0, 0]`
- final code: `4`
- continuous PMOS/NMOS switch width um: `8.0` / `8.0`
- continuous PMOS bank: `1` parallel device(s)
- bottom diode clamp: `True` (area `1000.0`)
- dead-time clamp: `False`
- conversion ground precharge: `False` (2.0 ns)
- top dummy capacitor: `0.5p`
- transient step ps: `20.0`
- conversions measured/required: `5`/`5`
- conversion coverage complete: `True`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[1.008868, 0.590193, 1.057449, 0.9346329]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.229638, 0.04779726, 0.0223069, 0.01077547], [0.08418543, 0.7307061, 0.01780115, 0.008745502], [0.003663575, 1.830756, 1.751877, -0.0001491671], [0.0008878899, 1.796488, 3.065454e-05, 1.799312]]`
- comparator differences V: `[-0.8738981, -0.8705675, -0.8685085, -0.8657103, -0.8668984, 0.8650743, -0.8672232, -0.8676127, -0.8678165, 0.8659535, -0.8661085, -0.8660022, -0.8654785, 0.8683213, 0.8651908, -0.8651911, 0.8657259, -0.8724884, -0.8702937, -0.8686581]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
