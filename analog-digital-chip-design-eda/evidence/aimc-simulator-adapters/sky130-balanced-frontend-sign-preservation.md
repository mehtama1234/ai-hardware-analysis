# Sky130 Balanced Frontend Sign Preservation

- status: `balanced_extracted_frontend_preserves_sign_not_comparator_proof`
- passing case count: `4`
- case count: `4`
- extracted frontend: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/sky130_balanced_capacitive_isolation_frontend_extracted.spice`

## First Principle

The balanced starter cell is still not a comparator. This test asks one smaller question: after extraction, does the physical frontend carry the sign of the sampled difference onto `sense_p - sense_n`?

A zero or wrong sign here means the layout is balanced but not useful yet. A correct sign only means the sense-node handoff is plausible; active reset devices, latch resolution, offset/noise, DRC, and LVS are still separate gates.

## Results

| reset mode | input diff mV | sample diff after V | sense diff before V | sense diff after V | expected sign | measured sign | sign preserved |
|---|---:|---:|---:|---:|---:|---:|---|
| `quiet_vcm` | `-0.152971` | `-1.530000000e-04` | `-1.540000000e-05` | `-1.600000000e-05` | `-1` | `-1` | `True` |
| `quiet_vcm` | `0.152971` | `1.530000000e-04` | `1.540000000e-05` | `1.500000000e-05` | `1` | `1` | `True` |
| `reset_pulse` | `-0.152971` | `-1.530000000e-04` | `-1.500000000e-05` | `-1.600000000e-05` | `-1` | `-1` | `True` |
| `reset_pulse` | `0.152971` | `1.530000000e-04` | `1.500000000e-05` | `1.500000000e-05` | `1` | `1` | `True` |

## Refused Claim

does not prove active reset devices, latch resolution, comparator offset, comparator noise, DRC/LVS, SAR conversion, or accepted post-layout converter evidence
