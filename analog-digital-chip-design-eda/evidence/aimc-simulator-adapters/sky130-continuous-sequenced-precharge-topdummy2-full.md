# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 0, 1, 1]`
- retained logical bits: `[0, 1, 0, 0]`
- final code: `4`
- continuous PMOS/NMOS switch width um: `8.0` / `8.0`
- continuous PMOS bank: `1` parallel device(s)
- bottom diode clamp: `False` (area `1.0`)
- dead-time clamp: `False` (width `1.0` um)
- conversion ground precharge: `False` (2.0 ns)
- top dummy capacitor: `2p`
- transient step ps: `20.0`
- conversions measured/required: `5`/`5`
- conversion coverage complete: `True`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[0.5701243, 0.2196736, 0.6450565, 0.5313783]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.177667, 0.04158852, 0.01967003, 0.009563467], [0.07460273, 0.7622317, 0.01526414, 0.007578991], [0.004147933, 1.830291, 1.750705, -0.0001150858], [0.0008695024, 1.796446, 2.650416e-05, 1.799338]]`
- comparator differences V: `[-0.8685572, 0.8648055, -0.8682869, -0.8674887, -0.8681301, 0.8648351, -0.8681541, -0.867336, -0.8677719, 0.8661766, -0.8661929, 0.8653413, 0.8657434, -0.8689981, -0.8689184, -0.868341, 0.8652489, -0.8691193, -0.8689805, -0.8683861]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
