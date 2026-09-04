# EDA Is Constraint Solving Over Physics, Logic, And Geometry

A chip begins as an intended behavior, but it is manufactured as shapes. EDA is the chain of translations that tries to preserve the intended behavior while moving from equations and logic into physical geometry.

The object being controlled is not a file format. It is a constraint set that must remain consistent while the design moves from behavior to gates to shapes.

Digital logic says which outputs must follow from which inputs. Timing constraints say when those outputs must be stable. Power constraints say how much switching and leakage can be tolerated. Design rules say which shapes can be manufactured. Extraction says the drawn wires and devices have added resistance, capacitance, coupling, delay, and noise.

The constraint is coupling. Moving a cell can shorten one wire and lengthen another. Widening a wire can reduce resistance but increase capacitance and routing congestion. Buffering a path can fix timing while increasing power and area. Shrinking area can hurt yield or make routing impossible.

Mathematically, an EDA flow is a sequence of constrained optimization and verification problems. The design is a graph, the layout is an embedding of that graph into physical space, and the final circuit equations include parasitics that were not explicit in the starting logic.

The concrete design move is translation with checks after each translation:

- RTL to logic gates
- gates to placed cells
- placed cells to routed wires
- routed wires to extracted circuit
- extracted circuit to timing, power, DRC, LVS, and functional evidence

A strong EDA method does not only produce a layout. The measurement is the evidence gathered after each translation: simulation, equivalence checking, timing reports, power reports, DRC, LVS, extraction, and signoff checks. These checks say what was preserved and which constraints became tighter.

The failure mode is false preservation. The design appears unchanged at the logical level, but the physical implementation violates timing, power, manufacturability, signal integrity, or yield.
