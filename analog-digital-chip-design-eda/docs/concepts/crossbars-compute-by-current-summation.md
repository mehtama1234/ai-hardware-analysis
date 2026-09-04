# Crossbars Compute By Current Summation

The object is a column current. A crossbar array has row wires, column wires, and devices at their intersections. Each device has a programmed conductance. When input voltages are placed on the rows, every device on a column contributes a current. Those currents meet on the same column wire, so the wire sums them by charge conservation. The dot product is not assembled by an instruction stream. It appears as a physical current.

For one column, the ideal equation is:

```text
I_column = G_1 V_1 + G_2 V_2 + ... + G_n V_n
```

That is the same mathematical form as a matrix-vector multiply. The row voltages are the vector. The conductance matrix is the weight matrix. The column currents are the output vector. This is the reason analog in-memory compute is tempting for foundation models: transformers spend much of their time applying large learned matrices to activation vectors.

The constraint is that the summing wire is also a physical object. It has resistance, capacitance, voltage drop, settling time, thermal noise, and finite current capacity. A larger array gives more reuse because many weights are read at once, but it also makes the column and row wires worse. The simple dot product equation assumes every cell sees the voltage we intended and every current reaches the sense circuit unchanged. Real arrays violate both assumptions.

The concrete design move is tiling. Instead of building one enormous crossbar, the matrix is cut into smaller arrays. Each tile computes a partial sum. Digital or mixed-signal accumulation combines the partial sums. Tiling gives up some analog density so that row voltage error, column current range, and settling time remain bounded. Another concrete move is bit slicing. A high-precision weight is split across several lower-precision cells or several cycles. That improves representation but increases conversion and accumulation work.

The measurement is output error as a function of array size, input scale, conductance spread, line resistance, and ADC precision. A useful lab does not only show that `Gx` works for four cells. It asks when the dot product stops looking like the intended dot product. Sweep the array from small to large. Sweep input amplitude. Add random conductance error. Add a column gain error. Then compare the analog current vector against the ideal matrix-vector result.

The failure mode is counting the column sum but ignoring the boundary around it. A crossbar can sum currents beautifully and still be a bad accelerator if the DACs feeding the rows, ADCs reading the columns, digital scaling, calibration, and data movement cost more than the saved multiply-adds. The first-principles lesson is that the crossbar computes one narrow thing: weighted current summation. A foundation-model accelerator needs that current sum to land inside a larger digital schedule without destroying precision, latency, energy, or correctness.
