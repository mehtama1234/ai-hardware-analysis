# Mismatch Turns Local Error Into Circuit Behavior

Mismatch is the difference between devices that were intended to be the same. It is manufacturing variation becoming circuit behavior.

The object being controlled is relative error. Many circuits depend on two transistors, resistors, or capacitors matching each other more than they depend on either part having an exact absolute value.

The constraint is that fabrication is local and imperfect. Threshold voltage, mobility, oxide thickness, line width, resistor value, and capacitor area vary across the die. Nearby devices tend to match better than far-apart devices, but they are never identical.

The mathematical shape is usually a random error term added to the ideal device:

```text
actual_value = intended_value + local_error
```

In analog design, that local error can become input offset, gain error, current mirror error, distortion, or degraded common-mode rejection. In digital design, variation can change delay, leakage, and noise margin.

The concrete design move is to reduce sensitivity to mismatch or average it out. Designers use larger devices, common-centroid layout, interdigitation, dummy devices, trimming, calibration, chopping, auto-zeroing, redundancy, and architectures where a mismatch error is measured and corrected.

Layout is part of the method, not decoration after the circuit is finished. If two devices define a current ratio, their orientation, neighborhood, well proximity, stress, temperature gradient, and routing parasitics become part of that ratio. A clean schematic pair can become an unbalanced physical pair if one side sees a different edge, wire, or local environment.

Calibration is the other path. Instead of pretending mismatch can be removed, the circuit measures its own error and stores a correction. That can work well, but it changes the problem: the design now needs a measurement phase, correction range, memory, and a way to keep the correction valid across temperature and aging.

The measurement is offset, matching sigma, yield across Monte Carlo runs, delay spread, gain spread, or calibrated residual error. A single typical simulation proves almost nothing about mismatch.

The failure mode is believing symmetry in the schematic creates symmetry on silicon. Matching is a physical claim. It must survive layout, gradients, stress, edge effects, and random device variation.
