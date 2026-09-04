# Sky130 Sample Switch Hold Mitigation Sweep

This page tests simple circuit knobs against the Sky130 sample-switch hold error.

The previous hold-mode run showed the real issue: the sampled node follows the input while the switch is on, but it moves after the switch turns off. This sweep changes sample capacitance and switch size, then measures whether the held-node movement shrinks.

This is still a starter circuit study, not a converter proof. It does not contain a comparator, SAR loop, reference ladder, extracted transistor layout, DRC/LVS, or accepted post-layout economics.

