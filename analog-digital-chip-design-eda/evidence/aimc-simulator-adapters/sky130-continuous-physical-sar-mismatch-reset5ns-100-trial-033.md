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
- cycle DAC values V: `[0.4417604, 0.8079664, 0.6905014, 0.6270541]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.085364e-08, 6.993924e-08, 6.947177e-08], [1.8, 1.8, 6.359269e-08, 6.496538e-08], [1.8, 6.785159e-08, 1.8, 6.81212e-08], [1.8, 6.826108e-08, 6.829127e-08, 1.8]]`
- comparator differences V: `[-0.8635004, 0.8611224, 0.8629518, 0.863695, 0.8649831, -0.8659039, -0.8633554, 0.8633692, 0.8646698, -0.8645879, 0.8648993, -0.8653643, 0.8648243, 0.8659961, -0.8667316, -0.8647667, 0.8644025, 0.8668118, 0.8650251, -0.868146]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
