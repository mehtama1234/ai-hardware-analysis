# AIMC Physical Evidence Gate

- status: `nominal_continuous_sar_map_passed_remaining_qualification_open`
- converter gate: `nominal_continuous_sar_map_passed_remaining_qualification_open`

| check | pass |
| --- | --- |
| `coupled_bit_sweep_complete` | `True` |
| `coupled_bit_polarity_complete` | `True` |
| `full_sar_claim_is_bounded` | `True` |
| `full_sar_calibration_complete` | `True` |
| `full_sar_nominal_representative_conversions_complete` | `True` |
| `full_sar_high_codes_measured` | `True` |
| `full_sar_spacing_gate_explicit` | `True` |
| `full_sar_range_gate_explicit` | `True` |
| `full_sar_code_map_gate_explicit` | `True` |
| `historical_partial_probe_preserved` | `True` |
| `differential_endpoint_probe_incomplete` | `True` |
| `physical_converter_not_promoted` | `True` |
| `same_topology_pvt_diagnostic_complete` | `True` |
| `failing_pvt_margin_probe_complete` | `True` |
| `same_topology_controlled_mismatch_complete` | `True` |
| `continuous_physical_sar_nominal_map_complete` | `True` |
| `promoted_continuous_sar_pvt_diagnostics_complete` | `True` |
| `continuous_sar_trim_calibration_runner_selects_passing_trim` | `True` |
| `continuous_sar_mismatch_population_complete` | `True` |
| `continuous_sar_reset_mismatch_population_complete` | `True` |
| `continuous_sar_reset5ns_negative_control_complete` | `True` |

## Claim Boundary

The nominal continuous five-conversion SAR map and calibrated PVT checks pass. The pre-reset declared 100-trial capacitor-variation stress population measured 95 full-map/legal passes; the reset-promoted rerun measured 90 full-map passes and 96 legal-bottom-plate passes. These are schematic-level stress results, not foundry Monte Carlo. Comparator noise/offset yield, extracted layout, board behavior, and silicon acceptance remain open.
