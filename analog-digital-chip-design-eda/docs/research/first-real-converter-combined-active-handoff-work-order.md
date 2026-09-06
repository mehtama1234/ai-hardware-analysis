# First Real Converter Combined Active Handoff Work Order

This page turns the current frontend-to-active-stage gap into one concrete next build.

The extracted frontend preserves sign but gives only a tiny sense voltage. The
separate Sky130 input-stage run shows gain. The direct handoff proxy timed out,
so the work became one bounded same-deck handoff candidate rather than another
disconnected estimate. That candidate now passes its schematic-level extracted
transistor test when the extracted isolation cell's sense-pin convention is
mapped explicitly.

The goal is simple: connect the passive frontend and active input stage in one
measurable circuit path, prove the sign is still correct, prove the active
output is large enough to hand to a latch, and keep the strict converter claim
closed until latch, SAR, energy, noise, area, DRC/LVS, and same-run payload
evidence exist. The current runner meets the bounded handoff portion at
`extracted_560k_4ua`: two signed cases complete, both corrected signs pass, and
the minimum corrected output is 0.5091 mV against a 0.500 mV target.

Reproduce it with:

```text
AIMC_TRANSISTOR_ACTIVE_ISOLATION_EXTRACTED=1 \
AIMC_TRANSISTOR_ACTIVE_ISOLATION_SWAP_SENSE_PINS=1 \
AIMC_TRANSISTOR_ACTIVE_ISOLATION_SINGLE_SETTING=extracted_560k_4ua \
python3 scripts/run_sky130_transistor_active_isolation_preamp.py
```
