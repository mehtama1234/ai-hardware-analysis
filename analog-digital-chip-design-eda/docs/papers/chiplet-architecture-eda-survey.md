# The Survey Of Chiplet-Based Integrated Architecture: An EDA Perspective

## Bibliographic Identity

- Title: The Survey of Chiplet-Based Integrated Architecture: An EDA Perspective
- Year: 2024
- Source: https://arxiv.org/abs/2411.04410
- Track: manufacturing-packaging-and-yield
- Subtheme: chiplet architecture and advanced packaging EDA

## First-Principles Reading

The object being controlled is system partitioning across multiple dies. A chiplet design decides what belongs together on one die, what can be separated, and how separated parts communicate through package-level links.

The constraint is that chiplets trade one hard problem for several coupled problems. Smaller dies can improve yield and reuse, but package interconnect, bandwidth, latency, power delivery, thermal behavior, test, and reliability become central.

The mathematical form is multi-objective partitioning and integration. The design must balance cost, yield, bandwidth, latency, area, thermal limits, and reliability across die and package choices.

The concrete method is survey and taxonomy. The paper organizes chiplet-based architecture work from an EDA perspective: architecture, partitioning, integration, physical design, and reliability analysis.

The evidence artifact is the map of EDA tasks and tradeoffs. This is valuable because chiplets need methods that understand both design automation and packaging constraints.

The failure boundary is package reality. A chiplet architecture can look attractive at block level while failing because interconnect, test, thermal, yield, or supply-chain assumptions do not hold.

## Concept Links

- `yield-is-probability-over-manufacturing-variation`
- `power-is-switching-leakage-and-delivery-loss`
- `routing-turns-connection-demand-into-geometry`

## What The Paper Teaches

The deeper lesson is that advanced packaging moves the design boundary. The chip is no longer only the die; the package becomes part of the system architecture.

