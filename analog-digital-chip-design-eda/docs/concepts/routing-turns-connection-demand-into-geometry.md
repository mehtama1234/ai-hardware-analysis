# Routing Turns Connection Demand Into Geometry

Routing draws the wires that connect the placed devices. It turns a list of required connections into manufacturable geometry.

The object being controlled is physical connectivity. Every net must connect the right pins without shorting to other nets, violating design rules, or creating unacceptable delay, capacitance, resistance, coupling, or current density.

The constraint is limited routing space. Metal layers have direction preferences, minimum widths, spacing rules, via rules, blockages, antenna rules, and power-grid reservations. More connections can be requested than a region can physically carry.

The mathematical shape is path finding under geometric rules. A route is a path through routing resources:

```text
net -> metal segments + vias
```

Each path consumes tracks and adds parasitics. Choosing one route changes what is available for other nets.

The concrete design move is assigning nets to layers, tracks, and vias while managing conflicts. Routers use global routing to estimate demand, detailed routing to produce legal shapes, shielding for sensitive nets, widening for current, spacing for noise, and rip-up-and-reroute when early choices block later nets.

The measurement is DRC cleanliness, open/short count, routed wire length, via count, congestion, timing after extraction, crosstalk, IR drop, electromigration, and antenna violations. A route is not done when lines are drawn; it is done when the drawn shapes pass the checks that matter for manufacturing and operation.

The failure mode is assuming connectivity equals correctness. A connected net can still be too slow, too noisy, too resistive, too hard to manufacture, or too damaging during fabrication.

