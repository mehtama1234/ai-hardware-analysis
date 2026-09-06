# Sky130 Coupled Physical SAR PVT

- status: `same_topology_representative_pvt_characterized_not_full_pvt_sar_proof`
- topology: `pmos_only_to_vdd`
- representative codes: `(0, 2, 4, 6, 7)`
- measured cases: `25` of `25`
- timed out cases: `0`
- correct comparator polarities: `25` of `25`
- reference profile: `{'tt_25c_1p80v': 0.604, 'ss_minus20c_1p62v': 0.58, 'ff_85c_1p98v': 0.604, 'sf_25c_1p80v': 0.604, 'fs_25c_1p80v': 0.604}`

| corner | measured | polarity | top-plate range V | minimum sampled spacing V |
| --- | ---: | ---: | ---: | ---: |
| `tt_25c_1p80v` | `5/5` | `5/5` | `0.002635..0.839503` | `0.118663` |
| `ss_minus20c_1p62v` | `5/5` | `5/5` | `0.002742..0.748990` | `0.110113` |
| `ff_85c_1p98v` | `5/5` | `5/5` | `0.002576..0.922052` | `0.130845` |
| `sf_25c_1p80v` | `5/5` | `5/5` | `0.002917..0.837723` | `0.120439` |
| `fs_25c_1p80v` | `5/5` | `5/5` | `0.002419..0.841852` | `0.120037` |

This is the first PVT artifact tied to the selected coupled PMOS-only topology. It is deliberately bounded to representative codes: the full 16-code calibration and five-code nominal SAR result remain separate artifacts, and mismatch/noise and continuous-SAR gates are still open.

## Refused Claim

does not prove all-code calibration at every corner, mismatch/noise yield, continuous multicycle SAR, extracted layout, board behavior, or silicon
