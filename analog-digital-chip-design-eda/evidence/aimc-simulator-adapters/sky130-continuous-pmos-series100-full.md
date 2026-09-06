# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[1, 1, 1, 0]`
- retained logical bits: `[0, 0, 0, 1]`
- final code: `1`
- continuous PMOS/NMOS switch width um: `8.0` / `8.0`
- continuous PMOS bank: `1` parallel device(s)
- bottom diode clamp: `False` (area `1.0`)
- dead-time clamp: `False` (width `1.0` um)
- conversion ground precharge: `False` (2.0 ns)
- top dummy capacitor: `0.5p`
- transient step ps: `20.0`
- conversions measured/required: `5`/`5`
- conversion coverage complete: `True`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[0.9992622, 0.6089138, 0.6869633, 0.5876699]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[0.9981724, 0.04451158, 0.02130773, 0.01042991], [0.0720325, 0.3904934, 0.01593664, 0.007865904], [0.02375372, 0.01051663, 1.555016, 0.001786241], [0.00101752, -2.255624e-05, -4.592763e-05, 1.794483]]`
- comparator differences V: `[-0.8744082, -0.8717051, -0.8705228, -0.8677736, -0.8675157, -0.8650674, -0.8650919, 0.8655803, -0.8667419, 0.8660634, -0.8666402, -0.8667904, -0.8653154, 0.8683222, 0.865043, -0.8660057, 0.86677, -0.8748336, -0.8719123, -0.8698756]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
