# A Flip-Flop Is A Timed Memory Decision

A flip-flop stores one bit by making a decision at a clock edge. It is not just a box labeled memory. It is a circuit that samples an input, resolves it, and holds the result for later logic.

The object being controlled is state across time. The input may change many times, but the stored value should change only when the clock says the decision is allowed.

The constraint is that the decision needs time. The input must be stable before the clock edge for setup time and remain stable after the edge for hold time:

```text
data stable before edge >= setup time
data stable after edge >= hold time
```

If those inequalities fail, the storage node may not resolve cleanly. The result can be wrong, delayed, or metastable.

The concrete design move is sequencing. Combinational logic computes a value between clock edges. The flip-flop samples that value at the next edge. The clock period must be long enough for launch, logic delay, wire delay, setup time, and clock uncertainty.

This is why digital chips are timed systems, not just logic systems. The same Boolean function can fail if the path is too slow or if the clock arrives with the wrong skew.

The measurement is setup slack, hold slack, clock-to-Q delay, metastability behavior, and reset behavior. Simulation checks some cases, but static timing analysis checks the timing inequalities over many paths and corners.

The failure mode is thinking memory is only a stored symbol. A flip-flop is a physical decision circuit. If the input arrives too late, too early, or too close to the edge, the symbolic story breaks.

