# SPICE Signed Crossbar Comparison

This report checks the differential signed-weight crossbar. A passive conductance cannot be negative, so a signed weight is represented by two nonnegative paths. The positive path carries the positive part of the weight. The negative path carries the magnitude of the negative part. The signed result is the positive column current minus the negative column current.

The object is a signed dot product made from physical currents:

```text
I_signed = I_positive - I_negative
I_expected = gscale * sum(row_voltage_i * signed_weight_i)
```

Worst relative difference between ngspice and the signed dot-product equation: `2.979e-16`.

## Comparison

| column | positive current A | negative current A | SPICE signed A | expected signed A | signed dot | abs error A | relative error |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 3.500000000e-05 | 7.500001000e-06 | 2.750000000e-05 | 2.750000000e-05 | 0.275000 | 0.000e+00 | 0.000e+00 |
| 2 | 5.750000000e-05 | 1.200000000e-05 | 4.550000000e-05 | 4.550000000e-05 | 0.455000 | 1.355e-20 | 2.979e-16 |

## First-Principles Reading

The unsigned crossbar proves current summation. The signed crossbar adds one more physical boundary: sign is not stored as negative conductance. It is stored as a difference between two ordinary conductance networks. That means a foundation-model weight is not only mapped into a cell value. It is mapped into a representation rule.

This matters because subtraction is not free. The two paths can have different mismatch, drift, wire drop, and readout error. A signed analog projection is correct only if the positive and negative currents are both measured well enough and the subtraction keeps the difference within the model's error budget.

The concrete design move is to expose the signed split before claiming transformer acceleration. A useful analog tile report should say how signed weights are encoded, how positive and negative currents are sensed, where subtraction happens, and how mismatch between the two halves enters the governor evidence.
