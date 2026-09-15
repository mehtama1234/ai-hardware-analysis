# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 0, 0, 1]`
- retained logical bits: `[0, 1, 1, 0]`
- final code: `6`
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
- cycle DAC values V: `[0.8456243, 0.3183401, 0.5370595, 0.730179]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.615409, 1.207293e-05, 9.617166e-06, 9.406616e-06], [0.0004314578, 1.61529, -0.0001119876, -9.274289e-05], [2.856652e-05, 1.615407, 1.61541, 3.395882e-06], [5.083845e-05, 1.615399, 1.615406, 1.615407]]`
- comparator differences V: `[-0.7303924, -0.7276828, 0.7287204, 0.7295232, -0.7331559, 0.7305638, 0.7311198, -0.7317784, -0.7331332, 0.7306178, 0.7315903, 0.7320563, -0.7329928, 0.7310634, 0.7324453, 0.7333414, 0.7335144, -0.7362464, -0.7355293, -0.7352983]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
