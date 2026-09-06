# Sky130 Corrected-Convention Capacitive Isolation Confirm

- status: `corrected_convention_capacitive_isolation_characterized_not_ready`
- output definition: `outp_minus_outn`
- case count: `4`
- measured case count: `0`
- timed-out case count: `4`
- passing case count: `0`
- confirmed coupling caps fF: ``
- half LSB 12b V: `2.197265625e-04`
- worst sampled differential kickback V: `not measured`
- minimum abs output diff V: `not measured`
- uses capacitive input isolation: `True`
- uses sampled nodes: `True`
- uses corrected latch output convention: `True`
- accepted post-layout written: `False`

## First Principle

The direct latch gate was too heavy for the sampled node. A tiny coupling capacitor changes the readout job: the sampled node no longer has to directly drive the latch transistor gate. It only has to move a small internal gate node enough for the latch to choose a side.

This run keeps the sampled nodes connected, keeps the corrected `outp - outn` output convention, and tests the two capacitor values that previously looked useful. The proof target is narrow: both signs must resolve and sampled-node movement must stay below half of one 12-bit LSB.

## Results

| cap fF | input diff mV | kickback V | half LSB V | output diff V | resolved | kickback pass |
|---:|---:|---:|---:|---:|---:|---:|
| `None` | `-0.15297058540778352` | failed | failed | failed | `False` | `False` |
| `None` | `0.15297058540778352` | failed | failed | failed | `False` | `False` |
| `None` | `-0.15297058540778352` | failed | failed | failed | `False` | `False` |
| `None` | `0.15297058540778352` | failed | failed | failed | `False` | `False` |

## Boundary

does not prove comparator noise, offset statistics, SAR bit cycling, extracted layout, DRC/LVS, or accepted post-layout converter evidence
