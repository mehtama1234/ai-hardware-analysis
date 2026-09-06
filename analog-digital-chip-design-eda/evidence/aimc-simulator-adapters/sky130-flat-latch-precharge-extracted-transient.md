# Sky130 Flat Extracted Latch plus Precharge Transient

- status: `flat_extracted_latch_precharge_transient_open`
- measured cases: `4` of `4`
- passing cases: `2`

This uses the exact flat Magic-extracted six-device topology and extracted capacitors, with bounded structural MOS models. The physical PMOS reset pair is active during the reset interval and released before evaluation.

| input differential mV | final output differential V | polarity | regenerated |
|---:|---:|---|---|
| `-10.0` | `1.35267` | `True` | `True` |
| `-0.5` | `1.34646` | `True` | `True` |
| `0.5` | `1.3458` | `False` | `True` |
| `10.0` | `1.33944` | `False` | `True` |

## Refused Claim

does not prove Sky130-model convergence, noise, mismatch, kickback, LVS, PVT yield, SAR conversion, or converter acceptance
