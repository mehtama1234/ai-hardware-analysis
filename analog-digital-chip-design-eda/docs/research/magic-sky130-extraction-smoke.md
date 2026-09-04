# Magic Sky130 Extraction Smoke

This page proves only the local Magic extraction path.

It creates a tiny non-converter Sky130 layout cell in a separate smoke-test folder, extracts it, and writes SPICE. That answers one narrow question: can the installed Magic and Sky130 setup produce an extracted circuit file on this machine?

It does not prove the AIMC converter. The real converter still requires `row_dac_10b`, `sar_readout_12b`, `shared_converter_mux`, and `aimc_converter_macro`, followed by extracted converter netlists, area records, and a same-run break-even rerun.
