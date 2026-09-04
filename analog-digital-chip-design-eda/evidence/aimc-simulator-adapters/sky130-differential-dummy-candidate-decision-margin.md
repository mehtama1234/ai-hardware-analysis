# Sky130 Differential Dummy Candidate Decision Margin

- status: `sky130_differential_dummy_candidate_decision_margin_defined_not_converter_proof`
- input sweep source: `sky130-differential-dummy-candidate-input-sweep`
- mismatch sweep source: `sky130-differential-dummy-candidate-mismatch-sweep`
- half LSB 12b V: `2.197265625e-04`
- worst input-sweep differential hold V: `6.300000000e-05`
- worst mismatch-sweep differential hold V: `5.090000000e-05`
- worst sample-hold error V: `6.300000000e-05`
- remaining comparator offset or noise budget mV: `0.1567`
- max passing tested comparator offset mV: `0.15`
- candidate post-layout written: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-differential-dummy-candidate-decision-margin.csv`

## First Principle

A later comparator does not see the sample-and-hold error separately from its own offset and noise. It sees one decision voltage. If the sample-and-hold already spends part of the half-LSB budget, the comparator must fit inside what remains.

The measured candidate leaves a finite voltage margin. This page turns that margin into a simple offset and noise budget. It is not a comparator simulation. It is the arithmetic gate that says how accurate the comparator must be before a SAR proof is meaningful.

## Offset Budget Table

| comparator offset mV | sample-hold error V | total decision error V | remaining margin V | passes half LSB |
|---:|---:|---:|---:|---|
| `0.020` | `6.300000000e-05` | `8.300000000e-05` | `1.367265625e-04` | `True` |
| `0.050` | `6.300000000e-05` | `1.130000000e-04` | `1.067265625e-04` | `True` |
| `0.100` | `6.300000000e-05` | `1.630000000e-04` | `5.672656250e-05` | `True` |
| `0.150` | `6.300000000e-05` | `2.130000000e-04` | `6.726562500e-06` | `True` |
| `0.200` | `6.300000000e-05` | `2.630000000e-04` | `-4.327343750e-05` | `False` |

## Reading

The candidate is useful only if the next comparator can keep its input-referred offset and decision noise inside the remaining margin. If the comparator spends more than that, the sample-and-hold pass no longer matters because the combined decision error crosses the 12-bit line.

## Refused Claim

does not simulate comparator transistors, random noise, SAR conversion, extracted layout, DRC/LVS signoff, or accepted replacement economics
