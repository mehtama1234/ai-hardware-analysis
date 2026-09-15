# Sky130 Coupled DAC And Comparator Bit

- status: `coupled_dac_comparator_bit_incomplete`
- measured trials: `0` of `16`
- correct polarity: `0` of `0`

- failing codes: `[]`

## What This Closes

The DAC and comparator are in one SPICE transient. The physical capacitor array produces the top-plate voltage, the comparator's transistor input switches sample that node, and the same preamp/latch resolves the decision. This removes the biggest abstraction in the earlier replay: the comparator no longer receives a numerically injected threshold.

Configuration: direct preamp `False`, top dummy `none`, top-to-VDD resistor `none`.

The working repair removes the source-follower stage that introduced a midrange sign offset and instead samples the physical DAC top plate directly after redistribution. The short schedule samples at 5.1-5.6 ns, enables the preamp at 5.7 ns, and fires the latch at 7.7 ns. This gives the 8 pF MSB time to settle before the decision while preventing the active preamp from loading the DAC during sampling. The all-code sweep is a complete nominal code-level handoff, but it still does not sequence retained bits into a full SAR conversion.

It is still only one bit-cycle boundary. The controller does not yet sequence four physical redistributions, retain bits, or repeat the experiment over PVT and mismatch.

## Results

| code | DAC top after redistribution V | DAC-reference diff V | comparator output diff V | correct polarity |
| ---: | ---: | ---: | ---: | --- |
| 0 | timeout/error | timeout/error | timeout/error | False |
| 1 | timeout/error | timeout/error | timeout/error | False |
| 2 | timeout/error | timeout/error | timeout/error | False |
| 3 | timeout/error | timeout/error | timeout/error | False |
| 4 | timeout/error | timeout/error | timeout/error | False |
| 5 | timeout/error | timeout/error | timeout/error | False |
| 6 | timeout/error | timeout/error | timeout/error | False |
| 7 | timeout/error | timeout/error | timeout/error | False |
| 8 | timeout/error | timeout/error | timeout/error | False |
| 9 | timeout/error | timeout/error | timeout/error | False |
| 10 | timeout/error | timeout/error | timeout/error | False |
| 11 | timeout/error | timeout/error | timeout/error | False |
| 12 | timeout/error | timeout/error | timeout/error | False |
| 13 | timeout/error | timeout/error | timeout/error | False |
| 14 | timeout/error | timeout/error | timeout/error | False |
| 15 | timeout/error | timeout/error | timeout/error | False |

## Refused Claim

does not prove a complete multi-bit SAR, DAC calibration, mismatch/noise yield, PVT closed-loop accuracy, extracted layout, board behavior, or silicon
