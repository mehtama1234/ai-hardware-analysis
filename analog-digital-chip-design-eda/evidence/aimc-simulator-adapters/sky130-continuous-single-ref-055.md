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
- cycle DAC values V: `[1.231117, 0.825829, 0.821377, 0.710729]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.203264, 0.04896358, 0.02290082, 0.01107463], [0.08422351, 0.7293774, 0.01780644, 0.008748526], [0.01395888, 0.005348621, 1.703035, 0.0006565474], [0.0002744201, -5.889875e-05, -3.206236e-05, 1.799193]]`
- comparator differences V: `[-0.8727693, -0.8707546, -0.8692716, -0.8673417]`

This is a measured one-transient closed-loop physical SAR candidate. It now records four physical decisions across each requested conversion; the current five-conversion run has complete coverage but incorrect codes and an out-of-range bottom plate.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
