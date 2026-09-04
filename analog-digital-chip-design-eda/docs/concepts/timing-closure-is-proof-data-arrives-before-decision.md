# Timing Closure Is Proof That Data Arrives Before The Decision

Timing closure is the process of proving that every timed data path meets its deadline. It is the bridge between logical correctness and physical implementation.

The object being controlled is arrival time. A launched value must travel through clock-to-Q delay, combinational gates, wires, and uncertainty before the receiving flip-flop makes its next decision.

The core setup inequality is:

```text
launch clock + clock_to_Q + logic_delay + wire_delay + setup <= capture clock
```

Hold timing checks the opposite danger: the new value must not arrive so quickly that it corrupts the old value during the receiving flip-flop's hold window.

The constraint is that physical design changes timing. Placement changes wire length. Routing changes capacitance and resistance. Buffering fixes one path and may hurt power or congestion. Clock-tree synthesis changes skew. Extraction reveals parasitics that were only estimated earlier.

The concrete design move is repeated repair. The flow resizes cells, inserts buffers, moves cells, adjusts routing, changes constraints, or revises the microarchitecture. Each repair changes the timing graph, so timing closure is an iterative proof, not a single calculation.

The measurement is slack. Positive setup slack means the value arrives before the deadline. Positive hold slack means it does not arrive too early. The design is not closed until the relevant paths pass across process, voltage, temperature, and operating modes.

The failure mode is believing RTL correctness proves chip correctness. RTL can describe the right function while the placed-and-routed chip fails because the physical path cannot deliver the value before the decision.

