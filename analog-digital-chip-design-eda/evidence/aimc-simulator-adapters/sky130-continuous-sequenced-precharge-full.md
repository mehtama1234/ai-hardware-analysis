# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 0, 0, 1]`
- retained logical bits: `[0, 1, 1, 0]`
- final code: `6`
- continuous PMOS/NMOS switch width um: `8.0` / `8.0`
- continuous PMOS bank: `1` parallel device(s)
- bottom diode clamp: `False` (area `1.0`)
- dead-time clamp: `False` (width `1.0` um)
- conversion ground precharge: `False` (2.0 ns)
- top dummy capacitor: `0.5p`
- transient step ps: `20.0`
- conversions measured/required: `5`/`5`
- conversion coverage complete: `True`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[0.6710503, 0.2345855, 0.7047671, 0.8131957]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.263566, 0.0461785, 0.0214876, 0.01036485], [0.08422201, 0.7294034, 0.01780681, 0.008748698], [0.00363985, 1.830683, 1.752071, -0.0001493445], [-0.001002863, 1.806742, 1.799048, 1.798882]]`
- comparator differences V: `[-0.8700773, -0.8656813, 0.8656778, 0.8662947, -0.865075, 0.8687484, 0.8650736, -0.8661634, -0.8656139, 0.8687835, 0.8652468, -0.8652287, 0.865283, -0.8705571, -0.8692813, -0.8679606, 0.8651743, -0.8699778, -0.8686183, -0.8675276]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
