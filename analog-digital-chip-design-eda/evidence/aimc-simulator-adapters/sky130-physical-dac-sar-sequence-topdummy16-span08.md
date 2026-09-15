# Sky130 Physical DAC SAR Sequence

- status: `physical_dac_sar_timeout_smoke`
- conversions: `16`
- comparator trials: `0` of `16` measured
- correct conversions: `0` of `16`

## What Is Physical

This runner performs a real most-significant-bit-first SAR sequence. It proposes a trial code, runs the physical capacitor DAC and transistor comparator together, reads the sign, and retains or clears the trial bit before proposing the next bit. The next decision sees the previous digital code, so this is stronger than replaying one fixed code per row.

Each comparison is currently a fresh transient with the same circuit reset. That preserves physical DAC/comparator behavior for every bit but does not yet prove clock-to-clock state retention inside one continuous SPICE deck. The artifact keeps that boundary explicit.

## Results

| expected code | input V | final code | comparisons | correct |
| ---: | ---: | ---: | ---: | --- |
| 0 | 0.925000 | 0 | 1 | False |
| 1 | 0.975000 | 0 | 1 | False |
| 2 | 1.025000 | 0 | 1 | False |
| 3 | 1.075000 | 0 | 1 | False |
| 4 | 1.125000 | 0 | 1 | False |
| 5 | 1.175000 | 0 | 1 | False |
| 6 | 1.225000 | 0 | 1 | False |
| 7 | 1.275000 | 0 | 1 | False |
| 8 | 1.325000 | 0 | 1 | False |
| 9 | 1.375000 | 0 | 1 | False |
| 10 | 1.425000 | 0 | 1 | False |
| 11 | 1.475000 | 0 | 1 | False |
| 12 | 1.525000 | 0 | 1 | False |
| 13 | 1.575000 | 0 | 1 | False |
| 14 | 1.625000 | 0 | 1 | False |
| 15 | 1.675000 | 0 | 1 | False |

## Refused Claim

does not prove one continuous multi-cycle SPICE deck, full input range, PVT accuracy, random mismatch/noise yield, extracted layout, board behavior, or silicon
