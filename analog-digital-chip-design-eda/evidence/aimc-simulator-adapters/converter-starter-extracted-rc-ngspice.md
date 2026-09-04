# Converter Starter Extracted RC Ngspice

- status: `starter_extracted_rc_ngspice_passed_not_converter_proof`
- source netlist: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/aimc_converter_macro_layout_smoke.spice`
- generated deck: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/aimc_converter_macro_extracted_rc_step.sp`
- ngspice returncode: `0`
- row final V: `1.800000000`
- column peak V: `0.017524010`
- digital peak V: `0.001089334`
- row 90 when s: `1.199360e-10`
- row 99 when s: `1.243690e-10`
- row 90 to 99 s: `4.433000e-12`
- candidate post-layout written: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/converter-starter-extracted-rc-ngspice.csv`

## First Principle

A node changes voltage only when charge moves onto or off of capacitance. The extracted Magic netlist gives the capacitances. The added resistors say how hard the outside circuit can push or pull those nodes. SPICE is now solving time-domain charge movement through that network instead of only using a one-line RC estimate.

This proves a narrow thing: the starter macro boundary can be driven as an extracted RC load in ngspice, and the row-drive node reaches the requested voltage in this fixture. It does not prove a row DAC, a SAR ADC, a mux switch stack, or a replacement decision.

## Refused Claim

does not simulate transistor converter behavior, comparator offset, DAC linearity, ADC decision error, supply current integration, DRC/LVS signoff, or accepted replacement economics
