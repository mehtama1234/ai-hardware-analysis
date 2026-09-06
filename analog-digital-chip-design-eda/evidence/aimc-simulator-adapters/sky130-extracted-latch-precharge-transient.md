# Sky130 Extracted Latch Precharge Balance Sweep

- status: `extracted_latch_precharge_balance_sweep_open`
- measured cases: `28` of `28`
- passing cases: `14`
- capacitance sweep fF: `[0.0, 1.0, 2.0, 4.0, 6.2, 8.0, 10.0]`

Both extracted output nodes are precharged through behavioral switches before the differential decision. The sweep tests whether compensating the extracted output-node capacitance imbalance improves polarity; the switches and compensation capacitor are not physical signoff devices.

| balance cap fF | input differential mV | final output diff V | polarity | regenerated |
|---:|---:|---:|---|---|
| `0.0` | `-10.0` | `-1.0626` | `False` | `True` |
| `0.0` | `-0.5` | `-1.08041` | `False` | `True` |
| `0.0` | `0.5` | `-1.08225` | `True` | `True` |
| `0.0` | `10.0` | `-1.09976` | `True` | `True` |
| `1.0` | `-10.0` | `-1.05673` | `False` | `True` |
| `1.0` | `-0.5` | `-1.07438` | `False` | `True` |
| `1.0` | `0.5` | `-1.07625` | `True` | `True` |
| `1.0` | `10.0` | `-1.09386` | `True` | `True` |
| `2.0` | `-10.0` | `-1.04841` | `False` | `True` |
| `2.0` | `-0.5` | `-1.0667` | `False` | `True` |
| `2.0` | `0.5` | `-1.06859` | `True` | `True` |
| `2.0` | `10.0` | `-1.08629` | `True` | `True` |
| `4.0` | `-10.0` | `-1.02266` | `False` | `True` |
| `4.0` | `-0.5` | `-1.04293` | `False` | `True` |
| `4.0` | `0.5` | `-1.04466` | `True` | `True` |
| `4.0` | `10.0` | `-1.06388` | `True` | `True` |
| `6.2` | `-10.0` | `0.967004` | `True` | `True` |
| `6.2` | `-0.5` | `0.847484` | `True` | `True` |
| `6.2` | `0.5` | `0.818436` | `False` | `True` |
| `6.2` | `10.0` | `-0.400809` | `True` | `False` |
| `8.0` | `-10.0` | `1.0492` | `True` | `True` |
| `8.0` | `-0.5` | `1.02883` | `True` | `True` |
| `8.0` | `0.5` | `1.02664` | `False` | `True` |
| `8.0` | `10.0` | `1.0053` | `False` | `True` |
| `10.0` | `-10.0` | `1.07172` | `True` | `True` |
| `10.0` | `-0.5` | `1.05404` | `True` | `True` |
| `10.0` | `0.5` | `1.05209` | `False` | `True` |
| `10.0` | `10.0` | `1.03416` | `False` | `True` |

## Refused Claim

does not prove physical precharge devices, Sky130-model convergence, kickback/noise/mismatch, LVS, SAR conversion, or converter acceptance
