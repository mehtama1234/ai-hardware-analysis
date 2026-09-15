# Sky130 Coupled DAC And Comparator Bit

- status: `coupled_dac_comparator_all_code_bit_sweep_characterized_not_full_sar_proof`
- measured trials: `16` of `16`
- correct polarity: `16` of `16`

- failing codes: `[]`

## What This Closes

The DAC and comparator are in one SPICE transient. The physical capacitor array produces the top-plate voltage, the comparator's transistor input switches sample that node, and the same preamp/latch resolves the decision. This removes the biggest abstraction in the earlier replay: the comparator no longer receives a numerically injected threshold.

Configuration: direct preamp `False`, top dummy `16p`, top-to-VDD resistor `none`.

The working repair removes the source-follower stage that introduced a midrange sign offset and instead samples the physical DAC top plate directly after redistribution. The current long schedule uses a 32/64 um source switch, 4.0 ns acquisition, a 5.0 ns bottom-plate transition, comparator sampling at 9.1-9.6 ns, preamp enable at 9.7 ns, and latch fire at 11.7 ns. This gives the 8 pF MSB time to settle before the decision while preventing the active preamp from loading the DAC during sampling. The all-code sweep is a complete nominal code-level handoff, but it still does not sequence retained bits into a full SAR conversion.

It is still only one bit-cycle boundary. The controller does not yet sequence four physical redistributions, retain bits, or repeat the experiment over PVT and mismatch.

## Results

| code | DAC top after redistribution V | DAC-reference diff V | comparator output diff V | correct polarity |
| ---: | ---: | ---: | ---: | --- |
| 0 | 0.900011 | -0.599989 | 1.434570 | True |
| 1 | 0.951398 | -0.548602 | 1.432620 | True |
| 2 | 1.002787 | -0.497213 | 1.430847 | True |
| 3 | 1.054154 | -0.445846 | 1.428580 | True |
| 4 | 1.103817 | -0.396183 | 1.425682 | True |
| 5 | 1.155364 | -0.344636 | 1.421935 | True |
| 6 | 1.206974 | -0.293026 | 1.417575 | True |
| 7 | 1.258491 | -0.241509 | 1.412680 | True |
| 8 | 1.309490 | -0.190510 | 1.407396 | True |
| 9 | 1.361050 | -0.138950 | 1.401672 | True |
| 10 | 1.412675 | -0.087325 | 1.395169 | True |
| 11 | 1.464149 | -0.035851 | 1.384775 | True |
| 12 | 1.515818 | 0.015818 | -1.375900 | True |
| 13 | 1.567302 | 0.067302 | -1.386077 | True |
| 14 | 1.618786 | 0.118786 | -1.388026 | True |
| 15 | 1.670243 | 0.170243 | -1.388827 | True |

## Refused Claim

does not prove a complete multi-bit SAR, DAC calibration, mismatch/noise yield, PVT closed-loop accuracy, extracted layout, board behavior, or silicon
