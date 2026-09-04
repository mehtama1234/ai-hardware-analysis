# Power Is Switching, Leakage, And Delivery Loss

Power is the rate at which the chip consumes energy. It is not one problem. It is the sum of several physical costs that appear when circuits switch, sit still, and receive current through imperfect power networks.

The object being controlled is energy per useful operation. A chip is better when it performs the intended work with less energy, less heat, and less voltage disturbance.

The constraint is that every useful electrical movement has a cost. Charging a capacitance costs energy. Holding transistors off is imperfect, so leakage remains. Delivering current through package, bumps, wires, and on-chip grids creates voltage drop and heat.

The main dynamic-power relation is:

```text
Pdynamic = alpha C V^2 f
```

`alpha` is switching activity, `C` is switched capacitance, `V` is supply voltage, and `f` is clock frequency. This equation explains why power is connected to architecture, layout, voltage choice, and workload behavior.

The concrete design move is to reduce useless switching or reduce the cost of necessary switching. Designers use clock gating, power gating, lower voltage, smaller capacitance, better locality, memory hierarchy, operand isolation, multi-threshold cells, and architectures that move less data.

The measurement is average power, peak power, energy per operation, thermal map, IR drop, electromigration margin, leakage across corners, and workload-specific activity. A design that passes a small test may fail when real switching creates heat or supply noise.

The failure mode is optimizing power as an afterthought. Power changes timing, reliability, cost, package choice, cooling, and battery life. A chip that computes the right answer but cannot deliver current safely is not a working product.

