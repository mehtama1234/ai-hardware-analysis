# Analog Converter Physical Cell Gate

This page is the acceptance boundary between a ready layout workbench and real converter layout evidence.

The workbench can have Magic, xschem, ngspice, Sky130 model files, helper scripts, and clear instructions. None of that is the converter. The converter begins to exist only when named physical cells are present and those cells can be extracted into files that affect the circuit equations.

The gate checks four cells:

- `row_dac_10b`
- `sar_readout_12b`
- `shared_converter_mux`
- `aimc_converter_macro`

It also checks the extracted netlist, model/area record, and same-run break-even rerun files that must follow those cells before the post-layout payload can be trusted.

Until this gate says the physical cells and extracted artifacts are present, the project can claim setup readiness, simulator readiness, and behavioral SPICE readiness. It cannot claim post-layout converter evidence.
