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
- cycle DAC values V: `[1.342165, 0.7347463, 0.6188804, 0.8004272]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.106456e-08, 7.00559e-08, 6.957848e-08], [6.834114e-08, 1.8, 6.834323e-08, 6.83435e-08], [6.834309e-08, 6.834385e-08, 1.8, 6.834408e-08], [6.833702e-08, 6.83416e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655358, -0.8643295, -0.8650789, -0.8653451, -0.8688442, -0.8646059, 0.8639129, -0.8659394, -0.868678, 0.8644621, -0.866493, -0.8651116, -0.8687523, 0.8659719, 0.8658725, -0.8665214, -0.8676432, 0.8654319, 0.8668648, 0.865942]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
