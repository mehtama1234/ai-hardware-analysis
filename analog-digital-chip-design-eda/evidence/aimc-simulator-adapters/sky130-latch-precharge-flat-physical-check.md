# Sky130 Flat Latch plus PMOS Precharge Physical Check

- status: `flat_latch_precharge_extracted_drc_clean_not_transient_or_converter_signoff`
- DRC errors: `0`
- NMOS devices: `4`
- PMOS devices: `2`
- cross-coupled feedback present: `True`
- PMOS precharge pair present: `True`

The latch and PMOS precharge pair are flattened into one physical parent and checked by Magic. This remains a physical integration artifact until an extracted Sky130 clocked transient and matching LVS are complete.

## Refused Claim

does not prove clocked transient regeneration, Sky130-model convergence, noise, mismatch, LVS against a schematic, PVT yield, SAR conversion, or converter acceptance
