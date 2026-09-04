# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 1, 1, 0]`
- retained logical bits: `[0, 0, 0, 1]`
- final code: `1`
- continuous PMOS/NMOS switch width um: `8.0` / `8.0`
- top dummy capacitor: `0.5p`
- transient step ps: `20.0`
- conversions measured/required: `5`/`5`
- conversion coverage complete: `True`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[1.090546, 0.6785001, 0.6743539, 0.5636418]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.218434, 0.04830242, 0.0225638, 0.01090472], [0.08419446, 0.7303923, 0.01780235, 0.008746198], [0.01397305, 0.005357685, 1.702909, 0.0006576941], [0.000275823, -5.900692e-05, -3.220981e-05, 1.799188]]`
- comparator differences V: `[-0.8760631, -0.8732765, -0.8709663, -0.8674902, -0.8679603, -0.8660114, -0.8650813, 0.8659051, -0.8671115, 0.8651071, -0.8667091, -0.8667327, -0.8663642, 0.8674046, 0.8650514, -0.8658495, -0.8650636, 0.869217, 0.8659492, 0.8650538]`

This is a measured one-transient closed-loop physical SAR candidate. It now records four physical decisions across each requested conversion; the current five-conversion run has complete coverage but incorrect codes and an out-of-range bottom plate.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
