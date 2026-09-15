# Sky130 Coupled DAC And Comparator Bit

- status: `coupled_dac_comparator_all_code_bit_sweep_characterized_not_full_sar_proof`
- measured trials: `12` of `16`
- correct polarity: `12` of `12`

- failing codes: `[]`

## What This Closes

The DAC and comparator are in one SPICE transient. The physical capacitor array produces the top-plate voltage, the comparator's transistor input switches sample that node, and the same preamp/latch resolves the decision. This removes the biggest abstraction in the earlier replay: the comparator no longer receives a numerically injected threshold.

Configuration: direct preamp `False`, top dummy `16p`, top-to-VDD resistor `none`.

The working repair removes the source-follower stage that introduced a midrange sign offset and instead samples the physical DAC top plate directly after redistribution. The current long schedule uses a 32/64 um source switch, 4.0 ns acquisition, a 5.0 ns bottom-plate transition, comparator sampling at 9.1-9.6 ns, preamp enable at 9.7 ns, and latch fire at 11.7 ns. This gives the 8 pF MSB time to settle before the decision while preventing the active preamp from loading the DAC during sampling. The all-code sweep is a complete nominal code-level handoff, but it still does not sequence retained bits into a full SAR conversion.

It is still only one bit-cycle boundary. The controller does not yet sequence four physical redistributions, retain bits, or repeat the experiment over PVT and mismatch.

## Results

| code | DAC top after redistribution V | DAC-reference diff V | comparator output diff V | correct polarity |
| ---: | ---: | ---: | ---: | --- |
| 0 | timeout/error | timeout/error | timeout/error | False |
| 1 | timeout/error | timeout/error | timeout/error | False |
| 2 | timeout/error | timeout/error | timeout/error | False |
| 3 | timeout/error | timeout/error | timeout/error | False |
| 4 | 1.062086 | -0.437914 | 1.428177 | True |
| 5 | 1.090188 | -0.409812 | 1.426513 | True |
| 6 | 1.116358 | -0.383642 | 1.424848 | True |
| 7 | 1.136848 | -0.363152 | 1.423317 | True |
| 8 | 1.179776 | -0.320224 | 1.418571 | True |
| 9 | 1.201216 | -0.298784 | 1.416693 | True |
| 10 | 1.221493 | -0.278507 | 1.414810 | True |
| 11 | 1.236500 | -0.263500 | 1.413347 | True |
| 12 | 1.267154 | -0.232846 | 1.410286 | True |
| 13 | 1.278290 | -0.221710 | 1.409086 | True |
| 14 | 1.289992 | -0.210008 | 1.407795 | True |
| 15 | 1.298664 | -0.201336 | 1.406802 | True |

## Refused Claim

does not prove a complete multi-bit SAR, DAC calibration, mismatch/noise yield, PVT closed-loop accuracy, extracted layout, board behavior, or silicon
