# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[0, 1, 1, 0]`
- retained logical bits: `[1, 0, 0, 1]`
- final code: `9`
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
- cycle DAC values V: `[0.4480291, 0.8142901, 0.6891687, 0.6342547]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.104507e-08, 7.000184e-08, 6.956539e-08], [1.8, 1.8, 6.320775e-08, 6.454049e-08], [1.8, 6.79408e-08, 1.8, 6.816052e-08], [1.8, 6.823491e-08, 6.827698e-08, 1.8]]`
- comparator differences V: `[-0.8635281, 0.8611245, 0.8629591, 0.8637042, 0.8650029, -0.8659977, -0.8633078, 0.8631431, 0.8646968, -0.8647556, 0.8649068, -0.8653606, 0.8647925, 0.8659639, -0.8667157, -0.864791, 0.8644262, 0.8668326, 0.8650441, -0.8681481]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
