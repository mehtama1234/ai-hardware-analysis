# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[0, 1, 0, 1]`
- retained logical bits: `[1, 0, 1, 0]`
- final code: `10`
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
- cycle DAC values V: `[0.4128339, 0.7734339, 0.6490825, 0.8310328]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.084919e-08, 6.991557e-08, 6.948697e-08], [1.8, 1.8, 6.353431e-08, 6.482725e-08], [1.8, 6.789537e-08, 1.8, 6.8138e-08], [1.8, 6.764398e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8634429, 0.8611294, 0.8629683, 0.8637272, 0.864867, -0.8652833, 0.8630804, -0.8663149, 0.8644526, -0.8631645, 0.8652472, -0.8637288, 0.8644267, 0.8661784, -0.8651684, 0.8656286, 0.8642653, 0.8666206, 0.8662805, -0.8672831]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
