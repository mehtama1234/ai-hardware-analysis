# Sky130 Bottom-Plate Topology Sweep

- status: `single_rail_topology_measured_high_code_spacing_still_inadequate`
- schedule: `long source acquisition`
- tested codes: `12, 13, 14, 15`
- threshold measurement: `9.0 ns`, before comparator switch closure

## Why This Test Exists

The original selected-bit cell turns on a PMOS to `VDD` and an NMOS to ground at the same time. That is a rail-contention topology, not a controlled single-rail redistribution switch. This sweep isolates the two single-rail alternatives.

| topology | code 12 V | code 13 V | code 14 V | code 15 V | code 14-to-15 spacing |
| --- | ---: | ---: | ---: | ---: | ---: |
| PMOS only to VDD, pre-sample rerun | 2.308795 | 2.364526 | 2.392186 | 2.408547 | 16.361 mV |
| both rails simultaneously, historical post-sample read | 2.388081 | 2.400222 | 2.408604 | 2.413184 | 4.580 mV |
| NMOS only to ground, historical post-sample read | 0.895716 | 0.891694 | 0.884766 | 0.827212 | -57.555 mV |

## Interpretation

The NMOS-only branch does not generate the intended high-code output because it pulls selected bottom plates toward ground. The PMOS-only branch is the physically coherent high-side alternative and removes the rail short, but it still leaves the upper ladder compressed: the clean pre-sample code `14→15` spacing is only `16.361 mV`, versus a 4-bit half-LSB of `56.25 mV`. All four PMOS-only comparator decisions preserve polarity, so the remaining failure is threshold formation, not comparator sign.

The earlier both-rail and NMOS-only rows were measured after comparator activity and are not valid DAC threshold measurements. They remain in the artifact only to preserve the debugging history; future acceptance data must use the pre-sample measurement point.

This also changes the status of the prior calibrated `5/5` result: that result was measured with the both-rails candidate and cannot be treated as calibration evidence for PMOS-only. A fresh calibration run must use the selected topology, and the next repair must address capacitor ratios, source acquisition, switch headroom, and control timing together.

## Refused Claim

This is a four-code nominal topology comparison. It does not prove a complete DAC, SAR calibration, PVT robustness, mismatch/noise yield, extracted layout, or silicon.
