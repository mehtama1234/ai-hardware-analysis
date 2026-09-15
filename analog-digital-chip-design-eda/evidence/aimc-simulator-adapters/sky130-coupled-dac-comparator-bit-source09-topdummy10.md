# Sky130 Coupled DAC And Comparator Bit

- status: `coupled_dac_comparator_all_code_bit_sweep_characterized_not_full_sar_proof`
- measured trials: `16` of `16`
- correct polarity: `16` of `16`

- failing codes: `[]`

## What This Closes

The DAC and comparator are in one SPICE transient. The physical capacitor array produces the top-plate voltage, the comparator's transistor input switches sample that node, and the same preamp/latch resolves the decision. This removes the biggest abstraction in the earlier replay: the comparator no longer receives a numerically injected threshold.

Configuration: direct preamp `False`, top dummy `10p`, top-to-VDD resistor `none`.

The working repair removes the source-follower stage that introduced a midrange sign offset and instead samples the physical DAC top plate directly after redistribution. The current long schedule uses a 32/64 um source switch, 4.0 ns acquisition, a 5.0 ns bottom-plate transition, comparator sampling at 9.1-9.6 ns, preamp enable at 9.7 ns, and latch fire at 11.7 ns. This gives the 8 pF MSB time to settle before the decision while preventing the active preamp from loading the DAC during sampling. The all-code sweep is a complete nominal code-level handoff, but it still does not sequence retained bits into a full SAR conversion.

It is still only one bit-cycle boundary. The controller does not yet sequence four physical redistributions, retain bits, or repeat the experiment over PVT and mismatch.

## Results

| code | DAC top after redistribution V | DAC-reference diff V | comparator output diff V | correct polarity |
| ---: | ---: | ---: | ---: | --- |
| 0 | 0.899979 | -0.600021 | 1.434571 | True |
| 1 | 0.971908 | -0.528092 | 1.431932 | True |
| 2 | 1.043851 | -0.456149 | 1.429089 | True |
| 3 | 1.115833 | -0.384167 | 1.424968 | True |
| 4 | 1.186849 | -0.313151 | 1.419369 | True |
| 5 | 1.258909 | -0.241091 | 1.412732 | True |
| 6 | 1.330955 | -0.169045 | 1.405238 | True |
| 7 | 1.402972 | -0.097028 | 1.396738 | True |
| 8 | 1.428243 | -0.071757 | 1.390463 | True |
| 9 | 1.507493 | 0.007493 | -1.376663 | True |
| 10 | 1.586658 | 0.086658 | -1.387347 | True |
| 11 | 1.663984 | 0.163984 | -1.388827 | True |
| 12 | 1.744864 | 0.244864 | -1.389581 | True |
| 13 | 1.820085 | 0.320085 | -1.390148 | True |
| 14 | 1.895085 | 0.395085 | -1.390678 | True |
| 15 | 1.969262 | 0.469262 | -1.391201 | True |

## Refused Claim

does not prove a complete multi-bit SAR, DAC calibration, mismatch/noise yield, PVT closed-loop accuracy, extracted layout, board behavior, or silicon
