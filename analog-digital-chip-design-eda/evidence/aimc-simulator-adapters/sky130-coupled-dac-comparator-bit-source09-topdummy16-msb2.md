# Sky130 Coupled DAC And Comparator Bit

- status: `coupled_dac_comparator_all_code_bit_sweep_characterized_not_full_sar_proof`
- measured trials: `14` of `16`
- correct polarity: `14` of `14`

- failing codes: `[]`

## What This Closes

The DAC and comparator are in one SPICE transient. The physical capacitor array produces the top-plate voltage, the comparator's transistor input switches sample that node, and the same preamp/latch resolves the decision. This removes the biggest abstraction in the earlier replay: the comparator no longer receives a numerically injected threshold.

Configuration: direct preamp `False`, top dummy `16p`, top-to-VDD resistor `none`.

The working repair removes the source-follower stage that introduced a midrange sign offset and instead samples the physical DAC top plate directly after redistribution. The current long schedule uses a 32/64 um source switch, 4.0 ns acquisition, a 5.0 ns bottom-plate transition, comparator sampling at 9.1-9.6 ns, preamp enable at 9.7 ns, and latch fire at 11.7 ns. This gives the 8 pF MSB time to settle before the decision while preventing the active preamp from loading the DAC during sampling. The all-code sweep is a complete nominal code-level handoff, but it still does not sequence retained bits into a full SAR conversion.

It is still only one bit-cycle boundary. The controller does not yet sequence four physical redistributions, retain bits, or repeat the experiment over PVT and mismatch.

## Results

| code | DAC top after redistribution V | DAC-reference diff V | comparator output diff V | correct polarity |
| ---: | ---: | ---: | ---: | --- |
| 0 | 0.900012 | -0.599988 | 1.434570 | True |
| 1 | 0.946389 | -0.553611 | 1.432796 | True |
| 2 | 0.993224 | -0.506776 | 1.431210 | True |
| 3 | 1.039612 | -0.460388 | 1.429303 | True |
| 4 | 1.088932 | -0.411068 | 1.426735 | True |
| 5 | 1.135169 | -0.364831 | 1.423625 | True |
| 6 | 1.181857 | -0.318143 | 1.419937 | True |
| 7 | 1.228238 | -0.271762 | 1.415842 | True |
| 8 | 1.391361 | -0.108639 | 1.392851 | True |
| 9 | 1.459013 | -0.040987 | 1.374337 | True |
| 10 | 1.527508 | 0.027508 | -1.385503 | True |
| 11 | 1.593339 | 0.093339 | -1.388140 | True |
| 12 | 1.664902 | 0.164902 | -1.389093 | True |
| 13 | 1.728150 | 0.228150 | -1.389633 | True |
| 14 | timeout/error | timeout/error | timeout/error | False |
| 15 | timeout/error | timeout/error | timeout/error | False |

## Refused Claim

does not prove a complete multi-bit SAR, DAC calibration, mismatch/noise yield, PVT closed-loop accuracy, extracted layout, board behavior, or silicon
