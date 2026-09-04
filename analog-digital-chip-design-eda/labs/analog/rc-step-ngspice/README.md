# Lab: RC Step Response

This lab shows why bandwidth is the price of storing charge.

## Object

The object being controlled is the voltage on the capacitor.

## Constraint

The capacitor voltage changes only when current moves charge through the resistor. The time constant is:

```text
tau = R C
```

## Concrete Design Move

Change `R1` or `C1` and rerun the transient simulation. Larger values slow the output node. Smaller values make the node follow the input faster.

## Measurement

```bash
ngspice rc_step.sp
```

Measure the time it takes `v(out)` to approach the input step. Compare it with `R*C`.

## Failure Mode

If the node cannot settle before the next circuit samples it, the system makes a decision from an unfinished voltage.

