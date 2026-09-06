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
- cycle DAC values V: `[0.4423486, 0.8051529, 0.6886342, 0.6315481]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.049886e-08, 6.971374e-08, 6.934656e-08], [1.8, 1.8, 6.418757e-08, 6.528595e-08], [1.8, 6.79344e-08, 1.8, 6.815222e-08], [1.8, 6.82475e-08, 6.828261e-08, 1.8]]`
- comparator differences V: `[-0.8634974, 0.8611339, 0.8629583, 0.8636986, 0.8649869, -0.8658702, -0.863291, 0.8632267, 0.8646703, -0.8644994, 0.8649165, -0.8654044, 0.8647483, 0.8660145, -0.8666238, -0.8647645, 0.8643995, 0.8668074, 0.8651509, -0.8681268]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
