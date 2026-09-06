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
- cycle DAC values V: `[1.334895, 0.7435249, 0.6215954, 0.8023586]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.163389e-08, 7.037959e-08, 6.979328e-08], [6.834264e-08, 1.8, 6.834336e-08, 6.834359e-08], [6.834301e-08, 6.834381e-08, 1.8, 6.834407e-08], [6.833701e-08, 6.834152e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655374, -0.8643624, -0.8650821, -0.8653419, -0.8688389, -0.8648105, 0.8638431, -0.8659665, -0.8686721, 0.8643334, -0.8666521, -0.8653199, -0.8687341, 0.8660046, 0.8657544, -0.8667436, -0.8675481, 0.8655271, 0.8668803, 0.8657327]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
