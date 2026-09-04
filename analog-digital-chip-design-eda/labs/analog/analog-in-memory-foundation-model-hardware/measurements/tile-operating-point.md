# AIMC Tile Operating Point

This file states the measured operating point that the current analog tile and digital governor examples assume. It is generated from the signed-crossbar SPICE proof, row-wire-drop SPICE proof, converter boundary sweep, and analog tile evidence table.

## Selected Boundary

| name | ADC | DAC | row case ohm | row loss % | converter error | converter energy x | SAR comparisons | signed-crossbar error | residual q8 | sensitivity q8 | drift age | governor assumption |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| lowest_energy_useful_converter_boundary | 6 | 4 | 100 | 6.93 | 0.0900 | 3.22 | 24 | 2.979e-16 | 12 | 140 | 4 | eligible for analog service while cumulative state budget remains available |

## First-Principles Reading

An operating point is the smallest honest claim a mixed-signal accelerator can make. It says which physical representation is being used, which converter boundary is being paid for, which wire-loss case is included, and which digital rule will accept or refuse the result.

The signed-crossbar proof says the weight sign is represented by two nonnegative current paths. The row-drop proof says the activation is not the same voltage at every cell. The converter sweep says how much precision is worth paying for before extra bits become expensive decoration. The tile evidence table turns those physical facts into governor inputs.

The concrete design move is to keep this operating point visible. If a later design changes ADC bits, DAC bits, row length, calibration schedule, or signed-weight encoding, this file should change before any performance claim is trusted.
