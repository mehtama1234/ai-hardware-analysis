# OpenLane: An Automated RTL-To-GDSII Flow

## Bibliographic Identity

- Title: OpenLane: An automated RTL to GDSII flow
- Year: 2020
- Source: https://github.com/The-OpenROAD-Project/OpenLane
- Track: physical-design-and-signoff
- Subtheme: automated open-source physical design

## First-Principles Reading

The object being controlled is the entire RTL-to-layout sequence. A designer writes RTL, but a chip must be taped out as checked geometry. OpenLane organizes the steps between those states so they can be run as a flow instead of assembled manually each time.

The constraint is hidden coupling between tools. Synthesis choices affect placement. Floorplan choices affect routing. Routing affects extracted timing. Design-rule checks can force layout changes. LVS can reveal that the physical connectivity no longer matches the intended circuit. A flow must therefore carry assumptions forward and check them repeatedly.

The mathematical form is a pipeline of constrained transformations. Each stage receives an artifact and emits another artifact under constraints:

```text
RTL -> gates -> floorplan -> placed design -> routed design -> extracted and checked layout
```

The equation-like point is preservation: the later artifact should still implement the earlier intent while satisfying additional physical constraints.

The concrete method is composition. OpenLane combines open tools such as synthesis, placement/routing, layout checking, and verification utilities into a repeatable flow. The value is not that automation removes engineering judgment. The value is that it makes the toolchain easier to run, inspect, compare, and teach.

The evidence artifact is the full run directory: generated netlists, DEF/GDS files, logs, timing reports, DRC/LVS status, extracted parasitics, and configuration files. The configuration matters because it states the assumptions under which the flow result was produced.

The failure boundary is silent assumption mismatch. A flow can complete while using weak constraints, an unsuitable PDK setup, incomplete checks, or unrealistic workload assumptions. Automation is useful only when the artifacts are read, not merely produced.

## Concept Links

- `eda-is-constraint-solving`
- `extraction-turns-shapes-back-into-circuit-equations`
- `verification-is-evidence-implementation-matches-intent`
- `routing-turns-connection-demand-into-geometry`

## What The Paper Teaches

The deeper lesson is that EDA automation is a chain of accountable translations. The user should ask what each stage claims to preserve, what evidence it emits, and what it leaves unproved.

