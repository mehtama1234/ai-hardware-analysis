# Sky130 Capacitive Isolation Physical Cell Gap

- status: `physical_cell_gap_blocks_post_layout_candidate`
- source handoff: `evidence/aimc-simulator-adapters/sky130-capacitive-isolation-post-layout-handoff.json`
- required object count: `6`
- present object count: `4`
- missing object count: `2`
- accepted ready now: `False`
- candidate post-layout written: `False`
- accepted post-layout written: `False`

## First Principle

The confirmed schematic is a behavior. A physical claim needs an object. The object is a named layout or schematic cell, an extracted netlist, a model corner, and rerun records made from that extracted netlist.

This audit keeps those two things separate. It lets the schematic result move forward, but blocks accepted evidence until the physical files are present.

## Required Objects

### layout_cell

- present: `True`
- why: the isolation capacitor and latch/sample connection must become a physical or schematic cell with a stable name
- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/sky130_capacitive_isolation_frontend.mag` present `True` bytes `880`
- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/sky130_capacitive_isolation_frontend.gds` present `False` bytes `0`
- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/sky130_capacitive_isolation_frontend.sch` present `False` bytes `0`

### extracted_frontend_netlist

- present: `True`
- why: post-layout proof must simulate the extracted circuit object, not the earlier generated schematic deck
- `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/sky130_capacitive_isolation_frontend_extracted.sp` present `False` bytes `0`
- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/sky130_capacitive_isolation_frontend_extracted.spice` present `True` bytes `853`

### model_or_corner_file

- present: `True`
- why: the rerun must say which process model and corner equations produced the numbers
- `evidence/aimc-simulator-adapters/candidate-post-layout/models/sky130-capacitive-isolation-ngspice.includes` present `True` bytes `229`
- `evidence/aimc-simulator-adapters/candidate-post-layout/models/sky130-ngspice.includes` present `False` bytes `0`

### post_layout_both_polarity_rerun

- present: `True`
- why: the schematic both-polarity pass must be repeated after extraction because parasitics change the sampled nodes
- `evidence/aimc-simulator-adapters/candidate-post-layout/rerun/sky130-capacitive-isolation-post-layout-both-polarity.json` present `True` bytes `3003`

### offset_noise_record

- present: `False`
- why: kickback alone does not prove comparator input-referred offset or noise
- `evidence/aimc-simulator-adapters/candidate-post-layout/rerun/sky130-capacitive-isolation-offset-noise.json` present `False` bytes `0`

### drc_lvs_record

- present: `False`
- why: a physical-cell claim needs a check that the drawn object matches the intended circuit and process rules
- `evidence/aimc-simulator-adapters/candidate-post-layout/models/sky130-capacitive-isolation-drc-lvs.json` present `False` bytes `0`

## Refused Claim

does not treat the starter layout or extracted RC netlist as accepted comparator evidence, does not run DRC/LVS, does not prove noise, and does not write accepted evidence
