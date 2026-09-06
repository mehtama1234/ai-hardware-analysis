# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 1, 1, 1]`
- retained logical bits: `[0, 0, 0, 0]`
- final code: `0`
- continuous PMOS/NMOS switch width um: `8.0` / `8.0`
- top dummy capacitor: `0.5p`
- transient step ps: `20.0`
- conversions measured/required: `1`/`5`
- conversion coverage complete: `False`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[1.231117, 0.8258568, 0.8213876, 0.7107298]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.203265, 0.04896357, 0.02290081, 0.01107463], [0.08422043, 0.7294807, 0.01780598, 0.008748268], [0.01393985, 0.005335917, 1.703208, 0.0006549339], [0.000274106, -5.887495e-05, -3.202939e-05, 1.799194]]`
- comparator differences V: `[-0.8708334, -0.8692861, -0.868055, -0.8661168]`

This is a measured one-transient closed-loop physical SAR candidate. It now records four physical decisions across each requested conversion; the current five-conversion run has complete coverage but incorrect codes and an out-of-range bottom plate.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
