# Seeded counter OpenLane package

This package is the physical-design input for the repaired `seeded_counter`
benchmark. The checked-in `src/counter.sv` is the expected repaired form; the
end-to-end experiment stages the model-approved disposable copy through
`AIMC_OPENLANE_VERILOG_SOURCE_DIR` so the canonical seeded defect is never
overwritten.

Example:

```bash
PDK_ROOT=/path/to/ciel/sky130/versions/<revision> \
AIMC_OPENLANE_DESIGN=counter \
AIMC_OPENLANE_PREP=seeded-counter-openlane-prep \
AIMC_OPENLANE_VERILOG_SOURCE_DIR=/path/to/repaired/source \
TAG=counter_model_generated_repair_rtl2gds \
bash scripts/run_aimc_openlane_flow.sh
```

The package supports local synthesis, placement, CTS, routing, extracted STA,
GDS, DRC, antenna, XOR, and LVS evidence. It is not commercial signoff or
silicon evidence.
