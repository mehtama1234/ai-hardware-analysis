# Sky130 Coupled DAC And Comparator Bit

- status: `coupled_dac_comparator_all_code_bit_sweep_characterized_not_full_sar_proof`
- measured trials: `16` of `16`
- correct polarity: `16` of `16`

- failing codes: `[]`

## What This Closes

The DAC and comparator are in one SPICE transient. The physical capacitor array produces the top-plate voltage, the comparator's transistor input switches sample that node, and the same preamp/latch resolves the decision. This removes the biggest abstraction in the earlier replay: the comparator no longer receives a numerically injected threshold.

Configuration: direct preamp `False`, top dummy `16p`, top-to-VDD resistor `none`.

The working repair removes the source-follower stage that introduced a midrange sign offset and instead samples the physical DAC top plate directly after redistribution. The current long schedule uses a 32/64 um source switch, 4.0 ns acquisition, a 5.0 ns bottom-plate transition, comparator sampling at 9.1-9.6 ns, preamp enable at 9.7 ns, and latch fire at 11.7 ns. This gives the 8 pF MSB time to settle before the decision while preventing the active preamp from loading the DAC during sampling. The all-code sweep is a complete nominal code-level handoff, but it still does not sequence retained bits into a full SAR conversion.

It is still only one bit-cycle boundary. The controller does not yet sequence four physical redistributions, retain bits, or repeat the experiment over PVT and mismatch.

## Results

| code | DAC top after redistribution V | DAC-reference diff V | comparator output diff V | correct polarity |
| ---: | ---: | ---: | ---: | --- |
| 0 | 0.900002 | -0.599998 | 1.434570 | True |
| 1 | 0.958022 | -0.541978 | 1.432397 | True |
| 2 | 1.016084 | -0.483916 | 1.430330 | True |
| 3 | 1.074094 | -0.425906 | 1.427526 | True |
| 4 | 1.131085 | -0.368915 | 1.423792 | True |
| 5 | 1.189261 | -0.310739 | 1.419219 | True |
| 6 | 1.247403 | -0.252597 | 1.413813 | True |
| 7 | 1.305496 | -0.194504 | 1.407900 | True |
| 8 | 1.312044 | -0.187956 | 1.405650 | True |
| 9 | 1.376098 | -0.123902 | 1.398374 | True |
| 10 | 1.440384 | -0.059616 | 1.388249 | True |
| 11 | 1.503181 | 0.003181 | -1.374828 | True |
| 12 | 1.569049 | 0.069049 | -1.386674 | True |
| 13 | 1.630677 | 0.130677 | -1.388375 | True |
| 14 | 1.692359 | 0.192359 | -1.389139 | True |
| 15 | 1.753144 | 0.253144 | -1.389662 | True |

## Refused Claim

does not prove a complete multi-bit SAR, DAC calibration, mismatch/noise yield, PVT closed-loop accuracy, extracted layout, board behavior, or silicon
