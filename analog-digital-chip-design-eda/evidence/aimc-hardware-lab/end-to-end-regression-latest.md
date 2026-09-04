# AIMC End-To-End Regression

- status: `pass_software_vertical_slice_physical_converter_blocked`
- generated: `2026-09-04T20:48:39.194335+00:00`
- task Python: `/home/mehtama1/git-repo/ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture/backend/.venv/bin/python`

| check | pass |
| --- | --- |
| `transformer_vertical_slice` | `True` |
| `deep_transformer_governor` | `True` |
| `tiny_task_evaluation` | `True` |
| `language_model_task_rehearsal` | `True` |
| `language_model_serving_package` | `True` |
| `shared_compiler_package` | `True` |
| `target_compiler` | `True` |
| `target_bytecode_reference` | `True` |
| `guarded_runtime` | `True` |
| `workload_comparison` | `True` |
| `physical_evidence_gate` | `True` |
| `charge_transfer_spec` | `True` |
| `continuous_physical_sar_spec` | `True` |
| `current_state` | `True` |
| `portfolio_validation` | `True` |
| `project_validation` | `True` |
| `site_build` | `True` |

## Artifact Checks

| check | pass |
| --- | --- |
| `tiny_task_pass` | `True` |
| `serving_task_rehearsal_pass` | `True` |
| `serving_package_carries_task_metric` | `True` |
| `crosssim_governor_accepts_12` | `True` |
| `aihwkit_governor_falls_back_12` | `True` |
| `guarded_runtime_has_12_models` | `True` |
| `guarded_runtime_has_46_fallbacks` | `True` |
| `compiler_has_12_models` | `True` |
| `target_compiler_covers_12_models` | `True` |
| `target_bytecode_is_reproducible_shape` | `True` |
| `target_bytecode_reference_interpreter_passes` | `True` |
| `sram_allocations_fit_profile` | `True` |
| `hardware_profile_is_bound` | `True` |
| `charge_transfer_spec_is_bound` | `True` |
| `continuous_sar_spec_is_bound` | `True` |
| `physical_gate_is_consistent_blocked` | `True` |

## Claim Boundary

This regression proves reproducible software-side workload, compiler, simulator-replay, guarded-runtime, and report-validation steps. It does not prove physical converter acceptance, measured board latency, measured energy, calibrated silicon, or production readiness.
