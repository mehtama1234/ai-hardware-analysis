# Sky130 Bootstrapped Switch Ngspice

- status: `sky130_bootstrapped_switch_characterized_not_converter_proof`
- topology: `idealized_input_referenced_bootstrapped_nfet_sample_switch`
- idealized bootstrap driver: `True`
- PDK model library: `/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice`
- generated deck: `labs/analog/analog-in-memory-foundation-model-hardware/spice/sky130_bootstrapped_switch.sp`
- case count: `3`
- measured case count: `3`
- timed out case count: `0`
- half LSB 12b V: `2.197265625e-04`
- worst acquisition abs error V: `0.000000000e+00`
- worst hold abs delta V: `1.045400000e-02`
- worst total abs error V: `1.045400000e-02`
- acquisition pass count: `3` of `3`
- hold delta pass count: `0` of `3`
- total error pass count: `0` of `3`
- candidate post-layout written: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-bootstrapped-switch-ngspice.csv`

## First Principle

A plain switch gets weaker when the input voltage moves closer to the fixed gate voltage. A bootstrapped switch attacks that by moving the gate with the input. The switch then sees a more constant gate-to-source voltage while sampling.

This fixture tests that idea in the simplest measurable way. The nfet switch is a Sky130 device, but the bootstrap driver is idealized. During sampling, the gate is driven near input plus supply. During hold, the gate is pulled back to zero. That is enough to ask whether constant overdrive helps the sample-and-hold problem before building a real bootstrap driver.

This is not a finished circuit. A real bootstrap needs devices that charge, hold, and discharge the gate safely. It must also respect oxide limits. This run is only a topology test.

## Results

| case | input V | boot V | acquired V | held V | acquisition error V | hold delta V | total error V |
|---|---:|---:|---:|---:|---:|---:|---:|
| low_bootstrap | `0.300000000` | `2.100000000` | `0.300000000` | `0.291491200` | `0.000000000e+00` | `8.508800000e-03` | `8.508800000e-03` |
| mid_bootstrap | `0.900000000` | `2.700000000` | `0.900000000` | `0.890543200` | `0.000000000e+00` | `9.456800000e-03` | `9.456800000e-03` |
| high_bootstrap | `1.500000000` | `3.300000000` | `1.500000000` | `1.489546000` | `0.000000000e+00` | `1.045400000e-02` | `1.045400000e-02` |

## Reading The Result

If acquisition improves but hold still fails, the switch has solved only the charging part. If hold improves too, the next task is to replace the idealized gate drive with a real bootstrap circuit and rerun the same low, mid, and high input checks.

## Refused Claim

does not prove a real bootstrap charge pump, reliability-safe gate voltage, comparator decision, SAR conversion, mismatch, noise, extracted transistor layout, DRC/LVS signoff, or accepted replacement economics
