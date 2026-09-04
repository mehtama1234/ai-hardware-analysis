# ALIGN: A System For Automating Analog Layout

## Bibliographic Identity

- Title: ALIGN: A System for Automating Analog Layout
- Year: 2020
- Source: https://arxiv.org/abs/2008.10682
- Track: analog-and-mixed-signal
- Subtheme: automatic analog layout generation

## First-Principles Reading

The object being controlled is preservation from analog netlist to physical layout. The schematic says which devices connect and what roles they play. The layout decides whether matching, parasitics, symmetry, and design rules let that schematic behavior survive.

The constraint is that analog layout carries circuit meaning. Two devices that look identical in a schematic can behave differently if layout gradients, routing parasitics, device orientation, or neighborhood effects differ. Analog automation must therefore preserve electrical relationships, not merely draw legal shapes.

The mathematical form is hierarchical constrained assembly. ALIGN reads hierarchy from the netlist, creates layout blocks, and assembles them under geometric and electrical constraints. The problem is part parsing, part placement, part routing, and part preservation of analog intent.

The concrete method is to generate analog layout from a SPICE netlist using hierarchy detection, parameterized cells, design-rule abstractions, and block assembly. The useful idea is that analog layout can be automated only when the tool names the circuit relationships it must protect.

The evidence artifact is generated GDSII layout across analog circuit families, along with the flow outputs and checks that show the layout is legal and connected to the intended netlist.

The failure boundary is post-layout behavior. A layout can be generated and still fail because extracted parasitics, mismatch, symmetry errors, or process-specific effects change gain, noise, stability, offset, or bandwidth.

## Concept Links

- `mismatch-turns-local-error-into-circuit-behavior`
- `extraction-turns-shapes-back-into-circuit-equations`
- `eda-is-constraint-solving`

## What The Paper Teaches

The deeper lesson is that analog EDA must automate relationships, not drawings. The layout is good only if it protects the electrical reasons the schematic was designed that way.

