# Voltage Is A State Variable

Voltage is the number a circuit uses to describe electrical state at a node. It is not the movement itself. It is the difference in electrical potential between that node and a reference.

The object being controlled is node potential. A circuit works only if each important node reaches the intended voltage range at the intended time and stays there long enough for the next circuit to use it.

The constraint is that voltage cannot change for free. A node has capacitance. Changing its voltage means moving charge onto or away from that capacitance. The basic relation is:

```text
Q = C V
```

If the capacitance is larger, the same voltage change requires more charge. If the current is limited, the node changes more slowly. This is why voltage, current, capacitance, and time cannot be understood separately.

The concrete design move is to create a path that charges or discharges the node. In a CMOS inverter, the pMOS device pulls the output node toward the supply, and the nMOS device pulls it toward ground. The output voltage is the result of which path is stronger at that moment.

For analog design, the exact voltage matters. A small unwanted movement can change gain, distortion, headroom, or noise margin. For digital design, the voltage is interpreted through ranges: low enough means zero, high enough means one, and the middle region is dangerous because later gates may not make a reliable decision.

The measurement is not only the final voltage. You also need rise time, fall time, settling error, overshoot, undershoot, and noise margin. These show whether the state reached the right region quickly and cleanly.

The failure mode is treating voltage as an ideal symbol. Real voltage is stored charge under device limits, parasitics, and noise. If the node cannot be moved fast enough, far enough, or quietly enough, the circuit fails even if the schematic logic looks correct.

