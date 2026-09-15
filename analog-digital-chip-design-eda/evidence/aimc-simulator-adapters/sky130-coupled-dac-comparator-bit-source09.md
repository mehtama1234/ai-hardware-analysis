# Sky130 Coupled DAC And Comparator Bit

- status: `coupled_dac_comparator_all_code_bit_sweep_characterized_not_full_sar_proof`
- measured trials: `16` of `16`
- correct polarity: `16` of `16`

- failing codes: `[]`

## What This Closes

The DAC and comparator are in one SPICE transient. The physical capacitor array produces the top-plate voltage, the comparator's transistor input switches sample that node, and the same preamp/latch resolves the decision. This removes the biggest abstraction in the earlier replay: the comparator no longer receives a numerically injected threshold.

Configuration: direct preamp `False`, top dummy `none`, top-to-VDD resistor `none`.

The working repair removes the source-follower stage that introduced a midrange sign offset and instead samples the physical DAC top plate directly after redistribution. The current long schedule uses a 32/64 um source switch, 4.0 ns acquisition, a 5.0 ns bottom-plate transition, comparator sampling at 9.1-9.6 ns, preamp enable at 9.7 ns, and latch fire at 11.7 ns. This gives the 8 pF MSB time to settle before the decision while preventing the active preamp from loading the DAC during sampling. The all-code sweep is a complete nominal code-level handoff, but it still does not sequence retained bits into a full SAR conversion.

It is still only one bit-cycle boundary. The controller does not yet sequence four physical redistributions, retain bits, or repeat the experiment over PVT and mismatch.

## Results

| code | DAC top after redistribution V | DAC-reference diff V | comparator output diff V | correct polarity |
| ---: | ---: | ---: | ---: | --- |
| 0 | 0.899879 | -0.600121 | 1.434572 | True |
| 1 | 1.019669 | -0.480331 | 1.430213 | True |
| 2 | 1.139467 | -0.360533 | 1.423326 | True |
| 3 | 1.259267 | -0.240733 | 1.412987 | True |
| 4 | 1.378487 | -0.121513 | 1.400326 | True |
| 5 | 1.498267 | -0.001733 | 1.375721 | True |
| 6 | 1.618163 | 0.118163 | -1.387791 | True |
| 7 | 1.736561 | 0.236561 | -1.389396 | True |
| 8 | 1.841334 | 0.341334 | -1.390234 | True |
| 9 | 1.966162 | 0.466162 | -1.391105 | True |
| 10 | 2.089408 | 0.589408 | -1.391990 | True |
| 11 | 2.206989 | 0.706989 | -1.392943 | True |
| 12 | 2.308992 | 0.808992 | -1.393984 | True |
| 13 | 2.364670 | 0.864670 | -1.394803 | True |
| 14 | 2.392305 | 0.892305 | -1.395239 | True |
| 15 | 2.408658 | 0.908658 | -1.395480 | True |

## Refused Claim

does not prove a complete multi-bit SAR, DAC calibration, mismatch/noise yield, PVT closed-loop accuracy, extracted layout, board behavior, or silicon
