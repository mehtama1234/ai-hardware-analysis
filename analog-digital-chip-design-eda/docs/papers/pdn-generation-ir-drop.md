# Power Distribution Network Generation For Optimizing IR-Drop Aware Timing

## Bibliographic Identity

- Title: Power Distribution Network Generation for Optimizing IR-Drop Aware Timing
- Year: 2020
- Source: https://dl.acm.org/doi/10.1145/3400302.3415628
- Track: physical-design-and-signoff
- Subtheme: power delivery and IR-drop-aware timing

## First-Principles Reading

The object being controlled is supply voltage at the transistors that switch. Logic gates are designed around an assumed supply, but the real voltage arrives through a resistive and inductive delivery network.

The constraint is that current creates voltage loss. When many cells draw current, the power grid drops voltage according to the same physical idea as Ohm's law. Less local voltage means weaker devices, slower switching, timing loss, and reliability pressure.

The mathematical form is constrained optimization over a power grid. The design has current demand, metal resources, grid topology, resistance, voltage-drop limits, timing impact, and routing competition. Improving the PDN consumes physical resources that other signals may need.

The concrete method is to refine a power distribution network so IR-drop-aware timing improves. The important move is treating power-grid design as part of timing closure, not as a separate signoff report after timing appears done.

The evidence artifact is the generated or refined PDN, IR-drop analysis, timing impact, and comparison with baseline grid choices. The paper belongs in this corpus because it links power delivery directly to timing evidence.

The failure boundary is dynamic and system context. A grid that passes one activity model can fail under different switching, package impedance, local hotspots, or electromigration limits.

## Concept Links

- `power-is-switching-leakage-and-delivery-loss`
- `timing-closure-is-proof-data-arrives-before-decision`
- `routing-turns-connection-demand-into-geometry`

## What The Paper Teaches

The deeper lesson is that timing is not only a data-path problem. A path can miss its deadline because the chip cannot deliver enough voltage to the gates that are supposed to switch.

