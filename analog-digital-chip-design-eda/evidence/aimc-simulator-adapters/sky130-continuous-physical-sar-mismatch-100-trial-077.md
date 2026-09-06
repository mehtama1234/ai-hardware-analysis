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
- cycle DAC values V: `[1.336632, 0.7444148, 0.6224932, 0.8067813]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.13621e-08, 7.019567e-08, 6.970147e-08], [6.834206e-08, 1.8, 6.834329e-08, 6.834353e-08], [6.834298e-08, 6.83438e-08, 1.8, 6.834406e-08], [6.83367e-08, 6.83414e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655328, -0.8643725, -0.8650888, -0.865404, -0.8688402, -0.8648617, 0.863804, -0.8660013, -0.8686657, 0.8643178, -0.8666127, -0.8653655, -0.8687298, 0.8660021, 0.8658227, -0.8666415, -0.8674603, 0.8654769, 0.8668688, 0.8659487]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
