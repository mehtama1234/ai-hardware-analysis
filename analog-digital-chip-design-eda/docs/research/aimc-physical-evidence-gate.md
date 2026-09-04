# AIMC Physical Evidence Gate

This page is the physical boundary for the mixed analog/digital/SRAM workload
program. It distinguishes a measured circuit characterization from an accepted
analog converter.

## Required Evidence

The converter path must provide a complete coupled DAC/comparator bit sweep, a
same-condition calibration table, representative SAR conversions, endpoint and
source-common-mode checks, and a claim boundary that refuses unsupported
layout, board, and silicon conclusions.

## Current Result

| check | result |
| --- | --- |
| coupled DAC/comparator bit sweep | `16/16` measured; all polarities correct |
| full calibrated SAR artifact | `16/16` calibration codes; `20/20` comparisons; bounded characterization |
| high-code threshold map | codes `14` and `15` measured; spacing gate passes at `103.481 mV` minimum |
| legal-range gate | passes for the low-source candidate: `0.002633..1.799311 V` |
| logical-to-physical map gate | passes for the rank-preserving measured map |
| historical partial high-code probe | retained as historical `14,15` timeout evidence |
| differential endpoint probe | codes `0, 1, 14, 15`: `0/4` measured, `4/4` timed out |
| boosted source-switch endpoint probe | codes `0, 15`: `0/2` measured, `2/2` timed out |
| same-topology PVT diagnostic | `25/25` representative cases measured; `24/25` comparator polarities correct; slow/cold/low-supply code `6` fails polarity |
| slow/cold/low-supply margin probe | `7/7` cases measured; only `3/7` polarities correct; transition boundary is margin-sensitive near `35 mV` |
| same-topology controlled mismatch | `20/20` cases measured; `20/20` polarities correct across four controlled perturbation sets |
| continuous physical SAR candidate | one 400 ns transient at 20 ps step; five conversions and 20 decisions measured; continuous mapping is `0→0`, `2→0`, `4→3`, `6→6`, `7→7`; top-plate samples are legal, but bottom-plate nodes leave range |
| physical converter decision | blocked: `sar_source_common_mode` |

The low-source PMOS-only map is the first full 16-code coupled calibration to
converge with legal endpoints, adequate spacing, and a rank-preserving bijective
map. That calibrated, isolated SAR artifact passes its named representative
conversions; the newer continuous five-conversion candidate does not. In the
continuous run, codes `0`, `6`, and `7` match, while codes `2` and `4` do not,
and some internal bottom-plate nodes leave the supply range. The next revision
must fix the cycle-to-cycle charge-transfer and control mapping, then pass
all-code PVT, mismatch, noise, and continuous-SAR evidence before promotion.

## Reproduction

```bash
python3 scripts/validate_aimc_physical_evidence.py
python3 scripts/run_aimc_end_to_end_regression.py
```

The physical validator currently passes `16/16` consistency checks while keeping
the converter blocked. The end-to-end regression passes its software checks and
records the same physical gate.

## Claim Boundary

Allowed: measured Sky130 schematic-level DAC/comparator and bounded calibrated
SAR characterization under the named fixture conditions.

Not allowed: full-range physical converter acceptance, PVT/mismatch/noise yield,
continuous multicycle SAR proof, extracted layout, board runtime, measured
energy, calibrated silicon, or production readiness.
