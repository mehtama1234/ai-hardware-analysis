# ABC: A System For Sequential Synthesis And Verification

## Bibliographic Identity

- Title: ABC: A System for Sequential Synthesis and Verification
- Year: 2010
- Source: https://people.eecs.berkeley.edu/~alanmi/abc/
- Track: digital-design-and-architecture
- Subtheme: logic synthesis and formal verification

## First-Principles Reading

The object being controlled is the logic representation. Before a digital circuit becomes cells and wires, it is a network of Boolean relationships and state elements that can be transformed.

The constraint is preservation under transformation. Logic optimization is allowed to change structure, but it must not change the intended behavior. Verification is the evidence that a transformation stayed inside that boundary.

The mathematical form is graph transformation plus equivalence reasoning. ABC is built around compact logic representations such as And-Inverter Graphs, then applies rewriting, mapping, and verification algorithms over those structures.

The concrete method is to put synthesis and verification close together. The same representation supports optimization and checking, so transformations can be explored while still asking whether the design remains equivalent to the intended function.

The evidence artifact is an optimized logic network, mapping result, or verification result. In the chip-design chain, this is pre-physical evidence: it can show that a logic-level transformation is valid before placement and routing add new constraints.

The failure boundary is physical implementation. ABC can reason about binary sequential logic, but it does not by itself prove timing closure, power delivery, signal integrity, layout legality, or yield.

## Concept Links

- `verification-is-evidence-implementation-matches-intent`
- `digital-logic-turns-voltage-into-symbols`
- `timing-closure-is-proof-data-arrives-before-decision`

## What The Paper Teaches

The deeper lesson is that digital design needs two linked abilities: changing logic to make it cheaper or faster, and proving that the change did not alter the intended behavior.

