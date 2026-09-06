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
- cycle DAC values V: `[1.499538, 1.037543, 0.799805, 0.6871063]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.799942, 9.791121e-05, 4.349712e-06, 1.870428e-06], [0.02111733, 1.793164, -0.005564462, -0.002099622], [-0.002153427, 0.001663743, 1.800163, 0.0001420597], [-0.0001429431, 0.0001074007, 2.470341e-05, 1.800005]]`
- comparator differences V: `[-0.8842889, -0.8769207, -0.872803, -0.8695386]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; a banked high-side candidate may improve charge transfer but remains separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
