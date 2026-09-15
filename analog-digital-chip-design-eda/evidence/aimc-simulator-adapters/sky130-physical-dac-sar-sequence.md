# Sky130 Physical DAC SAR Sequence

- status: `physical_dac_sar_sequence_characterized_not_continuous_multicycle_proof`
- conversions: `16`
- comparator trials: `64` of `64` measured
- correct conversions: `11` of `16`

## What Is Physical

This runner performs a real most-significant-bit-first SAR sequence. It proposes a trial code, runs the physical capacitor DAC and transistor comparator together, reads the sign, and retains or clears the trial bit before proposing the next bit. The next decision sees the previous digital code, so this is stronger than replaying one fixed code per row.

Each comparison is currently a fresh transient with the same circuit reset. That preserves physical DAC/comparator behavior for every bit but does not yet prove clock-to-clock state retention inside one continuous SPICE deck. The artifact keeps that boundary explicit.

## Results

| expected code | input V | final code | comparisons | correct |
| ---: | ---: | ---: | ---: | --- |
| 0 | 0.956250 | 0 | 4 | True |
| 1 | 1.068750 | 1 | 4 | True |
| 2 | 1.181250 | 2 | 4 | True |
| 3 | 1.293750 | 3 | 4 | True |
| 4 | 1.406250 | 4 | 4 | True |
| 5 | 1.518750 | 5 | 4 | True |
| 6 | 1.631250 | 6 | 4 | True |
| 7 | 1.743750 | 7 | 4 | True |
| 8 | 1.856250 | 8 | 4 | True |
| 9 | 1.968750 | 9 | 4 | True |
| 10 | 2.081250 | 9 | 4 | False |
| 11 | 2.193750 | 10 | 4 | False |
| 12 | 2.306250 | 11 | 4 | False |
| 13 | 2.418750 | 15 | 4 | False |
| 14 | 2.531250 | 15 | 4 | False |
| 15 | 2.643750 | 15 | 4 | True |

## Refused Claim

does not prove one continuous multi-cycle SPICE deck, full input range, PVT accuracy, random mismatch/noise yield, extracted layout, board behavior, or silicon
