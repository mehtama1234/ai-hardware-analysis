# Converter Post-Layout Readiness

This file turns the completed local converter SPICE handoff into the next stricter gate.

- status: `local_converter_handoff_complete_post_layout_not_ready`
- local converter handoff complete: `True`
- claim-ready to replace break-even: `False`
- current measurement level: `circuit_simulation`
- missing replacement items: `10`

## First-Principles Reading

A clean SPICE load model answers whether the chosen converter target is internally coherent. Post-layout evidence answers a different question: whether the same circuit still works after wires, device sizes, parasitic capacitance, routing resistance, reference paths, and physical area are present.

The break-even table is about cost. Cost cannot be replaced by a schematic-level or load-model number if layout changes capacitance, routing, area, or timing. The replacement artifact must therefore carry post-layout energy, extracted latency, extracted noise, extracted area, and the same sharing rule into the break-even calculation.

## Completed Local Handoff Tests

- `row_dac_settling_spice_passes_simple_load`
- `sar_readout_spice_passes_simple_sample_load`
- `shared_converter_loading_spice_passes_simple_mux_load`
- `converter_supply_energy_spice_complete_simple_load`

## Missing Before Break-Even Replacement

- extracted parasitic netlist for row DAC, SAR readout, shared mux, references, and sample path
- post-layout simulation command, process corner, voltage, temperature, and model files
- post-layout ADC energy per conversion on a named rail
- post-layout DAC energy per row drive on a named rail
- post-layout mux and reference energy tied to the same conversion window
- post-layout settling time and conversion time for the same 10-bit input and 12-bit output target
- post-layout output noise RMS and input-referred noise under the 0.004 output-noise budget
- extracted ADC and DAC area in square micrometers
- explicit sharing rule for 64 rows, 4 columns, 4 converter instances, and 16 outputs per conversion cost
- rerun break-even table using the extracted energy, latency, area, sharing, and noise values

## Refused Claim

does not claim post-layout extraction exists, does not claim DRC/LVS signoff, does not claim measured silicon, and does not upgrade board energy
