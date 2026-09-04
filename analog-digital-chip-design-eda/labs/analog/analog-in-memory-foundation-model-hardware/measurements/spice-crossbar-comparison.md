# SPICE Crossbar Comparison

This report compares the current printed by ngspice for the four-by-four resistive crossbar against the first-principles conductance sum.

The object is one column current:

```text
I_column = V_row1 / R_row1_column + V_row2 / R_row2_column + ...
```

The zero-volt sense source holds the column at virtual ground, so each resistor current is set by row voltage divided by cell resistance.

Worst relative difference between ngspice and the direct conductance sum: `5.483e-08`.

## Comparison

| column | SPICE current A | conductance sum A | abs error A | relative error |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 6.145833000e-05 | 6.145833333e-05 | 3.333e-12 | 5.424e-08 |
| 2 | 8.105556000e-05 | 8.105555556e-05 | 4.444e-12 | 5.483e-08 |
| 3 | 5.712121000e-05 | 5.712121212e-05 | 2.121e-12 | 3.714e-08 |
| 4 | 6.111111000e-05 | 6.111111111e-05 | 1.111e-12 | 1.818e-08 |

## First-Principles Reading

This is the smallest useful analog in-memory compute claim. A conductance stores a weight as `1/R`. A row voltage carries an activation. A column current is the sum of the branch currents. SPICE is solving the same circuit equations that the direct conductance sum writes down by hand.

The later Python tile models add programming error, drift, converter quantization, row drop, calibration, and governor decisions. This comparison anchors those models to the base physical operation: weighted current summation at a virtual-ground column.
