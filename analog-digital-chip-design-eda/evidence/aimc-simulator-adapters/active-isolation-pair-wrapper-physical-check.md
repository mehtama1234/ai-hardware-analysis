# Active Isolation Pair Wrapper Physical Check

- status: `active_isolation_pair_wrapper_drc_extract_lvs_passed_not_converter_signoff`
- cell: `sky130_active_isolation_pair_wrapper`
- DRC errors: `0`
- extracted SPICE: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/sky130_active_isolation_pair_wrapper_extracted.spice`
- unique LVS match: `True`
- devices seen: `True`

This is a bounded hierarchical physical sub-block check. It connects the real transistor layout cell to a parent wrapper and verifies the extracted two-device topology. It is not full converter signoff.

## Refused Claim

does not prove the full converter, top-level connectivity, latch/SAR behavior, post-layout metrics, or accepted converter evidence
