# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
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
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[1.343941, 0.8594866, 0.5622617, 0.6882423]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.37909e-08, 7.009406e-08, 6.947829e-08], [6.891284e-08, 1.8, 6.840086e-08, 6.838068e-08], [6.834508e-08, 6.834469e-08, 1.8, 6.83444e-08], [6.834061e-08, 6.834246e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655386, -0.8650084, -0.8649903, -0.8649025, -0.8688484, -0.8665621, 0.8645603, -0.863427, -0.8686828, -0.8645393, 0.865195, 0.8655326, -0.8687539, 0.8661715, 0.8647486, -0.866558, -0.8675794, 0.8664688, 0.8668666, 0.8660254]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
