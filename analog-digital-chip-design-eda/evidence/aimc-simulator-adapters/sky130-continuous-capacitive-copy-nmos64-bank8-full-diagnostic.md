# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 1, 0, 0]`
- retained logical bits: `[0, 0, 1, 1]`
- final code: `3`
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
- cycle DAC values V: `[1.321516, 0.8535939, 0.6239024, 0.7446026]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.8, 7.748652e-08, 7.239489e-08, 7.026047e-08], [6.894744e-08, 1.8, 6.842825e-08, 6.838337e-08], [6.834603e-08, 6.834517e-08, 1.8, 6.834452e-08], [6.834264e-08, 6.834347e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8650408, -0.8649932, -0.8657017, 0.8638655, -0.8662257, -0.8646251, 0.8668519, 0.8662769, -0.865704, 0.8654702, 0.8650289, -0.8649747, -0.8651643, 0.8677593, 0.8667293, 0.8659768, 0.8654452, -0.8684692, -0.8668896, -0.8655064]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
