# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[0, 1, 1, 1]`
- retained logical bits: `[1, 0, 0, 0]`
- final code: `8`
- continuous PMOS/NMOS switch width um: `8.0` / `8.0`
- continuous PMOS bank: `1` parallel device(s)
- dead-time clamp: `False`
- conversion ground precharge: `False` (2.0 ns)
- top dummy capacitor: `0.5p`
- transient step ps: `20.0`
- conversions measured/required: `5`/`5`
- conversion coverage complete: `True`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[0.6781341, 0.8816877, 0.9405238, 0.6260008]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.246307, 0.04698008, 0.02189533, 0.01056949], [1.556389, 1.063079, 0.06794161, 0.05830919], [1.791788, 0.01419753, 1.728855, 0.001887046], [1.781978, 0.002313879, 0.0009811381, 1.801933]]`
- comparator differences V: `[-0.8759689, -0.8690628, -0.8676592, 0.866736, 0.8650716, -0.8670351, -0.8675117, -0.8650838, 0.8689507, 0.8670645, -0.8653387, 0.8668951, 0.870204, 0.8704078, 0.8685207, 0.8686832, 0.8714068, 0.8714737, 0.8705523, 0.8703222]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
