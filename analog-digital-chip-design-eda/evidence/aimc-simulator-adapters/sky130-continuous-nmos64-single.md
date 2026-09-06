# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 1, 1, 1]`
- retained logical bits: `[0, 0, 0, 0]`
- final code: `0`
- continuous PMOS/NMOS switch width um: `8.0` / `64.0`
- continuous PMOS bank: `1` parallel device(s)
- dead-time clamp: `False`
- conversion ground precharge: `False` (2.0 ns)
- top dummy capacitor: `0.5p`
- transient step ps: `20.0`
- conversions measured/required: `1`/`5`
- conversion coverage complete: `False`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[1.177845, 0.8076328, 0.7825599, 0.6797446]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.189124, 0.005662776, 0.002805756, 0.001396541], [0.008584623, 0.9400929, 0.002103004, 0.001047965], [0.001476434, 0.0006965115, 1.702929, 0.0001669654], [1.100335e-05, 4.820585e-06, 2.273348e-06, 1.799289]]`
- comparator differences V: `[-0.8753643, -0.8730135, -0.8710963, -0.8690512]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
