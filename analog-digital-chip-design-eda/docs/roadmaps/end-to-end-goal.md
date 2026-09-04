# End-To-End Goal

Build a first-principles chip design and EDA corpus that can teach analog design, digital design, and design automation as one connected system.

## Standard For Every Article

Each article must answer:

1. What physical, logical, or geometric object is being controlled?
2. What constraint makes the problem hard?
3. What mathematical form describes the constraint?
4. What concrete design move changes the object?
5. What measurement proves the move worked?
6. What failure remains after the move?

## Main Tracks

### Analog Design

Analog design is the control of continuous electrical quantities under noise, mismatch, device limits, and layout parasitics. The core objects are voltage, current, charge, gain, bandwidth, phase, and uncertainty.

### Digital Design

Digital design is the conversion of voltage behavior into reliable symbolic state transitions. The core objects are Boolean function, register state, clock edge, critical path, switching energy, and timing proof.

### EDA

EDA is the machinery that turns an intended circuit into a manufacturable layout while preserving function under physical constraints. The core objects are netlists, constraints, standard cells, placement coordinates, routed wires, extracted parasitics, and verification evidence.

### AI For EDA

AI for EDA is useful only when it improves a concrete design loop: generate, check, repair, search, size, place, route, or verify. The central question is whether the model reduces engineering uncertainty or merely produces plausible text.

## First Milestone

Create 20 concept articles, 6 labs, and one synthesis page:

- 8 analog concept articles
- 6 digital concept articles
- 4 EDA concept articles
- 2 AI-for-EDA concept articles
- 2 SPICE labs
- 2 Verilog simulation/synthesis labs
- 2 EDA flow labs
- 1 synthesis page tying voltage, state, geometry, timing, and verification together

## Current AIMC Evidence Gate

The current foundation-model hardware thread has one project-level check:

```bash
./scripts/check_aimc_bridge.sh
```

That gate regenerates analog-derived RTL vectors, runs the micro-tile controller simulation, compares the hardware trace against the generated CSV, reruns Yosys synthesis, checks the OpenLane package, rebuilds the site, and runs the project validator. This keeps the analog explanation, RTL behavior, synthesis evidence, physical-flow readiness, and rendered documentation tied together.
