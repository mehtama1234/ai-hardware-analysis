# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 1, 1, 1]`
- retained logical bits: `[0, 0, 0, 0]`
- final code: `0`
- continuous PMOS/NMOS switch width um: `8.0` / `8.0`
- continuous PMOS bank: `8` parallel device(s)
- dead-time clamp: `False`
- top dummy capacitor: `0.5p`
- transient step ps: `20.0`
- conversions measured/required: `1`/`5`
- conversion coverage complete: `False`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[1.521937, 1.059551, 0.8219478, 0.7090859]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.799941, 9.908902e-05, 4.394761e-06, 1.886168e-06], [0.02112858, 1.79316, -0.005567335, -0.002100726], [-0.002148911, 0.00166024, 1.800162, 0.0001417654], [-0.0001431866, 0.0001075812, 2.474499e-05, 1.800005]]`
- comparator differences V: `[-0.8762538, -0.8712584, -0.8684603, -0.8659033]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked and dead-time-clamped candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
