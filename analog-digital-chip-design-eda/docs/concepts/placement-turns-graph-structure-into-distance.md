# Placement Turns Graph Structure Into Distance

Placement chooses where cells and blocks sit on silicon. It turns a netlist graph into physical distance.

The object being controlled is location. Logic that is close together usually has shorter wires, lower capacitance, lower delay, and less routing demand. Logic that is far apart pays distance in timing, power, and congestion.

The constraint is that a chip is not an empty plane. Macros, memories, analog blocks, power grids, clock structures, routing layers, keepouts, density rules, and pin locations restrict where cells can go.

The mathematical shape is graph embedding under constraints. The netlist says which nodes must connect. Placement assigns coordinates:

```text
cell_i -> (x_i, y_i)
```

The cost is not just total wire length. The placer also cares about timing-critical nets, congestion, density, macro channels, power delivery, clocking, and legalization.

The concrete design move is arranging connected logic so the most important communication is short and routable. Tools cluster related cells, spread density, place macros, move critical paths closer, reserve channels, and legalize cells onto valid rows.

Macro placement is the sharpest version of the problem. A memory or large block can block routing channels, force long detours, or make a clean clock tree impossible. Once large blocks are fixed, the smaller cells inherit the geometry those decisions created.

The measurement is estimated wire length, congestion map, timing estimate, density, macro-channel health, power-grid impact, and routability. Later routing and extraction can prove the estimate wrong, so placement is judged by what survives after routing.

The failure mode is treating placement as aesthetic layout. A visually tidy placement can create long critical wires, blocked routing channels, bad clock distribution, or local power density problems. Placement is a physical argument about communication cost.
