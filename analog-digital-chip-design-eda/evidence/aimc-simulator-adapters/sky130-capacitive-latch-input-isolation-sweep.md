# Sky130 Capacitive Latch Input Isolation Sweep

- status: `sky130_capacitive_latch_input_isolation_found_candidate_not_noise_or_layout_proof`
- topology: `coupled_sample_hold_with_capacitive_latch_input_isolation`
- target combined offset/noise mV: `0.1530`
- hard kickback limit V: `2.197265625e-04`
- recommended kickback target V: `1.098632813e-04`
- best coupling capacitor fF: `0.09999999999999999`
- best kickback V: `1.191000000e-04`
- best resolved correct polarity: `True`
- passing candidate count: `2`
- candidate post-layout written: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-capacitive-latch-input-isolation-sweep.csv`

## First Principle

Direct latch input gates moved the sampled nodes because the sampled capacitors were tied to a fast regenerative circuit. A coupling capacitor tries to separate those two jobs. The sample-and-hold keeps the original charge. A smaller internal input node receives only enough of the voltage difference to steer the latch.

This is a trade. A smaller coupling capacitor should reduce kickback, but it may also starve the latch of signal. The useful question is whether any tested capacitor keeps sampled-node movement below the half-LSB line while the latch still resolves with the correct polarity.

## Results

| coupling cap fF | kickback V | hard limit V | gate diff after V | output diff V | resolved | kickback pass |
|---:|---:|---:|---:|---:|---|---|
| `0.100` | `1.191000000e-04` | `2.197265625e-04` | `3.049767700e-01` | `1.369890000e+00` | `True` | `True` |
| `0.200` | `2.022000000e-04` | `2.197265625e-04` | `2.591442800e-01` | `1.365390000e+00` | `True` | `True` |
| `0.500` | `3.474000000e-04` | `2.197265625e-04` | `1.782696300e-01` | `1.356270000e+00` | `True` | `False` |
| `1.000` | `4.557000000e-04` | `2.197265625e-04` | `1.171825700e-01` | `1.357760000e+00` | `True` | `False` |
| `2.000` | `5.393000000e-04` | `2.197265625e-04` | `6.964144000e-02` | `1.363630000e+00` | `True` | `False` |

## Refused Claim

does not prove comparator noise, offset statistics, SAR bit cycling, extracted layout, DRC/LVS signoff, or accepted replacement economics
