# Magic Sky130 Compatibility

This page separates two blockers.

The first blocker is the missing converter layout: `row_dac_10b`, `sar_readout_12b`, `shared_converter_mux`, and `aimc_converter_macro` still do not exist.

The second blocker is tool compatibility. The installed Ubuntu Magic binary can be present and still be the wrong binary for this Sky130 extraction setup. The smoke test decides that by asking Magic to load Sky130 and extract a tiny non-converter cell.

If the smoke fails, the next tool action is to build a newer local Magic under `/home/mehtama1/eda-tools/magic` and rerun the smoke before attempting converter extraction.
