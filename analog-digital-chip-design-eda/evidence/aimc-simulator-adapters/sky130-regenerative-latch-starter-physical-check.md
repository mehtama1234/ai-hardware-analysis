# Sky130 Regenerative Latch Starter Physical Check

- status: `regenerative_latch_starter_extracted_drc_clean_feedback_verified_not_transient_or_converter_signoff`
- DRC errors: `0`
- extracted NFET devices: `4`
- named nets present: `{'sense_p': True, 'sense_n': True, 'out_p': True, 'out_n': True, 'tail': True}`

This is the first real-device regenerative-latch physical slice. Magic extraction records distinct input/output/common-tail nets and the intended feedback-gate labels. Output-to-gate feedback routing, transient regeneration, and full comparator/converter acceptance remain open.

## Refused Claim

does not prove transient regeneration, comparator noise/offset, LVS against a schematic, SAR conversion, full converter signoff, or accepted post-layout evidence
