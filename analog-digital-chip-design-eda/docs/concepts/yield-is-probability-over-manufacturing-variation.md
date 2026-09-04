# Yield Is Probability Over Manufacturing Variation

Yield is the fraction of manufactured dies that work well enough to sell. It is where circuit design meets probability, defects, and process variation.

The object being controlled is probability of a good die. A design is not finished when one instance works in simulation. It must work across many manufactured instances with random defects and systematic variation.

The constraint is that fabrication is imperfect. Particles, lithography variation, line-edge roughness, overlay error, local mismatch, wafer gradients, packaging stress, and test limits all create differences between intended and manufactured chips.

The mathematical shape is probability over conditions:

```text
yield = P(chip passes required tests)
```

The event inside that probability includes timing, power, analog accuracy, memory repair, functional behavior, leakage, and reliability. Yield is therefore connected to design margin.

The concrete design move is to add margin, regularity, redundancy, repair, calibration, and testability where variation would otherwise cause failure. Designers use larger devices, error correction, spare memory rows, binning, guardbands, design-for-test, statistical timing, and layout practices that reduce sensitivity.

The measurement is wafer sort yield, final test yield, defect density, parametric distribution, shmoo plots, failure analysis, repair rate, bin split, and yield learning across lots. Simulation estimates risk, but silicon data teaches which failure mechanisms dominate.

Yield also decides economics. The cost of a wafer is paid before knowing how many good dies it contains. If die area is large or yield is low, each good chip becomes much more expensive. This connects device physics and layout choices directly to product cost.

The failure mode is treating yield as a factory-only problem. Design choices determine how much variation the chip can tolerate. A fast, small, elegant circuit with no margin may become expensive if too few copies survive manufacturing.
