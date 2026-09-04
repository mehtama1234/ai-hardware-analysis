# Sky130 Frontend Sense Efficiency Audit

This page is generated from `evidence/aimc-simulator-adapters/sky130-frontend-sense-efficiency-audit.md`.

It explains why the latest extracted frontend candidates improved the signal but still did not reach the latch target.

The object is the sense-node voltage that must feed the comparator. The first-principles question is simple: how much of the sampled voltage difference survives as voltage at the comparator input?

