# Design-Space Search Is Trading Expensive Measurements

Design-space search chooses among circuit, architecture, or layout options when each real measurement is costly. This is common in analog sizing, accelerator architecture, physical design, and process-aware optimization.

The object being controlled is the next experiment. A designer has a space of possible designs and a limited budget for simulation, synthesis, place-and-route, or silicon experiments.

The constraint is that the design surface is coupled and expensive to evaluate. Changing transistor width affects gain, bandwidth, noise, power, and capacitance. Changing an accelerator tile changes utilization, memory traffic, area, and timing. Changing a floorplan changes wire length, routing demand, clocking, and power delivery.

The mathematical shape is optimization under expensive observations:

```text
choose design x -> measure f(x) -> update belief -> choose next x
```

The function `f` can include many metrics and constraints. A useful search method does not only look for a high score. It must respect hard constraints such as stability, timing, DRC, LVS, area, power, and yield.

The concrete design move is to choose candidates that are informative and plausible. Methods include sweeps, Bayesian optimization, evolutionary search, reinforcement learning, surrogate models, constraint pruning, and human-guided local repair.

The measurement is not only the best final design. It is also sample efficiency: how many expensive tool runs were needed, how often the search violated hard constraints, and whether the chosen design remains good after extraction, corners, or workload changes.

The failure mode is optimizing the proxy instead of the chip. A search can find a design that scores well under a cheap model but fails when checked by a slower, more faithful tool.

