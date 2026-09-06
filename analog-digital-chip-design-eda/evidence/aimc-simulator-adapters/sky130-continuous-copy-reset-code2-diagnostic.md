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
- conversions measured/required: `1`/`5`
- conversion coverage complete: `False`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[0.4039399, 0.8665877, 0.6295347, 0.7457105]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.8, 7.61092e-08, 7.178536e-08, 6.99723e-08], [1.800001, 1.799999, 3.95976e-08, 5.455323e-08], [1.8, 6.841593e-08, 1.8, 6.835953e-08], [1.8, 6.769533e-08, 1.8, 1.8]]`
- comparator differences V: `[0.8685556, -0.8701615, 0.8655778, -0.8655358]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
