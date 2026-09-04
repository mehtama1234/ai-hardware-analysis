# SPICE Row-Wire-Drop Comparison

This report compares a row-wire crossbar SPICE run against two hand calculations: the ideal no-drop current and a distributed row-resistance model.

The ideal model assumes every cell sees the driver voltage:

```text
I_ideal = V_in / R_cell1 + V_in / R_cell2 + V_in / R_cell3 + V_in / R_cell4
```

The distributed model solves the row tap voltages first, then sums `V_tap / R_cell` at each tap.

Worst current loss versus the ideal no-drop model: `26.63%`.
Worst relative difference between ngspice and the distributed row model: `1.978e-07`.

## Comparison

| rseg ohm | v(n1) | v(n2) | v(n3) | v(n4) | SPICE current A | ideal current A | distributed current A | ideal current loss % | model relative error |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 25 | 0.792147 | 0.786274 | 0.782367 | 0.780416 | 3.141205000e-04 | 3.200000000e-04 | 3.141205054e-04 | 1.84 | 1.734e-08 |
| 100 | 0.770218 | 0.748139 | 0.733541 | 0.726278 | 2.978175000e-04 | 3.200000000e-04 | 2.978175146e-04 | 6.93 | 4.892e-08 |
| 500 | 0.682601 | 0.599331 | 0.546029 | 0.520027 | 2.347988000e-04 | 3.200000000e-04 | 2.347987536e-04 | 26.63 | 1.978e-07 |

## First-Principles Reading

The ideal crossbar formula treats row voltage as a shared fact. Row-wire resistance makes that false. Current leaves the row at each cell, and that current causes voltage drop along the metal before the next cell is reached. The cells farther from the driver therefore see a smaller activation.

This is why analog in-memory compute needs a physical error model. The mathematical dot product assumes one activation value per row. The circuit gives different effective activations along the row. The governor later sees the result as residual error, but the cause starts here: charge movement through nonzero wire resistance changes the value being multiplied.
