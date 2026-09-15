# Sky130 Coupled DAC And Comparator Bit

- status: `coupled_dac_comparator_all_code_bit_sweep_characterized_not_full_sar_proof`
- measured trials: `16` of `16`
- correct polarity: `16` of `16`

- failing codes: `[]`

## What This Closes

The DAC and comparator are in one SPICE transient. The physical capacitor array produces the top-plate voltage, the comparator's transistor input switches sample that node, and the same preamp/latch resolves the decision. This removes the biggest abstraction in the earlier replay: the comparator no longer receives a numerically injected threshold.

Configuration: direct preamp `False`, top dummy `none`, top-to-VDD resistor `none`.

The working repair removes the source-follower stage that introduced a midrange sign offset and instead samples the physical DAC top plate directly after redistribution. The short schedule samples at 5.1-5.6 ns, enables the preamp at 5.7 ns, and fires the latch at 7.7 ns. This gives the 8 pF MSB time to settle before the decision while preventing the active preamp from loading the DAC during sampling. The all-code sweep is a complete nominal code-level handoff, but it still does not sequence retained bits into a full SAR conversion.

It is still only one bit-cycle boundary. The controller does not yet sequence four physical redistributions, retain bits, or repeat the experiment over PVT and mismatch.

## Results

| code | DAC top after redistribution V | DAC-reference diff V | comparator output diff V | correct polarity |
| ---: | ---: | ---: | ---: | --- |
| 0 | 1.197753 | -0.302247 | 1.418084 | True |
| 1 | 1.316073 | -0.183927 | 1.406419 | True |
| 2 | 1.434214 | -0.065786 | 1.391565 | True |
| 3 | 1.552305 | 0.052305 | -1.384382 | True |
| 4 | 1.670408 | 0.170408 | -1.388496 | True |
| 5 | 1.788537 | 0.288537 | -1.389557 | True |
| 6 | 1.906701 | 0.406701 | -1.390414 | True |
| 7 | 2.021189 | 0.521189 | -1.391406 | True |
| 8 | 2.142024 | 0.642024 | -1.392092 | True |
| 9 | 2.259869 | 0.759869 | -1.393217 | True |
| 10 | 2.373407 | 0.873407 | -1.395387 | True |
| 11 | 2.472595 | 0.972595 | -1.396583 | True |
| 12 | 2.549177 | 1.049177 | -1.396826 | True |
| 13 | 2.579467 | 1.079467 | -1.397168 | True |
| 14 | 2.587374 | 1.087374 | -1.397180 | True |
| 15 | 2.590184 | 1.090184 | -1.397171 | True |

## Refused Claim

does not prove a complete multi-bit SAR, DAC calibration, mismatch/noise yield, PVT closed-loop accuracy, extracted layout, board behavior, or silicon
