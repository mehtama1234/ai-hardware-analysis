# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 0, 1, 1]`
- retained logical bits: `[0, 1, 0, 0]`
- final code: `4`
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
- cycle DAC values V: `[1.249459, 0.6586165, 0.8975035, 0.8737387]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 4.473557e-06, 4.473526e-06, 4.473521e-06], [4.47348e-06, 1.8, 4.473481e-06, 4.473481e-06], [4.473471e-06, 1.8, 1.8, 4.473479e-06], [4.473472e-06, 1.8, 4.473479e-06, 1.8]]`
- comparator differences V: `[-1.056973, -1.056996, -1.05686, -1.056514, -1.058601, 1.051485, -1.057295, -1.057038, -1.058507, 1.055681, -1.054594, -1.05178, -1.057913, 1.057033, 1.056407, -1.053943, -1.054819, 1.057442, 1.05736, 1.055634]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
