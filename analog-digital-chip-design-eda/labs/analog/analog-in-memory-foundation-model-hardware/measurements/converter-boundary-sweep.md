# Converter Boundary Sweep

This sweep asks how many ADC and DAC bits are worth paying for at one analog tile boundary. The object is not converter precision by itself. The object is a measured projection value that must be accurate enough to become model state while cheap enough that analog compute still has a reason to exist.

The sweep uses the same four-output dot product as the tile evidence model and the `100 ohm` SPICE row-wire-drop case. It varies DAC bits, ADC bits, comparator noise, and row settling. It reports relative output error, a simple relative converter-energy estimate, and the SAR comparison count needed for the four output columns.

## Summary

- cases: 216
- useful boundary cases: 42
- SPICE row-drop current loss used: 6.93%
- lowest-energy case: ADC 3, DAC 3, error 0.3889, energy 1.00x
- lowest-error case: ADC 8, DAC 8, error 0.0312, energy 16.00x
- lowest-energy useful case: ADC 6, DAC 4, error 0.0900, energy 3.22x

## Representative Cases

| ADC | DAC | noise | settling | error | energy x | comparisons | useful | interpretation |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 3 | 3 | 0.000 | 1.00 | 0.3889 | 1.00 | 12 | 0 | too much model-facing error |
| 4 | 4 | 0.000 | 1.00 | 0.3796 | 1.00 | 16 | 0 | too much model-facing error |
| 6 | 6 | 0.004 | 1.00 | 0.0900 | 4.00 | 24 | 1 | reasonable converter boundary |
| 8 | 8 | 0.004 | 1.00 | 0.0467 | 16.00 | 32 | 0 | precision costs more than the error reduction justifies |
| 8 | 8 | 0.012 | 0.97 | 0.0467 | 16.00 | 32 | 0 | precision costs more than the error reduction justifies |

## First-Principles Reading

A DAC error happens before the crossbar sums current. One row voltage is shared by many cells, so one wrong row level pushes many output columns together. An ADC error happens after the current sum. It can collapse distinct column currents into the same code or add comparator-noise decisions near code boundaries.

More bits reduce quantization step size, but they do not remove row drop, incomplete settling, comparator noise, or conductance drift. Once those effects dominate, extra bits make the code look more exact without making the underlying measurement more correct. That is why the sweep marks a case useful only when error is inside the model-facing budget and converter cost has not grown far beyond the cheapest low-error boundary.

The concrete design move is to choose converter precision as a tile policy, not as a slogan. The governor should see residual evidence from the actual boundary. The system scheduler should know the energy and latency cost of that boundary. A foundation-model accelerator wins only when the array, converters, correction, calibration, and digital fallback rule all fit the same token budget.
