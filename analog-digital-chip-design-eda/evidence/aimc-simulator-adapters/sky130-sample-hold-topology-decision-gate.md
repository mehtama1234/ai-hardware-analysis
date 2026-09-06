# Sky130 Sample-Hold Topology Decision Gate

- status: `sky130_sample_hold_topology_gate_requires_buffered_or_bootstrapped_design`
- half LSB at 12 bits V: `2.197265625e-04`
- on-state sample switch passes: `True`
- all existing hold topologies pass: `False`
- candidate post-layout written: `False`
- accepted post-layout written: `False`

## What The Measurements Say

| evidence | measured voltage movement or error | passes 12-bit half LSB | meaning |
| --- | ---: | --- | --- |
| `on_state_sample_switch` | `1.369000000e-04` | `True` | the switch can charge the sample node closely enough while it is still on |
| `plain_hold_mode` | `5.557000000e-03` | `False` | the held value moves too far after the switch turns off |
| `larger_cap_or_switch_resize` | `1.632500000e-03` | `False` | more capacitance reduces voltage movement, but not enough |
| `dummy_cancellation` | `1.481300000e-03` | `False` | opposite clock charge helps, but still leaves too much held-voltage error |
| `bottom_plate_fixture` | `7.677000000e-03` | `False` | the current two-node bottom-plate fixture does not fix the stored voltage |
| `buffered_source_follower_candidate` | `not measured` | `False` | the naive source-follower buffer produced no measured cases, so it is not acceptable evidence |
| `idealized_bootstrapped_switch_candidate` | `1.045400000e-02` | `False` | the idealized bootstrapped Sky130 switch converged and acquired correctly, but hold movement remains above the 12-bit target |
| `sky130_differential_sampling_candidate` | `2.086600000e-03` | `False` | the one-case Sky130 differential transmission-gate fixture now measures, but its decision-voltage movement is still above the 12-bit target |
| `differential_sampling_control_proof` | `3.000000000e-04` | `False` | the ideal-switch control proof shows common disturbance cancels, but mismatch remains as decision error |
| `sky130_differential_dummy_cancellation` | `4.060000000e-05` | `True` | matched opposite-clock dummy devices produced one passing Sky130 decision-voltage case, so this is the next candidate front end to broaden and stress |
| `sky130_differential_dummy_input_sweep` | `6.300000000e-05` | `True` | the fixed 0.50x differential dummy candidate passed low, mid, and high nominal input cases |
| `sky130_differential_dummy_mismatch_sweep` | `5.090000000e-05` | `True` | the fixed candidate passed the controlled +/-1% and +/-2% one-sided width-mismatch cases |
| `sky130_single_device_charge_injection` | `not measured` | `False` | even the one-device Sky130 gate-edge fixture produced no measured cases under bounded ngspice runs |
| `sky130_clock_edge_sweep` | `1.049100000e-03` | `False` | the one-case baseline edge check measured cleanly, but the mid-input held voltage still moves more than the 12-bit target |

## First-Principles Reading

A sample-and-hold circuit has two jobs. First it must let charge enter the capacitor so the capacitor voltage becomes the input voltage. Then it must stop charge from moving so the stored voltage stays still while the digital decision is made.

The first job is working in the simple transmission-gate fixture. While the switch is on, the capacitor gets close enough to the input for the 12-bit half-LSB line. That is useful, but it is only the acquisition part of the circuit.

The second job is failing. When the switch turns off, charge from the clocked devices and nearby nodes changes the stored charge. The capacitor voltage then moves. Since voltage movement is charge movement divided by capacitance, a larger capacitor helps, but it also costs more energy and takes longer to settle. In the measured sweep it helps by a real amount, but the best result is still above the target.

Dummy cancellation is the same problem attacked from the other side. It adds an opposite clocked device to push charge back onto the node. That can reduce the error when the size and timing are close, but it is not a law of the circuit. The measured best dummy case still misses the target, so it cannot be promoted into a converter proof.

The current bottom-plate fixture also does not solve it. Bottom-plate sampling should disconnect the sensitive side before the worst clock disturbance arrives, but this implemented two-node fixture still moves the stored differential voltage too much. That means the idea may still be useful, but this circuit is not the accepted topology.

The newer stronger sketches are not accepted either. The naive source-follower buffer, idealized bootstrapped switch, and one-device Sky130 gate-edge fixture all failed to produce measured cases under bounded ngspice runs. The Sky130 differential transmission-gate fixture now measures one mid-input point, but the differential decision voltage still moves too much. The differential dummy-cancellation fixture changes that one fact: one matched dummy size brings the measured decision-voltage movement below the half-LSB line, the fixed candidate passes low, mid, and high nominal input cases, and the controlled width-mismatch sweep also passes. That is a candidate front end, not a converter proof.

The differential control proof does produce numbers. It shows the key law: common movement can cancel from a differential decision, but mismatch remains. In its measured rows, the common-injection cases pass and the mismatched-injection case fails the 12-bit line. That means differential sampling is still worth pursuing, but only with a transistor fixture that can show matched disturbance, not just assumed matched disturbance.

The design target is now numeric. The best measured decision-voltage case is `6.300000000e-05` V against a `2.197265625e-04` V half-LSB line.

The differential matching requirement is also numeric. The next differential sample-hold must keep unmatched movement below `0.2197 mV` and reject about `89.5%` of the common disturbance.

The next executable work order is `broaden_differential_dummy_cancellation_candidate`. It says to copy the known-running transmission-gate hold-mode deck exactly, change one variable at a time, and require every accepted case to finish inside the bridge runtime bound.

## Next Circuit To Build

The next proof should not be another broad architecture page. It should make one transistor-level fixture stable enough to measure:

- `differential_dummy_cancellation`: first priority, because it is the first measured Sky130 sample-hold fixture here with passing decision-voltage hold cases across low, mid, high, and controlled one-sided width mismatch.
- `fully_differential_sampling`: keep as the baseline comparison, because the control proof says the decision voltage can reject shared disturbance.
- `bootstrapped_switch`: second priority, because constant switch overdrive may reduce input-dependent acquisition and charge injection.
- `buffered_sample_and_hold`: useful only after the buffer is explicitly biased and numerically stable.

The next run must report acquisition error, hold movement, supply energy, and convergence for low, mid, and high input. If it does not beat the half-LSB line in hold mode, it is still only a characterization result.

## Refused Claim

does not prove a working ADC, DAC, comparator, SAR loop, extracted layout, DRC/LVS signoff, or accepted post-layout converter economics
