# Sky130 Flat Latch Input/Feedback Strength Sweep

- status: `flat_latch_input_strength_sweep_complete_not_physical_width_or_converter_signoff`
- measured cases: `80` of `80`
- passing cases: `0`

The sweep changes only structural model strengths of the extracted sense and feedback devices. It is a sizing target for the next physical revision, not physical evidence of changed transistor widths.

| input ratio | feedback ratio | passing cases | total cases |
|---:|---:|---:|---:|
| `1.0` | `0.25` | `0` | `4` |
| `1.0` | `0.5` | `0` | `4` |
| `1.0` | `0.75` | `0` | `4` |
| `1.0` | `1.0` | `0` | `4` |
| `2.0` | `0.25` | `0` | `4` |
| `2.0` | `0.5` | `0` | `4` |
| `2.0` | `0.75` | `0` | `4` |
| `2.0` | `1.0` | `0` | `4` |
| `4.0` | `0.25` | `0` | `4` |
| `4.0` | `0.5` | `0` | `4` |
| `4.0` | `0.75` | `0` | `4` |
| `4.0` | `1.0` | `0` | `4` |
| `6.0` | `0.25` | `0` | `4` |
| `6.0` | `0.5` | `0` | `4` |
| `6.0` | `0.75` | `0` | `4` |
| `6.0` | `1.0` | `0` | `4` |
| `8.0` | `0.25` | `0` | `4` |
| `8.0` | `0.5` | `0` | `4` |
| `8.0` | `0.75` | `0` | `4` |
| `8.0` | `1.0` | `0` | `4` |

## Refused Claim

does not prove changed physical widths, Sky130-model behavior, mismatch/noise, LVS, PVT yield, SAR conversion, or converter acceptance
