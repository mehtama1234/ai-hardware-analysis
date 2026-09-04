# Sky130 Bottom-Switch Scale Sweep

- status: `bottom_switch_scaling_negative_result`
- measured cases: `4` of `4`
- bottom-switch scale: `0.5` of the current candidate
- acquisition: `0.9 V` source, long `4.0 ns` acquisition and `5.0 ns` redistribution schedule

## What Was Tested

The current coupled DAC uses bottom-plate PMOS/NMOS switches sized at `16/8 um`. This control run halves both widths and repeats the difficult high-code region. The question is narrow: are the upper-code thresholds compressed mainly because these bottom switches are too large and load the floating plates?

| code | current width scale top V | half-width top V | change V | polarity |
| ---: | ---: | ---: | ---: | --- |
| 12 | 2.388081 | 2.287187 | -0.100894 | correct |
| 13 | 2.400222 | 2.337996 | -0.062226 | correct |
| 14 | 2.408604 | 2.359495 | -0.049109 | correct |
| 15 | 2.413184 | 2.370848 | -0.042336 | correct |

## Interpretation

The smaller switches preserve sign but make the upper-range voltage lower. They do not restore the missing spacing; code `12` is still only about `50.8 mV` above code `13`, and code `14` is only about `11.4 mV` below code `15`. This rejects “just shrink the bottom switch” as the primary repair. The remaining compression is more consistent with source acquisition, plate initialization, switch topology, supply headroom, and the capacitor/control waveform acting together.

The result is useful because it separates comparator behavior from DAC transfer behavior: all four comparator decisions remain correct while the analog threshold changes materially. The next circuit experiment should change the charge-transfer topology or provide controlled gate headroom, then repeat the same high-code sweep and measure energy and settling cost.

## Refused Claim

This is a four-case nominal sizing comparison. It does not prove an optimum switch width, random mismatch/noise yield, PVT robustness, extracted layout, or silicon behavior.
