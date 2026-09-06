# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 1, 1, 1]`
- retained logical bits: `[0, 0, 0, 0]`
- final code: `0`
- continuous PMOS/NMOS switch width um: `8.0` / `8.0`
- continuous PMOS bank: `8` parallel device(s)
- dead-time clamp: `True`
- top dummy capacitor: `0.5p`
- transient step ps: `20.0`
- conversions measured/required: `1`/`5`
- conversion coverage complete: `False`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[1.516282, 1.052958, 0.8165259, 0.7036249]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.799941, 9.891901e-05, 4.384156e-06, 1.882798e-06], [0.01829368, 1.794061, -0.004833153, -0.001819969], [-0.001882628, 0.001454078, 1.800142, 0.0001243985], [-0.0001227818, 9.242422e-05, 2.12822e-05, 1.800004]]`
- comparator differences V: `[-0.8850885, -0.8771945, -0.8731643, -0.8698794]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked and dead-time-clamped candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
