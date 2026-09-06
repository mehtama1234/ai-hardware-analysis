# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 1, 1, 0]`
- retained logical bits: `[0, 0, 0, 1]`
- final code: `1`
- continuous PMOS/NMOS switch width um: `8.0` / `8.0`
- continuous PMOS bank: `8` parallel device(s)
- dead-time clamp: `False`
- top dummy capacitor: `0.5p`
- transient step ps: `20.0`
- conversions measured/required: `5`/`5`
- conversion coverage complete: `True`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[1.345016, 0.8851591, 0.6464773, 0.5355086]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.799943, 9.592936e-05, 4.274732e-06, 1.844061e-06], [0.02110141, 1.793169, -0.005560518, -0.002098101], [-0.002142122, 0.001655006, 1.800162, 0.0001413237], [-0.0001441607, 0.0001083042, 2.491154e-05, 1.800005]]`
- comparator differences V: `[-0.8854049, -0.8773177, -0.8729346, -0.8682045, -0.8718957, -0.8693134, -0.8654283, 0.8662349, -0.8686061, -0.8668546, 0.8666277, 0.8657859, -0.8664645, 0.8657464, -0.8650458, 0.865226, -0.8650941, 0.8679948, 0.8661891, 0.8651583]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked and dead-time-clamped candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
