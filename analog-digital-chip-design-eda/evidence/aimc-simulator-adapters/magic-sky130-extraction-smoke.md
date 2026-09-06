# Magic Sky130 Extraction Smoke

- status: `magic_sky130_extraction_smoke_passed_not_converter_evidence`
- passed: `True`
- smoke dir: `labs/analog/analog-in-memory-foundation-model-hardware/tool-smoke/magic-sky130-extraction`
- PDK Magic rc present: `True`
- writes candidate post-layout evidence: `False`

## First Principle

Before a real converter can be extracted, the tool must be able to read the process rules, save a layout cell, derive an extracted circuit view, and write SPICE. This smoke test proves only that tool path.

It uses a tiny metal wire, not a converter. That keeps the tool proof separate from the circuit proof.

## Command

`/home/mehtama1/eda-tools/magic-8.3.682/bin/magic -dnull -noconsole -rcfile /home/mehtama1/eda-tools/pdks/sky130A/libs.tech/magic/sky130A.magicrc /home/mehtama1/git-repo/ai-hardware-analysis/analog-digital-chip-design-eda/labs/analog/analog-in-memory-foundation-model-hardware/tool-smoke/magic-sky130-extraction/run-smoke.tcl`

## Outputs

- magic_cell: `labs/analog/analog-in-memory-foundation-model-hardware/tool-smoke/magic-sky130-extraction/aimc_magic_smoke_wire.mag` present `True` bytes `142`
- extract_file: `labs/analog/analog-in-memory-foundation-model-hardware/tool-smoke/magic-sky130-extraction/aimc_magic_smoke_wire.ext` present `True` bytes `559`
- spice_file: `labs/analog/analog-in-memory-foundation-model-hardware/tool-smoke/magic-sky130-extraction/aimc_magic_smoke_wire.spice` present `True` bytes `154`

## Refused Claim

does not prove a DAC, ADC, mux, converter macro, extracted converter payload, area record, break-even rerun, or accepted post-layout evidence
