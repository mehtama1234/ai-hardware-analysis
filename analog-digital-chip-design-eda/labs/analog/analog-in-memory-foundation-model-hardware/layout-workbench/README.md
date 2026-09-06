# Analog Converter Layout Starter Package

This folder is a starting workbench for the converter layout pass. It is not post-layout evidence.

The source SPICE decks already check converter behavior. This folder names the physical cells, extraction command shape, and measurement record shape needed before the strict post-layout payload can be filled.

## Physical Objects

- `row_dac_10b`: row-drive DAC path for the 10-bit input target.
- `sar_readout_12b`: sample path, comparator path, and SAR readout boundary for the 12-bit output target.
- `shared_converter_mux`: mux and loading path for the shared converter rule.
- `aimc_converter_macro`: top boundary that contains DAC, ADC, references, mux, and sample path.

## Rule

Do not copy these starter files into `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/` as if they were extracted. The candidate folder needs real extracted SPICE, DSPF, or SPEF plus the model/setup files and break-even rerun from the same run.

## Local Toolchain Handoff

The repository does not replace system EDA tools. A compatible local toolchain can
be selected explicitly before running the checks:

```sh
export PDK_ROOT=/home/mehtama1/eda-tools/pdks
export MAGIC_BIN=/home/mehtama1/eda-tools/magic-8.3.682/bin/magic
export NETGEN_BIN=/home/mehtama1/eda-tools/netgen-1.5/bin/netgen
bash labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/run-layout-env-check.sh
```

The current local builds are Magic `8.3.682` and Netgen `1.5.323`. The checker
requires Magic `8.3.411` or newer because the installed Sky130 technology file
uses that techfile format. It also requires Netgen before an LVS result can be
considered.

The starter extraction and cap-only RC transient are useful toolchain smoke
tests. They do not prove that the named converter has active transistor
circuitry, that a schematic matches the layout, or that post-layout SAR behavior
is accepted. Those claims require active converter geometry, a real schematic
netlist, a PDK-aware LVS setup, and same-run extracted transient measurements.
