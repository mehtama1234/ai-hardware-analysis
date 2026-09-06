# Sky130 Wide-Input Weak-Feedback Physical Check

- status: `wide_input_weak_feedback_extracted_drc_clean_not_transient_or_converter_signoff`
- DRC errors: `0`
- NMOS devices: `4`
- PMOS devices: `2`
- extracted NMOS gate lengths: `[240, 120, 240, 120]`
- feedback present: `True`

This candidate widens the matched sense pair and lengthens the two feedback gates. It is a physical sizing experiment, not converter signoff.

## Refused Claim

does not prove improved transient polarity, Sky130-model behavior, LVS, noise, mismatch, PVT yield, SAR conversion, or converter acceptance
