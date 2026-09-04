# Lab: Counter Synthesis With Yosys

This lab connects RTL to gates. It uses the counter from `../counter-verilog`.

## Object

The object being controlled is preservation of the counter's state-update behavior after synthesis.

## Constraint

Synthesis is allowed to change implementation structure, but it must preserve the intended function.

## Concrete Design Move

Run Yosys to elaborate and synthesize the RTL:

```bash
yosys synth_counter.ys
```

## Measurement

Inspect `counter_synth.v`. The artifact should contain a gate-level or lowered representation of the counter. The important question is what behavior was preserved and what timing evidence is still missing.

## Failure Mode

A synthesized netlist can preserve logic while saying little about physical timing, placement, routing, power, or manufacturability.

