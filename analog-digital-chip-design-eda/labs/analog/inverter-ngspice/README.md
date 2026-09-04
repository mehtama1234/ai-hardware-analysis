# Lab: CMOS Inverter In SPICE

This lab uses a toy CMOS inverter to show the first physical move behind digital logic: charging and discharging a capacitive node through transistor-controlled current paths.

## Object

The object being controlled is the output node voltage.

## Constraint

The output node cannot change instantly. It must be charged toward `VDD` or discharged toward ground through devices with finite strength.

## Concrete Design Move

The pMOS device creates the pull-up path. The nMOS device creates the pull-down path. The input voltage chooses which path is stronger.

## Measurement

Run the transient simulation and inspect `v(in)` and `v(out)`.

```bash
ngspice inverter.sp
```

Useful questions:

- Does the output reach the expected rail?
- How long does the transition take?
- What would change if the pMOS width were smaller?
- What would change if load capacitance were added?

## Failure Mode

The schematic can express inversion while the physical circuit is too slow, too weak, or too sensitive to load.

