# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_nominal_map_passed`
- expected code: `2`
- comparator clear flags: `[1, 1, 0, 1]`
- retained logical bits: `[0, 0, 1, 0]`
- final code: `2`
- continuous PMOS/NMOS switch width um: `8.0` / `64.0`
- continuous PMOS bank: `8` parallel device(s)
- bottom diode clamp: `False` (area `1.0`)
- dead-time clamp: `False` (width `1.0` um)
- conversion ground precharge: `False` (2.0 ns)
- top dummy capacitor: `0.5p`
- transient step ps: `20.0`
- conversions measured/required: `5`/`5`
- conversion coverage complete: `True`
- all conversions correct: `True`
- measured: `True`
- cycle DAC values V: `[1.337659, 0.737704, 0.6198069, 0.8008515]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.102316e-08, 7.002182e-08, 6.954307e-08], [6.834133e-08, 1.8, 6.834323e-08, 6.834351e-08], [6.834306e-08, 6.834384e-08, 1.8, 6.834408e-08], [6.833705e-08, 6.834158e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655312, -0.8643416, -0.8650805, -0.8653393, -0.8688387, -0.8646801, 0.8638859, -0.8659455, -0.868674, 0.8644281, -0.8665506, -0.8651689, -0.8687379, 0.8659819, 0.8658357, -0.8665927, -0.8675596, 0.8654547, 0.8668691, 0.8658881]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
