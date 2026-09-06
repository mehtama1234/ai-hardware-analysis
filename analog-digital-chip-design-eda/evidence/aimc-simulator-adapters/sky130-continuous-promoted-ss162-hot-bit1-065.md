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
- cycle DAC values V: `[1.272146, 0.649624, 0.8814596, 0.7669895]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.619993, 6.351594e-07, 4.701197e-07, 2.217792e-07], [4.819527e-09, 1.62, 2.099292e-09, 1.97299e-09], [1.430854e-09, 1.62, 1.62, 1.82465e-09], [1.553031e-09, 1.62, 1.794255e-09, 1.62]]`
- comparator differences V: `[-0.9845374, -0.9812144, -0.9810641, -0.9788131, -0.9846248, 0.9753667, -0.9815722, -0.9793873, -0.9845852, 0.9797651, -0.9772611, 0.9790416, -0.9828861, 0.9818151, 0.980899, 0.9795332, -0.9785193, 0.9823634, 0.982341, 0.9816369]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
