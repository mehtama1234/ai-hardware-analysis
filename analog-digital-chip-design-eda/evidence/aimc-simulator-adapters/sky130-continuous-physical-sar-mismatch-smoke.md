# Sky130 Continuous Physical SAR Mismatch Sweep

- status: `continuous_sar_mismatch_stress_measured_not_foundry_yield_proof`
- trials: `3/3`
- seed: `130`
- capacitor mismatch model: independent Gaussian perturbations around base scales `[1.0, 0.75, 1.0, 1.0]`, sigma `1.0%`
- full five-conversion code-map passes: `3/3`
- legal bottom-plate passes: `3/3`

## Purpose

Each trial runs the same continuous four-bit, five-conversion physical SAR transient used by the nominal candidate. Only the four binary DAC capacitor scales are perturbed. The seed and sigma are recorded so the exact trial population can be replayed.

## Trial Summary

| trial | scales | status | code map | map pass | bottom legal |
| ---: | --- | --- | --- | --- | --- |
| 0 | 0.99207, 0.74926, 0.99897, 0.98215 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 1 | 0.99873, 0.74874, 1.00057, 1.00907 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 2 | 1.01449, 0.74837, 0.98535, 0.99732 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |

## Interpretation

A full-map pass means all five representative conversions produced their expected retained code and the reported bottom-plate values stayed within the declared supply range. This is stronger than an isolated DAC mismatch sweep because the perturbed values pass through the actual decision-dependent continuous controller.

## Claim Boundary

This is a reproducible capacitor-variation stress model, not foundry Monte Carlo. It does not prove random device mismatch, comparator offset/noise yield, extracted-layout behavior, DRC/LVS signoff, board behavior, or silicon acceptance.
