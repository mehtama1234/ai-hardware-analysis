# DACs Turn Activation Codes Into Row Voltages

The object is a row voltage that stands for a digital activation value. In an analog in-memory compute tile, the stored weights live as conductances, but the input vector must still arrive as voltages on the rows. A DAC is the boundary that turns a number into a physical level. If that level is wrong, every cell on that row multiplies by the wrong input.

The constraint is that a row voltage is shared. One DAC error is not one multiply error. It fans out across every cell that reads that row during that cycle. A small gain error in the DAC scales the whole row. A small offset error adds a bias to every column receiving that row's contribution. Settling error means the row has not reached the requested voltage before the array is sensed.

The mathematical shape is:

```text
x_code -> V_row = gain * quantize(x_code) + offset + settling_error
I_column = sum(G_cell * V_row)
```

This means the DAC error is multiplied by the programmed conductances and summed into many outputs. It is not isolated at the input. The row boundary creates correlated error across output channels.

The concrete design move is to choose activation precision and voltage range together. A wider voltage range can improve separation between codes, but it may increase current, power, device stress, and nonlinearity. A narrower range can save energy but makes each code step smaller and more vulnerable to noise. The DAC bit count must be chosen with the crossbar conductance range, ADC range, and model tolerance.

The measurement is output error versus DAC bits, gain error, offset error, and settling fraction. A useful experiment should show that row-voltage error harms the whole column set, while ADC error appears after summation. Those two errors have different shapes and need different correction.

The failure mode is to count the crossbar as if the input vector arrived perfectly. If DACs are slow, large, or inaccurate, the analog array waits for them or computes with wrong voltages. If the DAC range is poorly matched to activation statistics, many inputs clip or collapse into too few useful levels. The right claim is not that analog compute avoids digital work. It moves the input numbers through a voltage boundary whose cost and error must be counted.
