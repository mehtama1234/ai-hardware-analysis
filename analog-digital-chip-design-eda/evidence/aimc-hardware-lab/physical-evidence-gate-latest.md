# AIMC Physical Evidence Gate

- status: `blocked_physical_converter_evidence_is_consistent`
- converter gate: `blocked_sar_source_common_mode`

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
| `continuous_physical_sar_attempt_is_bounded` | `True` |

## Claim Boundary

The measured evidence is internally consistent and preserves the distinction between bounded characterization and converter acceptance. It does not prove full-range physical SAR acceptance, PVT/mismatch/noise yield, extracted layout, board behavior, or silicon.
