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
- cycle DAC values V: `[1.340383, 0.7436294, 0.6255601, 0.8072904]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.176909e-08, 7.047792e-08, 6.987046e-08], [6.834241e-08, 1.8, 6.834333e-08, 6.834357e-08], [6.834287e-08, 6.834376e-08, 1.8, 6.834404e-08], [6.833672e-08, 6.834143e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655349, -0.8643673, -0.8650932, -0.8653865, -0.8688431, -0.8648452, 0.8637258, -0.8660095, -0.8686712, 0.86432, -0.8666387, -0.8653036, -0.8687433, 0.8660036, 0.8657956, -0.8666428, -0.8675465, 0.8654855, 0.8668724, 0.865939]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
