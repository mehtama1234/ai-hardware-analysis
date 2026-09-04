# Sky130 Transistor DAC Settling Sweep

- status: `dac_settling_timed_characterization`
- codes: `(8, 15)`
- times ns: `(3, 5, 10, 20, 40, 70)`
- measured cases: `2` of `2`
- half-LSB target V: `5.625000000e-02`

## Why Timing Is Part Of Accuracy

The comparator does not see an abstract DAC code. It sees the top-plate voltage at the instant it makes a decision. This sweep samples the same transistor-switched array at several times after redistribution. If an early sample passes and a late sample fails, the clock is too slow; if no time passes, the transfer function or switch topology must be repaired.

## Results

| code | time ns | top plate V | error LSB | half-LSB pass |
| ---: | ---: | ---: | ---: | --- |
| 8 | 3 | 1.684761 | -1.024 | False |
| 8 | 5 | 1.843548 | 0.387 | True |
| 8 | 10 | 1.860079 | 0.534 | False |
| 8 | 20 | 1.860110 | 0.534 | False |
| 8 | 40 | 1.860110 | 0.534 | False |
| 8 | 70 | 1.860109 | 0.534 | False |
| 15 | 3 | 2.630763 | 0.385 | True |
| 15 | 5 | 2.605509 | 0.160 | True |
| 15 | 10 | 2.560977 | -0.236 | True |
| 15 | 20 | 2.503072 | -0.750 | False |
| 15 | 40 | 2.435266 | -1.353 | False |
| 15 | 70 | 2.380633 | -1.839 | False |

## Interpretation

For this fixture, a faster comparator decision is not a demonstrated fix. The measured early-to-late movement is large, but the static transfer error remains outside the half-LSB target at the representative codes. The SAR must use a measured settle time and a corrected DAC transfer together; either one alone is insufficient.

## Refused Claim

does not prove a full-code calibration, mismatch yield, comparator noise, SAR accuracy, extracted layout, board behavior, or silicon
