# Lab: Reading Timing Closure

This lab is a reading and artifact lab until a full standard-cell timing flow is installed.

## Object

The object being controlled is data arrival time at each receiving register.

## Constraint

For setup timing, the data must arrive before the next sampling edge. For hold timing, it must not arrive too soon after the current edge.

## Concrete Design Move

Take a timing report from a synthesis or place-and-route flow and mark each term:

- launch clock
- clock-to-Q delay
- combinational delay
- wire delay
- setup or hold requirement
- skew and uncertainty
- slack

## Measurement

The measurement is slack. Positive slack means the path meets the stated timing inequality. Negative slack means the physical implementation has not proved the timed behavior.

## Failure Mode

Timing can fail even when simulation shows the right logical sequence. Simulation tests examples; timing closure checks path deadlines.

