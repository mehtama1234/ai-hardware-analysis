# Sky130 Comparator Input-Stage Ngspice

- status: `sky130_comparator_input_stage_polarity_proxy_passed_not_latch_or_noise_proof`
- topology: `resistively_loaded_sky130_nfet_differential_pair_with_ideal_tail_bias`
- PDK model library: `/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice`
- generated deck: `labs/analog/analog-in-memory-foundation-model-hardware/spice/sky130_comparator_input_stage.sp`
- target combined offset/noise mV: `0.1530`
- hard budget mV: `0.1567`
- estimated static zero crossing mV: `0.000000000e+00`
- polarity pass count: `6` of `6`
- all cases correct polarity: `True`
- offset proxy passes target: `True`
- candidate post-layout written: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-comparator-input-stage-ngspice.csv`

## First Principle

A comparator starts as a sign test. Two nearby voltages enter a circuit. The circuit must turn the larger one into the correct side of an output difference.

This fixture tests only that first piece. It uses a Sky130 nfet differential pair with ideal tail bias and resistive loads. The input difference is swept around the tiny budget left by the measured sample-and-hold candidate. If the output polarity flips at the right place, the input stage is at least pointing in the correct direction.

This is much weaker than a real ADC comparator. It is not a clocked latch. A real comparator must latch, reject kickback, resolve before the SAR bit deadline, and survive device mismatch and noise. This page exists to make the next transistor step executable without pretending that a simple input pair is the finished decision circuit.

## Results

| case | input diff mV | outp V | outn V | output diff V | gain V/V | polarity correct |
|---|---:|---:|---:|---:|---:|---|
| `negative_hard_budget_edge` | `-0.156727` | `0.800721000` | `0.799278800` | `-1.442200000e-03` | `9.202014` | `True` |
| `negative_target_edge` | `-0.152971` | `0.800703700` | `0.799296100` | `-1.407600000e-03` | `9.201769` | `True` |
| `negative_half_target` | `-0.076485` | `0.800351800` | `0.799648000` | `-7.038000000e-04` | `9.201769` | `True` |
| `positive_half_target` | `0.076485` | `0.799648000` | `0.800351800` | `7.038000000e-04` | `9.201769` | `True` |
| `positive_target_edge` | `0.152971` | `0.799296100` | `0.800703700` | `1.407600000e-03` | `9.201769` | `True` |
| `positive_hard_budget_edge` | `0.156727` | `0.799278800` | `0.800721000` | `1.442200000e-03` | `9.202014` | `True` |

## Refused Claim

does not prove a clocked comparator latch, comparator noise, kickback, metastability, SAR conversion, extracted layout, DRC/LVS signoff, or accepted replacement economics
