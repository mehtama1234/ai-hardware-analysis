# EDA Lab Track

The EDA labs will connect the concept articles to tool evidence.

## Workflow Contract

Consumes: RTL controller blocks, synthesis scripts, OpenLane prep packages, timing constraints, generated netlists, and physical-flow reports.

Produces: synthesis evidence, OpenLane readiness checks, routed/no-CTS/CTS attempt reports, timing-readiness notes, and physical-flow boundaries for backend evidence.

Supports: the claim that selected digital control blocks can move from Verilog toward gates and physical geometry in the local open-source flow.

Refuses: production signoff, analog macro integration, final timing closure for every block, foundry-qualified DRC/LVS, packaged chip reliability, and measured silicon behavior.

Handoff: EDA evidence should be exported as physical-flow evidence, not as a chip-success claim. It strengthens the controller implementation claim while leaving production readiness blocked.

## Where This Lands In The Combined Workbench

This lab is the physical-flow boundary of the larger AIMC workflow.

```text
synthesized controller
  -> OpenLane package
  -> placement and routing attempt
  -> timing/DRC/LVS/antenna summary
  -> local power and area context
  -> backend evidence import
  -> claim readiness
```

The useful claim is not "the chip is done." The useful claim is narrower: a selected digital control block can enter an open-source physical-design flow under recorded constraints, and the resulting report can be inspected as evidence.

The current backend claim effect is also narrow. OpenLane-derived area, timing, and power context can explain local implementation cost, but it does not support measured energy. The measurement upgrade requires a synchronized runtime and power record as defined in `docs/research/board-and-power-measurement-boundary.md`.

## Current Labs

1. `aimc-control-plane-timing-readiness`: reads synthesized request-control and operation-partition netlists and states what is ready for STA versus what timing evidence is still missing.
2. `aimc-control-plane-openlane-prep`: packages the registered request controller for OpenLane and records the completed no-CTS exploratory physical run.
3. `aimc-operation-partition-openlane-prep`: packages the transformer operation partition with a clocked physical wrapper and records the completed no-CTS exploratory physical run.
4. `timing-closure-reading`: explains timing closure as deadline evidence rather than synthesis success.
5. `layout-verification-reading`: explains DRC, LVS, and extraction as checks on physical preservation.

## Next Planned Labs

1. Isolate the OpenLane/OpenROAD CTS behavior; both full-wrapper and output-registered operation-partition attempts reached `Number of created patterns = 50000` and did not complete.
2. Add a real Liberty/OpenSTA timing run for both AIMC control blocks.
3. Compare post-route parasitic timing for request-level control versus operation-level partition logic.
4. Inspect the generated GDS/DEF for pin placement, area, and route shape.
5. Add a small SRAM/KV-cache controller so the digital side starts to represent memory traffic, not only path choice.

## First-Principles Thread

EDA is not a button that makes chips. It is a sequence of claims:

- synthesis claims the gate netlist preserves RTL behavior
- placement claims physical distance can support the timing and routing needs
- routing claims the required connections can become legal geometry
- extraction claims the geometry can be read back as circuit equations
- signoff claims the manufactured object should still satisfy the design requirements

Each lab should name the claim, run the tool, inspect the artifact, and state what the artifact does not prove.
