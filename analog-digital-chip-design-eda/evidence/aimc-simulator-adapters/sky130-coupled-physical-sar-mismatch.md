# Sky130 Coupled Physical SAR Mismatch

- status: `same_topology_controlled_mismatch_characterized_not_statistical_yield_proof`
- topology: `pmos_only_to_vdd`
- representative codes: `(0, 2, 4, 6, 7)`
- measured cases: `20` of `20`
- timed out cases: `0`
- correct comparator polarities: `20` of `20`

| mismatch case | measured | polarity | top-plate range V | minimum sampled spacing V |
| --- | ---: | ---: | ---: | ---: |
| `matched_nominal` | `5/5` | `5/5` | `0.002633..0.840764` | `0.119902` |
| `msb_plus_2pct` | `5/5` | `5/5` | `0.002648..0.832013` | `0.118537` |
| `lsb_minus_2pct` | `5/5` | `5/5` | `0.002631..0.839487` | `0.117634` |
| `switch_minus_10pct` | `5/5` | `5/5` | `0.002652..0.840523` | `0.119857` |

This controlled sweep tests sensitivity of the selected topology. It is not a substitute for the 100-trial mismatch requirement in the acceptance contract; those trials must eventually run through calibrated SAR decisions, not only one-cycle polarity checks.

## Refused Claim

does not prove random mismatch yield, 100-trial acceptance, noise, PVT closure, continuous SAR, extracted layout, board behavior, or silicon
