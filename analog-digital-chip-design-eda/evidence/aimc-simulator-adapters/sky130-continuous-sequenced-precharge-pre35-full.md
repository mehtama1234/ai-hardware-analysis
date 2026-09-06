# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 1, 0, 1]`
- retained logical bits: `[0, 0, 1, 0]`
- final code: `2`
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
- cycle DAC values V: `[0.6720463, 0.2350767, 0.2339651, 0.3546948]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.265133, 0.04610042, 0.02144824, 0.01034518], [0.08419857, 0.7301898, 0.01780331, 0.008746736], [0.0139249, 0.005325899, 1.703345, 0.0006536632], [0.0001883323, -0.0001405183, 1.80051, 1.799303]]`
- comparator differences V: `[-0.8698693, -0.86486, 0.8649312, -0.8653082, -0.8688578, -0.8648028, 0.8652068, -0.8650256, -0.8684776, 0.8659143, -0.8667551, -0.865105, -0.8650617, 0.8689915, 0.8652285, -0.86551, -0.8650711, 0.8691264, 0.8653053, -0.8654584]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
