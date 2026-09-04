# Lab: Layout Verification Reading

This lab prepares the physical-design checks: DRC, LVS, extraction, and post-layout simulation.

## Object

The object being controlled is preservation from intended circuit to manufactured geometry.

## Constraint

Drawn shapes must obey manufacturing rules and still represent the intended netlist after parasitics are included.

## Concrete Design Move

Use a small layout artifact once Magic or KLayout is installed. Run or inspect:

- DRC for geometry legality
- LVS for connectivity equivalence
- extraction for parasitic resistance and capacitance
- post-layout simulation or timing for electrical behavior

## Measurement

The measurement is not one pass/fail flag. It is a set of evidence: no relevant DRC errors, LVS match, extracted parasitics understood, and post-layout behavior still inside the design boundary.

## Failure Mode

A layout can look visually correct while failing manufacturing rules, connecting the wrong nodes, or adding parasitics that change circuit behavior.

