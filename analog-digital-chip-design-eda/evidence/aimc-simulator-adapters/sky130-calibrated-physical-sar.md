# Sky130 Calibrated Physical SAR

- status: `calibrated_physical_sar_characterized_not_continuous_multicycle_proof`
- calibration codes measured: `16` of `16`
- physical comparisons: `20` of `20`
- correct conversions: `5` of `5`

- acquisition candidate: `32/64 um source switch with 4.0 ns acquisition and 5.0 ns redistribution`

- bottom-plate topology: `PMOS-only selected connection to VDD`
- DAC threshold measurement: `9.0 ns`, before comparator switch closure

## Calibration Method

The uncalibrated DAC uses binary physical codes, but its measured voltage is not an ideal binary ladder. This runner first measures every physical code at the same source common mode used by the SAR. For each logical code, it chooses the physical code whose measured threshold is closest to the ideal logical threshold. The SAR then retains logical bits while applying the mapped physical trial code to the real DAC.

Calibration is useful only if it is tied to the same source common mode and decision timing as the workload. A table measured at another input level or after comparator activity is not silently reused.

This low-source PMOS-only calibration measures all 16 codes and passes the bounded conversion below. Its threshold range is `0.002633..1.799311 V`; the minimum adjacent spacing is `0.103412 V`, and the legal-range gate is `True`. The logical-to-physical map is injective: `True`. These gates remain separate from the conversion count and prevent a single successful conversion from becoming converter acceptance.

## Results

| expected logical code | input V | final logical code | comparisons | correct |
| ---: | ---: | ---: | ---: | --- |
| 0 | 0.000000 | 0 | 4 | True |
| 2 | 0.302156 | 2 | 4 | True |
| 4 | 0.541228 | 4 | 4 | True |
| 6 | 0.780813 | 6 | 4 | True |
| 7 | 0.892470 | 7 | 4 | True |

## Refused Claim

does not prove calibration across PVT or mismatch/noise, one continuous multi-cycle SPICE state machine, extracted layout, board behavior, or silicon
