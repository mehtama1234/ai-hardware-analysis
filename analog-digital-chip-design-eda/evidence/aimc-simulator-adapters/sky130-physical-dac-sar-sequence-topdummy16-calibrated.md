# Sky130 Physical DAC SAR Sequence

- status: `physical_dac_sar_full_code_campaign_characterized_not_continuous_multicycle_proof`
- conversions: `16`
- comparator trials: `5` of `21` measured
- correct conversions: `0` of `16`

## What Is Physical

This runner performs a real most-significant-bit-first SAR sequence. It proposes a trial code, runs the physical capacitor DAC and transistor comparator together, reads the sign, and retains or clears the trial bit before proposing the next bit. The next decision sees the previous digital code, so this is stronger than replaying one fixed code per row.

Each comparison is currently a fresh transient with the same circuit reset. That preserves physical DAC/comparator behavior for every bit but does not yet prove clock-to-clock state retention inside one continuous SPICE deck. The artifact keeps that boundary explicit.

## Results

| expected code | input V | final code | comparisons | correct |
| ---: | ---: | ---: | ---: | --- |
| 0 | 0.870991 | 0 | 3 | False |
| 1 | 0.929012 | 0 | 3 | False |
| 2 | 0.987053 | 0 | 1 | False |
| 3 | 1.045089 | 0 | 2 | False |
| 4 | 1.102590 | 0 | 1 | False |
| 5 | 1.160173 | 0 | 1 | False |
| 6 | 1.218332 | 0 | 1 | False |
| 7 | 1.276450 | 0 | 1 | False |
| 8 | 1.308770 | 0 | 1 | False |
| 9 | 1.344071 | 0 | 1 | False |
| 10 | 1.408241 | 0 | 1 | False |
| 11 | 1.471783 | 0 | 1 | False |
| 12 | 1.536115 | 0 | 1 | False |
| 13 | 1.599863 | 0 | 1 | False |
| 14 | 1.661518 | 0 | 1 | False |
| 15 | 1.722751 | 0 | 1 | False |

## Refused Claim

does not prove one continuous multi-cycle SPICE deck, full input range, PVT accuracy, random mismatch/noise yield, extracted layout, board behavior, or silicon
