# First Real Converter Frontend Active Handoff Estimate

This page connects the extracted frontend measurement to the already measured Sky130 comparator input-stage gain.

The extracted frontend preserves sign but leaves only a small sense-node voltage. The input-stage evidence shows that a Sky130 differential pair gives about 9.2 V/V gain near this small-signal region. This estimate asks what the active output would be if that measured gain were applied to the extracted frontend output.

This is not accepted converter evidence. It is not a same-deck simulation. It is a reason to build the next real deck: one combined frontend-plus-input-stage circuit with active devices, extracted parasitics, bounded operating point, and then latch timing.
