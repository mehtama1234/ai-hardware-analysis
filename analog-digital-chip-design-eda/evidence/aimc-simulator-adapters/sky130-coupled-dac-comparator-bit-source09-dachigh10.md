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
| 1 | 0.935106 | -0.564894 | 1.433118 | True |
| 2 | 0.944083 | -0.555917 | 1.432772 | True |
| 3 | 0.986666 | -0.513334 | 1.431256 | True |
| 4 | 0.956480 | -0.543520 | 1.432314 | True |
| 5 | 1.007754 | -0.492246 | 1.430421 | True |
| 6 | 1.027581 | -0.472419 | 1.429620 | True |
| 7 | 1.093900 | -0.406100 | 1.425823 | True |
| 8 | 0.986227 | -0.513773 | 1.431211 | True |
| 9 | 1.067886 | -0.432114 | 1.427320 | True |
| 10 | 1.109348 | -0.390652 | 1.424614 | True |
| 11 | 1.235103 | -0.264897 | 1.414048 | True |
| 12 | 1.224850 | -0.275150 | 1.414694 | True |
| 13 | 1.456686 | -0.043314 | 1.387935 | True |
| 14 | 1.736691 | 0.236691 | -1.388861 | True |
| 15 | 1.897324 | 0.397324 | -1.388397 | True |

## Refused Claim

does not prove a complete multi-bit SAR, DAC calibration, mismatch/noise yield, PVT closed-loop accuracy, extracted layout, board behavior, or silicon
