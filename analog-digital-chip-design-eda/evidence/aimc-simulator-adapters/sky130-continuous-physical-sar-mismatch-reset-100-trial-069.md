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
- cycle DAC values V: `[1.335123, 0.7361457, 0.6231901, 0.8067262]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.113817e-08, 7.01284e-08, 6.962278e-08], [6.83412e-08, 1.8, 6.834321e-08, 6.834349e-08], [6.834295e-08, 6.83438e-08, 1.8, 6.834405e-08], [6.833669e-08, 6.834145e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655374, -0.8643377, -0.8650894, -0.8653589, -0.8688449, -0.8646504, 0.8638111, -0.8660256, -0.8686637, 0.8644352, -0.8665729, -0.8652036, -0.8687303, 0.8659891, 0.8658088, -0.8666836, -0.8675376, 0.8654501, 0.8668804, 0.8658009]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
