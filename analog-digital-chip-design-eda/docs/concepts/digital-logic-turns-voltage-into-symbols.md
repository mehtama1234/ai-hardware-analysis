# Digital Logic Turns Voltage Into Symbols

Digital logic is not separate from analog behavior. It is an agreement to interpret voltage ranges as symbols.

The object being controlled is a decision boundary. A receiving gate must decide whether an input voltage means zero or one. The circuit is reliable when valid low and high ranges are separated by enough margin.

The constraint is that real signals do not jump instantly between perfect values. They rise and fall through intermediate voltages. They see noise, supply droop, crosstalk, process variation, and load capacitance.

The mathematical shape is a transfer curve. For an inverter, the output voltage is a function of the input voltage:

```text
Vout = f(Vin)
```

The useful digital behavior comes from the steep middle of this curve and the stable ends. Small input changes near the switching threshold can cause large output changes. That is what makes restoration possible: a weak or noisy input can become a clean output if it is still inside the allowed range.

The concrete design move is choosing device strengths and thresholds so the gate has noise margin, drive strength, and acceptable delay. The pMOS and nMOS networks must pull the output hard enough toward valid rails under load.

The measurement is noise margin, propagation delay, transition time, power, and logical correctness across corners. A Boolean truth table is not enough because it ignores whether the voltage decision arrives in time and survives noise.

The failure mode is treating bits as abstract values too early. Every bit on a chip is carried by voltage on capacitance through imperfect devices and wires. Digital design works because the circuit repeatedly restores messy voltages into allowed symbolic ranges.

