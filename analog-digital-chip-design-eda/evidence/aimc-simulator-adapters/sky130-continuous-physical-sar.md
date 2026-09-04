# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 1, 1, 1]`
- retained logical bits: `[0, 0, 0, 0]`
- final code: `0`
- continuous PMOS/NMOS switch width um: `8.0` / `8.0`
- top dummy capacitor: `0.5p`
- transient step ps: `20.0`
- conversions measured/required: `5`/`5`
- conversion coverage complete: `True`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[1.097282, 0.6858213, 0.6819284, 0.5712572]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.217105, 0.04836157, 0.02259391, 0.01091988], [0.08422263, 0.7294462, 0.01780655, 0.008748549], [0.0139341, 0.005331971, 1.703262, 0.0006544322], [0.0002740644, -5.887261e-05, -3.202519e-05, 1.799194]]`
- comparator differences V: `[-0.8763386, -0.8735509, -0.8718344, -0.8696796, -0.8725137, -0.8695123, -0.8679292, -0.8660906, -0.868233, -0.8654265, 0.8655002, 0.8650612, -0.8654951, 0.8674389, 0.8650542, -0.8658965, -0.8650905, 0.8691525, 0.8659188, 0.8650624]`

This is a measured one-transient closed-loop physical SAR candidate. It now records four physical decisions across each requested conversion; the current five-conversion run has complete coverage but incorrect codes and an out-of-range bottom plate.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
