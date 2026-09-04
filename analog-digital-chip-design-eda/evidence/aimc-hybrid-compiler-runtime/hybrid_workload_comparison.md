# Hybrid Workload Compiler Review

This report audits one shared compiler/runtime handoff across transformer, serving, and edge-workload packages.

## Requirements

1. Every package names its workload, model, metric, baseline, and claim boundary.
2. Every operator has one analog-memory or digital-support placement.
3. Every analog candidate names converter, calibration, tile, SRAM, and fallback information.
4. Digital decisions preserve explicit reasons, including cost-driven fallback.
5. The same packages feed a shared command and runtime schedule.
6. Physical converter evidence remains separate from simulator and task rehearsal evidence.

## Workload Results

| workload | model | operators | analog selected | digital | metric/result | proof |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `tiny_mlp_task_hybrid_vertical_slice_v1` | `tiny-mlp` | 6 | 0 | 6 | `classification_accuracy` / `n/a` | model-backed synthetic task rehearsal |
| `projection-stack-v1` | `projection-stack` | 7 | 4 | 3 | `relative_l2_output_difference_on_projection_stack_trained_weight_replay` / `5.06456e-08` | CrossSim trained-weight replay |
| `deep_transformer_mlp_stack_vertical_slice_v1` | `deep-transformer-mlp-stack` | 16 | 12 | 4 | `relative_l2_output_difference_on_calibrated_deep_transformer_mlp_stack_replay` / `6.71635e-08` | calibrated simulator replay |
| `attention_block_hybrid_vertical_slice_v1` | `attention-block` | 8 | 4 | 4 | `relative_l2_output_difference_on_calibrated_attention_block_replay` / `4.17733e-08` | calibrated simulator replay |
| `transformer_mlp_block_hybrid_vertical_slice_v1` | `transformer-mlp-block` | 8 | 4 | 4 | `relative_l2_output_difference_on_calibrated_transformer_mlp_block_replay` / `4.94498e-08` | calibrated simulator replay |
| `wake-nonwake-audio-v1` | `wake-nonwake-mlp` | 6 | 0 | 6 | `wake_word_f1` / `n/a` | model-backed generated-audio task rehearsal |
| `small-language-model-serving-v1` | `small-language-model-serving-shape-v1` | 14 | 6 | 8 | `next_token_accuracy` / `n/a` | synthetic token-quality rehearsal plus normalized planning replay |
| `wearable-keyword-v1` | `keyword-detector-v3-intake` | 6 | 4 | 2 | `intake_placement_and_cost_policy_replay` / `n/a` | imported intake estimate |
| `smart-camera-inspection-v1` | `camera-defect-classifier-intake` | 5 | 3 | 2 | `intake_placement_and_cost_policy_replay` / `n/a` | imported intake estimate |
| `robot-sensor-policy-v1` | `fusion-transformer-small-intake` | 5 | 3 | 2 | `intake_placement_and_cost_policy_replay` / `n/a` | imported intake estimate |
| `compact-vision-or-defect-v1` | `compact-defect-classifier-intake` | 5 | 3 | 2 | `intake_placement_and_cost_policy_replay` / `n/a` | imported intake estimate |
| `vla-or-physical-ai-v1` | `vla-policy-intake` | 5 | 3 | 2 | `intake_placement_and_cost_policy_replay` / `n/a` | imported intake estimate |

## Shared Handoff

- workloads/models: `12`
- operators: `91`
- commands: `321`
- register writes: `460`
- planning cycles: `687`
- target bytecode words: `321` deterministic `64`-bit review words
- SRAM allocation: `12/12` workload maps fit within the stated `64 KiB` arena
- schedule verified: `true`
- physical converter gate: `blocked_sar_source_common_mode`
- physically guarded fallback commands: `46`
- digital-only planning comparison: `included per workload in hybrid_runtime_estimate.json`

The tiny MLP, deep MLP stack, single MLP block, attention projections, and fixed projections in the normalized serving package retain analog candidates. The tiny MLP and wake-word packages pass bounded task rehearsals but are selected digital under the current guarded path because the physical converter is blocked or converter overhead is not amortized. In the physically guarded runtime trace, analog candidate commands explicitly fall back to digital because the converter gate is blocked.

The target compiler lowers the shared schedule into deterministic review bytecode and per-workload SRAM maps. These artifacts make the handoff inspectable and repeatable; they are not an ISA-validated firmware image and have not been observed running on a board.

## Tests

```bash
python3 scripts/generate_tiny_mlp_hybrid_execution_package.py
python3 scripts/generate_transformer_mlp_block_execution_package.py
python3 scripts/generate_audio_hybrid_execution_package.py
python3 scripts/generate_language_model_serving_package.py
python3 scripts/run_language_model_serving_task_rehearsal.py
python3 scripts/generate_projection_stack_package.py
python3 scripts/generate_edge_intake_packages.py
python3 scripts/build_hybrid_compiler_runtime_package.py
python3 scripts/compile_hybrid_transformer_execution_package.py
python3 scripts/run_hybrid_runtime_estimator.py
python3 scripts/validate_aimc_physical_evidence.py
python3 scripts/run_aimc_end_to_end_regression.py
python3 scripts/validate_project.py
```

## Claim Boundary

the compiler can apply workload-dependent mixed-memory placement and produce one deterministic target schedule plus bounded target-review artifacts.
physical converter acceptance, measured board runtime, measured energy, calibrated silicon, field task accuracy, and production readiness.
