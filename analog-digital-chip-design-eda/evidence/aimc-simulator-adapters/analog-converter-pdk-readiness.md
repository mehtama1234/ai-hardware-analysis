# Analog Converter PDK Readiness

- status: `sky130_pdk_ready_first_converter_starter_cell_present`
- PDK root: `/home/mehtama1/eda-tools/pdks`
- PDK: `sky130A`
- all required PDK files present: `True`
- selected process corner: `tt`
- selected voltage V: `1.8`
- selected temperature C: `25`
- workbench has converter physical cells: `True`

## First Principle

A process file gives meaning to drawn shapes. Without it, a rectangle is only a drawing. With it, the tools can interpret layers, design rules, parasitic extraction, device models, and simulation corners. This audit proves that the local Sky130 process support is present, while also saying that the converter cells themselves still have to be drawn or imported.

## Required PDK Files

- magic_tech: `/home/mehtama1/eda-tools/pdks/ciel/sky130/versions/0fe599b2afb6708d281543108caf8310912f54af/sky130A/libs.tech/magic/sky130A.tech` exists `True` bytes `164660`
- magic_rc: `/home/mehtama1/eda-tools/pdks/ciel/sky130/versions/0fe599b2afb6708d281543108caf8310912f54af/sky130A/libs.tech/magic/sky130A.magicrc` exists `True` bytes `3713`
- xschem_rc: `/home/mehtama1/eda-tools/pdks/ciel/sky130/versions/0fe599b2afb6708d281543108caf8310912f54af/sky130A/libs.tech/xschem/xschemrc` exists `True` bytes `21397`
- ngspice_model_library: `/home/mehtama1/eda-tools/pdks/ciel/sky130/versions/0fe599b2afb6708d281543108caf8310912f54af/sky130A/libs.tech/ngspice/sky130.lib.spice` exists `True` bytes `6349`
- ngspice_tt_corner: `/home/mehtama1/eda-tools/pdks/ciel/sky130/versions/0fe599b2afb6708d281543108caf8310912f54af/sky130A/libs.tech/ngspice/corners/tt.spice` exists `True` bytes `2676`

## Candidate Payload Mapping

- simulation.model_files: `/home/mehtama1/eda-tools/pdks/ciel/sky130/versions/0fe599b2afb6708d281543108caf8310912f54af/sky130A/libs.tech/ngspice/sky130.lib.spice, /home/mehtama1/eda-tools/pdks/ciel/sky130/versions/0fe599b2afb6708d281543108caf8310912f54af/sky130A/libs.tech/ngspice/corners/tt.spice`
- simulation.process_corner: `sky130A_tt_1p8V_25C`
- simulation.voltage_v: `1.8`
- simulation.temperature_c: `25`
- extraction.parasitic_format: `extracted-spice`

## Next Real Actions

- create or import sky130A physical cells for row_dac_10b, sar_readout_12b, shared_converter_mux, and aimc_converter_macro
- run Magic DRC using the sky130A tech file
- run extraction against the named macro
- run ngspice with sky130.lib.spice and the tt corner
- copy the extracted netlist, model files, and same-run rerun into the candidate payload workspace

## Refused Claim

does not prove converter layout, DRC, LVS, extraction, post-layout simulation, measured silicon, or accepted evidence
