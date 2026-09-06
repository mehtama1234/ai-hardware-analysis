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
- cycle DAC values V: `[0.4578488, 0.8186968, 0.6973818, 0.6424354]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.128867e-08, 7.017012e-08, 6.968753e-08], [1.8, 1.8, 6.296917e-08, 6.436946e-08], [1.8, 6.790116e-08, 1.8, 6.814067e-08], [1.8, 6.822484e-08, 6.827002e-08, 1.8]]`
- comparator differences V: `[-0.8635887, 0.8611237, 0.8630178, 0.863712, 0.8650191, -0.8660583, -0.8636219, 0.8629255, 0.8647392, -0.8648711, 0.8648348, -0.8655128, 0.86487, 0.8659381, -0.8667706, -0.8648383, 0.8644512, 0.8668333, 0.8649943, -0.8681639]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
