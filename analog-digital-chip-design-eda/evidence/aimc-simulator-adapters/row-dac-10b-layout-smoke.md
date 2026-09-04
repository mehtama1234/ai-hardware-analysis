# Row DAC 10b Layout Smoke

- status: `row_dac_10b_layout_smoke_passed_not_candidate_evidence`
- cell: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/row_dac_10b.mag`
- cell present: `True`
- passed: `True`
- writes candidate post-layout evidence: `False`

## First Principle

The first physical step is not to claim converter quality. It is to make a named cell that the layout tool can read and turn into an extracted circuit file.

This cell is a starter row-drive boundary with rails, a row-drive node, and switch-column placeholders. It proves the extraction path for one named block, not the electrical correctness of a full 10-bit DAC.

## Command

`/home/mehtama1/eda-tools/magic/bin/magic -dnull -noconsole -rcfile /home/mehtama1/eda-tools/pdks/sky130A/libs.tech/magic/sky130A.magicrc /home/mehtama1/git-repo/analog-digital-chip-design-eda/labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/extract-row-dac-10b-smoke.tcl`

## Outputs

- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/row_dac_10b.ext` present `True` bytes `1217`
- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/row_dac_10b_layout_smoke.spice` present `True` bytes `256`

## Refused Claim

does not prove a production 10-bit DAC, matching, monotonicity, DRC clean signoff, LVS, area, accepted post-layout payload, or model replacement readiness
