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
- cycle DAC values V: `[1.227574, 1.019191, 0.608625, 0.7160671]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.799999, 1.659214e-07, 9.44669e-08, 8.07929e-08], [2.289191e-07, 1.799999, 9.555256e-08, 8.125503e-08], [6.834359e-08, 6.834377e-08, 1.8, 6.834422e-08], [6.834031e-08, 6.834131e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8654656, -0.8654169, -0.8650644, -0.8647942, -0.8687477, -0.8680231, 0.8640404, -0.864415, -0.8685603, -0.8671102, 0.8652941, 0.8654098, -0.8682277, -0.8643319, 0.8652782, 0.8661664, -0.8659765, 0.866879, -0.8659554, 0.8660523]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
