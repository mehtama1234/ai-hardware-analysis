# Sky130 Corrected-Convention Isolation Range Stress

- status: `corrected_convention_isolation_range_stress_passed_not_noise_or_layout_proof`
- output definition: `outp_minus_outn`
- case count: `12`
- measured case count: `12`
- timed-out case count: `0`
- passing case count: `12`
- tested coupling caps fF: `0.1, 0.2`
- tested input diff mV: `0.152971, 0.305941, 0.764853`
- worst sampled differential kickback V: `2.023000000e-04`
- half LSB 12b V: `2.197265625e-04`
- minimum abs output diff V: `1.373291900e+00`
- accepted post-layout written: `False`

## First Principle

A comparator candidate that only works at one tiny input is fragile. The next question is whether the same isolated latch input still resolves when the sampled difference is moved above the target edge.

This run keeps the same tiny capacitive isolation and corrected `outp - outn` convention. It sweeps both signs at one, two, and five times the target-edge differential. The gate is still narrow: no noise, no layout, no SAR loop. It only asks whether nominal schematic behavior stays stable over a small useful range.

## Results

| cap fF | input diff mV | kickback V | output diff V | resolved | kickback pass |
|---:|---:|---:|---:|---:|---:|
| `0.100` | `-0.152971` | `1.191000000e-04` | `-1.373291900e+00` | `True` | `True` |
| `0.100` | `0.152971` | `1.191000000e-04` | `1.373291900e+00` | `True` | `True` |
| `0.100` | `-0.305941` | `1.191000000e-04` | `-1.373291900e+00` | `True` | `True` |
| `0.100` | `0.305941` | `1.191000000e-04` | `1.373291900e+00` | `True` | `True` |
| `0.100` | `-0.764853` | `1.191000000e-04` | `-1.373291900e+00` | `True` | `True` |
| `0.100` | `0.764853` | `1.191000000e-04` | `1.373291900e+00` | `True` | `True` |
| `0.200` | `-0.152971` | `2.022000000e-04` | `-1.373291900e+00` | `True` | `True` |
| `0.200` | `0.152971` | `2.022000000e-04` | `1.373291900e+00` | `True` | `True` |
| `0.200` | `-0.305941` | `2.022000000e-04` | `-1.373291900e+00` | `True` | `True` |
| `0.200` | `0.305941` | `2.022000000e-04` | `1.373291900e+00` | `True` | `True` |
| `0.200` | `-0.764853` | `2.023000000e-04` | `-1.373291900e+00` | `True` | `True` |
| `0.200` | `0.764853` | `2.023000000e-04` | `1.373291900e+00` | `True` | `True` |

## Boundary

does not prove comparator noise, offset statistics, clock timing margin, SAR bit cycling, extracted layout, DRC/LVS, or accepted post-layout converter evidence
