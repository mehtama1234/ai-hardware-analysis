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
- cycle DAC values V: `[1.335684, 0.7373671, 0.6172327, 0.8018931]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.088904e-08, 6.992128e-08, 6.950777e-08], [6.834119e-08, 1.8, 6.834323e-08, 6.834348e-08], [6.834316e-08, 6.834387e-08, 1.8, 6.834409e-08], [6.833688e-08, 6.83415e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655354, -0.8643422, -0.8650786, -0.8653627, -0.8688367, -0.8646721, 0.8639479, -0.865959, -0.868672, 0.8644348, -0.866512, -0.8652471, -0.8687315, 0.8659792, 0.8658647, -0.8666059, -0.8675208, 0.8654464, 0.8668655, 0.8658784]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
