# Transconductance Is Control Gain

Transconductance measures how much output current changes when input voltage changes. It is the local control gain of a transistor.

The object being controlled is the slope between voltage and current:

```text
gm = dIout / dVin
```

This slope matters because many analog circuits work by turning a small voltage change into a current change, then turning that current change back into a voltage across a load or impedance.

The constraint is that the slope is not free. Higher transconductance usually costs bias current, device width, capacitance, or headroom. A designer cannot simply ask for more gain without paying somewhere else.

The concrete design move is choosing device size and bias current. More bias current can increase `gm`, but it increases power. Larger devices can reduce some noise and mismatch, but they add capacitance. More capacitance slows the circuit and can make stability harder.

In a simple common-source amplifier, the small-signal voltage gain is roughly:

```text
Av ~= -gm Rout
```

That expression shows the two sides of the problem. The transistor must convert input voltage into current, and the output node must convert that current into voltage. If either `gm` or output resistance is weak, gain falls.

The measurement is not only gain. You also check bandwidth, distortion, input-referred noise, output swing, and stability. A high `gm` design that cannot swing, settles too slowly, or oscillates is not a good amplifier.

The failure mode is treating transconductance as an isolated device number. In a real circuit, `gm` is connected to capacitance, bias, noise, linearity, and poles. It is useful only inside the full constraint set.

