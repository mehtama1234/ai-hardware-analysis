# Sky130 Coupled Physical SAR PVT

- status: `same_topology_representative_pvt_characterized_not_full_pvt_sar_proof`
- topology: `pmos_only_to_vdd`
- representative codes: `(0, 2, 4, 6, 7)`
- measured cases: `5` of `5`
- timed out cases: `0`
- correct comparator polarities: `5` of `5`

| corner | measured | polarity | top-plate range V | minimum sampled spacing V |
| --- | ---: | ---: | ---: | ---: |
| `ss_minus20c_1p62v` | `5/5` | `5/5` | `0.002742..0.748990` | `0.110113` |

This is the first PVT artifact tied to the selected coupled PMOS-only topology. It is deliberately bounded to representative codes: the full 16-code calibration and five-code nominal SAR result remain separate artifacts, and mismatch/noise and continuous-SAR gates are still open.

## Refused Claim

does not prove all-code calibration at every corner, mismatch/noise yield, continuous multicycle SAR, extracted layout, board behavior, or silicon
