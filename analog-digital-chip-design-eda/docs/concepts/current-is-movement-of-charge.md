# Current Is Movement Of Charge

Current is the rate at which charge moves. It is the action that changes voltage, powers loads, creates gain, and also creates loss.

The object being controlled is charge flow through a device or wire. A circuit designer decides where charge is allowed to move, how strongly it moves, and how that movement changes when an input changes.

The basic relation is:

```text
I = dQ / dt
```

The constraint is that charge movement has cost and delay. If a node needs charge `Q` to move by a useful voltage amount, and the available current is small, the movement takes time. If the current is large, the movement can be fast, but it may burn power, create noise, or exceed reliability limits.

In a MOS transistor, current is controlled by terminal voltages. The gate voltage changes the channel, and the drain-source voltage creates movement through that channel. The device is useful because a small signal at the gate can control a larger current path.

The concrete design move is biasing. Biasing sets the resting current so the device sits in the region where the circuit needs it. Too little current can make the circuit slow, noisy, or nonlinear. Too much current wastes power and can reduce headroom.

For digital circuits, current is most visible during switching. Gates draw dynamic current when charging and discharging capacitances, and leakage current even when they are not switching. For analog circuits, current is also the operating point: it sets transconductance, noise, output resistance, bandwidth, and power.

The measurement is current over time and current under corners. A design that works at typical conditions may fail when threshold voltage, temperature, or supply changes.

The failure mode is thinking of current as just power cost. Current is also control authority. If the circuit cannot move enough charge at the right time, it cannot hold its state, settle its output, or drive the next stage.
