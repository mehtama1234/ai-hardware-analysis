# Sky130 Polarity-Corrected Transistor Handoff

- status: `polarity_corrected_transistor_handoff_passed_schematic_sign_map_not_layout_or_strict`
- source transistor status: `transistor_active_isolation_preamp_failed_schematic`
- polarity contract: `converter_positive_input_is_negative_raw_preamp_output_diff`
- setting count: `3`
- case count: `6`
- passing setting count: `2`
- first passing setting: `medium_iso_pair_8ua`
- best setting: `medium_iso_pair_8ua`
- best minimum abs polarity-corrected output diff V: `7.932000000e-04`
- output margin target V: `5.000000000e-04`
- reruns ngspice: `False`
- accepted post-layout written: `False`

## First Principle

A signed analog value is not only a voltage size. It is a voltage size plus a named direction. If the circuit always turns positive input into negative output and negative input into positive output, the circuit is not random. It is inverted.

That inversion can be useful only if the next block is told the truth. The converter contract must say which raw preamp side means positive model value. Then both signs are checked after that contract is applied.

This page does not create a new circuit result. It re-reads the measured transistor isolation/preamp result and asks whether a named polarity contract would make the already measured schematic satisfy sign and margin.

## Setting Summary

| setting | cases | sign pass after contract | margin pass after contract | min corrected output mV | min sense ratio |
|---|---:|---:|---:|---:|---:|
| `medium_iso_pair_8ua` | `2` | `2` | `2` | `0.793200` | `1.013072` |
| `small_iso_pair_4ua` | `2` | `2` | `2` | `0.624100` | `0.529412` |
| `tiny_iso_pair_2ua` | `2` | `2` | `0` | `0.206400` | `0.013072` |

## Boundary

does not prove a new circuit, layout, DRC/LVS, offset stability over corners, noise, latch decision, SAR conversion, post-layout converter energy, or accepted converter evidence
