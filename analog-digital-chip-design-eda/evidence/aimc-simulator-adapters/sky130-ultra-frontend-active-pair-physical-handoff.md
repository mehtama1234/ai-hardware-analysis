# Sky130 Ultra Frontend to Active Pair Physical Handoff

- status: `physical_passive_to_active_handoff_extracted_drc_clean_not_converter_signoff`
- cell: `sky130_ultra_frontend_active_pair_flat`
- DRC errors: `0`
- extracted: `True`
- active devices: `2`
- sense-P gate connected: `True`
- sense-N gate connected: `True`
- sense-P/N short equivalence: `False`

The flat composite layout places the passive ultra-sense frontend beside the real transistor isolation pair and routes each sense net through explicit contact stacks. Magic extraction records the transistor gates on the named sense-P and sense-N nets without a sense-P/N short. This remains a sub-block result, not full converter acceptance.

## Refused Claim

does not prove latch resolution, SAR conversion, full converter LVS, post-layout metrics, robustness, or accepted converter evidence
