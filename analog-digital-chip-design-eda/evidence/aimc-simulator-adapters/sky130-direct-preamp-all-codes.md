# Sky130 Coupled DAC And Comparator Bit

- status: `coupled_dac_comparator_all_code_bit_sweep_characterized_not_full_sar_proof`
- measured trials: `15` of `16`
- correct polarity: `12` of `15`

- failing codes: `[1, 2, 4]`

## What This Closes

The DAC and comparator are in one SPICE transient. The physical capacitor array produces the top-plate voltage, the comparator's transistor input switches sample that node, and the same preamp/latch resolves the decision. This removes the biggest abstraction in the earlier replay: the comparator no longer receives a numerically injected threshold.

The working repair removes the source-follower stage that introduced a midrange sign offset and instead samples the physical DAC top plate directly after redistribution. The current long schedule uses a 32/64 um source switch, 4.0 ns acquisition, a 5.0 ns bottom-plate transition, comparator sampling at 9.1-9.6 ns, preamp enable at 9.7 ns, and latch fire at 11.7 ns. This gives the 8 pF MSB time to settle before the decision while preventing the active preamp from loading the DAC during sampling. The all-code sweep is a complete nominal code-level handoff, but it still does not sequence retained bits into a full SAR conversion.

It is still only one bit-cycle boundary. The controller does not yet sequence four physical redistributions, retain bits, or repeat the experiment over PVT and mismatch.

## Results

| code | DAC top after redistribution V | DAC-reference diff V | comparator output diff V | correct polarity |
| ---: | ---: | ---: | ---: | --- |
| 0 | timeout/error | timeout/error | timeout/error | False |
| 1 | 1.351042 | -0.148958 | -1.393624 | False |
| 2 | 1.416447 | -0.083553 | -1.379798 | False |
| 3 | 1.599733 | 0.099733 | -1.364383 | True |
| 4 | 1.476255 | -0.023745 | -1.362677 | False |
| 5 | 1.725780 | 0.225780 | -1.361817 | True |
| 6 | 2.027502 | 0.527502 | -1.363155 | True |
| 7 | 2.327248 | 0.827248 | -1.363784 | True |
| 8 | 1.528820 | 0.028820 | -1.358943 | True |
| 9 | 1.806605 | 0.306605 | -1.358314 | True |
| 10 | 2.091003 | 0.591003 | -1.358166 | True |
| 11 | 2.368381 | 0.868381 | -1.358614 | True |
| 12 | 2.273989 | 0.773989 | -1.355336 | True |
| 13 | 2.455562 | 0.955562 | -1.355936 | True |
| 14 | 2.625294 | 1.125294 | -1.357858 | True |
| 15 | 2.683882 | 1.183882 | -1.358403 | True |

## Refused Claim

does not prove a complete multi-bit SAR, DAC calibration, mismatch/noise yield, PVT closed-loop accuracy, extracted layout, board behavior, or silicon
