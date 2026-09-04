# Sky130 Coupled Comparator Sample-Capacitance Sweep

This sweep varies only the comparator sample capacitance while keeping the physical DAC, transistor switches, and late sampling schedule fixed. It tests whether DAC loading and decision resolution trade against each other.

| sample capacitance | code | DAC top V | DAC-reference diff V | preamp diff V | measured |
| --- | ---: | ---: | ---: | --- | --- |
| 0.2p | 14 | 1.680679 | 0.680679 | 1.047128 | True |
| 0.2p | 15 | 2.081689 | 1.081689 | 1.150851 | True |
| 0.02p | 14 | 1.999598 | 0.999598 | 1.034666 | True |
| 0.02p | 15 | 2.096115 | 1.096115 | 1.053206 | True |
| 0.002p | 14 | 1.689434 | 0.689434 | 1.031763 | True |
| 0.002p | 15 | 1.776002 | 0.776002 | 1.047385 | True |

## Interpretation

The result is not monotonic with capacitance. A smaller sample capacitor reduces direct charge sharing but also changes the transient settling and the amount of charge available to the comparator input storage. The value must therefore be selected with a full timing, code, PVT, mismatch, and noise sweep rather than by one full-scale number.

## Refused Claim

does not prove optimal sizing, full SAR accuracy, mismatch/noise yield, extracted layout, board behavior, or silicon
