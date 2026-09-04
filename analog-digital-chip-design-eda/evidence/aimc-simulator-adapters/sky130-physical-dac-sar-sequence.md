# Sky130 Physical DAC SAR Sequence

- status: `physical_dac_sar_sequence_characterized_not_continuous_multicycle_proof`
- conversions: `5`
- comparator trials: `20` of `20` measured
- correct conversions: `0` of `5`

## What Is Physical

This runner performs a real most-significant-bit-first SAR sequence. It proposes a trial code, runs the physical capacitor DAC and transistor comparator together, reads the sign, and retains or clears the trial bit before proposing the next bit. The next decision sees the previous digital code, so this is stronger than replaying one fixed code per row.

Each comparison is currently a fresh transient with the same circuit reset. That preserves physical DAC/comparator behavior for every bit but does not yet prove clock-to-clock state retention inside one continuous SPICE deck. The artifact keeps that boundary explicit.

## Results

| expected code | input V | final code | comparisons | correct |
| ---: | ---: | ---: | ---: | --- |
| 0 | 0.956250 | 5 | 4 | False |
| 2 | 1.181250 | 8 | 4 | False |
| 4 | 1.406250 | 10 | 4 | False |
| 6 | 1.631250 | 13 | 4 | False |
| 7 | 1.743750 | 14 | 4 | False |

## Refused Claim

does not prove one continuous multi-cycle SPICE deck, full input range, PVT accuracy, random mismatch/noise yield, extracted layout, board behavior, or silicon
