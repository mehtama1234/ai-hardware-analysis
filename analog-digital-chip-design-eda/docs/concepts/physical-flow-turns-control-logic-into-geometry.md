# Physical Flow Turns Control Logic Into Geometry

The object is a clocked digital decision becoming placed and routed silicon geometry. In the AIMC control-plane case, the decision is small: choose digital fallback, analog projection, or batched analog decode, then emit a reason code. But even a small controller is not a chip until the decision survives physical implementation.

The constraint is that synthesis only changes RTL into logic. Physical design must place that logic somewhere, connect it with wires, deliver power, distribute the clock, and prove that signals arrive before the next register samples them.

## Why Geometry Changes The Claim

RTL says what should happen at a clock edge:

```text
inputs at this edge -> path and reason at next edge
```

Synthesis lowers that into registers, gates, muxes, and comparisons. But physical design changes the cost of the logic. A comparator far from its input pins has longer wires. A mux chain placed poorly can add delay. Reset and clock routing can create skew. Power drop can slow cells.

The same Boolean decision can be easy or hard to time depending on where it sits.

## The Concrete Design Move

The design move is to package the controller for a physical flow:

- Verilog source
- top-module name
- clock port
- clock period
- input delay
- output delay
- pin-order intent
- floorplan utilization target
- process and cell-library assumptions

Those files do not prove timing. They make the timing question runnable.

For the control plane, the design package asks:

```text
Can path[1:0] and reason[2:0] be produced within one scheduler clock period?
```

The answer requires a real timing report, not a successful Verilog simulation.

## Measurement

The measurement is a physical-flow artifact set:

- synthesized standard-cell netlist
- floorplan utilization
- placed cell locations
- routed wires
- static timing report
- worst negative slack
- total negative slack
- design-rule check count
- layout-versus-schematic status

The most important single number is slack:

```text
slack = required arrival time - actual arrival time
```

Positive slack means the timed decision is proven under the stated assumptions. Negative slack means the decision may be logically correct but too late.

## Failure Mode

The failure mode is stopping at RTL or generic synthesis and calling the controller implemented. RTL simulation checks behavior. Yosys lowering checks that the design can become logic. Physical implementation checks whether the logic can exist as timed geometry.

Another failure mode is using weak constraints. A design can pass an easy clock period and fail the real scheduler deadline. Constraints are part of the claim.

The first-principles claim is that digital control becomes chip evidence only when behavior, logic, geometry, and timing all describe the same object.

In the current AIMC controller lab, that chain now has two levels of evidence. The CTS-enabled OpenLane run reaches detailed placement and placement-stage timing, then stalls during CTS characterization. A separate no-CTS exploratory run completes routing, extraction, GDS generation, DRC, LVS, antenna checking, and final report generation. That is real physical-flow evidence, but the missing clock tree means full timing closure remains open.
