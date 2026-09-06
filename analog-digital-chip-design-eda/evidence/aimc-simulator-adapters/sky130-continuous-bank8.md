# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 1, 1, 1]`
- retained logical bits: `[0, 0, 0, 0]`
- final code: `0`
- continuous PMOS/NMOS switch width um: `8.0` / `8.0`
- continuous PMOS bank: `8` parallel device(s)
- top dummy capacitor: `0.5p`
- transient step ps: `20.0`
- conversions measured/required: `1`/`5`
- conversion coverage complete: `False`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[1.521937, 1.059555, 0.8219437, 0.7090848]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.799941, 9.909022e-05, 4.394807e-06, 1.886184e-06], [0.0211711, 1.793147, -0.005578323, -0.002104934], [-0.002155354, 0.001665232, 1.800163, 0.0001421849], [-0.0001436116, 0.0001078963, 2.481758e-05, 1.800005]]`
- comparator differences V: `[-0.8853648, -0.8772935, -0.873281, -0.8699978]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; a banked high-side candidate may improve charge transfer but remains separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
