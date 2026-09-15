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
- cycle DAC values V: `[1.28874, 0.6972329, 0.5833574, 0.7985584]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 1.037449e-06, 1.037436e-06, 1.037433e-06], [1.03741e-06, 1.8, 1.037413e-06, 1.037413e-06], [1.037414e-06, 1.037414e-06, 1.8, 1.037414e-06], [1.037406e-06, 1.037411e-06, 1.8, 1.8]]`
- comparator differences V: `[-0.7341865, -0.7332013, -0.7331007, -0.7333547, -0.7362762, -0.7327173, 0.7326987, -0.7335837, -0.7360781, 0.7328398, -0.733675, -0.7333084, -0.7359042, 0.7334626, 0.7337572, -0.734395, -0.7348452, 0.7336532, 0.7341676, 0.7338109]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
