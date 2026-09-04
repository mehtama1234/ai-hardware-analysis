# Sky130 Transistor DAC Mismatch Sweep

- status: `dac_mismatch_characterized_not_yield_or_sar_proof`
- cases: `4` with codes `(0, 8, 15)`
- measured: `12` of `12`
- timed out: `0`
- half-LSB passes: `4` of `12`
- monotonic cases: `4` of `4`

## What This Tests

The nominal DAC already has transfer error. This run changes one or more capacitor values by a controlled two percent and repeats low, middle, and high codes. It keeps the transistor switches, clocks, and 70 ns read point the same, so the result exposes how sensitive the threshold is to capacitor-ratio error.

The early-to-late number is also retained. A large change means the comparator timing is part of the error; a stable but wrong value points more toward charge ratio or switch conduction than insufficient wait time.

## Results

| case | code | settled error LSB | early-to-late V | half-LSB pass |
| --- | ---: | ---: | ---: | --- |
| matched_nominal | 0 | 0.002 | 0.000000 | True |
| matched_nominal | 8 | 0.534 | 0.175348 | False |
| matched_nominal | 15 | -1.839 | 0.250130 | False |
| msb_plus_2pct | 0 | 0.002 | 0.000000 | True |
| msb_plus_2pct | 8 | 0.613 | 0.181010 | False |
| msb_plus_2pct | 15 | -1.830 | 0.249351 | False |
| lsb_minus_2pct | 0 | 0.002 | 0.000000 | True |
| lsb_minus_2pct | 8 | 0.546 | 0.174940 | False |
| lsb_minus_2pct | 15 | -1.840 | 0.250194 | False |
| alternating_plus_minus_2pct | 0 | 0.002 | 0.000000 | True |
| alternating_plus_minus_2pct | 8 | 0.647 | 0.180649 | False |
| alternating_plus_minus_2pct | 15 | -1.833 | 0.249572 | False |

## Interpretation

This is a controlled sensitivity result, not a statistical yield result. To turn it into a calibration decision, the next run must draw mismatch across every capacitor and switch, repeat every code, and run the resulting thresholds through the closed-loop SAR. A nominal code table cannot represent that distribution.

## Refused Claim

does not prove random mismatch yield, calibration validity, comparator noise, SAR accuracy, extracted layout, board behavior, or silicon
