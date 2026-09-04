# Sky130 Differential Dummy Candidate Offset Noise Stress

- status: `sky130_differential_dummy_candidate_offset_noise_stress_defined_not_comparator_proof`
- decision margin source: `sky130-differential-dummy-candidate-decision-margin`
- half LSB 12b V: `2.197265625e-04`
- sample-hold error V: `6.300000000e-05`
- remaining comparator offset or noise budget mV: `0.1567`
- case count: `20`
- passing case count: `17`
- failing case count: `3`
- max passing decision uncertainty mV: `0.1530`
- min failing decision uncertainty mV: `0.1581`
- candidate post-layout written: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-differential-dummy-candidate-offset-noise-stress.csv`

## First Principle

The comparator adds uncertainty to the same voltage that the sample-and-hold already moved. Offset is a fixed shift. Decision noise is a random spread. Before a transistor comparator is worth drawing, the combined uncertainty must fit inside the remaining half-LSB budget.

This table uses a conservative scalar check. It combines offset and RMS noise as one input-referred decision uncertainty, then adds that to the measured worst sample-hold error. It is a budget stress test, not a transistor-level comparator simulation.

## Stress Table

| comparator offset mV | decision noise RMS mV | decision uncertainty mV | total decision error V | remaining margin V | passes half LSB |
|---:|---:|---:|---:|---:|---|
| `0.00` | `0.00` | `0.0000` | `6.300000000e-05` | `1.567265625e-04` | `True` |
| `0.00` | `0.03` | `0.0300` | `9.300000000e-05` | `1.267265625e-04` | `True` |
| `0.00` | `0.05` | `0.0500` | `1.130000000e-04` | `1.067265625e-04` | `True` |
| `0.00` | `0.08` | `0.0800` | `1.430000000e-04` | `7.672656250e-05` | `True` |
| `0.00` | `0.10` | `0.1000` | `1.630000000e-04` | `5.672656250e-05` | `True` |
| `0.05` | `0.00` | `0.0500` | `1.130000000e-04` | `1.067265625e-04` | `True` |
| `0.05` | `0.03` | `0.0583` | `1.213095189e-04` | `9.841704355e-05` | `True` |
| `0.05` | `0.05` | `0.0707` | `1.337106781e-04` | `8.601588438e-05` | `True` |
| `0.05` | `0.08` | `0.0943` | `1.573398113e-04` | `6.238675118e-05` | `True` |
| `0.05` | `0.10` | `0.1118` | `1.748033989e-04` | `4.492316362e-05` | `True` |
| `0.10` | `0.00` | `0.1000` | `1.630000000e-04` | `5.672656250e-05` | `True` |
| `0.10` | `0.03` | `0.1044` | `1.674030651e-04` | `5.232349741e-05` | `True` |
| `0.10` | `0.05` | `0.1118` | `1.748033989e-04` | `4.492316362e-05` | `True` |
| `0.10` | `0.08` | `0.1281` | `1.910624847e-04` | `2.866407775e-05` | `True` |
| `0.10` | `0.10` | `0.1414` | `2.044213562e-04` | `1.530520626e-05` | `True` |
| `0.15` | `0.00` | `0.1500` | `2.130000000e-04` | `6.726562500e-06` | `True` |
| `0.15` | `0.03` | `0.1530` | `2.159705854e-04` | `3.755977092e-06` | `True` |
| `0.15` | `0.05` | `0.1581` | `2.211138830e-04` | `-1.387320509e-06` | `False` |
| `0.15` | `0.08` | `0.1700` | `2.330000000e-04` | `-1.327343750e-05` | `False` |
| `0.15` | `0.10` | `0.1803` | `2.432775638e-04` | `-2.355100127e-05` | `False` |

## Reading

The next comparator target is not a vague low-noise request. It must keep input-referred offset and decision noise under the measured remaining budget, or the passing sample-and-hold candidate no longer supports a 12-bit decision.

## Refused Claim

does not simulate comparator devices, noise spectra, metastability, SAR conversion, extracted layout, DRC/LVS signoff, or accepted replacement economics
