# Sky130 Coupled DAC And Comparator Bit

- status: `coupled_dac_comparator_all_code_bit_sweep_characterized_not_full_sar_proof`
- measured trials: `16` of `16`
- correct polarity: `16` of `16`

- failing codes: `[]`

## What This Closes

The DAC and comparator are in one SPICE transient. The physical capacitor array produces the top-plate voltage, the comparator's transistor input switches sample that node, and the same preamp/latch resolves the decision. This removes the biggest abstraction in the earlier replay: the comparator no longer receives a numerically injected threshold.

The working repair removes the source-follower stage that introduced a midrange sign offset and instead samples the physical DAC top plate directly after redistribution. The current long schedule uses a 32/64 um source switch, 4.0 ns acquisition, a 5.0 ns bottom-plate transition, comparator sampling at 9.1-9.6 ns, preamp enable at 9.7 ns, and latch fire at 11.7 ns. This gives the 8 pF MSB time to settle before the decision while preventing the active preamp from loading the DAC during sampling. The all-code sweep is a complete nominal code-level handoff, but it still does not sequence retained bits into a full SAR conversion.

It is still only one bit-cycle boundary. The controller does not yet sequence four physical redistributions, retain bits, or repeat the experiment over PVT and mismatch.

## Results

| code | DAC top after redistribution V | DAC-reference diff V | comparator output diff V | correct polarity |
| ---: | ---: | ---: | ---: | --- |
| 0 | 1.198240 | -0.301760 | 1.418380 | True |
| 1 | 1.316353 | -0.183647 | 1.406722 | True |
| 2 | 1.434289 | -0.065711 | 1.391831 | True |
| 3 | 1.552166 | 0.052166 | -1.384598 | True |
| 4 | 1.670058 | 0.170058 | -1.388784 | True |
| 5 | 1.787958 | 0.287958 | -1.389850 | True |
| 6 | 1.905923 | 0.405923 | -1.390709 | True |
| 7 | 2.006222 | 0.506222 | -1.391519 | True |
| 8 | 2.140388 | 0.640388 | -1.392394 | True |
| 9 | 2.253094 | 0.753094 | -1.393477 | True |
| 10 | 2.332714 | 0.832714 | -1.394756 | True |
| 11 | 2.367011 | 0.867011 | -1.395366 | True |
| 12 | 2.388081 | 0.888081 | -1.395573 | True |
| 13 | 2.400222 | 0.900222 | -1.395701 | True |
| 14 | 2.408604 | 0.908604 | -1.395852 | True |
| 15 | 2.413184 | 0.913184 | -1.396010 | True |

## Refused Claim

does not prove a complete multi-bit SAR, DAC calibration, mismatch/noise yield, PVT closed-loop accuracy, extracted layout, board behavior, or silicon
