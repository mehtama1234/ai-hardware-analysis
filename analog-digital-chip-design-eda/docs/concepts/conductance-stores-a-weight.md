# Conductance Stores A Weight

The object is conductance: the ease with which a device lets current pass when a voltage is placed across it. In a digital memory cell the stored bit is read as a symbol. In analog in-memory compute the stored value is read as a physical slope. If the voltage is the input and the current is the output, the cell is acting like a multiplier because `I = G * V`. The weight is not a number sitting beside the compute unit. The weight is the device response itself.

The constraint is that a device is not an ideal real number. It has a minimum conductance, maximum conductance, programming error, read noise, drift, temperature dependence, and finite endurance. A neural network weight can be positive or negative, but one passive conductance is usually nonnegative. A common concrete design move is therefore to represent one signed weight with two devices or two columns: one stores the positive part and one stores the negative part. The circuit subtracts the two currents after reading. That turns signed arithmetic into a difference of physical currents.

The mathematical shape is simple before the nonidealities enter:

```text
y = Gx
```

For one cell:

```text
I = G * V
```

For a programmed device:

```text
G_actual = G_target + programming_error + drift + noise
```

So the real operation is not `I = G_target V`. It is `I = G_actual V`, and the gap between target and actual becomes model error. This is why analog memory compute must be read as a controlled approximation, not as a free matrix multiply.

The concrete design move is to choose a conductance range and mapping rule. A digital weight is scaled into a target conductance range. The programmer pulses the device until the measured conductance is close enough. The runtime circuit then applies voltages and reads currents. Calibration measures systematic column or device error and stores correction factors in digital memory. The analog part performs the cheap physical multiplication; the digital part remembers what the analog part actually became.

The measurement is not only top-1 accuracy or tokens per second. The first measurement is conductance error: target versus measured conductance after programming. The second is read stability: repeated reads of the same input. The third is drift: how the conductance changes over time. The fourth is model-level damage: how much the layer output changes after the weight matrix is replaced by its physical approximation.

The failure mode is pretending the programmed cell is the requested weight. If the conductance range is too narrow, weights collapse into too few distinguishable levels. If the range is too wide, small weights are hard to represent and large currents stress the array. If drift is not measured, yesterday's weight is not today's weight. If signed weights are mapped poorly, subtraction doubles noise. The device can store a weight only when the architecture also stores the evidence that the physical slope is close enough for the model computation using it.
