# MAGICAL: Toward Fully Automated Analog IC Layout Leveraging Human And Machine Intelligence

## Bibliographic Identity

- Title: MAGICAL: Toward Fully Automated Analog IC Layout Leveraging Human and Machine Intelligence
- Year: 2019
- Source: https://ieeexplore.ieee.org/document/8942060/
- Track: analog-and-mixed-signal
- Subtheme: machine-assisted analog layout automation

## First-Principles Reading

The object being controlled is analog layout choice: where devices go, how related devices are matched, and how wires are drawn so the physical circuit still behaves like the designed circuit.

The constraint is that much analog layout knowledge is tacit. Human layout engineers know to protect symmetry, reduce sensitive parasitics, keep matched devices in shared environments, and route critical nets carefully. Automation must make those habits explicit enough to search and check.

The mathematical form is constrained placement and routing with pattern knowledge. The layout engine must choose legal geometry while respecting analog constraints that are not captured by simple connectivity alone.

The concrete method is to combine human-inspired layout structure with machine-assisted search or prediction. The method tries to reduce manual effort by encoding or learning parts of the layout decision process.

The evidence artifact is generated layout quality, runtime reduction, and circuit-level comparison against manual or baseline approaches. For analog layout, the meaningful evidence is not only geometry legality; it is whether post-layout circuit behavior remains inside the intended boundary.

The failure boundary is unexplained automation. If a tool makes layout choices without preserving the analog reason for those choices, it can produce layouts that look plausible but degrade matching, stability, noise, or bandwidth.

## Concept Links

- `mismatch-turns-local-error-into-circuit-behavior`
- `feedback-trades-gain-for-control`
- `ai-for-eda-is-a-checked-design-loop`

## What The Paper Teaches

The deeper lesson is that analog automation needs a bridge between human circuit intent and machine search. Layout choices are engineering claims about physical error, not cosmetic arrangements.

