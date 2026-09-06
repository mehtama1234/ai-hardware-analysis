# Sky130 PMOS Precharge Pair Physical Check

- status: `pmos_precharge_pair_extracted_drc_clean_not_latch_or_converter_signoff`
- DRC errors: `0`
- extracted PMOS devices: `2`
- named nets: `{'vdd': True, 'precharge_p': True, 'precharge_n': True, 'reset': True}`

This is a matched PMOS precharge physical starter for the latch reset phase. It is separate from the latch until an integrated parent route and extracted transient are demonstrated.

## Refused Claim

does not prove integrated latch routing, reset timing, transient regeneration, noise, mismatch, LVS, PVT yield, SAR conversion, or converter acceptance
