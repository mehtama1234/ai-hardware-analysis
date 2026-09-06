# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 1, 1, 0]`
- retained logical bits: `[0, 0, 0, 1]`
- final code: `1`
- continuous PMOS/NMOS switch width um: `8.0` / `8.0`
- continuous PMOS bank: `1` parallel device(s)
- bottom diode clamp: `False` (area `1.0`)
- dead-time clamp: `True` (width `16.0` um)
- conversion ground precharge: `False` (2.0 ns)
- top dummy capacitor: `0.5p`
- transient step ps: `20.0`
- conversions measured/required: `5`/`5`
- conversion coverage complete: `True`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[1.094341, 0.7590079, 0.6598129, 0.5477712]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.257142, 0.04642481, 0.02161782, 0.01043123], [0.07013006, 1.134482, 0.01455305, 0.007034158], [0.008561278, 0.001947575, 1.749326, 0.0002506123], [0.0003155025, -0.0001208429, -4.062194e-05, 1.799331]]`
- comparator differences V: `[-0.8760944, -0.874045, -0.871028, -0.8672815, -0.8678535, -0.8668519, -0.8650728, 0.866119, -0.867045, -0.8652117, 0.8664388, 0.8654693, -0.8653572, 0.866785, 0.8650531, -0.865615, -0.8653482, 0.8684336, 0.8659672, 0.8650497]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
