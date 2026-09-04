# Magic Sky130 Compatibility

- status: `magic_sky130_extraction_path_ready_not_converter_evidence`
- system Magic: `/usr/bin/magic`
- system Magic version: `8.3.105`
- local Magic: `/home/mehtama1/eda-tools/magic/bin/magic`
- local Magic present: `True`
- local Magic version: `8.3.682`
- smoke status: `magic_sky130_extraction_smoke_passed_not_converter_evidence`
- smoke passed: `True`
- smoke return code: `0`
- smoke Magic binary: `/home/mehtama1/eda-tools/magic/bin/magic`

## First Principle

Extraction is a contract between the layout tool and the process file. If the tool cannot read the process extraction rules, it cannot turn shapes into circuit equations.

The converter cells are still missing, but this is a separate blocker: even a tiny non-converter extraction smoke currently fails with the installed Magic binary.

## Upgrade Command

`MAGIC_PREFIX=$HOME/eda-tools/magic MAGIC_SRC=$HOME/eda-tools/magic-src ./scripts/install_local_magic_from_source.sh`

## Observed Blocker

The local Magic binary is installed and the tiny Sky130 extraction smoke passes. The remaining blocker is the absence of real converter layout cells and extracted converter artifacts.

## Refused Claim

does not install tools by itself, does not create converter layout, and does not write post-layout evidence
