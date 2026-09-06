# Sky130 Extracted Regenerative Latch Starter Transient

- status: `extracted_regenerative_latch_bistability_open`
- measured cases: `8` of `8`
- passing cases: `4`

This is a bounded extracted-netlist transient test with resistive loads. It sweeps both input polarity and initial output bias to distinguish regenerative bistability from one-sided startup. It is not comparator or converter signoff.

| input differential mV | initial output bias mV | final output differential V | polarity | regenerated |
|---:|---:|---:|---|---|
| `-0.5` | `-10.0` | `-1.07149` | `False` | `True` |
| `-0.5` | `10.0` | `1.07356` | `True` | `True` |
| `0.5` | `-10.0` | `-1.07347` | `True` | `True` |
| `0.5` | `10.0` | `1.07158` | `False` | `True` |
| `-10.0` | `-10.0` | `-1.05239` | `False` | `True` |
| `-10.0` | `10.0` | `1.09206` | `True` | `True` |
| `10.0` | `-10.0` | `-1.09197` | `True` | `True` |
| `10.0` | `10.0` | `1.05247` | `False` | `True` |

## Refused Claim

does not prove noise, mismatch, kickback budget, LVS against a schematic, PVT yield, SAR conversion, or accepted converter evidence
