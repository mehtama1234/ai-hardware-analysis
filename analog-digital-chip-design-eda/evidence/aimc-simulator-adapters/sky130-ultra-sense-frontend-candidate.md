# Sky130 Ultra Sense Frontend Candidate

- status: `ultra_sense_candidate_transfer_still_below_latch_target`
- direct sample-to-sense capacitance fF: `0.800000`
- direct coupling improvement over balanced starter: `9.11x`
- minimum sample-to-sense transfer ratio: `0.437908`
- required transfer target: `1.000000`
- passing sign cases: `4` of `4`

## First Principle

The last target said the frontend needed a bigger sense-node signal, not merely a cleaner sign. This candidate moves the sample and sense conductors closer together on both sides, then extracts the actual capacitance.

The useful question is not whether the drawing looks more symmetric. The useful question is whether the extracted circuit sends more of the sampled voltage difference to the sense nodes while preserving both signs.

## Physical Result

| quantity | value |
|---|---:|
| `sense_p` total capacitance | `3.292970 fF` |
| `sense_n` total capacitance | `3.292970 fF` |
| sense capacitance delta | `0.000000 fF` |
| sample_p to sense_p | `0.800000 fF` |
| sample_n to sense_n | `0.800000 fF` |

## Transient Result

| reset mode | input diff mV | sense diff after V | transfer ratio | sign preserved |
|---|---:|---:|---:|---|
| `quiet_vcm` | `-0.152971` | `-6.700000000e-05` | `0.437908` | `True` |
| `quiet_vcm` | `0.152971` | `6.700000000e-05` | `0.437908` | `True` |
| `reset_pulse` | `-0.152971` | `-6.700000000e-05` | `0.437908` | `True` |
| `reset_pulse` | `0.152971` | `6.700000000e-05` | `0.437908` | `True` |

## Next Gate

This ultra candidate gets closer, but transfer is still below the latch target. The next physical move should reduce wasted sense capacitance or add a measured preamp/buffer.

## Refused Claim

does not prove latch resolution, active reset devices, comparator offset, comparator noise, DRC/LVS, SAR conversion, or accepted post-layout converter evidence
