# Sky130 Measured Sense Differential Preamp

- status: `measured_sense_differential_preamp_passed_not_extracted_frontend_or_strict_evidence`
- uses measured frontend sense voltage: `True`
- uses extracted frontend transient: `False`
- uses Sky130 differential preamp: `True`
- case count: `2`
- measured case count: `2`
- timed-out case count: `0`
- sign pass count: `2`
- output margin pass count: `2`
- minimum abs preamp output diff V: `6.264000000e-04`
- minimum sense-to-preamp gain V/V: `9.349254`
- same-run strict payload ready: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-measured-sense-differential-preamp.csv`

## First Principle

The failed extracted-frontend preamp run mixed two possible causes: the preamp bias might be wrong, or the extracted frontend might become unstable when attached to the preamp gates. This runner removes the frontend and drives the preamp with the already measured sense voltages.

If this passes, the preamp can resolve the voltage in principle and the next problem is loading the extracted frontend. If this fails, the preamp bias itself is wrong and should be tuned before reconnecting the frontend.

## Results

| reset mode | input diff mV | sense diff uV | preamp output diff mV | gain V/V | sign preserved | margin pass |
|---|---:|---:|---:|---:|---|---|
| `reset_pulse` | `-0.152971` | `-67.000000` | `-0.626400` | `9.349254` | `True` | `True` |
| `reset_pulse` | `0.152971` | `67.000000` | `0.626400` | `9.349254` | `True` | `True` |

## Refused Claim

does not prove extracted frontend loading, latch behavior, SAR conversion, post-layout energy, DRC/LVS, or accepted converter evidence
