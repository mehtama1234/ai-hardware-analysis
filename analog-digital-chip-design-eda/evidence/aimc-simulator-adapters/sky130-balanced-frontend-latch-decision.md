# Sky130 Balanced Frontend Latch Decision

- status: `balanced_frontend_latch_decision_open_sense_signal_too_small`
- extracted frontend sign-preserved cases: `4` of `4`
- minimum absolute sense differential V: `1.500000000e-05`
- ideal latch input target V: `1.529705854e-04`
- minimum sense-to-latch-input ratio: `0.098058`
- accepted ready now: `False`

## First Principle

The extracted balanced frontend now preserves sign, but a sign is not the same as a digital decision. A latch needs enough input difference before its positive feedback starts. If the frontend gives the latch a much smaller difference than the already-tested latch target, the correct claim is not that the comparator works. The correct claim is that the sense handoff is promising but too small to accept without a real latch rerun.

This page compares two measured objects. The earlier latch proxy passed when driven by the full target-edge input difference. The extracted balanced frontend gives only the sense-node difference measured after extraction. That sense difference is roughly one-tenth of the latch target, so latch decision remains an open gate.

## Results

| reset mode | input diff mV | sense diff after V | sign preserved | sense-to-latch-target ratio |
|---|---:|---:|---|---:|
| `quiet_vcm` | `-0.152971` | `-1.600000000e-05` | `True` | `0.104595` |
| `quiet_vcm` | `0.152971` | `1.500000000e-05` | `True` | `0.098058` |
| `reset_pulse` | `-0.152971` | `-1.600000000e-05` | `True` | `0.104595` |
| `reset_pulse` | `0.152971` | `1.500000000e-05` | `True` | `0.098058` |

## Next Gate

The next proof has to either strengthen the extracted sense-node differential or rerun a bounded latch fixture that resolves from this smaller sense-node input. Until then, the digital governor cannot treat this frontend as accepted comparator evidence.

## Refused Claim

does not prove latch resolution from the extracted sense nodes, extracted latch layout, active reset devices, comparator offset, comparator noise, DRC/LVS, SAR conversion, or accepted post-layout converter evidence
