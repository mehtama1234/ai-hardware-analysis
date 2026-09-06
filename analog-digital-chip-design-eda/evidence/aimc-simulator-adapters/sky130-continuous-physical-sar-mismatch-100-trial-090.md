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
- cycle DAC values V: `[1.344349, 0.7328744, 0.6214904, 0.8080023]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.092407e-08, 6.998017e-08, 6.956279e-08], [6.834069e-08, 1.8, 6.834319e-08, 6.834345e-08], [6.8343e-08, 6.834382e-08, 1.8, 6.834406e-08], [6.833652e-08, 6.834144e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655383, -0.864328, -0.8650884, -0.8654198, -0.8688462, -0.8646024, 0.863834, -0.8660167, -0.8686737, 0.8644742, -0.8664345, -0.8651316, -0.868748, 0.8659556, 0.8659482, -0.8664054, -0.8675593, 0.8653544, 0.8668489, 0.8661161]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
