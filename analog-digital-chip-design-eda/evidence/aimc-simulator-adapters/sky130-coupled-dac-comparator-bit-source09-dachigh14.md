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
| 1 | 0.993059 | -0.506941 | 1.431217 | True |
| 2 | 1.086130 | -0.413870 | 1.426891 | True |
| 3 | 1.179289 | -0.320711 | 1.420207 | True |
| 4 | 1.249407 | -0.250593 | 1.413328 | True |
| 5 | 1.348104 | -0.151896 | 1.403308 | True |
| 6 | 1.446778 | -0.053222 | 1.390465 | True |
| 7 | 1.542623 | 0.042623 | -1.381545 | True |
| 8 | 1.505756 | 0.005756 | -1.379282 | True |
| 9 | 1.644084 | 0.144084 | -1.388606 | True |
| 10 | 1.775637 | 0.275637 | -1.389762 | True |
| 11 | 1.889495 | 0.389495 | -1.390550 | True |
| 12 | 2.007764 | 0.507764 | -1.391298 | True |
| 13 | 2.105224 | 0.605224 | -1.392000 | True |
| 14 | 2.198761 | 0.698761 | -1.392705 | True |
| 15 | 2.274761 | 0.774761 | -1.393495 | True |

## Refused Claim

does not prove a complete multi-bit SAR, DAC calibration, mismatch/noise yield, PVT closed-loop accuracy, extracted layout, board behavior, or silicon
