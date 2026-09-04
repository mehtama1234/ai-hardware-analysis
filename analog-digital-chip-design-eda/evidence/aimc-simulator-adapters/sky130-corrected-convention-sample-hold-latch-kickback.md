# Sky130 Corrected-Convention Sample-Hold Latch Kickback

- status: `corrected_convention_coupled_kickback_characterized_not_ready`
- topology: `differential_dummy_sample_hold_driving_clocked_sky130_latch_input_pair_with_outp_minus_outn_output_contract`
- output definition: `outp_minus_outn`
- case count: `2`
- measured case count: `2`
- timed-out case count: `0`
- resolved correct polarity count: `0`
- kickback below half LSB count: `0`
- half LSB 12b V: `2.197265625e-04`
- worst sampled differential kickback V: `1.197690000e-02`
- all cases pass coupled gate: `False`
- uses sampled nodes: `True`
- uses corrected latch output convention: `True`
- accepted post-layout written: `False`

## First Principle

The latch can only become a converter bit after two separate questions are true. First, the rail naming must match the source signal. Second, the latch clock must not disturb the sampled analog value too much.

The prior convention diagnostic answered the first question: the digital sign is `outp - outn`. This run keeps the same coupled sample-hold and latch fixture, applies that convention, and measures the sampled differential value before and after latch evaluation.

If the latch resolves correctly but the sampled-node movement is larger than half of one 12-bit LSB, the converter is still not ready. The sign is readable, but the act of reading changes the stored value too much.

## Results

| case | input diff mV | sampled diff before V | sampled diff after V | kickback V | output diff V | resolved | kickback pass |
|---|---:|---:|---:|---:|---:|---:|---:|
| `negative_target_edge` | `-0.152971` | `-4.900000000e-05` | `1.192790000e-02` | `1.197690000e-02` | `1.304808000e+00` | `False` | `False` |
| `positive_target_edge` | `0.152971` | `4.900000000e-05` | `-1.192790000e-02` | `1.197690000e-02` | `-1.304808000e+00` | `False` | `False` |

## Boundary

does not prove comparator noise, input-referred offset statistics, SAR bit cycling, extracted layout, DRC/LVS, or accepted post-layout converter evidence
