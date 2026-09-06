# Converter Starter DRC Audit

This page records the first DRC-enabled check of the four named layout-workbench starter cells. It is intentionally separate from converter acceptance: the cells are still architectural placeholders, and a DRC-clean placeholder is not a valid DAC, ADC, or SAR layout.

The reproducible command is:

```text
python3 scripts/run_converter_starter_drc_audit.py
```

The generated evidence is `evidence/aimc-simulator-adapters/converter-starter-drc-audit.json` and `converter-starter-drc-audit.md`. The audit records each Magic return code and parsed DRC error count. It does not run LVS, extracted converter simulation, or post-layout acceptance.

## Refused claim

This audit does not prove a real converter layout, LVS, extracted DAC/comparator behavior, matching, parasitic accuracy, area, energy, or accepted post-layout evidence.
