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
- cycle DAC values V: `[1.334613, 0.742988, 0.6186352, 0.8017864]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.145191e-08, 7.024491e-08, 6.973316e-08], [6.834226e-08, 1.8, 6.834333e-08, 6.834356e-08], [6.834312e-08, 6.834385e-08, 1.8, 6.834408e-08], [6.833695e-08, 6.834149e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655377, -0.8643608, -0.8650796, -0.8653563, -0.8688384, -0.8647986, 0.8639163, -0.8659579, -0.8686717, 0.8643386, -0.8666066, -0.8653585, -0.8687322, 0.8660012, 0.865794, -0.8667199, -0.8675339, 0.8655162, 0.8668743, 0.8657607]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
