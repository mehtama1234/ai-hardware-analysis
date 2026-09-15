# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[0, 0, 0, 0]`
- retained logical bits: `[1, 1, 1, 1]`
- final code: `15`
- continuous PMOS/NMOS switch width um: `8.0` / `64.0`
- continuous PMOS bank: `8` parallel device(s)
- bottom diode clamp: `False` (area `1.0`)
- dead-time clamp: `False` (width `1.0` um)
- conversion ground precharge: `False` (2.0 ns)
- top dummy capacitor: `0.5p`
- transient step ps: `100.0`
- conversions measured/required: `5`/`5`
- conversion coverage complete: `True`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[0.02985594, -0.7453689, -0.6872649, -0.6597734]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.8, 1.8, 1.8, 1.800004], [0.04743213, 1.805083, 1.803505, 1.802663], [0.01597085, 0.004877684, 1.802511, 1.801866], [0.001568401, 0.003446536, 0.002237636, 1.801339]]`
- comparator differences V: `[-0.8672682, -0.8668111, -0.8659898, -0.8646166, 0.8662195, 0.8655616, 0.8655402, 0.8655531, -0.8623178, -0.8653701, -0.8744145, -0.8860759, 0.8672648, 0.8670803, 0.8673837, 0.8677329, 0.863658, 0.8682918, 0.8688882, 0.8689108]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient; fixed-decision diagnostic when enabled; not closed-loop qualification, PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
