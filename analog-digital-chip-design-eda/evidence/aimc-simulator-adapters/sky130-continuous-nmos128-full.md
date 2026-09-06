# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_failed`
- expected code: `2`
- comparator clear flags: `n/a`
- retained logical bits: `n/a`
- final code: `n/a`
- continuous PMOS/NMOS switch width um: `n/a` / `n/a`
- continuous PMOS bank: `1` parallel device(s)
- dead-time clamp: `False`
- conversion ground precharge: `False` (n/a ns)
- top dummy capacitor: `n/a`
- transient step ps: `20.0`
- conversions measured/required: `0`/`5`
- conversion coverage complete: `False`
- all conversions correct: `False`
- measured: `False`
- cycle DAC values V: `n/a`
- cycle DAC legal range: `False`
- gate legal range: `False`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `n/a`
- comparator differences V: `n/a`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
continuous physical SAR implementation attempt only; no acceptance evidence
