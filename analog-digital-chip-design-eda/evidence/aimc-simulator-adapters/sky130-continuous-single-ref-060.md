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
- cycle DAC values V: `[1.231117, 0.825849, 0.8213833, 0.7107295]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.203264, 0.04896357, 0.02290082, 0.01107463], [0.08422122, 0.7294543, 0.01780609, 0.008748334], [0.01394701, 0.005340696, 1.703143, 0.0006555409], [0.0002741919, -5.888146e-05, -3.203841e-05, 1.799194]]`
- comparator differences V: `[-0.8717791, -0.8700063, -0.8686449, -0.8667485]`

This is a measured one-transient closed-loop physical SAR candidate. It now records four physical decisions across each requested conversion; the current five-conversion run has complete coverage but incorrect codes and an out-of-range bottom plate.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
