# Local Converter Circuit Estimate

This file fills the converter evidence contract with local planning numbers. It is useful because every field is explicit. It is not measured evidence.

- status: `local_estimate_complete_not_claim_ready`
- claim-ready to replace break-even: `False`
- ADC bits: `12`
- DAC bits: `10`
- output noise RMS: `0.004`
- rows served: `64`
- columns served: `4`
- outputs sharing converter cost: `16`

## First-Principles Reading

This estimate makes the hidden assumptions visible. The ADC cost is treated as the expensive edge decision. The DAC cost is treated as row-drive work. The latency is split into settling time and comparison time. The area is split into ADC and DAC area. The sharing rule says how many useful outputs pay for one converter cost.

Because the measurement level is still `local_estimate`, this record cannot upgrade the claim. Its value is that a later circuit simulation can replace the same fields without changing the workflow.

## Refused Claim

does not replace break-even assumptions, measured converter energy, post-layout area, silicon noise, or board power
