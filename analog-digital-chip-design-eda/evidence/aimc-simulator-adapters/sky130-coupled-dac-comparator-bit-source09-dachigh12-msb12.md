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
| 0 | 0.899908 | -0.600092 | 1.434571 | True |
| 1 | 0.972325 | -0.527675 | 1.431930 | True |
| 2 | 1.029995 | -0.470005 | 1.429664 | True |
| 3 | 1.105768 | -0.394232 | 1.425496 | True |
| 4 | 1.080312 | -0.419688 | 1.426586 | True |
| 5 | 1.168111 | -0.331889 | 1.420330 | True |
| 6 | 1.253311 | -0.246689 | 1.412628 | True |
| 7 | 1.340841 | -0.159159 | 1.403852 | True |
| 8 | 1.219548 | -0.280452 | 1.414608 | True |
| 9 | 1.368822 | -0.131178 | 1.399264 | True |
| 10 | 1.521690 | 0.021690 | -1.379777 | True |
| 11 | 1.664647 | 0.164647 | -1.388697 | True |
| 12 | 1.810756 | 0.310756 | -1.389951 | True |
| 13 | 1.923615 | 0.423615 | -1.390644 | True |
| 14 | 2.016500 | 0.516500 | -1.391168 | True |
| 15 | 2.097055 | 0.597055 | -1.391741 | True |

## Refused Claim

does not prove a complete multi-bit SAR, DAC calibration, mismatch/noise yield, PVT closed-loop accuracy, extracted layout, board behavior, or silicon
