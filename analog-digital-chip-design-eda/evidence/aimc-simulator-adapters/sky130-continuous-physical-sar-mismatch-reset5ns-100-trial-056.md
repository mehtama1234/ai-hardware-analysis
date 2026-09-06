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
- cycle DAC values V: `[1.335664, 0.7409815, 0.620482, 0.8049589]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.166336e-08, 7.040321e-08, 6.985315e-08], [6.834231e-08, 1.8, 6.834333e-08, 6.834356e-08], [6.834305e-08, 6.834383e-08, 1.8, 6.834407e-08], [6.833675e-08, 6.834144e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655374, -0.8643511, -0.86508, -0.8653691, -0.8688366, -0.8647529, 0.8638703, -0.8660012, -0.8686729, 0.8643726, -0.8665995, -0.8653528, -0.8687357, 0.8659968, 0.8657946, -0.8667459, -0.867576, 0.8655073, 0.8668744, 0.8657254]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
