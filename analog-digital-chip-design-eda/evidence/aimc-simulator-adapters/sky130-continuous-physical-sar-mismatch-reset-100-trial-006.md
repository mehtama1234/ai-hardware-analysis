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
- cycle DAC values V: `[1.343122, 0.728678, 0.6179114, 0.8042575]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.0805e-08, 6.991628e-08, 6.951499e-08], [6.83406e-08, 1.8, 6.83432e-08, 6.834346e-08], [6.834313e-08, 6.834387e-08, 1.8, 6.834408e-08], [6.833667e-08, 6.834152e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655391, -0.8643113, -0.8650814, -0.8653798, -0.8688406, -0.8644626, 0.8639355, -0.8659911, -0.8686712, 0.8645243, -0.8663961, -0.8650792, -0.8687498, 0.8659519, 0.8659345, -0.8664712, -0.8676497, 0.8653739, 0.8668649, 0.8659803]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
