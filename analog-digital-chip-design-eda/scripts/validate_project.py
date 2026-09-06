#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "README.md",
    "docs/synthesis.md",
    "docs/paper-corpus-synthesis.md",
    "docs/analog-in-memory-foundation-model-synthesis.md",
    "docs/coverage-audit.md",
    "docs/roadmaps/end-to-end-goal.md",
    "docs/concepts/eda-is-constraint-solving.md",
    "docs/concepts/voltage-is-a-state-variable.md",
    "docs/concepts/current-is-movement-of-charge.md",
    "docs/concepts/transconductance-is-control-gain.md",
    "docs/concepts/digital-logic-turns-voltage-into-symbols.md",
    "docs/concepts/digital-control-logic-makes-analog-compute-checkable.md",
    "docs/concepts/flip-flop-is-a-timed-memory-decision.md",
    "docs/concepts/timing-closure-is-proof-data-arrives-before-decision.md",
    "docs/concepts/noise-is-uncertainty-at-the-signal-boundary.md",
    "docs/concepts/mismatch-turns-local-error-into-circuit-behavior.md",
    "docs/concepts/feedback-trades-gain-for-control.md",
    "docs/concepts/stability-means-disturbances-shrink-over-time.md",
    "docs/concepts/bandwidth-is-the-price-of-storing-charge.md",
    "docs/concepts/adcs-turn-continuous-voltage-into-bounded-decisions.md",
    "docs/concepts/power-is-switching-leakage-and-delivery-loss.md",
    "docs/concepts/area-is-a-physical-budget.md",
    "docs/concepts/placement-turns-graph-structure-into-distance.md",
    "docs/concepts/physical-flow-turns-control-logic-into-geometry.md",
    "docs/concepts/routing-turns-connection-demand-into-geometry.md",
    "docs/concepts/extraction-turns-shapes-back-into-circuit-equations.md",
    "docs/concepts/verification-is-evidence-implementation-matches-intent.md",
    "docs/concepts/yield-is-probability-over-manufacturing-variation.md",
    "docs/concepts/ai-for-eda-is-a-checked-design-loop.md",
    "docs/concepts/design-space-search-is-trading-expensive-measurements.md",
    "docs/concepts/sar-adcs-turn-current-into-a-timed-digital-decision.md",
    "docs/concepts/dacs-turn-activation-codes-into-row-voltages.md",
    "docs/concepts/analog-compute-is-a-boundary-chain.md",
    "docs/concepts/prefill-and-decode-stress-different-hardware.md",
    "docs/concepts/where-analog-compute-actually-helps.md",
    "docs/concepts/attention-is-changing-memory-not-fixed-weights.md",
    "docs/concepts/softmax-turns-score-error-into-selection-error.md",
    "docs/concepts/transformer-block-error-is-state-drift.md",
    "docs/concepts/stable-bias-accumulates-across-layers.md",
    "docs/concepts/calibration-is-a-schedule-not-a-single-fix.md",
    "docs/concepts/tile-health-monitoring-spends-calibration-where-error-grows.md",
    "docs/concepts/analog-serving-policy-decides-when-to-use-the-array.md",
    "docs/concepts/hybrid-analog-digital-accelerators-need-a-control-plane.md",
    "docs/concepts/analog-placement-is-not-analog-acceptance.md",
    "docs/concepts/analog-compute-needs-a-trust-boundary.md",
    "docs/concepts/analog-foundation-models-need-a-digital-referee.md",
    "docs/concepts/analog-tile-is-a-measurement-chain.md",
    "docs/research/paper-taxonomy.md",
    "docs/research/analog-to-digital-to-model-error-flow.md",
    "docs/research/final-accepted-converter-gate.md",
    "docs/research/first-real-converter-candidate-execution-plan.md",
    "docs/research/first-real-converter-candidate-packet.md",
    "docs/research/first-real-converter-rehearsal-payload.md",
    "docs/research/first-real-converter-blocker-work-order.md",
    "docs/research/first-real-converter-physical-object-audit.md",
    "docs/research/first-real-converter-physical-object-assembly.md",
    "docs/research/first-real-converter-energy-candidate.md",
    "docs/research/first-real-converter-latency-candidate.md",
    "docs/research/first-real-converter-noise-candidate.md",
    "docs/research/first-real-converter-area-candidate.md",
    "docs/research/first-real-converter-break-even-candidate.md",
    "docs/research/first-real-converter-candidate-loop-strict-readiness.md",
    "docs/research/first-real-converter-same-candidate-extracted-rc.md",
    "docs/research/first-real-converter-frontend-to-input-stage-proxy.md",
    "docs/research/first-real-converter-frontend-active-handoff-estimate.md",
    "docs/research/first-real-converter-combined-active-handoff-work-order.md",
    "docs/research/sky130-frontend-input-stage-handoff-candidate.md",
    "docs/research/sky130-transistor-handoff-replacement-work-order.md",
    "docs/research/sky130-frontend-transistor-input-stage-handoff-candidate.md",
    "docs/research/from-active-macro-to-real-transistor-handoff.md",
    "docs/research/sky130-transistor-handoff-decomposition.md",
    "docs/research/sky130-transistor-handoff-probe-ladder.md",
    "docs/research/sky130-frontend-sense-to-transistor-op-handoff.md",
    "docs/research/sky130-frontend-sense-to-transistor-short-transient.md",
    "docs/research/sky130-frontend-sense-to-transistor-ramp-startup.md",
    "docs/research/sky130-extracted-frontend-to-transistor-gate-startup.md",
    "docs/research/sky130-extracted-frontend-gate-coupling-sweep.md",
    "docs/research/sky130-extracted-frontend-source-follower-handoff.md",
    "docs/research/sky130-extracted-frontend-differential-preamp.md",
    "docs/research/sky130-measured-sense-differential-preamp.md",
    "docs/research/sky130-measured-sense-preamp-bias-sweep.md",
    "docs/research/sky130-measured-sense-preamp-op-map.md",
    "docs/research/sky130-preamp-known-good-sanity-gap.md",
    "docs/research/sky130-preamp-known-good-reproduction.md",
    "docs/research/sky130-extracted-frontend-preamp-gain-sweep.md",
    "docs/research/sky130-frontend-preamp-interface-redesign-target.md",
    "docs/research/sky130-frontend-preamp-capacitance-budget.md",
    "docs/research/sky130-frontend-preamp-interface-work-order.md",
    "docs/research/sky130-frontend-preamp-interface-candidate.md",
    "docs/research/sky130-lower-waste-frontend-preamp-candidate.md",
    "docs/research/sky130-combined-coupling-waste-frontend-preamp-candidate.md",
    "docs/research/sky130-active-isolation-preamp-target.md",
    "docs/research/sky130-active-isolation-preamp-candidate.md",
    "docs/research/sky130-offset-calibrated-active-isolation-preamp.md",
    "docs/research/sky130-transistor-active-isolation-preamp.md",
    "docs/research/sky130-swapped-transistor-active-isolation-preamp.md",
    "docs/research/sky130-polarity-corrected-transistor-handoff.md",
    "docs/research/sky130-polarity-contract-latch-sar-risk.md",
    "docs/research/sky130-polarity-named-isolated-latch-work-order.md",
    "docs/research/sky130-source-follower-isolated-latch-candidate.md",
    "docs/research/sky130-sampled-internal-decision-cap-latch-candidate.md",
    "docs/research/sky130-two-phase-preamp-latch-candidate.md",
    "docs/research/sky130-isolated-latch-debug-ladder.md",
    "docs/research/sky130-preamp-alone-latch-debug.md",
    "docs/research/sky130-preamp-op-latch-debug.md",
    "docs/research/sky130-known-good-shape-preamp-op-latch-debug.md",
    "docs/research/sky130-preamp-op-deck-diff-diagnosis.md",
    "docs/research/sky130-known-good-shape-preamp-transient-latch-debug.md",
    "docs/research/sky130-latch-alone-from-preamp-voltage-debug.md",
    "docs/research/sky130-latch-alone-swapped-preamp-voltage-debug.md",
    "docs/research/sky130-swapped-latch-clock-timing-debug.md",
    "docs/research/sky130-clocked-latch-output-convention-diagnostic.md",
    "docs/research/sky130-corrected-convention-sample-hold-latch-kickback.md",
    "docs/research/sky130-corrected-convention-capacitive-isolation-confirm.md",
    "docs/research/sky130-corrected-convention-isolation-range-stress.md",
    "docs/research/analog-in-memory-foundation-model-reading-map.md",
    "docs/research/hybrid-aimc-system-architecture.md",
    "docs/research/transformer-operation-partition-for-hybrid-aimc.md",
    "docs/research/mixed-signal-trust-boundary-spec.md",
    "docs/research/toolchain-map.md",
    "docs/research/ai-hardware-architecture-to-working-lab-bridge.md",
    "docs/research/combined-aimc-workbench-end-to-end-goal.md",
    "docs/research/aimc-hardware-profile.md",
    "docs/research/aimc-end-to-end-proof-explanation.md",
    "docs/research/aimc-remaining-proof-spine.md",
    "docs/research/aimc-evidence-ledger.md",
    "docs/research/aimc-page-flow-audit.md",
    "docs/research/comparator-decision-margin-from-first-principles.md",
    "docs/research/converter-evidence-ladder.md",
    "docs/research/cross-repo-aimc-loop-proof.md",
    "docs/research/passive-frontend-vs-active-preamp.md",
    "docs/research/current-aimc-system-state.md",
    "docs/research/onnx-fixture-inventory.md",
    "docs/research/aihwkit-residual-diagnostic.md",
    "docs/research/aihwkit-ideal-forward-mapping-proof.md",
    "docs/research/aihwkit-forward-setting-sweep.md",
    "docs/research/aihwkit-physical-setting-review.md",
    "docs/research/aihwkit-current-tile-boundary-replay.md",
    "docs/research/aihwkit-converter-upgrade-target.md",
    "docs/research/aihwkit-converter-cost-model.md",
    "docs/research/aihwkit-target-noise-sensitivity.md",
    "docs/research/aihwkit-converter-break-even.md",
    "docs/research/converter-circuit-evidence-contract.md",
    "docs/research/local-converter-circuit-estimate.md",
    "docs/research/converter-circuit-simulation-estimate.md",
    "docs/research/converter-spice-handoff-spec.md",
    "docs/research/row-dac-settling-spice-evidence.md",
    "docs/research/sar-readout-spice-evidence.md",
    "docs/research/shared-converter-loading-spice-evidence.md",
    "docs/research/converter-supply-energy-spice-evidence.md",
    "docs/research/converter-post-layout-readiness.md",
    "docs/research/converter-post-layout-evidence-contract.md",
    "docs/research/converter-post-layout-payload-template.md",
    "docs/research/converter-post-layout-payload-validator.md",
    "docs/research/converter-post-layout-break-even-rerun-path.md",
    "docs/research/converter-post-layout-strict-intake.md",
    "docs/research/converter-post-layout-positive-path.md",
    "docs/research/converter-post-layout-submission-path.md",
    "docs/research/converter-post-layout-real-payload-package.md",
    "docs/research/converter-post-layout-payload-preflight.md",
    "docs/research/converter-post-layout-candidate-workspace.md",
    "docs/research/converter-post-layout-candidate-workspace-audit.md",
    "docs/research/converter-post-layout-candidate-fill-checklist.md",
    "docs/research/converter-post-layout-candidate-progress-report.md",
    "docs/research/converter-post-layout-candidate-progress-gate.md",
    "docs/research/converter-post-layout-candidate-preflight-gate.md",
    "docs/research/converter-post-layout-candidate-submission-gate.md",
    "docs/research/converter-post-layout-candidate-readiness-run.md",
    "docs/research/converter-post-layout-handoff-manifest.md",
    "docs/research/converter-post-layout-blocker-ledger.md",
    "docs/research/converter-post-layout-candidate-edit-plan.md",
    "docs/research/converter-post-layout-same-run-gate.md",
    "docs/research/converter-post-layout-candidate-identity-initializer.md",
    "docs/research/converter-post-layout-real-candidate-builder.md",
    "docs/research/converter-post-layout-submission-preview.md",
    "docs/research/converter-post-layout-evidence-leakage-audit.md",
    "docs/research/converter-post-layout-temporary-submission-proof.md",
    "docs/research/converter-post-layout-real-artifact-discovery.md",
    "docs/research/converter-post-layout-real-run-recipe.md",
    "docs/research/converter-post-layout-real-run-recipe-coverage.md",
    "docs/research/backend-hardware-placement-first-principles.md",
    "docs/research/evidence-import-and-claim-readiness-first-principles.md",
    "docs/research/digital-physical-artifact-boundary.md",
    "docs/research/aihwkit-crosssim-adapter-boundary.md",
    "docs/research/current-simulator-adapter-status.md",
    "docs/research/analog-simulator-adapter-output-contract.md",
    "docs/research/simulator-to-post-layout-gap-audit.md",
    "docs/research/analog-converter-layout-work-order.md",
    "docs/research/analog-converter-layout-starter-package.md",
    "docs/research/analog-converter-layout-tool-readiness.md",
    "docs/research/analog-converter-pdk-readiness.md",
    "docs/research/magic-sky130-extraction-smoke.md",
    "docs/research/magic-sky130-compatibility.md",
    "docs/research/row-dac-10b-layout-smoke.md",
    "docs/research/converter-starter-layout-smoke.md",
    "docs/research/converter-starter-post-layout-candidate.md",
    "docs/research/converter-starter-physical-artifacts.md",
    "docs/research/converter-starter-parasitic-load-estimate.md",
    "docs/research/converter-starter-parasitic-break-even-rerun.md",
    "docs/research/converter-starter-extracted-rc-ngspice.md",
    "docs/research/sky130-transistor-sample-switch-ngspice.md",
    "docs/research/sky130-sample-switch-hold-mode-ngspice.md",
    "docs/research/sky130-sample-switch-hold-mitigation-sweep.md",
    "docs/research/sky130-sample-switch-dummy-cancellation-ngspice.md",
    "docs/research/sky130-bottom-plate-sampling-ngspice.md",
    "docs/research/sky130-sample-hold-topology-decision-gate.md",
    "docs/research/sky130-buffered-sample-hold-ngspice.md",
    "docs/research/sky130-bootstrapped-switch-ngspice.md",
    "docs/research/sky130-fully-differential-sampling-ngspice.md",
    "docs/research/sky130-differential-dummy-cancellation-ngspice.md",
    "docs/research/sky130-differential-dummy-candidate-input-sweep.md",
    "docs/research/sky130-differential-dummy-candidate-mismatch-sweep.md",
    "docs/research/sky130-differential-dummy-candidate-decision-margin.md",
    "docs/research/sky130-differential-dummy-candidate-offset-noise-stress.md",
    "docs/research/sky130-comparator-acceptance-fixture-spec.md",
    "docs/research/sky130-comparator-input-stage-ngspice.md",
    "docs/research/sky130-clocked-comparator-latch-ngspice.md",
    "docs/research/sky130-sample-hold-latch-kickback-ngspice.md",
    "docs/research/sky130-latch-input-size-kickback-sweep.md",
    "docs/research/sky130-comparator-isolation-target.md",
    "docs/research/sky130-capacitive-latch-input-isolation-sweep.md",
    "docs/research/sky130-capacitive-isolation-both-polarity-confirm.md",
    "docs/research/sky130-capacitive-isolation-post-layout-handoff.md",
    "docs/research/sky130-capacitive-isolation-physical-cell-gap.md",
    "docs/research/sky130-capacitive-isolation-post-layout-both-polarity.md",
    "docs/research/sky130-capacitive-isolation-extracted-port-mapping-diagnostic.md",
    "docs/research/sky130-capacitive-isolation-extracted-coupling-strength-sweep.md",
    "docs/research/sky130-extracted-frontend-redesign-target.md",
    "docs/research/sky130-balanced-frontend-work-order.md",
    "docs/research/sky130-balanced-frontend-starter-extraction.md",
    "docs/research/sky130-balanced-frontend-sign-preservation.md",
    "docs/research/sky130-balanced-frontend-latch-decision.md",
    "docs/research/sky130-balanced-frontend-sense-gain-target.md",
    "docs/research/sky130-strong-sense-frontend-candidate.md",
    "docs/research/sky130-ultra-sense-frontend-candidate.md",
    "docs/research/sky130-frontend-sense-efficiency-audit.md",
    "docs/research/differential-sampling-control-proof-ngspice.md",
    "docs/research/sky130-single-device-charge-injection-ngspice.md",
    "docs/research/sky130-sample-switch-clock-edge-sweep.md",
    "docs/research/sky130-sample-hold-design-target.md",
    "docs/research/sky130-differential-matching-requirement.md",
    "docs/research/sky130-next-transistor-fixture-work-order.md",
    "docs/research/analog-converter-sky130-workbench-env.md",
    "docs/research/analog-converter-physical-cell-gate.md",
    "docs/research/analog-converter-physical-flow-run.md",
    "docs/research/guarded-simulator-payload-import.md",
    "docs/research/optional-aimc-simulator-install-path.md",
    "docs/research/optional-simulator-payload-run-path.md",
    "docs/research/workload-shaped-simulator-evidence.md",
    "docs/research/tensor-shaped-simulator-evidence.md",
    "docs/research/trained-weight-simulator-evidence.md",
    "docs/research/projection-stack-simulator-evidence.md",
    "docs/research/transformer-mlp-block-simulator-evidence.md",
    "docs/research/calibrated-transformer-mlp-block-simulator-evidence.md",
    "docs/research/calibrated-deep-transformer-mlp-stack-simulator-evidence.md",
    "docs/research/attention-block-simulator-evidence.md",
    "docs/research/calibrated-attention-block-simulator-evidence.md",
    "docs/research/calibrated-residual-governor-bridge.md",
    "docs/research/residual-aware-placement-decisions.md",
    "docs/research/crosssim-layout-risk-adapter.md",
    "docs/research/simulator-to-placement-decision-boundary.md",
    "docs/research/measured-runtime-power-claim-upgrade-path.md",
    "docs/research/next-aimc-evidence-work-queue.md",
    "docs/research/board-and-power-measurement-boundary.md",
    "docs/papers/paper-note-template.md",
    "docs/papers/openroad-flow.md",
    "docs/papers/openlane-flow.md",
    "docs/papers/circuit-training-placement.md",
    "docs/papers/dacs-ai-for-eda-survey.md",
    "docs/papers/analog-sizing-bayesian-optimization.md",
    "sources/papers/paper-entry-schema.json",
    "sources/papers/seed-paper-index.json",
    "sources/evidence/analog-simulator-adapter-output-schema.json",
    "sources/evidence/converter-circuit-evidence-schema.json",
    "sources/evidence/converter-post-layout-evidence-schema.json",
    "sources/local-traces/seed-material.md",
    "scripts/check_tools.sh",
    "scripts/check_aimc_bridge.sh",
    "scripts/check_aimc_openlane_readiness.sh",
    "scripts/run_aimc_openlane_flow.sh",
    "scripts/install_local_magic_from_source.sh",
    "scripts/export_aimc_hardware_lab_evidence.py",
    "scripts/export_strict_analog_tool_evidence.py",
    "scripts/generate_analog_simulator_adapter_dry_run.py",
    "scripts/run_optional_aimc_simulator_payloads.py",
    "scripts/run_workload_aimc_simulator_payloads.py",
    "scripts/run_tensor_shape_aimc_simulator_payloads.py",
    "scripts/run_trained_weight_aimc_simulator_payloads.py",
    "scripts/run_projection_stack_aimc_simulator_payloads.py",
    "scripts/run_transformer_mlp_block_aimc_simulator_payloads.py",
    "scripts/run_calibrated_transformer_mlp_block_aimc_simulator_payloads.py",
    "scripts/run_calibrated_deep_transformer_mlp_stack_aimc_simulator_payloads.py",
    "scripts/run_attention_block_aimc_simulator_payloads.py",
    "scripts/run_calibrated_attention_block_aimc_simulator_payloads.py",
    "scripts/run_calibrated_residual_governor_bridge.py",
    "scripts/audit_simulator_to_post_layout_gap.py",
    "scripts/audit_digital_physical_artifact_boundary.py",
    "scripts/generate_analog_converter_layout_work_order.py",
    "scripts/run_residual_aware_placement_decisions.py",
    "scripts/generate_crosssim_layout_risk_adapter.py",
    "scripts/import_analog_simulator_payload.py",
    "scripts/validate_analog_simulator_adapter_contract.py",
    "scripts/install_optional_aimc_simulators.sh",
    "scripts/import_backend_hardware_placement.py",
    "scripts/prove_cross_repo_aimc_loop.py",
    "scripts/generate_onnx_fixture_inventory.py",
    "scripts/generate_aihwkit_residual_diagnostic.py",
    "scripts/generate_aihwkit_ideal_forward_mapping_proof.py",
    "scripts/generate_aihwkit_forward_setting_sweep.py",
    "scripts/generate_aihwkit_physical_setting_review.py",
    "scripts/generate_aihwkit_current_tile_boundary_replay.py",
    "scripts/generate_aihwkit_converter_upgrade_target.py",
    "scripts/generate_aihwkit_converter_cost_model.py",
    "scripts/generate_aihwkit_target_noise_sensitivity.py",
    "scripts/generate_aihwkit_converter_break_even.py",
    "scripts/generate_converter_circuit_evidence_contract.py",
    "scripts/generate_local_converter_circuit_estimate.py",
    "scripts/generate_converter_circuit_simulation_estimate.py",
    "scripts/generate_converter_spice_handoff_spec.py",
    "scripts/generate_row_dac_settling_spice_evidence.py",
    "scripts/generate_sar_readout_spice_evidence.py",
    "scripts/generate_shared_converter_loading_spice_evidence.py",
    "scripts/generate_converter_supply_energy_spice_evidence.py",
    "scripts/generate_converter_post_layout_readiness.py",
    "scripts/generate_converter_post_layout_evidence_contract.py",
    "scripts/generate_converter_post_layout_payload_template.py",
    "scripts/validate_converter_post_layout_payload.py",
    "scripts/generate_converter_post_layout_payload_validator_report.py",
    "scripts/rerun_converter_break_even_from_post_layout_payload.py",
    "scripts/generate_converter_post_layout_break_even_rerun_path.py",
    "scripts/generate_converter_post_layout_strict_intake_report.py",
    "scripts/generate_converter_post_layout_positive_path_report.py",
    "scripts/submit_converter_post_layout_payload.py",
    "scripts/generate_converter_post_layout_submission_path_report.py",
    "scripts/generate_converter_post_layout_real_run_recipe.py",
    "scripts/generate_converter_post_layout_real_run_recipe_coverage.py",
    "scripts/initialize_converter_post_layout_candidate_identity.py",
    "scripts/build_converter_post_layout_candidate_from_real_run.py",
    "scripts/generate_first_real_converter_candidate_packet.py",
    "scripts/generate_first_real_converter_rehearsal_payload.py",
    "scripts/generate_first_real_converter_blocker_work_order.py",
    "scripts/assemble_first_real_converter_physical_object.py",
    "scripts/audit_first_real_converter_physical_object.py",
    "scripts/generate_first_real_converter_energy_candidate.py",
    "scripts/generate_first_real_converter_latency_candidate.py",
    "scripts/generate_first_real_converter_noise_candidate.py",
    "scripts/generate_first_real_converter_area_candidate.py",
    "scripts/generate_first_real_converter_break_even_candidate.py",
    "scripts/audit_first_real_converter_candidate_loop_strict_readiness.py",
    "scripts/run_first_real_converter_same_candidate_extracted_rc.py",
    "scripts/run_first_real_converter_frontend_to_input_stage_proxy.py",
    "scripts/generate_first_real_converter_frontend_active_handoff_estimate.py",
    "scripts/generate_first_real_converter_combined_active_handoff_work_order.py",
    "scripts/run_sky130_frontend_input_stage_handoff_candidate.py",
    "scripts/generate_sky130_transistor_handoff_replacement_work_order.py",
    "scripts/run_sky130_frontend_transistor_input_stage_handoff_candidate.py",
    "scripts/run_sky130_transistor_handoff_probe_ladder.py",
    "scripts/run_sky130_frontend_sense_to_transistor_op_handoff.py",
    "scripts/run_sky130_frontend_sense_to_transistor_short_transient.py",
    "scripts/run_sky130_frontend_sense_to_transistor_ramp_startup.py",
    "scripts/run_sky130_extracted_frontend_to_transistor_gate_startup.py",
    "scripts/run_sky130_extracted_frontend_gate_coupling_sweep.py",
    "scripts/run_sky130_extracted_frontend_source_follower_handoff.py",
    "scripts/run_sky130_extracted_frontend_differential_preamp.py",
    "scripts/run_sky130_measured_sense_differential_preamp.py",
    "scripts/run_sky130_measured_sense_preamp_bias_sweep.py",
    "scripts/run_sky130_measured_sense_preamp_op_map.py",
    "scripts/generate_sky130_preamp_known_good_sanity_gap.py",
    "scripts/run_sky130_preamp_known_good_reproduction.py",
    "scripts/run_sky130_extracted_frontend_preamp_gain_sweep.py",
    "scripts/generate_sky130_frontend_preamp_interface_redesign_target.py",
    "scripts/generate_sky130_frontend_preamp_capacitance_budget.py",
    "scripts/generate_sky130_frontend_preamp_interface_work_order.py",
    "scripts/run_sky130_frontend_preamp_interface_candidate.py",
    "scripts/run_sky130_lower_waste_frontend_preamp_candidate.py",
    "scripts/run_sky130_combined_coupling_waste_frontend_preamp_candidate.py",
    "scripts/generate_sky130_active_isolation_preamp_target.py",
    "scripts/run_sky130_active_isolation_preamp_candidate.py",
    "scripts/run_sky130_offset_calibrated_active_isolation_preamp.py",
    "scripts/run_sky130_transistor_active_isolation_preamp.py",
    "scripts/run_sky130_swapped_transistor_active_isolation_preamp.py",
    "scripts/generate_sky130_polarity_corrected_transistor_handoff.py",
    "scripts/generate_sky130_polarity_contract_latch_sar_risk.py",
    "scripts/generate_sky130_polarity_named_isolated_latch_work_order.py",
    "scripts/run_sky130_source_follower_isolated_latch_candidate.py",
    "scripts/run_sky130_sampled_internal_decision_cap_latch_candidate.py",
    "scripts/run_sky130_two_phase_preamp_latch_candidate.py",
    "scripts/generate_sky130_isolated_latch_debug_ladder.py",
    "scripts/run_sky130_preamp_alone_latch_debug.py",
    "scripts/run_sky130_preamp_op_latch_debug.py",
    "scripts/run_sky130_known_good_shape_preamp_op_latch_debug.py",
    "scripts/generate_sky130_preamp_op_deck_diff_diagnosis.py",
    "scripts/run_sky130_known_good_shape_preamp_transient_latch_debug.py",
    "scripts/run_sky130_latch_alone_from_preamp_voltage_debug.py",
    "scripts/run_sky130_dynamic_offset_cancelled_latch.py",
    "scripts/run_sky130_latch_alone_swapped_preamp_voltage_debug.py",
    "scripts/preview_converter_post_layout_submission.py",
    "scripts/audit_converter_post_layout_evidence_leakage.py",
    "scripts/prove_converter_post_layout_temporary_submission.py",
    "scripts/audit_converter_post_layout_real_artifact_discovery.py",
    "scripts/generate_current_aimc_system_state.py",
    "scripts/generate_next_evidence_work_queue.py",
    "scripts/install_ubuntu_eda_tools.sh",
    "scripts/build_site.py",
    "site/index.html",
    "site/synthesis.html",
    "site/paper-synthesis.html",
    "site/analog-in-memory-foundation-model-synthesis.html",
    "site/coverage-audit.html",
    "site/concepts.html",
    "site/labs.html",
    "site/research.html",
    "site/research/current-simulator-adapter-status.html",
    "site/research/analog-simulator-adapter-output-contract.html",
    "site/research/guarded-simulator-payload-import.html",
    "site/research/optional-aimc-simulator-install-path.html",
    "site/research/optional-simulator-payload-run-path.html",
    "site/research/workload-shaped-simulator-evidence.html",
    "site/research/tensor-shaped-simulator-evidence.html",
    "site/research/trained-weight-simulator-evidence.html",
    "site/research/projection-stack-simulator-evidence.html",
    "site/research/transformer-mlp-block-simulator-evidence.html",
    "site/research/calibrated-transformer-mlp-block-simulator-evidence.html",
    "site/research/calibrated-deep-transformer-mlp-stack-simulator-evidence.html",
    "site/research/attention-block-simulator-evidence.html",
    "site/research/calibrated-attention-block-simulator-evidence.html",
    "site/research/calibrated-residual-governor-bridge.html",
    "site/research/residual-aware-placement-decisions.html",
    "site/research/crosssim-layout-risk-adapter.html",
    "site/research/onnx-fixture-inventory.html",
    "site/research/aihwkit-residual-diagnostic.html",
    "site/research/aihwkit-ideal-forward-mapping-proof.html",
    "site/research/aihwkit-forward-setting-sweep.html",
    "site/research/aihwkit-physical-setting-review.html",
    "site/research/aihwkit-current-tile-boundary-replay.html",
    "site/research/aihwkit-converter-upgrade-target.html",
    "site/research/aihwkit-converter-cost-model.html",
    "site/research/aihwkit-target-noise-sensitivity.html",
    "site/research/current-aimc-system-state.html",
    "site/research/aimc-hardware-profile.html",
    "site/research/simulator-to-placement-decision-boundary.html",
    "site/research/measured-runtime-power-claim-upgrade-path.html",
    "site/research/next-aimc-evidence-work-queue.html",
    "site/research/sky130-extracted-frontend-to-transistor-gate-startup.html",
    "site/research/sky130-extracted-frontend-gate-coupling-sweep.html",
    "site/research/sky130-extracted-frontend-source-follower-handoff.html",
    "site/research/sky130-extracted-frontend-differential-preamp.html",
    "site/research/sky130-measured-sense-differential-preamp.html",
    "site/research/sky130-measured-sense-preamp-bias-sweep.html",
    "site/research/sky130-measured-sense-preamp-op-map.html",
    "site/research/sky130-preamp-known-good-sanity-gap.html",
    "site/research/sky130-preamp-known-good-reproduction.html",
    "site/research/sky130-extracted-frontend-preamp-gain-sweep.html",
    "site/research/sky130-frontend-preamp-interface-redesign-target.html",
    "site/research/sky130-frontend-preamp-capacitance-budget.html",
    "site/research/sky130-frontend-preamp-interface-work-order.html",
    "site/research/sky130-frontend-preamp-interface-candidate.html",
    "site/research/sky130-lower-waste-frontend-preamp-candidate.html",
    "site/research/sky130-combined-coupling-waste-frontend-preamp-candidate.html",
    "site/research/sky130-active-isolation-preamp-target.html",
    "site/research/sky130-active-isolation-preamp-candidate.html",
    "site/research/sky130-offset-calibrated-active-isolation-preamp.html",
    "site/research/sky130-transistor-active-isolation-preamp.html",
    "site/research/sky130-swapped-transistor-active-isolation-preamp.html",
    "site/research/sky130-polarity-corrected-transistor-handoff.html",
    "site/research/sky130-polarity-contract-latch-sar-risk.html",
    "site/research/sky130-polarity-named-isolated-latch-work-order.html",
    "site/research/sky130-source-follower-isolated-latch-candidate.html",
    "site/research/sky130-sampled-internal-decision-cap-latch-candidate.html",
    "site/research/sky130-two-phase-preamp-latch-candidate.html",
    "site/research/sky130-isolated-latch-debug-ladder.html",
    "site/research/sky130-preamp-alone-latch-debug.html",
    "site/research/sky130-preamp-op-latch-debug.html",
    "site/research/sky130-known-good-shape-preamp-op-latch-debug.html",
    "site/research/sky130-preamp-op-deck-diff-diagnosis.html",
    "site/research/sky130-known-good-shape-preamp-transient-latch-debug.html",
    "site/research/sky130-latch-alone-from-preamp-voltage-debug.html",
    "site/research/sky130-latch-alone-swapped-preamp-voltage-debug.html",
    "site/research/sky130-swapped-latch-clock-timing-debug.html",
    "site/research/sky130-clocked-latch-output-convention-diagnostic.html",
    "site/research/sky130-corrected-convention-sample-hold-latch-kickback.html",
    "site/research/sky130-corrected-convention-capacitive-isolation-confirm.html",
    "site/research/sky130-corrected-convention-isolation-range-stress.html",
    "site/papers.html",
    "evidence/aimc-hardware-lab/manifest.json",
    "evidence/aimc-hardware-lab/import-batch.json",
    "evidence/aimc-hardware-lab/compiler_mapping.json",
    "evidence/aimc-hardware-lab/analog_error_simulation.json",
    "evidence/aimc-hardware-lab/analog_error_simulation_strict_tool.json",
    "evidence/aimc-hardware-lab/board_runtime.json",
    "evidence/aimc-hardware-lab/power_thermal.json",
    "evidence/aimc-hardware-lab/task_accuracy.json",
    "evidence/aimc-hardware-lab/physical_flow.json",
    "evidence/aimc-hardware-lab/cross-repo-loop-proof.json",
    "evidence/aimc-hardware-lab/cross-repo-loop-proof.md",
    "evidence/aimc-hardware-lab/onnx-fixture-inventory.json",
    "evidence/aimc-hardware-lab/onnx-fixture-inventory.md",
    "evidence/aimc-hardware-lab/current-aimc-system-state.json",
    "evidence/aimc-hardware-lab/current-aimc-system-state.md",
    "evidence/aimc-hardware-lab/hardware-profile-educational-hybrid-tile-v1.json",
    "evidence/aimc-hardware-lab/next-evidence-work-queue.json",
    "evidence/aimc-hardware-lab/next-evidence-work-queue.md",
    "evidence/aimc-simulator-adapters/aihwkit-residual-diagnostic.json",
    "evidence/aimc-simulator-adapters/aihwkit-residual-diagnostic.md",
    "evidence/aimc-simulator-adapters/aihwkit-ideal-forward-mapping-proof.json",
    "evidence/aimc-simulator-adapters/aihwkit-ideal-forward-mapping-proof.md",
    "evidence/aimc-simulator-adapters/aihwkit-forward-setting-sweep.json",
    "evidence/aimc-simulator-adapters/aihwkit-forward-setting-sweep.md",
    "evidence/aimc-simulator-adapters/aihwkit-physical-setting-review.json",
    "evidence/aimc-simulator-adapters/aihwkit-physical-setting-review.md",
    "evidence/aimc-simulator-adapters/aihwkit-current-tile-boundary-replay.json",
    "evidence/aimc-simulator-adapters/aihwkit-current-tile-boundary-replay.md",
    "evidence/aimc-simulator-adapters/aihwkit-converter-upgrade-target.json",
    "evidence/aimc-simulator-adapters/aihwkit-converter-upgrade-target.md",
    "evidence/aimc-simulator-adapters/aihwkit-converter-cost-model.json",
    "evidence/aimc-simulator-adapters/aihwkit-converter-cost-model.md",
    "evidence/aimc-simulator-adapters/aihwkit-target-noise-sensitivity.json",
    "evidence/aimc-simulator-adapters/aihwkit-target-noise-sensitivity.md",
    "evidence/aimc-simulator-adapters/aihwkit-converter-break-even.json",
    "evidence/aimc-simulator-adapters/aihwkit-converter-break-even.md",
    "evidence/aimc-simulator-adapters/converter-circuit-evidence-contract.json",
    "evidence/aimc-simulator-adapters/converter-circuit-evidence-contract.md",
    "evidence/aimc-simulator-adapters/local-converter-circuit-estimate.json",
    "evidence/aimc-simulator-adapters/local-converter-circuit-estimate.md",
    "evidence/aimc-simulator-adapters/converter-circuit-simulation-estimate.json",
    "evidence/aimc-simulator-adapters/converter-circuit-simulation-estimate.md",
    "evidence/aimc-simulator-adapters/converter-spice-handoff-spec.json",
    "evidence/aimc-simulator-adapters/converter-spice-handoff-spec.md",
    "evidence/aimc-simulator-adapters/row-dac-settling-spice-evidence.json",
    "evidence/aimc-simulator-adapters/row-dac-settling-spice-evidence.md",
    "evidence/aimc-simulator-adapters/sar-readout-spice-evidence.json",
    "evidence/aimc-simulator-adapters/sar-readout-spice-evidence.md",
    "evidence/aimc-simulator-adapters/shared-converter-loading-spice-evidence.json",
    "evidence/aimc-simulator-adapters/shared-converter-loading-spice-evidence.md",
    "evidence/aimc-simulator-adapters/converter-supply-energy-spice-evidence.json",
    "evidence/aimc-simulator-adapters/converter-supply-energy-spice-evidence.md",
    "evidence/aimc-simulator-adapters/converter-post-layout-readiness.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-readiness.md",
    "evidence/aimc-simulator-adapters/converter-post-layout-evidence-contract.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-evidence-contract.md",
    "sources/evidence/converter-post-layout-payload.template.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-payload-template.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-payload-template.md",
    "evidence/aimc-simulator-adapters/dry-run/converter-post-layout-evidence.placeholder.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-payload-validator.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-payload-validator.md",
    "evidence/aimc-simulator-adapters/converter-post-layout-break-even-rerun-path.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-break-even-rerun-path.md",
    "evidence/aimc-simulator-adapters/dry-run/converter-post-layout-evidence.shape-only-missing-files.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-strict-intake-report.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-strict-intake-report.md",
    "evidence/aimc-simulator-adapters/converter-post-layout-positive-path-report.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-positive-path-report.md",
    "evidence/aimc-simulator-adapters/converter-post-layout-submission-path-report.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-submission-path-report.md",
    "evidence/aimc-simulator-adapters/converter-post-layout-real-payload-package.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-real-payload-package.md",
    "evidence/aimc-simulator-adapters/converter-post-layout-payload-preflight-report.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-payload-preflight-report.md",
    "evidence/aimc-simulator-adapters/converter-post-layout-candidate-workspace.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-candidate-workspace.md",
    "evidence/aimc-simulator-adapters/converter-post-layout-candidate-workspace-audit.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-candidate-workspace-audit.md",
    "evidence/aimc-simulator-adapters/converter-post-layout-candidate-fill-checklist.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-candidate-fill-checklist.md",
    "evidence/aimc-simulator-adapters/converter-post-layout-candidate-progress-report.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-candidate-progress-report.md",
    "evidence/aimc-simulator-adapters/converter-post-layout-candidate-progress-gate.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-candidate-progress-gate.md",
    "evidence/aimc-simulator-adapters/converter-post-layout-candidate-preflight-gate.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-candidate-preflight-gate.md",
    "evidence/aimc-simulator-adapters/converter-post-layout-candidate-submission-gate.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-candidate-submission-gate.md",
    "evidence/aimc-simulator-adapters/converter-post-layout-candidate-readiness-run.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-candidate-readiness-run.md",
    "evidence/aimc-simulator-adapters/converter-post-layout-candidate-readiness-preflight.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-candidate-readiness-preflight.md",
    "evidence/aimc-simulator-adapters/converter-post-layout-handoff-manifest.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-handoff-manifest.md",
    "evidence/aimc-simulator-adapters/converter-post-layout-blocker-ledger.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-blocker-ledger.md",
    "evidence/aimc-simulator-adapters/converter-post-layout-candidate-edit-plan.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-candidate-edit-plan.md",
    "evidence/aimc-simulator-adapters/converter-post-layout-same-run-gate.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-same-run-gate.md",
    "evidence/aimc-simulator-adapters/converter-post-layout-real-run-recipe.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-real-run-recipe.md",
    "evidence/aimc-simulator-adapters/converter-post-layout-real-run-recipe-coverage.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-real-run-recipe-coverage.md",
    "evidence/aimc-simulator-adapters/converter-post-layout-candidate-identity-initializer.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-candidate-identity-initializer.md",
    "evidence/aimc-simulator-adapters/converter-post-layout-real-candidate-builder.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-real-candidate-builder.md",
    "evidence/aimc-simulator-adapters/converter-post-layout-submission-preview.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-submission-preview.md",
    "evidence/aimc-simulator-adapters/converter-post-layout-evidence-leakage-audit.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-evidence-leakage-audit.md",
    "evidence/aimc-simulator-adapters/converter-post-layout-temporary-submission-proof.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-temporary-submission-proof.md",
    "evidence/aimc-simulator-adapters/converter-post-layout-real-artifact-discovery.json",
    "evidence/aimc-simulator-adapters/converter-post-layout-real-artifact-discovery.md",
    "evidence/aimc-simulator-adapters/first-real-converter-same-candidate-extracted-rc.json",
    "evidence/aimc-simulator-adapters/first-real-converter-same-candidate-extracted-rc.md",
    "evidence/aimc-simulator-adapters/first-real-converter-frontend-to-input-stage-proxy.json",
    "evidence/aimc-simulator-adapters/first-real-converter-frontend-to-input-stage-proxy.md",
    "evidence/aimc-simulator-adapters/first-real-converter-frontend-active-handoff-estimate.json",
    "evidence/aimc-simulator-adapters/first-real-converter-frontend-active-handoff-estimate.md",
    "evidence/aimc-simulator-adapters/first-real-converter-combined-active-handoff-work-order.json",
    "evidence/aimc-simulator-adapters/first-real-converter-combined-active-handoff-work-order.md",
    "evidence/aimc-simulator-adapters/sky130-frontend-input-stage-handoff-candidate.json",
    "evidence/aimc-simulator-adapters/sky130-frontend-input-stage-handoff-candidate.md",
    "evidence/aimc-simulator-adapters/sky130-transistor-handoff-replacement-work-order.json",
    "evidence/aimc-simulator-adapters/sky130-transistor-handoff-replacement-work-order.md",
    "evidence/aimc-simulator-adapters/sky130-frontend-transistor-input-stage-handoff-candidate.json",
    "evidence/aimc-simulator-adapters/sky130-frontend-transistor-input-stage-handoff-candidate.md",
    "evidence/aimc-simulator-adapters/sky130-transistor-handoff-decomposition.json",
    "evidence/aimc-simulator-adapters/sky130-transistor-handoff-decomposition.md",
    "evidence/aimc-simulator-adapters/sky130-transistor-handoff-probe-ladder.json",
    "evidence/aimc-simulator-adapters/sky130-transistor-handoff-probe-ladder.md",
    "evidence/aimc-simulator-adapters/sky130-frontend-sense-to-transistor-op-handoff.json",
    "evidence/aimc-simulator-adapters/sky130-frontend-sense-to-transistor-op-handoff.md",
    "evidence/aimc-simulator-adapters/sky130-frontend-sense-to-transistor-short-transient.json",
    "evidence/aimc-simulator-adapters/sky130-frontend-sense-to-transistor-short-transient.md",
    "evidence/aimc-simulator-adapters/sky130-frontend-sense-to-transistor-ramp-startup.json",
    "evidence/aimc-simulator-adapters/sky130-frontend-sense-to-transistor-ramp-startup.md",
    "evidence/aimc-simulator-adapters/sky130-extracted-frontend-to-transistor-gate-startup.json",
    "evidence/aimc-simulator-adapters/sky130-extracted-frontend-to-transistor-gate-startup.md",
    "evidence/aimc-simulator-adapters/sky130-extracted-frontend-gate-coupling-sweep.json",
    "evidence/aimc-simulator-adapters/sky130-extracted-frontend-gate-coupling-sweep.md",
    "evidence/aimc-simulator-adapters/sky130-extracted-frontend-source-follower-handoff.json",
    "evidence/aimc-simulator-adapters/sky130-extracted-frontend-source-follower-handoff.md",
    "evidence/aimc-simulator-adapters/sky130-extracted-frontend-differential-preamp.json",
    "evidence/aimc-simulator-adapters/sky130-extracted-frontend-differential-preamp.md",
    "evidence/aimc-simulator-adapters/sky130-measured-sense-differential-preamp.json",
    "evidence/aimc-simulator-adapters/sky130-measured-sense-differential-preamp.md",
    "evidence/aimc-simulator-adapters/sky130-measured-sense-preamp-bias-sweep.json",
    "evidence/aimc-simulator-adapters/sky130-measured-sense-preamp-bias-sweep.md",
    "evidence/aimc-simulator-adapters/sky130-measured-sense-preamp-op-map.json",
    "evidence/aimc-simulator-adapters/sky130-measured-sense-preamp-op-map.md",
    "evidence/aimc-simulator-adapters/sky130-preamp-known-good-sanity-gap.json",
    "evidence/aimc-simulator-adapters/sky130-preamp-known-good-sanity-gap.md",
    "evidence/aimc-simulator-adapters/sky130-preamp-known-good-reproduction.json",
    "evidence/aimc-simulator-adapters/sky130-preamp-known-good-reproduction.md",
    "evidence/aimc-simulator-adapters/sky130-extracted-frontend-preamp-gain-sweep.json",
    "evidence/aimc-simulator-adapters/sky130-extracted-frontend-preamp-gain-sweep.md",
    "evidence/aimc-simulator-adapters/sky130-frontend-preamp-interface-redesign-target.json",
    "evidence/aimc-simulator-adapters/sky130-frontend-preamp-interface-redesign-target.md",
    "evidence/aimc-simulator-adapters/sky130-frontend-preamp-capacitance-budget.json",
    "evidence/aimc-simulator-adapters/sky130-frontend-preamp-capacitance-budget.md",
    "evidence/aimc-simulator-adapters/sky130-frontend-preamp-interface-work-order.json",
    "evidence/aimc-simulator-adapters/sky130-frontend-preamp-interface-work-order.md",
    "evidence/aimc-simulator-adapters/sky130-frontend-preamp-interface-candidate.json",
    "evidence/aimc-simulator-adapters/sky130-frontend-preamp-interface-candidate.md",
    "evidence/aimc-simulator-adapters/sky130-lower-waste-frontend-preamp-candidate.json",
    "evidence/aimc-simulator-adapters/sky130-lower-waste-frontend-preamp-candidate.md",
    "evidence/aimc-simulator-adapters/sky130-combined-coupling-waste-frontend-preamp-candidate.json",
    "evidence/aimc-simulator-adapters/sky130-combined-coupling-waste-frontend-preamp-candidate.md",
    "evidence/aimc-simulator-adapters/sky130-active-isolation-preamp-target.json",
    "evidence/aimc-simulator-adapters/sky130-active-isolation-preamp-target.md",
    "evidence/aimc-simulator-adapters/sky130-active-isolation-preamp-candidate.json",
    "evidence/aimc-simulator-adapters/sky130-active-isolation-preamp-candidate.md",
    "evidence/aimc-simulator-adapters/sky130-offset-calibrated-active-isolation-preamp.json",
    "evidence/aimc-simulator-adapters/sky130-offset-calibrated-active-isolation-preamp.md",
    "evidence/aimc-simulator-adapters/sky130-transistor-active-isolation-preamp.json",
    "evidence/aimc-simulator-adapters/sky130-transistor-active-isolation-preamp.md",
    "evidence/aimc-simulator-adapters/sky130-swapped-transistor-active-isolation-preamp.json",
    "evidence/aimc-simulator-adapters/sky130-swapped-transistor-active-isolation-preamp.md",
    "evidence/aimc-simulator-adapters/sky130-polarity-corrected-transistor-handoff.json",
    "evidence/aimc-simulator-adapters/sky130-polarity-corrected-transistor-handoff.md",
    "evidence/aimc-simulator-adapters/sky130-polarity-contract-latch-sar-risk.json",
    "evidence/aimc-simulator-adapters/sky130-polarity-contract-latch-sar-risk.md",
    "evidence/aimc-simulator-adapters/sky130-polarity-named-isolated-latch-work-order.json",
    "evidence/aimc-simulator-adapters/sky130-polarity-named-isolated-latch-work-order.md",
    "evidence/aimc-simulator-adapters/sky130-source-follower-isolated-latch-candidate.json",
    "evidence/aimc-simulator-adapters/sky130-source-follower-isolated-latch-candidate.md",
    "evidence/aimc-simulator-adapters/sky130-sampled-internal-decision-cap-latch-candidate.json",
    "evidence/aimc-simulator-adapters/sky130-sampled-internal-decision-cap-latch-candidate.md",
    "evidence/aimc-simulator-adapters/sky130-two-phase-preamp-latch-candidate.json",
    "evidence/aimc-simulator-adapters/sky130-two-phase-preamp-latch-candidate.md",
    "evidence/aimc-simulator-adapters/sky130-isolated-latch-debug-ladder.json",
    "evidence/aimc-simulator-adapters/sky130-isolated-latch-debug-ladder.md",
    "evidence/aimc-simulator-adapters/sky130-preamp-alone-latch-debug.json",
    "evidence/aimc-simulator-adapters/sky130-preamp-alone-latch-debug.md",
    "evidence/aimc-simulator-adapters/sky130-preamp-op-latch-debug.json",
    "evidence/aimc-simulator-adapters/sky130-preamp-op-latch-debug.md",
    "evidence/aimc-simulator-adapters/sky130-known-good-shape-preamp-op-latch-debug.json",
    "evidence/aimc-simulator-adapters/sky130-known-good-shape-preamp-op-latch-debug.md",
    "evidence/aimc-simulator-adapters/sky130-preamp-op-deck-diff-diagnosis.json",
    "evidence/aimc-simulator-adapters/sky130-preamp-op-deck-diff-diagnosis.md",
    "evidence/aimc-simulator-adapters/sky130-known-good-shape-preamp-transient-latch-debug.json",
    "evidence/aimc-simulator-adapters/sky130-known-good-shape-preamp-transient-latch-debug.md",
    "evidence/aimc-simulator-adapters/sky130-latch-alone-from-preamp-voltage-debug.json",
    "evidence/aimc-simulator-adapters/sky130-latch-alone-from-preamp-voltage-debug.md",
    "evidence/aimc-simulator-adapters/sky130-latch-alone-swapped-preamp-voltage-debug.json",
    "evidence/aimc-simulator-adapters/sky130-latch-alone-swapped-preamp-voltage-debug.md",
    "evidence/aimc-simulator-adapters/sky130-swapped-latch-clock-timing-debug.json",
    "evidence/aimc-simulator-adapters/sky130-swapped-latch-clock-timing-debug.md",
    "evidence/aimc-simulator-adapters/sky130-clocked-latch-output-convention-diagnostic.json",
    "evidence/aimc-simulator-adapters/sky130-clocked-latch-output-convention-diagnostic.md",
    "evidence/aimc-simulator-adapters/sky130-corrected-convention-sample-hold-latch-kickback.json",
    "evidence/aimc-simulator-adapters/sky130-corrected-convention-sample-hold-latch-kickback.md",
    "evidence/aimc-simulator-adapters/sky130-corrected-convention-capacitive-isolation-confirm.json",
    "evidence/aimc-simulator-adapters/sky130-corrected-convention-capacitive-isolation-confirm.md",
    "evidence/aimc-simulator-adapters/sky130-corrected-convention-isolation-range-stress.json",
    "evidence/aimc-simulator-adapters/sky130-corrected-convention-isolation-range-stress.md",
    "evidence/aimc-simulator-adapters/simulator-to-post-layout-gap-audit.json",
    "evidence/aimc-simulator-adapters/simulator-to-post-layout-gap-audit.md",
    "evidence/aimc-hardware-lab/digital-physical-artifact-boundary.json",
    "evidence/aimc-hardware-lab/digital-physical-artifact-boundary.md",
    "evidence/aimc-simulator-adapters/analog-converter-layout-work-order.json",
    "evidence/aimc-simulator-adapters/analog-converter-layout-work-order.md",
    "evidence/aimc-simulator-adapters/analog-converter-layout-starter-package.json",
    "evidence/aimc-simulator-adapters/analog-converter-layout-starter-package.md",
    "evidence/aimc-simulator-adapters/analog-converter-layout-tool-readiness.json",
    "evidence/aimc-simulator-adapters/analog-converter-layout-tool-readiness.md",
    "evidence/aimc-simulator-adapters/analog-converter-pdk-readiness.json",
    "evidence/aimc-simulator-adapters/analog-converter-pdk-readiness.md",
    "evidence/aimc-simulator-adapters/magic-sky130-extraction-smoke.json",
    "evidence/aimc-simulator-adapters/magic-sky130-extraction-smoke.md",
    "evidence/aimc-simulator-adapters/magic-sky130-compatibility.json",
    "evidence/aimc-simulator-adapters/magic-sky130-compatibility.md",
    "evidence/aimc-simulator-adapters/row-dac-10b-layout-smoke.json",
    "evidence/aimc-simulator-adapters/row-dac-10b-layout-smoke.md",
    "evidence/aimc-simulator-adapters/converter-starter-layout-smoke.json",
    "evidence/aimc-simulator-adapters/converter-starter-layout-smoke.md",
    "evidence/aimc-simulator-adapters/analog-converter-sky130-workbench-env.json",
    "evidence/aimc-simulator-adapters/analog-converter-sky130-workbench-env.md",
    "evidence/aimc-simulator-adapters/analog-converter-physical-cell-gate.json",
    "evidence/aimc-simulator-adapters/analog-converter-physical-cell-gate.md",
    "evidence/aimc-simulator-adapters/analog-converter-physical-flow-run.json",
    "evidence/aimc-simulator-adapters/analog-converter-physical-flow-run.md",
    "evidence/aimc-simulator-adapters/crosssim-layout-risk-adapter.json",
    "evidence/aimc-simulator-adapters/crosssim-layout-risk-adapter.md",
    "evidence/aimc-simulator-adapters/simulator-adapter-status.json",
    "evidence/aimc-simulator-adapters/simulator-adapter-status.md",
    "evidence/aimc-simulator-adapters/dry-run/aihwkit-analog-error-simulation.dry-run.json",
    "evidence/aimc-simulator-adapters/dry-run/crosssim-analog-error-simulation.dry-run.json",
    "labs/analog/inverter-ngspice/inverter.sp",
    "labs/analog/inverter-ngspice/README.md",
    "labs/analog/rc-step-ngspice/README.md",
    "labs/analog/rc-step-ngspice/rc_step.sp",
    "labs/digital/counter-verilog/counter.v",
    "labs/digital/counter-verilog/counter_tb.v",
    "labs/digital/counter-verilog/README.md",
    "labs/digital/aimc-control-plane-rtl/README.md",
    "labs/digital/aimc-control-plane-rtl/aimc_control_plane.v",
    "labs/digital/aimc-control-plane-rtl/aimc_control_plane_tb.v",
    "labs/digital/aimc-control-plane-rtl/aimc_operation_partition.v",
    "labs/digital/aimc-control-plane-rtl/aimc_operation_partition_tb.v",
    "labs/digital/aimc-control-plane-rtl/aimc_tile_readout.v",
    "labs/digital/aimc-control-plane-rtl/aimc_tile_readout_tb.v",
    "labs/digital/aimc-control-plane-rtl/aimc_micro_tile_controller.v",
    "labs/digital/aimc-control-plane-rtl/aimc_micro_tile_controller_tb.v",
    "labs/digital/aimc-control-plane-rtl/aimc_tile_service_scheduler.v",
    "labs/digital/aimc-control-plane-rtl/aimc_tile_service_scheduler_tb.v",
    "labs/digital/aimc-control-plane-rtl/aimc_error_budget_governor.v",
    "labs/digital/aimc-control-plane-rtl/aimc_error_budget_governor_tb.v",
    "labs/digital/aimc-control-plane-rtl/aimc_scheduler_governor.v",
    "labs/digital/aimc-control-plane-rtl/aimc_scheduler_governor_tb.v",
    "labs/digital/aimc-control-plane-rtl/aimc_scheduler_governor_pipelined.v",
    "labs/digital/aimc-control-plane-rtl/aimc_scheduler_governor_pipelined_tb.v",
    "labs/digital/aimc-control-plane-rtl/aimc_model_impact_governor_tb.v",
    "labs/digital/aimc-control-plane-rtl/generated_tile_scheduler_cases.vh",
    "labs/digital/aimc-control-plane-rtl/generated_error_budget_governor_cases.vh",
    "labs/digital/aimc-control-plane-rtl/generated_model_impact_governor_cases.vh",
    "labs/digital/aimc-control-plane-rtl/generated_micro_tile_cases.vh",
    "labs/digital/aimc-control-plane-rtl/check_generated_micro_tile_trace.py",
    "labs/digital/aimc-control-plane-rtl/check_generated_scheduler_trace.py",
    "labs/digital/aimc-control-plane-rtl/check_generated_error_budget_governor_trace.py",
    "labs/digital/aimc-control-plane-rtl/check_generated_model_impact_governor_trace.py",
    "labs/digital/aimc-control-plane-rtl/check_generated_integrated_scheduler_governor_trace.py",
    "labs/digital/aimc-control-plane-rtl/check_generated_pipelined_scheduler_governor_trace.py",
    "labs/digital/aimc-control-plane-synthesis/README.md",
    "labs/digital/aimc-control-plane-synthesis/synth_aimc_control_plane.ys",
    "labs/digital/aimc-control-plane-synthesis/synth_aimc_operation_partition.ys",
    "labs/digital/aimc-control-plane-synthesis/synth_aimc_tile_readout.ys",
    "labs/digital/aimc-control-plane-synthesis/synth_aimc_micro_tile_controller.ys",
    "labs/digital/aimc-control-plane-synthesis/synth_aimc_tile_service_scheduler.ys",
    "labs/digital/aimc-control-plane-synthesis/synth_aimc_error_budget_governor.ys",
    "labs/digital/aimc-control-plane-synthesis/synth_aimc_scheduler_governor.ys",
    "labs/digital/aimc-control-plane-synthesis/synth_aimc_scheduler_governor_pipelined.ys",
    "labs/digital/aimc-control-plane-synthesis/reports/README.md",
    "labs/digital/aimc-control-plane-synthesis/reports/synthesis-interpretation.md",
    "labs/digital/aimc-control-plane-synthesis/reports/aimc_operation_partition_synth.log",
    "labs/digital/aimc-control-plane-synthesis/reports/aimc_operation_partition_synth.v",
    "labs/digital/aimc-control-plane-synthesis/reports/aimc_tile_readout_synth.log",
    "labs/digital/aimc-control-plane-synthesis/reports/aimc_tile_readout_synth.v",
    "labs/digital/aimc-control-plane-synthesis/reports/aimc_micro_tile_controller_synth.log",
    "labs/digital/aimc-control-plane-synthesis/reports/aimc_micro_tile_controller_synth.v",
    "labs/digital/aimc-control-plane-synthesis/reports/aimc_tile_service_scheduler_synth.log",
    "labs/digital/aimc-control-plane-synthesis/reports/aimc_tile_service_scheduler_synth.v",
    "labs/digital/aimc-control-plane-synthesis/reports/aimc_error_budget_governor_synth.log",
    "labs/digital/aimc-control-plane-synthesis/reports/aimc_error_budget_governor_synth.v",
    "labs/digital/aimc-control-plane-synthesis/reports/aimc_scheduler_governor_synth.log",
    "labs/digital/aimc-control-plane-synthesis/reports/aimc_scheduler_governor_synth.v",
    "labs/digital/aimc-control-plane-synthesis/reports/aimc_scheduler_governor_pipelined_synth.log",
    "labs/digital/aimc-control-plane-synthesis/reports/aimc_scheduler_governor_pipelined_synth.v",
    "labs/digital/yosys-counter-synthesis/README.md",
    "labs/digital/yosys-counter-synthesis/synth_counter.ys",
    "labs/eda/README.md",
    "labs/eda/aimc-control-plane-timing-readiness/README.md",
    "labs/eda/aimc-control-plane-timing-readiness/analyze_timing_readiness.py",
    "labs/eda/aimc-control-plane-openlane-prep/README.md",
    "labs/eda/aimc-control-plane-openlane-prep/openlane-partial-run-report.md",
    "labs/eda/aimc-control-plane-openlane-prep/openlane-no-cts-final-report.md",
    "labs/eda/aimc-control-plane-openlane-prep/openlane-no-cts-metrics-summary.md",
    "labs/eda/aimc-control-plane-openlane-prep/config.json",
    "labs/eda/aimc-control-plane-openlane-prep/config.tcl",
    "labs/eda/aimc-control-plane-openlane-prep/config_no_cts.tcl",
    "labs/eda/aimc-control-plane-openlane-prep/constraint.sdc",
    "labs/eda/aimc-control-plane-openlane-prep/extract_openlane_metrics.py",
    "labs/eda/aimc-control-plane-openlane-prep/pin_order.cfg",
    "labs/eda/aimc-control-plane-openlane-prep/src/aimc_control_plane.v",
    "labs/eda/aimc-control-plane-openlane-prep/src/constraint.sdc",
    "labs/eda/aimc-operation-partition-openlane-prep/README.md",
    "labs/eda/aimc-operation-partition-openlane-prep/config.json",
    "labs/eda/aimc-operation-partition-openlane-prep/config.tcl",
    "labs/eda/aimc-operation-partition-openlane-prep/config_no_cts.tcl",
    "labs/eda/aimc-operation-partition-openlane-prep/config_output_registered.tcl",
    "labs/eda/aimc-operation-partition-openlane-prep/config_output_registered_no_cts.tcl",
    "labs/eda/aimc-operation-partition-openlane-prep/analyze_cts_attempts.py",
    "labs/eda/aimc-operation-partition-openlane-prep/run_isolated_cts_experiment.sh",
    "labs/eda/aimc-operation-partition-openlane-prep/isolated-cts-experiment-plan.md",
    "labs/eda/aimc-operation-partition-openlane-prep/cts-debug-summary.md",
    "labs/eda/aimc-operation-partition-openlane-prep/openlane-cts-attempt-report.md",
    "labs/eda/aimc-operation-partition-openlane-prep/openlane-no-cts-final-report.md",
    "labs/eda/aimc-operation-partition-openlane-prep/constraint.sdc",
    "labs/eda/aimc-operation-partition-openlane-prep/pin_order.cfg",
    "labs/eda/aimc-operation-partition-openlane-prep/src/aimc_operation_partition.v",
    "labs/eda/aimc-operation-partition-openlane-prep/src/aimc_operation_partition_physical.v",
    "labs/eda/aimc-operation-partition-openlane-prep/src/aimc_operation_partition_output_registered.v",
    "labs/eda/aimc-operation-partition-openlane-prep/src/constraint.sdc",
    "labs/eda/aimc-micro-tile-controller-openlane-prep/README.md",
    "labs/eda/aimc-micro-tile-controller-openlane-prep/config.json",
    "labs/eda/aimc-micro-tile-controller-openlane-prep/config.tcl",
    "labs/eda/aimc-micro-tile-controller-openlane-prep/config_no_cts.tcl",
    "labs/eda/aimc-micro-tile-controller-openlane-prep/openlane-no-cts-final-report.md",
    "labs/eda/aimc-micro-tile-controller-openlane-prep/analyze_no_cts_result.py",
    "labs/eda/aimc-micro-tile-controller-openlane-prep/openlane-no-cts-metrics-summary.md",
    "labs/eda/aimc-micro-tile-controller-openlane-prep/constraint.sdc",
    "labs/eda/aimc-micro-tile-controller-openlane-prep/pin_order.cfg",
    "labs/eda/aimc-micro-tile-controller-openlane-prep/src/aimc_micro_tile_controller.v",
    "labs/eda/aimc-micro-tile-controller-openlane-prep/src/aimc_operation_partition.v",
    "labs/eda/aimc-micro-tile-controller-openlane-prep/src/aimc_tile_readout.v",
    "labs/eda/aimc-micro-tile-controller-openlane-prep/src/constraint.sdc",
    "labs/eda/aimc-tile-service-scheduler-openlane-prep/README.md",
    "labs/eda/aimc-tile-service-scheduler-openlane-prep/config.json",
    "labs/eda/aimc-tile-service-scheduler-openlane-prep/config.tcl",
    "labs/eda/aimc-tile-service-scheduler-openlane-prep/config_no_cts.tcl",
    "labs/eda/aimc-tile-service-scheduler-openlane-prep/openlane-no-cts-final-report.md",
    "labs/eda/aimc-tile-service-scheduler-openlane-prep/openlane-no-cts-metrics-summary.md",
    "labs/eda/aimc-tile-service-scheduler-openlane-prep/openlane-cts-final-report.md",
    "labs/eda/aimc-tile-service-scheduler-openlane-prep/openlane-cts-metrics-summary.md",
    "labs/eda/aimc-tile-service-scheduler-openlane-prep/analyze_no_cts_result.py",
    "labs/eda/aimc-tile-service-scheduler-openlane-prep/constraint.sdc",
    "labs/eda/aimc-tile-service-scheduler-openlane-prep/pin_order.cfg",
    "labs/eda/aimc-tile-service-scheduler-openlane-prep/src/aimc_tile_service_scheduler.v",
    "labs/eda/aimc-tile-service-scheduler-openlane-prep/src/aimc_tile_service_scheduler_physical.v",
    "labs/eda/aimc-tile-service-scheduler-openlane-prep/src/constraint.sdc",
    "labs/eda/aimc-error-budget-governor-openlane-prep/README.md",
    "labs/eda/aimc-error-budget-governor-openlane-prep/config.json",
    "labs/eda/aimc-error-budget-governor-openlane-prep/config.tcl",
    "labs/eda/aimc-error-budget-governor-openlane-prep/config_no_cts.tcl",
    "labs/eda/aimc-error-budget-governor-openlane-prep/openlane-no-cts-final-report.md",
    "labs/eda/aimc-error-budget-governor-openlane-prep/openlane-no-cts-metrics-summary.md",
    "labs/eda/aimc-error-budget-governor-openlane-prep/openlane-cts-final-report.md",
    "labs/eda/aimc-error-budget-governor-openlane-prep/openlane-cts-metrics-summary.md",
    "labs/eda/aimc-error-budget-governor-openlane-prep/analyze_no_cts_result.py",
    "labs/eda/aimc-error-budget-governor-openlane-prep/constraint.sdc",
    "labs/eda/aimc-error-budget-governor-openlane-prep/pin_order.cfg",
    "labs/eda/aimc-error-budget-governor-openlane-prep/src/aimc_error_budget_governor.v",
    "labs/eda/aimc-error-budget-governor-openlane-prep/src/aimc_error_budget_governor_physical.v",
    "labs/eda/aimc-error-budget-governor-openlane-prep/src/constraint.sdc",
    "labs/eda/aimc-scheduler-governor-openlane-prep/README.md",
    "labs/eda/aimc-scheduler-governor-openlane-prep/config.json",
    "labs/eda/aimc-scheduler-governor-openlane-prep/config.tcl",
    "labs/eda/aimc-scheduler-governor-openlane-prep/config_no_cts.tcl",
    "labs/eda/aimc-scheduler-governor-openlane-prep/config_8ns.tcl",
    "labs/eda/aimc-scheduler-governor-openlane-prep/config_8ns_fanout20.tcl",
    "labs/eda/aimc-scheduler-governor-openlane-prep/config_no_cts_8ns.tcl",
    "labs/eda/aimc-scheduler-governor-openlane-prep/analyze_no_cts_result.py",
    "labs/eda/aimc-scheduler-governor-openlane-prep/openlane-no-cts-5ns-timing-boundary-report.md",
    "labs/eda/aimc-scheduler-governor-openlane-prep/openlane-no-cts-5ns-metrics-summary.md",
    "labs/eda/aimc-scheduler-governor-openlane-prep/openlane-no-cts-8ns-final-report.md",
    "labs/eda/aimc-scheduler-governor-openlane-prep/openlane-no-cts-8ns-metrics-summary.md",
    "labs/eda/aimc-scheduler-governor-openlane-prep/openlane-cts-8ns-final-report.md",
    "labs/eda/aimc-scheduler-governor-openlane-prep/openlane-cts-8ns-metrics-summary.md",
    "labs/eda/aimc-scheduler-governor-openlane-prep/openlane-cts-8ns-control-reset-fanout20-final-report.md",
    "labs/eda/aimc-scheduler-governor-openlane-prep/openlane-cts-8ns-control-reset-fanout20-metrics-summary.md",
    "labs/eda/aimc-scheduler-governor-openlane-prep/constraint.sdc",
    "labs/eda/aimc-scheduler-governor-openlane-prep/constraint_8ns.sdc",
    "labs/eda/aimc-scheduler-governor-openlane-prep/pin_order.cfg",
    "labs/eda/aimc-scheduler-governor-openlane-prep/src/aimc_tile_service_scheduler.v",
    "labs/eda/aimc-scheduler-governor-openlane-prep/src/aimc_error_budget_governor.v",
    "labs/eda/aimc-scheduler-governor-openlane-prep/src/aimc_scheduler_governor.v",
    "labs/eda/aimc-scheduler-governor-openlane-prep/src/aimc_scheduler_governor_physical.v",
    "labs/eda/aimc-scheduler-governor-openlane-prep/src/constraint.sdc",
    "labs/eda/aimc-scheduler-governor-openlane-prep/src/constraint_8ns.sdc",
    "labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/README.md",
    "labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/config.json",
    "labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/config.tcl",
    "labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/config_5ns_fanout20.tcl",
    "labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/config_8ns.tcl",
    "labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/config_8ns_fanout20.tcl",
    "labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/config_no_cts.tcl",
    "labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/config_no_cts_8ns.tcl",
    "labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/constraint.sdc",
    "labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/constraint_8ns.sdc",
    "labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/pin_order.cfg",
    "labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/analyze_no_cts_result.py",
    "labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/openlane-5ns-metrics-summary.md",
    "labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/openlane-5ns-split-metrics-summary.md",
    "labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/openlane-5ns-control-reset-fanout20-metrics-summary.md",
    "labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/src/aimc_tile_service_scheduler.v",
    "labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/src/aimc_error_budget_governor.v",
    "labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/src/aimc_scheduler_governor.v",
    "labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/src/aimc_scheduler_governor_pipelined.v",
    "labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/src/constraint.sdc",
    "labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/src/constraint_8ns.sdc",
    "labs/eda/timing-closure-reading/README.md",
    "labs/eda/layout-verification-reading/README.md",
    "labs/analog/analog-in-memory-foundation-model-hardware/python/transformer_partition_simulator.py",
    "labs/analog/analog-in-memory-foundation-model-hardware/python/tile_readout_boundary.py",
    "labs/analog/analog-in-memory-foundation-model-hardware/python/micro_tile_execution_trace.py",
    "labs/analog/analog-in-memory-foundation-model-hardware/python/generate_micro_tile_rtl_vectors.py",
    "labs/analog/analog-in-memory-foundation-model-hardware/python/transformer_layer_trust_trace.py",
    "labs/analog/analog-in-memory-foundation-model-hardware/python/error_budget_ledger.py",
    "labs/analog/analog-in-memory-foundation-model-hardware/python/error_budget_governor_trace.py",
    "labs/analog/analog-in-memory-foundation-model-hardware/python/tile_telemetry_policy.py",
    "labs/analog/analog-in-memory-foundation-model-hardware/python/multi_tile_scheduler_runtime.py",
    "labs/analog/analog-in-memory-foundation-model-hardware/python/integrated_scheduler_governor_runtime.py",
    "labs/analog/analog-in-memory-foundation-model-hardware/python/spice_crossbar_comparison.py",
    "labs/analog/analog-in-memory-foundation-model-hardware/python/spice_signed_crossbar_comparison.py",
    "labs/analog/analog-in-memory-foundation-model-hardware/python/spice_row_drop_comparison.py",
    "labs/analog/analog-in-memory-foundation-model-hardware/python/analog_tile_error_evidence.py",
    "labs/analog/analog-in-memory-foundation-model-hardware/python/analog_tile_state_trace.py",
    "labs/analog/analog-in-memory-foundation-model-hardware/python/converter_boundary_sweep.py",
    "labs/analog/analog-in-memory-foundation-model-hardware/python/row_dac_settling_spice.py",
    "labs/analog/analog-in-memory-foundation-model-hardware/python/sar_readout_12bit_spice.py",
    "labs/analog/analog-in-memory-foundation-model-hardware/python/shared_converter_loading_spice.py",
    "labs/analog/analog-in-memory-foundation-model-hardware/python/converter_supply_energy_spice.py",
    "labs/analog/analog-in-memory-foundation-model-hardware/spice/row_dac_settling_10bit.sp",
    "labs/analog/analog-in-memory-foundation-model-hardware/spice/sar_readout_12bit.sp",
    "labs/analog/analog-in-memory-foundation-model-hardware/spice/shared_converter_loading.sp",
    "labs/analog/analog-in-memory-foundation-model-hardware/spice/converter_supply_energy.sp",
    "labs/analog/analog-in-memory-foundation-model-hardware/python/tile_operating_point.py",
    "labs/analog/analog-in-memory-foundation-model-hardware/python/analog_nonideality_stack.py",
    "labs/analog/analog-in-memory-foundation-model-hardware/python/measured_tile_transformer_impact.py",
    "labs/analog/analog-in-memory-foundation-model-hardware/python/model_impact_governor_requests.py",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/transformer-partition-results.md",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/spice-crossbar-comparison.csv",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/spice-crossbar-comparison.md",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/spice-signed-crossbar-comparison.csv",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/spice-signed-crossbar-comparison.md",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/spice-row-drop-comparison.csv",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/spice-row-drop-comparison.md",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/analog-tile-error-evidence.csv",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/analog-tile-error-evidence.md",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/analog-tile-state-trace.csv",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/analog-tile-state-trace.md",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/converter-boundary-sweep.csv",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/converter-boundary-sweep.md",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/tile-operating-point.csv",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/tile-operating-point.md",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/analog-nonideality-stack.csv",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/analog-nonideality-stack.md",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/measured-tile-transformer-impact.csv",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/measured-tile-transformer-impact.md",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/model-impact-governor-requests.csv",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/model-impact-governor-requests.md",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/backend-hardware-placement.json",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/backend-hardware-placement-governor-input.csv",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/backend-hardware-placement-governor-input.md",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/generated-micro-tile-rtl-vectors.csv",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/generated-micro-tile-rtl-vectors.md",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/multi-tile-scheduler-runtime.csv",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/multi-tile-scheduler-runtime.md",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/error-budget-governor-trace.csv",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/error-budget-governor-trace.md",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/integrated-scheduler-governor-runtime.csv",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/integrated-scheduler-governor-runtime.md",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/converter-circuit-simulation-estimate.csv",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/row-dac-settling-spice.csv",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/row-dac-settling-spice.md",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/sar-readout-12bit-spice.csv",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/sar-readout-12bit-spice.md",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/shared-converter-loading-spice.csv",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/shared-converter-loading-spice.md",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/converter-supply-energy-spice.csv",
    "labs/analog/analog-in-memory-foundation-model-hardware/measurements/converter-supply-energy-spice.md",
]

REQUIRED_PHRASES = {
    "README.md": [
        "Analog, Digital Chip Design, and EDA",
        "Tool Stack",
        "First Writing Goal",
    ],
    "docs/roadmaps/end-to-end-goal.md": [
        "Analog Design",
        "Digital Design",
        "EDA",
        "AI For EDA",
    ],
    "docs/synthesis.md": [
        "charge -> voltage/current",
        "false preservation",
        "verified manufactured chip",
    ],
    "docs/paper-corpus-synthesis.md": [
        "preservation under translation",
        "Open Flows Make The Translation Visible",
        "AI For EDA Is Useful Only Inside A Checked Loop",
        "Signoff Turns Hidden Physics Into Explicit Risk",
    ],
    "docs/coverage-audit.md": [
        "Current Proven Coverage",
        "Track Balance",
        "Thin Areas To Fix Next",
        "Next 25-Paper Target",
    ],
    "docs/analog-in-memory-foundation-model-synthesis.md": [
        "weight number -> programmed conductance",
        "Why Foundation Models Are A Hard Target",
        "The Architecture Argument",
        "The Scheduling Boundary",
        "The Wire Boundary",
        "The Input Boundary",
        "The Cost Boundary",
        "Analog Compute Is A Boundary Chain",
        "Prefill And Decode Stress Different Hardware",
        "Where Analog Compute Actually Helps",
        "Attention Is Changing Memory, Not Fixed Weights",
        "Softmax Turns Score Error Into Selection Error",
        "Transformer Block Error Is State Drift",
        "Stable Bias Accumulates Across Layers",
        "Calibration Is A Schedule, Not A Single Fix",
        "Tile Health Monitoring Spends Calibration Where Error Grows",
        "Analog Serving Policy Decides When To Use The Array",
        "Hybrid Analog Digital Accelerators Need A Control Plane",
        "Digital Control Logic Makes Analog Compute Checkable",
        "Analog Placement Is Not Analog Acceptance",
        "Hybrid AIMC System Architecture",
        "Transformer Operation Partition For Hybrid AIMC",
        "Physical Flow Turns Control Logic Into Geometry",
    ],
    "docs/research/analog-in-memory-foundation-model-reading-map.md": [
        "Analog Foundation Models",
        "Efficient Transformer Adaptation For AIMC",
        "AIMC Attention With Gain Cells",
        "Theme Articles To Derive",
    ],
    "docs/concepts/eda-is-constraint-solving.md": [
        "constraint set",
        "RTL to logic gates",
        "false preservation",
    ],
}


def fail(message: str) -> int:
    print(f"FAIL {message}")
    return 1


def main() -> int:
    for rel in REQUIRED:
        path = ROOT / rel
        if not path.exists():
            return fail(f"missing {rel}")
        if path.is_file() and path.stat().st_size == 0:
            return fail(f"empty {rel}")

    for rel, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                return fail(f"{rel} missing phrase {phrase!r}")

    concept_dir = ROOT / "docs" / "concepts"
    required_concept_markers = [
        "The object",
        "constraint",
        "concrete design move",
        "measurement",
        "failure mode",
    ]
    for concept_path in concept_dir.glob("*.md"):
        text = concept_path.read_text(encoding="utf-8")
        if len(text.split()) < 250:
            return fail(f"{concept_path.relative_to(ROOT)} is too short for first-principles treatment")
        lowered = text.lower()
        for marker in required_concept_markers:
            if marker.lower() not in lowered:
                return fail(f"{concept_path.relative_to(ROOT)} missing conceptual marker {marker!r}")

    concept_count = len(list((ROOT / "docs" / "concepts").glob("*.md")))
    if concept_count < 22:
        return fail("expected at least 22 concept articles after AI-for-EDA batch")
    analog_lab_count = len(list((ROOT / "labs" / "analog").glob("*")))
    digital_lab_count = len(list((ROOT / "labs" / "digital").glob("*")))
    eda_lab_count = len([p for p in (ROOT / "labs" / "eda").glob("*") if p.is_dir()])
    total_lab_count = analog_lab_count + digital_lab_count + eda_lab_count
    if total_lab_count < 6:
        return fail("expected at least 6 labs for the first milestone")

    concept_page_count = len(list((ROOT / "site" / "concepts").glob("*.html")))
    lab_page_count = len(list((ROOT / "site" / "labs").glob("*.html")))
    research_page_count = len(list((ROOT / "site" / "research").glob("*.html")))
    if concept_page_count != concept_count:
        return fail("site concept page count does not match concept article count")
    if lab_page_count < total_lab_count:
        return fail("site lab page count does not cover all labs")
    if research_page_count < 2:
        return fail("site research page count does not cover the research maps")

    site_index = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
    for marker in ["Concept Atlas", "Lab Track", "local research site"]:
        if marker not in site_index:
            return fail(f"site/index.html missing marker {marker!r}")
    for marker in [
        "AIMC Review Path",
        "Cross-Repo Loop Proof",
        "Current System State",
        "ONNX Fixture Inventory",
        "Simulator To Placement Decision",
        "AIHWKIT Residual Diagnostic",
        "AIHWKIT Ideal Forward Mapping",
        "AIHWKIT Forward Setting Sweep",
        "AIHWKIT Physical Setting Review",
        "AIHWKIT Current Tile Replay",
        "AIHWKIT Converter Upgrade Target",
        "AIHWKIT Converter Cost Model",
        "AIHWKIT Target Noise Sensitivity",
        "AIHWKIT Converter Break-Even",
        "Converter Circuit Evidence Contract",
        "Local Converter Circuit Estimate",
        "Converter Circuit-Simulation Estimate",
        "Converter SPICE Handoff Spec",
        "Row-DAC Settling SPICE Evidence",
        "SAR Readout SPICE Evidence",
        "Shared Converter Loading SPICE Evidence",
        "Converter Supply Energy SPICE Evidence",
        "Converter Post-Layout Readiness",
        "Converter Post-Layout Evidence Contract",
        "Converter Post-Layout Payload Template",
        "Converter Post-Layout Payload Validator",
        "Converter Post-Layout Break-Even Rerun Path",
        "Converter Post-Layout Strict Intake",
        "Converter Post-Layout Positive Path",
        "Converter Post-Layout Submission Path",
        "Converter Candidate Progress",
        "Converter Candidate Progress Gate",
        "Converter Candidate Preflight Gate",
        "Converter Candidate Submission Gate",
        "Converter Candidate Readiness Run",
        "Converter Post-Layout Handoff Manifest",
        "Residual-Aware Placement",
        "CrossSim Layout Risk",
        "Measured Runtime And Power",
        "Next Evidence Work Queue",
        "research/current-aimc-system-state.html",
        "research/onnx-fixture-inventory.html",
        "research/simulator-to-placement-decision-boundary.html",
        "research/aihwkit-residual-diagnostic.html",
        "research/aihwkit-ideal-forward-mapping-proof.html",
        "research/aihwkit-forward-setting-sweep.html",
        "research/aihwkit-physical-setting-review.html",
        "research/aihwkit-current-tile-boundary-replay.html",
        "research/aihwkit-converter-upgrade-target.html",
        "research/aihwkit-converter-cost-model.html",
        "research/aihwkit-target-noise-sensitivity.html",
        "research/aihwkit-converter-break-even.html",
        "research/converter-circuit-evidence-contract.html",
        "research/local-converter-circuit-estimate.html",
        "research/converter-circuit-simulation-estimate.html",
        "research/converter-spice-handoff-spec.html",
        "research/row-dac-settling-spice-evidence.html",
        "research/sar-readout-spice-evidence.html",
        "research/shared-converter-loading-spice-evidence.html",
        "research/converter-supply-energy-spice-evidence.html",
        "research/digital-physical-artifact-boundary.html",
        "research/simulator-to-post-layout-gap-audit.html",
        "research/analog-converter-layout-work-order.html",
        "research/analog-converter-layout-starter-package.html",
        "research/analog-converter-layout-tool-readiness.html",
        "research/analog-converter-pdk-readiness.html",
        "research/magic-sky130-extraction-smoke.html",
        "research/magic-sky130-compatibility.html",
        "research/row-dac-10b-layout-smoke.html",
        "research/converter-starter-layout-smoke.html",
        "research/analog-converter-sky130-workbench-env.html",
        "research/analog-converter-physical-cell-gate.html",
        "research/analog-converter-physical-flow-run.html",
        "research/converter-post-layout-readiness.html",
        "research/converter-post-layout-evidence-contract.html",
        "research/converter-post-layout-payload-template.html",
        "research/converter-post-layout-payload-validator.html",
        "research/converter-post-layout-break-even-rerun-path.html",
        "research/converter-post-layout-strict-intake.html",
        "research/converter-post-layout-positive-path.html",
        "research/converter-post-layout-submission-path.html",
        "research/converter-post-layout-candidate-progress-report.html",
        "research/converter-post-layout-candidate-progress-gate.html",
        "research/converter-post-layout-candidate-preflight-gate.html",
        "research/converter-post-layout-candidate-submission-gate.html",
        "research/converter-post-layout-candidate-readiness-run.html",
        "research/converter-post-layout-handoff-manifest.html",
        "research/converter-post-layout-blocker-ledger.html",
        "research/converter-post-layout-candidate-edit-plan.html",
        "research/converter-post-layout-same-run-gate.html",
        "research/crosssim-layout-risk-adapter.html",
        "research/measured-runtime-power-claim-upgrade-path.html",
        "research/next-aimc-evidence-work-queue.html",
        "research/aimc-end-to-end-proof-explanation.html",
        "research/aimc-remaining-proof-spine.html",
        "research/converter-evidence-ladder.html",
        "research/analog-to-digital-to-model-error-flow.html",
        "research/final-accepted-converter-gate.html",
        "research/first-real-converter-candidate-execution-plan.html",
        "research/first-real-converter-candidate-packet.html",
        "research/first-real-converter-rehearsal-payload.html",
        "research/first-real-converter-blocker-work-order.html",
        "research/first-real-converter-physical-object-audit.html",
        "research/first-real-converter-physical-object-assembly.html",
        "research/first-real-converter-energy-candidate.html",
        "research/first-real-converter-latency-candidate.html",
        "research/first-real-converter-noise-candidate.html",
        "research/first-real-converter-area-candidate.html",
        "research/first-real-converter-break-even-candidate.html",
        "research/first-real-converter-candidate-loop-strict-readiness.html",
        "research/first-real-converter-same-candidate-extracted-rc.html",
        "research/first-real-converter-frontend-to-input-stage-proxy.html",
        "research/first-real-converter-frontend-active-handoff-estimate.html",
        "research/first-real-converter-combined-active-handoff-work-order.html",
        "research/sky130-frontend-input-stage-handoff-candidate.html",
        "research/sky130-transistor-handoff-replacement-work-order.html",
    ]:
        if marker not in site_index:
            return fail(f"site/index.html missing AIMC review-path marker {marker!r}")

    site_research = (ROOT / "site" / "research.html").read_text(encoding="utf-8")
    for marker in ["Research Maps", "Paper Taxonomy", "Toolchain Map", "AIMC End-To-End Proof Explanation", "AIMC Remaining Proof Spine", "Comparator Decision Margin From First Principles", "Passive Frontend Vs Active Preamp", "From Active Macro To Real Transistor Handoff", "Sky130 Transistor Handoff Decomposition", "Sky130 Transistor Handoff Probe Ladder", "Sky130 Frontend Sense To Transistor OP Handoff", "Sky130 Frontend Sense To Transistor Short Transient", "Sky130 Frontend Sense To Transistor Ramp Startup", "Sky130 Preamp Known-Good Reproduction", "Sky130 Extracted Frontend Preamp Gain Sweep", "Sky130 Frontend Preamp Interface Redesign Target", "Sky130 Frontend Preamp Capacitance Budget", "Sky130 Frontend Preamp Interface Work Order", "Converter Evidence Ladder", "Analog-To-Digital-To-Model Error Flow", "Final Accepted Converter Gate", "First Real Converter Candidate Execution Plan", "First Real Converter Candidate Packet", "First Real Converter Rehearsal Payload", "First Real Converter Blocker Work Order", "First Real Converter Physical Object Audit", "First Real Converter Physical Object Assembly", "First Real Converter Energy Candidate", "First Real Converter Latency Candidate", "First Real Converter Noise Candidate", "First Real Converter Area Candidate", "First Real Converter Break-Even Candidate", "First Real Converter Candidate Loop Strict Readiness", "First Real Converter Same-Candidate Extracted RC", "First Real Converter Frontend To Input-Stage Proxy", "First Real Converter Frontend Active Handoff Estimate", "First Real Converter Combined Active Handoff Work Order", "Sky130 Frontend Input-Stage Handoff Candidate", "Sky130 Transistor Handoff Replacement Work Order", "Current Simulator Adapter Status", "Current AIMC System State", "ONNX Fixture Inventory", "AIHWKIT Residual Diagnostic", "AIHWKIT Ideal Forward Mapping Proof", "AIHWKIT Forward Setting Sweep", "AIHWKIT Physical Setting Review", "AIHWKIT Current Tile Boundary Replay", "AIHWKIT Converter Upgrade Target", "AIHWKIT Converter Cost Model", "AIHWKIT Target Noise Sensitivity", "AIHWKIT Converter Break-Even Boundary", "Converter Circuit-Simulation Estimate", "Converter SPICE Handoff Spec", "Row-DAC Settling SPICE Evidence", "SAR Readout SPICE Evidence", "Shared Converter Loading SPICE Evidence", "Converter Supply Energy SPICE Evidence", "Digital Physical Artifact Boundary", "Simulator To Post-Layout Gap Audit", "Analog Converter Layout Work Order", "Analog Converter Layout Starter Package", "Analog Converter Layout Tool Readiness", "Analog Converter PDK Readiness", "Magic Sky130 Extraction Smoke", "Magic Sky130 Compatibility", "Row DAC 10b Layout Smoke", "Converter Starter Layout Smoke", "Converter Starter Post-Layout Candidate", "Converter Starter Physical Artifacts", "Converter Starter Parasitic Load Estimate", "Converter Starter Parasitic Break-Even Rerun", "Converter Starter Extracted RC Ngspice", "Sky130 Transistor Sample Switch Ngspice", "Sky130 Sample Switch Hold Mode Ngspice", "Sky130 Sample Switch Hold Mitigation Sweep", "Sky130 Sample Switch Dummy Cancellation Ngspice", "Sky130 Bottom Plate Sampling Ngspice", "Sky130 Sample-Hold Topology Decision Gate", "Sky130 Buffered Sample-Hold Ngspice", "Sky130 Bootstrapped Switch Ngspice", "Sky130 Fully Differential Sampling Ngspice", "Sky130 Capacitive Isolation Both-Polarity Confirm", "Sky130 Capacitive Isolation Post-Layout Handoff", "Sky130 Capacitive Isolation Physical Cell Gap", "Sky130 Capacitive Isolation Post-Layout Both-Polarity", "Sky130 Capacitive Isolation Extracted Port-Mapping Diagnostic", "Sky130 Capacitive Isolation Extracted Coupling-Strength Sweep", "Sky130 Extracted Frontend Redesign Target", "Sky130 Balanced Frontend Work Order", "Sky130 Balanced Frontend Starter Extraction", "Sky130 Balanced Frontend Sign Preservation", "Sky130 Balanced Frontend Latch Decision", "Sky130 Balanced Frontend Sense-Gain Target", "Sky130 Strong Sense Frontend Candidate", "Sky130 Ultra Sense Frontend Candidate", "Sky130 Frontend Sense Efficiency Audit", "Differential Sampling Control Proof Ngspice", "Sky130 Single-Device Charge Injection Ngspice", "Sky130 Sample Switch Clock Edge Sweep", "Sky130 Sample-Hold Design Target", "Sky130 Differential Matching Requirement", "Sky130 Next Transistor Fixture Work Order", "Analog Converter Sky130 Workbench Environment", "Analog Converter Physical Cell Gate", "Analog Converter Physical Flow Run", "Converter Post-Layout Readiness", "Converter Post-Layout Evidence Contract", "Converter Post-Layout Payload Template", "Converter Post-Layout Payload Validator", "Converter Post-Layout Break-Even Rerun Path", "Converter Post-Layout Strict Intake", "Converter Post-Layout Positive Path", "Converter Post-Layout Submission Path", "Converter Post-Layout Candidate Progress Report", "Converter Post-Layout Candidate Progress Gate", "Converter Post-Layout Candidate Preflight Gate", "Converter Post-Layout Candidate Submission Gate", "Converter Post-Layout Candidate Readiness Run", "Converter Post-Layout Handoff Manifest", "Converter Post-Layout Blocker Ledger", "Converter Post-Layout Candidate Edit Plan", "Converter Post-Layout Same-Run Gate", "Analog Simulator Adapter Output Contract", "Guarded Simulator Payload Import", "Optional AIMC Simulator Install Path", "Optional Simulator Payload Run Path", "Workload-Shaped Simulator Evidence", "Tensor-Shaped Simulator Evidence", "Projection-Stack Simulator Evidence", "Attention-Block Simulator Evidence", "Calibrated Attention-Block Simulator Evidence", "Simulator To Placement Decision Boundary", "CrossSim Layout-Risk Adapter", "Measured Runtime And Power Claim Upgrade Path", "Next AIMC Evidence Work Queue"]:
        if marker not in site_research:
            return fail(f"site/research.html missing marker {marker!r}")

    end_to_end_explanation_page = (ROOT / "site" / "research" / "aimc-end-to-end-proof-explanation.html").read_text(encoding="utf-8")
    for marker in ["model operation", "analog array signal", "comparator decision", "mixed-signal trust boundary", "0.437908", "2.28x", "sense-efficiency audit", "cannot yet claim accepted post-layout converter evidence"]:
        if marker not in end_to_end_explanation_page:
            return fail(f"site/research/aimc-end-to-end-proof-explanation.html missing marker {marker!r}")

    remaining_spine_page = (ROOT / "site" / "research" / "aimc-remaining-proof-spine.html").read_text(encoding="utf-8")
    for marker in ["AIMC Remaining Proof Spine", "model operation", "simulator target", "sampled voltage", "isolated latch decision", "converter code", "digital correction and fallback", "model placement decision", "0.1 fF", "12/12", "outp - outn", "strict preflight still rejects", "clock stress", "model placement rerun"]:
        if marker not in remaining_spine_page:
            return fail(f"site/research/aimc-remaining-proof-spine.html missing marker {marker!r}")

    comparator_margin_page = (ROOT / "site" / "research" / "comparator-decision-margin-from-first-principles.html").read_text(encoding="utf-8")
    for marker in ["Comparator Decision Margin From First Principles", "two physical nodes", "0.1567 mV", "0.1530 mV", "worst sampled differential kickback", "Sign preservation asks", "Passive Isolation Versus Active Gain", "does not create accepted post-layout converter evidence"]:
        if marker not in comparator_margin_page:
            return fail(f"site/research/comparator-decision-margin-from-first-principles.html missing marker {marker!r}")

    passive_vs_active_page = (ROOT / "site" / "research" / "passive-frontend-vs-active-preamp.html").read_text(encoding="utf-8")
    for marker in ["Passive Frontend Vs Active Preamp", "Should the circuit protect the tiny signal, or should it amplify the tiny signal?", "0.437908", "0.8 fF", "3.292970 fF", "Too much direct connection causes kickback", "Passive efficiency candidate", "Active preamp candidate", "does not create accepted post-layout converter evidence"]:
        if marker not in passive_vs_active_page:
            return fail(f"site/research/passive-frontend-vs-active-preamp.html missing marker {marker!r}")

    active_to_transistor_page = (ROOT / "site" / "research" / "from-active-macro-to-real-transistor-handoff.html").read_text(encoding="utf-8")
    for marker in ["From Active Macro To Real Transistor Handoff", "Can the tiny frontend voltage drive real transistor gates", "0.437908", "The active macro was not fake progress", "timed out run = failed handoff evidence", "passing extracted transistor handoff at schematic level", "accepted post-layout converter evidence"]:
        if marker not in active_to_transistor_page:
            return fail(f"site/research/from-active-macro-to-real-transistor-handoff.html missing marker {marker!r}")

    transistor_handoff_decomposition_page = (ROOT / "site" / "research" / "sky130-transistor-handoff-decomposition.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Transistor Handoff Decomposition", "combined_real_transistor_handoff_is_current_blocker", "extracted_frontend_sign_and_transfer_passes", "standalone_sky130_input_stage_polarity_passes", "combined_active_macro_handoff_passes", "preamp_known_good_reproduction_passes", "known_good_reproduction_op_measured_case_count", "combined_real_transistor_handoff_runs_to_completion", "does not prove transistor handoff"]:
        if marker not in transistor_handoff_decomposition_page:
            return fail(f"site/research/sky130-transistor-handoff-decomposition.html missing marker {marker!r}")

    transistor_handoff_probe_page = (ROOT / "site" / "research" / "sky130-transistor-handoff-probe-ladder.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Transistor Handoff Probe Ladder", "probe count", "measured probe count", "full handoff status", "The full handoff fails where too many things are joined at once", "does not create accepted post-layout converter evidence"]:
        if marker not in transistor_handoff_probe_page:
            return fail(f"site/research/sky130-transistor-handoff-probe-ladder.html missing marker {marker!r}")

    frontend_sense_to_transistor_op_page = (ROOT / "site" / "research" / "sky130-frontend-sense-to-transistor-op-handoff.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Frontend Sense To Transistor OP Handoff", "uses measured frontend sense voltage", "uses Sky130 transistor input stage", "minimum abs output diff V", "The full transient handoff joins two hard things", "does not prove the full extracted-frontend transient handoff"]:
        if marker not in frontend_sense_to_transistor_op_page:
            return fail(f"site/research/sky130-frontend-sense-to-transistor-op-handoff.html missing marker {marker!r}")

    frontend_sense_to_transistor_op = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-frontend-sense-to-transistor-op-handoff.json").read_text(encoding="utf-8"))
    if frontend_sense_to_transistor_op.get("result_type") != "sky130_frontend_sense_to_transistor_op_handoff":
        return fail("Sky130 frontend sense to transistor OP handoff has wrong result_type")
    if frontend_sense_to_transistor_op.get("uses_measured_frontend_sense_voltage") is not True:
        return fail("Sky130 frontend sense to transistor OP handoff should use measured frontend sense voltage")
    if frontend_sense_to_transistor_op.get("uses_sky130_transistor_input_stage") is not True:
        return fail("Sky130 frontend sense to transistor OP handoff should use Sky130 transistor input stage")
    if frontend_sense_to_transistor_op.get("uses_extracted_frontend_transient") is not False:
        return fail("Sky130 frontend sense to transistor OP handoff must not claim extracted frontend transient")
    if frontend_sense_to_transistor_op.get("case_count") != 4:
        return fail("Sky130 frontend sense to transistor OP handoff should inspect four frontend cases")
    if frontend_sense_to_transistor_op.get("measured_case_count", 0) < 1:
        return fail("Sky130 frontend sense to transistor OP handoff should measure at least one case")
    if frontend_sense_to_transistor_op.get("sign_pass_count") != frontend_sense_to_transistor_op.get("measured_case_count"):
        return fail("Sky130 frontend sense to transistor OP handoff measured cases should preserve sign")
    if frontend_sense_to_transistor_op.get("output_margin_pass_count") != frontend_sense_to_transistor_op.get("measured_case_count"):
        return fail("Sky130 frontend sense to transistor OP handoff measured cases should pass output margin")
    if frontend_sense_to_transistor_op.get("same_run_strict_payload_ready") is not False:
        return fail("Sky130 frontend sense to transistor OP handoff must not claim strict payload readiness")
    if frontend_sense_to_transistor_op.get("accepted_post_layout_written") is not False:
        return fail("Sky130 frontend sense to transistor OP handoff must not write accepted evidence")

    frontend_sense_to_transistor_short = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-frontend-sense-to-transistor-short-transient.json").read_text(encoding="utf-8"))
    if frontend_sense_to_transistor_short.get("result_type") != "sky130_frontend_sense_to_transistor_short_transient":
        return fail("Sky130 frontend sense to transistor short transient has wrong result_type")
    if frontend_sense_to_transistor_short.get("uses_measured_frontend_sense_voltage") is not True:
        return fail("Sky130 frontend sense to transistor short transient should use measured frontend sense voltage")
    if frontend_sense_to_transistor_short.get("uses_sky130_transistor_input_stage") is not True:
        return fail("Sky130 frontend sense to transistor short transient should use Sky130 transistor input stage")
    if frontend_sense_to_transistor_short.get("uses_op_initial_conditions") is not True:
        return fail("Sky130 frontend sense to transistor short transient should use OP initial conditions")
    if frontend_sense_to_transistor_short.get("uses_extracted_frontend_transient") is not False:
        return fail("Sky130 frontend sense to transistor short transient must not claim full frontend transient")
    if frontend_sense_to_transistor_short.get("case_count", 0) < 1:
        return fail("Sky130 frontend sense to transistor short transient should inspect at least one OP-measured case")
    if frontend_sense_to_transistor_short.get("measured_case_count") != frontend_sense_to_transistor_short.get("case_count"):
        return fail("Sky130 frontend sense to transistor short transient should measure every selected OP case")
    if frontend_sense_to_transistor_short.get("sign_pass_count") != frontend_sense_to_transistor_short.get("case_count"):
        return fail("Sky130 frontend sense to transistor short transient should preserve sign")
    if frontend_sense_to_transistor_short.get("output_margin_pass_count") != frontend_sense_to_transistor_short.get("case_count"):
        return fail("Sky130 frontend sense to transistor short transient should pass output margin")
    if frontend_sense_to_transistor_short.get("same_run_strict_payload_ready") is not False:
        return fail("Sky130 frontend sense to transistor short transient must not claim strict payload readiness")
    if frontend_sense_to_transistor_short.get("accepted_post_layout_written") is not False:
        return fail("Sky130 frontend sense to transistor short transient must not write accepted evidence")
    frontend_sense_to_transistor_short_page = (ROOT / "site" / "research" / "sky130-frontend-sense-to-transistor-short-transient.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Frontend Sense To Transistor Short Transient", "uses OP initial conditions", "minimum output retention ratio", "The OP handoff proves a static point", "does not prove the full extracted-frontend transient handoff"]:
        if marker not in frontend_sense_to_transistor_short_page:
            return fail(f"site/research/sky130-frontend-sense-to-transistor-short-transient.html missing marker {marker!r}")

    frontend_sense_to_transistor_ramp = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-frontend-sense-to-transistor-ramp-startup.json").read_text(encoding="utf-8"))
    if frontend_sense_to_transistor_ramp.get("result_type") != "sky130_frontend_sense_to_transistor_ramp_startup":
        return fail("Sky130 frontend sense to transistor ramp startup has wrong result_type")
    if frontend_sense_to_transistor_ramp.get("uses_measured_frontend_sense_voltage") is not True:
        return fail("Sky130 frontend sense to transistor ramp startup should use measured frontend sense voltage")
    if frontend_sense_to_transistor_ramp.get("uses_sky130_transistor_input_stage") is not True:
        return fail("Sky130 frontend sense to transistor ramp startup should use Sky130 transistor input stage")
    if frontend_sense_to_transistor_ramp.get("uses_input_ramp_from_common_mode") is not True:
        return fail("Sky130 frontend sense to transistor ramp startup should ramp from common mode")
    if frontend_sense_to_transistor_ramp.get("uses_extracted_frontend_transient") is not False:
        return fail("Sky130 frontend sense to transistor ramp startup must not claim full frontend transient")
    if frontend_sense_to_transistor_ramp.get("case_count", 0) < 1:
        return fail("Sky130 frontend sense to transistor ramp startup should inspect at least one OP-measured case")
    if frontend_sense_to_transistor_ramp.get("measured_case_count") != frontend_sense_to_transistor_ramp.get("case_count"):
        return fail("Sky130 frontend sense to transistor ramp startup should measure every selected OP case")
    if frontend_sense_to_transistor_ramp.get("sign_pass_count") != frontend_sense_to_transistor_ramp.get("case_count"):
        return fail("Sky130 frontend sense to transistor ramp startup should preserve sign")
    if frontend_sense_to_transistor_ramp.get("output_margin_pass_count") != frontend_sense_to_transistor_ramp.get("case_count"):
        return fail("Sky130 frontend sense to transistor ramp startup should pass output margin")
    if frontend_sense_to_transistor_ramp.get("same_run_strict_payload_ready") is not False:
        return fail("Sky130 frontend sense to transistor ramp startup must not claim strict payload readiness")
    if frontend_sense_to_transistor_ramp.get("accepted_post_layout_written") is not False:
        return fail("Sky130 frontend sense to transistor ramp startup must not write accepted evidence")
    frontend_sense_to_transistor_ramp_page = (ROOT / "site" / "research" / "sky130-frontend-sense-to-transistor-ramp-startup.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Frontend Sense To Transistor Ramp Startup", "uses input ramp from common mode", "minimum gain V/V", "A steady operating point can hide startup problems", "does not prove the extracted frontend transient handoff"]:
        if marker not in frontend_sense_to_transistor_ramp_page:
            return fail(f"site/research/sky130-frontend-sense-to-transistor-ramp-startup.html missing marker {marker!r}")

    assisted_gate = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-extracted-frontend-to-transistor-gate-startup.json").read_text(encoding="utf-8"))
    if assisted_gate.get("result_type") != "sky130_extracted_frontend_to_transistor_gate_startup":
        return fail("Sky130 extracted frontend to transistor gate startup has wrong result_type")
    if assisted_gate.get("status") != "extracted_frontend_to_transistor_assisted_gate_startup_failed":
        return fail("Sky130 extracted frontend to transistor gate startup should record the current assisted failure")
    if assisted_gate.get("uses_extracted_frontend_netlist") is not True:
        return fail("Sky130 extracted frontend to transistor gate startup should use extracted frontend netlist")
    if assisted_gate.get("uses_sky130_transistor_input_stage") is not True:
        return fail("Sky130 extracted frontend to transistor gate startup should use Sky130 transistor input stage")
    if assisted_gate.get("uses_assisted_gate_startup") is not True:
        return fail("Sky130 extracted frontend to transistor gate startup should declare assisted gate startup")
    if assisted_gate.get("uses_full_free_gate_handoff") is not False:
        return fail("Sky130 extracted frontend to transistor gate startup must not claim full free gate handoff")
    if assisted_gate.get("uses_clocked_latch") is not False or assisted_gate.get("uses_sar_loop") is not False:
        return fail("Sky130 extracted frontend to transistor gate startup must not claim latch or SAR proof")
    if assisted_gate.get("case_count") != 2 or assisted_gate.get("measured_case_count") != 2:
        return fail("Sky130 extracted frontend to transistor gate startup should measure two reset-pulse cases")
    if assisted_gate.get("timed_out_case_count") != 0:
        return fail("Sky130 extracted frontend to transistor gate startup should not time out in the current evidence")
    if assisted_gate.get("sign_pass_count") != 1 or assisted_gate.get("output_margin_pass_count") != 1:
        return fail("Sky130 extracted frontend to transistor gate startup should record one passing polarity and one failing polarity")
    if assisted_gate.get("minimum_abs_output_diff_v", 1.0) >= 0.0005:
        return fail("Sky130 extracted frontend to transistor gate startup should expose the current failed output-margin floor")
    if assisted_gate.get("same_run_strict_payload_ready") is not False:
        return fail("Sky130 extracted frontend to transistor gate startup must not claim strict payload readiness")
    if assisted_gate.get("accepted_post_layout_written") is not False:
        return fail("Sky130 extracted frontend to transistor gate startup must not write accepted evidence")
    for path_field in ["source_frontend_netlist", "generated_deck", "csv"]:
        path_value = assisted_gate.get(path_field)
        if not path_value or not (ROOT / str(path_value)).exists():
            return fail(f"Sky130 extracted frontend to transistor gate startup missing {path_field}")
    assisted_gate_page = (ROOT / "site" / "research" / "sky130-extracted-frontend-to-transistor-gate-startup.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Extracted Frontend To Transistor Gate Startup", "uses assisted gate startup", "uses full free gate handoff: <code>False</code>", "sign pass count: <code>1</code>", "output margin pass count: <code>1</code>", "The open problem is no longer whether a small voltage can be amplified", "does not prove the full free extracted-frontend-to-transistor handoff"]:
        if marker not in assisted_gate_page:
            return fail(f"site/research/sky130-extracted-frontend-to-transistor-gate-startup.html missing marker {marker!r}")

    gate_sweep = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-extracted-frontend-gate-coupling-sweep.json").read_text(encoding="utf-8"))
    if gate_sweep.get("result_type") != "sky130_extracted_frontend_gate_coupling_sweep":
        return fail("Sky130 extracted frontend gate coupling sweep has wrong result_type")
    if gate_sweep.get("status") != "gate_coupling_sweep_found_no_passing_assisted_setting":
        return fail("Sky130 extracted frontend gate coupling sweep should record no passing assisted setting")
    if gate_sweep.get("uses_extracted_frontend_netlist") is not True:
        return fail("Sky130 extracted frontend gate coupling sweep should use extracted frontend netlist")
    if gate_sweep.get("uses_sky130_transistor_input_stage") is not True:
        return fail("Sky130 extracted frontend gate coupling sweep should use Sky130 transistor input stage")
    if gate_sweep.get("uses_assisted_gate_startup") is not True:
        return fail("Sky130 extracted frontend gate coupling sweep should declare assisted gate startup")
    if gate_sweep.get("uses_full_free_gate_handoff") is not False:
        return fail("Sky130 extracted frontend gate coupling sweep must not claim full free gate handoff")
    if gate_sweep.get("setting_count") != 4 or gate_sweep.get("case_count") != 8:
        return fail("Sky130 extracted frontend gate coupling sweep should run four settings and eight cases")
    if gate_sweep.get("measured_case_count") != 0 or gate_sweep.get("timed_out_case_count") != 8:
        return fail("Sky130 extracted frontend gate coupling sweep should currently record eight timeouts")
    if gate_sweep.get("passing_setting_count") != 0:
        return fail("Sky130 extracted frontend gate coupling sweep should not claim a passing setting")
    if gate_sweep.get("same_run_strict_payload_ready") is not False:
        return fail("Sky130 extracted frontend gate coupling sweep must not claim strict payload readiness")
    if gate_sweep.get("accepted_post_layout_written") is not False:
        return fail("Sky130 extracted frontend gate coupling sweep must not write accepted evidence")
    for path_field in ["source_frontend_netlist", "generated_deck", "csv"]:
        path_value = gate_sweep.get(path_field)
        if not path_value or not (ROOT / str(path_value)).exists():
            return fail(f"Sky130 extracted frontend gate coupling sweep missing {path_field}")
    gate_sweep_page = (ROOT / "site" / "research" / "sky130-extracted-frontend-gate-coupling-sweep.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Extracted Frontend Gate Coupling Sweep", "gate_coupling_sweep_found_no_passing_assisted_setting", "setting count: <code>4</code>", "timed-out case count: <code>8</code>", "passing setting count: <code>0</code>", "frontend needs a buffer", "does not prove full free gate handoff"]:
        if marker not in gate_sweep_page:
            return fail(f"site/research/sky130-extracted-frontend-gate-coupling-sweep.html missing marker {marker!r}")

    source_follower = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-extracted-frontend-source-follower-handoff.json").read_text(encoding="utf-8"))
    if source_follower.get("result_type") != "sky130_extracted_frontend_source_follower_handoff":
        return fail("Sky130 extracted frontend source-follower handoff has wrong result_type")
    if source_follower.get("status") != "source_follower_handoff_failed":
        return fail("Sky130 extracted frontend source-follower handoff should record current failure")
    if source_follower.get("uses_extracted_frontend_netlist") is not True:
        return fail("Sky130 extracted frontend source-follower handoff should use extracted frontend netlist")
    if source_follower.get("uses_sky130_source_follower_buffer") is not True:
        return fail("Sky130 extracted frontend source-follower handoff should use source-follower buffer")
    if source_follower.get("uses_sky130_transistor_input_stage") is not True:
        return fail("Sky130 extracted frontend source-follower handoff should use Sky130 transistor input stage")
    if source_follower.get("uses_clocked_latch") is not False or source_follower.get("uses_sar_loop") is not False:
        return fail("Sky130 extracted frontend source-follower handoff must not claim latch or SAR proof")
    if source_follower.get("case_count") != 2 or source_follower.get("measured_case_count") != 2:
        return fail("Sky130 extracted frontend source-follower handoff should measure two cases")
    if source_follower.get("timed_out_case_count") != 0:
        return fail("Sky130 extracted frontend source-follower handoff should not time out in current evidence")
    if source_follower.get("sign_pass_count") != 0 or source_follower.get("output_margin_pass_count") != 0:
        return fail("Sky130 extracted frontend source-follower handoff should fail sign and margin in current evidence")
    if source_follower.get("minimum_sample_to_sense_transfer_ratio", 1.0) >= 0.1:
        return fail("Sky130 extracted frontend source-follower handoff should expose frontend transfer collapse")
    if source_follower.get("minimum_sense_to_buffer_transfer_ratio", 1.0) >= 0.001:
        return fail("Sky130 extracted frontend source-follower handoff should expose buffer transfer collapse")
    if source_follower.get("same_run_strict_payload_ready") is not False:
        return fail("Sky130 extracted frontend source-follower handoff must not claim strict payload readiness")
    if source_follower.get("accepted_post_layout_written") is not False:
        return fail("Sky130 extracted frontend source-follower handoff must not write accepted evidence")
    for path_field in ["source_frontend_netlist", "generated_deck", "csv"]:
        path_value = source_follower.get(path_field)
        if not path_value or not (ROOT / str(path_value)).exists():
            return fail(f"Sky130 extracted frontend source-follower handoff missing {path_field}")
    source_follower_page = (ROOT / "site" / "research" / "sky130-extracted-frontend-source-follower-handoff.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Extracted Frontend Source-Follower Handoff", "source_follower_handoff_failed", "uses Sky130 source-follower buffer", "sign pass count: <code>0</code>", "output margin pass count: <code>0</code>", "A buffer is a promise to separate two jobs", "does not prove latch behavior"]:
        if marker not in source_follower_page:
            return fail(f"site/research/sky130-extracted-frontend-source-follower-handoff.html missing marker {marker!r}")

    differential_preamp = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-extracted-frontend-differential-preamp.json").read_text(encoding="utf-8"))
    if differential_preamp.get("result_type") != "sky130_extracted_frontend_differential_preamp":
        return fail("Sky130 extracted frontend differential preamp has wrong result_type")
    if differential_preamp.get("status") != "differential_preamp_handoff_failed":
        return fail("Sky130 extracted frontend differential preamp should record current failure")
    if differential_preamp.get("uses_extracted_frontend_netlist") is not True:
        return fail("Sky130 extracted frontend differential preamp should use extracted frontend netlist")
    if differential_preamp.get("uses_sky130_differential_preamp") is not True:
        return fail("Sky130 extracted frontend differential preamp should use Sky130 differential preamp")
    if differential_preamp.get("uses_clocked_latch") is not False or differential_preamp.get("uses_sar_loop") is not False:
        return fail("Sky130 extracted frontend differential preamp must not claim latch or SAR proof")
    if differential_preamp.get("case_count") != 2:
        return fail("Sky130 extracted frontend differential preamp should test two reset-pulse cases")
    if differential_preamp.get("measured_case_count") != 2 or differential_preamp.get("timed_out_case_count") != 0:
        return fail("Sky130 extracted frontend differential preamp should measure both cases without timeout")
    if differential_preamp.get("sign_pass_count") != 2 or differential_preamp.get("output_margin_pass_count") != 0:
        return fail("Sky130 extracted frontend differential preamp should preserve sign but fail output margin")
    if differential_preamp.get("same_run_strict_payload_ready") is not False:
        return fail("Sky130 extracted frontend differential preamp must not claim strict payload readiness")
    if differential_preamp.get("accepted_post_layout_written") is not False:
        return fail("Sky130 extracted frontend differential preamp must not write accepted evidence")
    for path_field in ["source_frontend_netlist", "generated_deck", "csv"]:
        path_value = differential_preamp.get(path_field)
        if not path_value or not (ROOT / str(path_value)).exists():
            return fail(f"Sky130 extracted frontend differential preamp missing {path_field}")
    differential_preamp_page = (ROOT / "site" / "research" / "sky130-extracted-frontend-differential-preamp.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Extracted Frontend Differential Preamp", "differential_preamp_handoff_failed", "uses Sky130 differential preamp", "measured case count: <code>2</code>", "timed-out case count: <code>0</code>", "sign pass count: <code>2</code>", "output margin pass count: <code>0</code>", "A differential preamp spends current", "does not prove latch behavior"]:
        if marker not in differential_preamp_page:
            return fail(f"site/research/sky130-extracted-frontend-differential-preamp.html missing marker {marker!r}")

    measured_preamp = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-measured-sense-differential-preamp.json").read_text(encoding="utf-8"))
    if measured_preamp.get("result_type") != "sky130_measured_sense_differential_preamp":
        return fail("Sky130 measured sense differential preamp has wrong result_type")
    if measured_preamp.get("status") != "measured_sense_differential_preamp_passed_not_extracted_frontend_or_strict_evidence":
        return fail("Sky130 measured sense differential preamp should pass without extracted frontend loading")
    if measured_preamp.get("uses_measured_frontend_sense_voltage") is not True:
        return fail("Sky130 measured sense differential preamp should use measured sense voltage")
    if measured_preamp.get("uses_extracted_frontend_transient") is not False:
        return fail("Sky130 measured sense differential preamp must not claim extracted frontend transient")
    if measured_preamp.get("uses_sky130_differential_preamp") is not True:
        return fail("Sky130 measured sense differential preamp should use Sky130 differential preamp")
    if measured_preamp.get("uses_clocked_latch") is not False or measured_preamp.get("uses_sar_loop") is not False:
        return fail("Sky130 measured sense differential preamp must not claim latch or SAR proof")
    if measured_preamp.get("case_count") != 2:
        return fail("Sky130 measured sense differential preamp should test two reset-pulse cases")
    if measured_preamp.get("measured_case_count") != 2 or measured_preamp.get("timed_out_case_count") != 0:
        return fail("Sky130 measured sense differential preamp should measure both cases without timeout")
    if measured_preamp.get("sign_pass_count") != 2 or measured_preamp.get("output_margin_pass_count") != 2:
        return fail("Sky130 measured sense differential preamp should pass sign and margin")
    if measured_preamp.get("same_run_strict_payload_ready") is not False:
        return fail("Sky130 measured sense differential preamp must not claim strict payload readiness")
    if measured_preamp.get("accepted_post_layout_written") is not False:
        return fail("Sky130 measured sense differential preamp must not write accepted evidence")
    for path_field in ["generated_deck", "csv"]:
        path_value = measured_preamp.get(path_field)
        if not path_value or not (ROOT / str(path_value)).exists():
            return fail(f"Sky130 measured sense differential preamp missing {path_field}")
    measured_preamp_page = (ROOT / "site" / "research" / "sky130-measured-sense-differential-preamp.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Measured Sense Differential Preamp", "measured_sense_differential_preamp_passed_not_extracted_frontend_or_strict_evidence", "uses measured frontend sense voltage", "uses extracted frontend transient: <code>False</code>", "measured case count: <code>2</code>", "timed-out case count: <code>0</code>", "sign pass count: <code>2</code>", "The failed extracted-frontend preamp run mixed two possible causes", "does not prove extracted frontend loading"]:
        if marker not in measured_preamp_page:
            return fail(f"site/research/sky130-measured-sense-differential-preamp.html missing marker {marker!r}")

    preamp_bias_sweep = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-measured-sense-preamp-bias-sweep.json").read_text(encoding="utf-8"))
    if preamp_bias_sweep.get("result_type") != "sky130_measured_sense_preamp_bias_sweep":
        return fail("Sky130 measured sense preamp bias sweep has wrong result_type")
    if preamp_bias_sweep.get("status") != "measured_sense_preamp_bias_sweep_found_passing_setting_not_extracted_frontend":
        return fail("Sky130 measured sense preamp bias sweep should record one passing setting")
    if preamp_bias_sweep.get("uses_measured_frontend_sense_voltage") is not True:
        return fail("Sky130 measured sense preamp bias sweep should use measured sense voltage")
    if preamp_bias_sweep.get("uses_extracted_frontend_transient") is not False:
        return fail("Sky130 measured sense preamp bias sweep must not claim extracted frontend transient")
    if preamp_bias_sweep.get("uses_sky130_differential_preamp") is not True:
        return fail("Sky130 measured sense preamp bias sweep should use Sky130 differential preamp")
    if preamp_bias_sweep.get("setting_count") != 4 or preamp_bias_sweep.get("case_count") != 8:
        return fail("Sky130 measured sense preamp bias sweep should run four settings and eight cases")
    if preamp_bias_sweep.get("measured_case_count") != 8 or preamp_bias_sweep.get("timed_out_case_count") != 0:
        return fail("Sky130 measured sense preamp bias sweep should measure all cases without timeout")
    if preamp_bias_sweep.get("passing_setting_count") != 1:
        return fail("Sky130 measured sense preamp bias sweep should claim one passing setting")
    if preamp_bias_sweep.get("same_run_strict_payload_ready") is not False:
        return fail("Sky130 measured sense preamp bias sweep must not claim strict payload readiness")
    if preamp_bias_sweep.get("accepted_post_layout_written") is not False:
        return fail("Sky130 measured sense preamp bias sweep must not write accepted evidence")
    for path_field in ["generated_deck", "csv"]:
        path_value = preamp_bias_sweep.get(path_field)
        if not path_value or not (ROOT / str(path_value)).exists():
            return fail(f"Sky130 measured sense preamp bias sweep missing {path_field}")
    preamp_bias_sweep_page = (ROOT / "site" / "research" / "sky130-measured-sense-preamp-bias-sweep.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Measured Sense Preamp Bias Sweep", "measured_sense_preamp_bias_sweep_found_passing_setting_not_extracted_frontend", "setting count: <code>4</code>", "measured case count: <code>8</code>", "timed-out case count: <code>0</code>", "passing setting count: <code>1</code>", "Before a preamp can be blamed for loading the extracted frontend", "does not prove extracted frontend loading"]:
        if marker not in preamp_bias_sweep_page:
            return fail(f"site/research/sky130-measured-sense-preamp-bias-sweep.html missing marker {marker!r}")

    preamp_op_map = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-measured-sense-preamp-op-map.json").read_text(encoding="utf-8"))
    if preamp_op_map.get("result_type") != "sky130_measured_sense_preamp_op_map":
        return fail("Sky130 measured sense preamp OP map has wrong result_type")
    if preamp_op_map.get("status") != "measured_sense_preamp_op_map_found_valid_bias_point_not_transient_or_extracted_frontend":
        return fail("Sky130 measured sense preamp OP map should record a valid DC bias point")
    if preamp_op_map.get("uses_dc_operating_point") is not True:
        return fail("Sky130 measured sense preamp OP map should use DC operating point")
    if preamp_op_map.get("uses_measured_frontend_sense_voltage") is not True:
        return fail("Sky130 measured sense preamp OP map should use measured sense voltage")
    if preamp_op_map.get("uses_extracted_frontend_transient") is not False:
        return fail("Sky130 measured sense preamp OP map must not claim extracted frontend transient")
    if preamp_op_map.get("setting_count") != 1 or preamp_op_map.get("case_count") != 2:
        return fail("Sky130 measured sense preamp OP map should run one setting and two cases")
    if preamp_op_map.get("op_measured_case_count") != 2 or preamp_op_map.get("timed_out_case_count") != 0:
        return fail("Sky130 measured sense preamp OP map should measure both OP cases with no timeout")
    if preamp_op_map.get("passing_setting_count") != 1:
        return fail("Sky130 measured sense preamp OP map should claim one valid DC bias point")
    if preamp_op_map.get("same_run_strict_payload_ready") is not False:
        return fail("Sky130 measured sense preamp OP map must not claim strict payload readiness")
    if preamp_op_map.get("accepted_post_layout_written") is not False:
        return fail("Sky130 measured sense preamp OP map must not write accepted evidence")
    for path_field in ["generated_deck", "csv"]:
        path_value = preamp_op_map.get(path_field)
        if not path_value or not (ROOT / str(path_value)).exists():
            return fail(f"Sky130 measured sense preamp OP map missing {path_field}")
    preamp_op_map_page = (ROOT / "site" / "research" / "sky130-measured-sense-preamp-op-map.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Measured Sense Preamp OP Map", "measured_sense_preamp_op_map_found_valid_bias_point_not_transient_or_extracted_frontend", "setting count: <code>1</code>", "OP measured case count: <code>2</code>", "timed-out case count: <code>0</code>", "passing setting count: <code>1</code>", "A transient run asks two questions at once", "does not prove transient startup"]:
        if marker not in preamp_op_map_page:
            return fail(f"site/research/sky130-measured-sense-preamp-op-map.html missing marker {marker!r}")

    preamp_reproduction = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-preamp-known-good-reproduction.json").read_text(encoding="utf-8"))
    if preamp_reproduction.get("result_type") != "sky130_preamp_known_good_reproduction":
        return fail("Sky130 preamp known-good reproduction has wrong result_type")
    if preamp_reproduction.get("status") != "known_good_reproduction_passed_for_known_and_measured_sense_inputs":
        return fail("Sky130 preamp known-good reproduction should pass known and measured sense inputs")
    if preamp_reproduction.get("case_count") != 2:
        return fail("Sky130 preamp known-good reproduction should run two cases")
    if preamp_reproduction.get("op_measured_case_count") != 2 or preamp_reproduction.get("timed_out_case_count") != 0:
        return fail("Sky130 preamp known-good reproduction should measure both OP cases with no timeout")
    if preamp_reproduction.get("polarity_pass_count") != 2:
        return fail("Sky130 preamp known-good reproduction should preserve polarity for both cases")
    if preamp_reproduction.get("strict_payload_ready") is not False:
        return fail("Sky130 preamp known-good reproduction must not claim strict payload readiness")
    if preamp_reproduction.get("accepted_post_layout_written") is not False:
        return fail("Sky130 preamp known-good reproduction must not write accepted evidence")
    for path_field in ["generated_deck", "csv"]:
        path_value = preamp_reproduction.get(path_field)
        if not path_value or not (ROOT / str(path_value)).exists():
            return fail(f"Sky130 preamp known-good reproduction missing {path_field}")
    reproduction_cases = {row.get("case") for row in preamp_reproduction.get("rows", [])}
    if reproduction_cases != {"known_good_positive_target_edge", "measured_frontend_positive_sense_edge"}:
        return fail("Sky130 preamp known-good reproduction should include known-good and measured-sense cases")
    preamp_reproduction_page = (ROOT / "site" / "research" / "sky130-preamp-known-good-reproduction.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Preamp Known-Good Reproduction", "known_good_reproduction_passed_for_known_and_measured_sense_inputs", "OP measured case count: <code>2</code>", "timed-out case count: <code>0</code>", "polarity pass count: <code>2</code>", "same node names, ideal tail, resistive loads", "does not prove extracted frontend loading"]:
        if marker not in preamp_reproduction_page:
            return fail(f"site/research/sky130-preamp-known-good-reproduction.html missing marker {marker!r}")

    preamp_gain_sweep = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-extracted-frontend-preamp-gain-sweep.json").read_text(encoding="utf-8"))
    if preamp_gain_sweep.get("result_type") != "sky130_extracted_frontend_preamp_gain_sweep":
        return fail("Sky130 extracted frontend preamp gain sweep has wrong result_type")
    if preamp_gain_sweep.get("status") != "extracted_frontend_preamp_gain_sweep_found_no_margin_passing_setting":
        return fail("Sky130 extracted frontend preamp gain sweep should record no margin-passing setting")
    if preamp_gain_sweep.get("setting_count") != 4 or preamp_gain_sweep.get("case_count") != 8:
        return fail("Sky130 extracted frontend preamp gain sweep should run four settings and eight cases")
    if preamp_gain_sweep.get("measured_case_count") != 8 or preamp_gain_sweep.get("timed_out_case_count") != 0:
        return fail("Sky130 extracted frontend preamp gain sweep should measure all cases without timeout")
    if preamp_gain_sweep.get("passing_setting_count") != 0:
        return fail("Sky130 extracted frontend preamp gain sweep must not claim a passing setting")
    if preamp_gain_sweep.get("accepted_post_layout_written") is not False:
        return fail("Sky130 extracted frontend preamp gain sweep must not write accepted evidence")
    if float(preamp_gain_sweep.get("best_setting", {}).get("minimum_abs_preamp_output_diff_v", 0.0)) >= float(preamp_gain_sweep.get("output_margin_target_v", 0.0)):
        return fail("Sky130 extracted frontend preamp gain sweep best setting should remain below margin target")
    for path_field in ["generated_deck", "csv"]:
        path_value = preamp_gain_sweep.get(path_field)
        if not path_value or not (ROOT / str(path_value)).exists():
            return fail(f"Sky130 extracted frontend preamp gain sweep missing {path_field}")
    preamp_gain_sweep_page = (ROOT / "site" / "research" / "sky130-extracted-frontend-preamp-gain-sweep.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Extracted Frontend Preamp Gain Sweep", "extracted_frontend_preamp_gain_sweep_found_no_margin_passing_setting", "setting count: <code>4</code>", "measured case count: <code>8</code>", "passing setting count: <code>0</code>", "best setting: <code>known_input_stage_bias</code>", "simple gain change", "does not prove latch behavior"]:
        if marker not in preamp_gain_sweep_page:
            return fail(f"site/research/sky130-extracted-frontend-preamp-gain-sweep.html missing marker {marker!r}")

    interface_target = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-frontend-preamp-interface-redesign-target.json").read_text(encoding="utf-8"))
    if interface_target.get("result_type") != "sky130_frontend_preamp_interface_redesign_target":
        return fail("Sky130 frontend preamp interface target has wrong result_type")
    if interface_target.get("status") != "frontend_to_preamp_interface_needs_more_voltage_before_latch_work":
        return fail("Sky130 frontend preamp interface target should require more voltage before latch work")
    if float(interface_target.get("required_transfer_improvement_x", 0.0)) <= 9.0:
        return fail("Sky130 frontend preamp interface target should require about 10x transfer improvement")
    if float(interface_target.get("standalone_to_attached_sense_loss_x", 0.0)) <= 10.0:
        return fail("Sky130 frontend preamp interface target should record about 10x attached sense loss")
    if interface_target.get("accepted_post_layout_written") is not False:
        return fail("Sky130 frontend preamp interface target must not write accepted evidence")
    interface_target_page = (ROOT / "site" / "research" / "sky130-frontend-preamp-interface-redesign-target.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Frontend Preamp Interface Redesign Target", "frontend_to_preamp_interface_needs_more_voltage_before_latch_work", "required transfer improvement x", "standalone-to-attached sense loss x", "A preamp cannot amplify voltage that never reaches its input", "does not prove a redesigned frontend"]:
        if marker not in interface_target_page:
            return fail(f"site/research/sky130-frontend-preamp-interface-redesign-target.html missing marker {marker!r}")

    cap_budget = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-frontend-preamp-capacitance-budget.json").read_text(encoding="utf-8"))
    if cap_budget.get("result_type") != "sky130_frontend_preamp_capacitance_budget":
        return fail("Sky130 frontend preamp capacitance budget has wrong result_type")
    if cap_budget.get("status") != "frontend_preamp_interface_capacitance_budget_requires_less_waste_or_more_useful_coupling":
        return fail("Sky130 frontend preamp capacitance budget should require less waste or more useful coupling")
    if float(cap_budget.get("average_useful_sample_to_sense_cap_ff", 0.0)) < 0.7:
        return fail("Sky130 frontend preamp capacitance budget should measure useful sample coupling")
    if float(cap_budget.get("average_sense_total_cap_ff", 0.0)) < 2.0:
        return fail("Sky130 frontend preamp capacitance budget should measure total sense capacitance")
    if float(cap_budget.get("total_cap_reduction_needed_x_if_useful_fixed", 0.0)) <= 1.5:
        return fail("Sky130 frontend preamp capacitance budget should require material capacitance reduction")
    if float(cap_budget.get("useful_coupling_increase_needed_x_if_total_fixed", 0.0)) <= 1.5:
        return fail("Sky130 frontend preamp capacitance budget should require material useful coupling increase")
    if cap_budget.get("accepted_post_layout_written") is not False:
        return fail("Sky130 frontend preamp capacitance budget must not write accepted evidence")
    cap_budget_page = (ROOT / "site" / "research" / "sky130-frontend-preamp-capacitance-budget.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Frontend Preamp Capacitance Budget", "average useful sample-to-sense capacitance fF", "average sense total capacitance fF", "current useful-over-total capacitance ratio", "The frontend stores a small voltage as charge", "does not edit layout"]:
        if marker not in cap_budget_page:
            return fail(f"site/research/sky130-frontend-preamp-capacitance-budget.html missing marker {marker!r}")

    interface_work_order = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-frontend-preamp-interface-work-order.json").read_text(encoding="utf-8"))
    if interface_work_order.get("result_type") != "sky130_frontend_preamp_interface_work_order":
        return fail("Sky130 frontend preamp interface work order has wrong result_type")
    if interface_work_order.get("status") != "frontend_preamp_interface_work_order_ready_not_design_proof":
        return fail("Sky130 frontend preamp interface work order should be ready but not a design proof")
    if interface_work_order.get("candidate_count") != 3:
        return fail("Sky130 frontend preamp interface work order should name three candidates")
    candidate_names = {item.get("name") for item in interface_work_order.get("candidates", [])}
    if candidate_names != {"lower_waste_sense_node", "stronger_useful_coupling", "low_input_capacitance_isolation"}:
        return fail("Sky130 frontend preamp interface work order has wrong candidate names")
    if float(interface_work_order.get("required_transfer_improvement_x", 0.0)) <= 9.0:
        return fail("Sky130 frontend preamp interface work order should carry the transfer target")
    if interface_work_order.get("accepted_post_layout_written") is not False:
        return fail("Sky130 frontend preamp interface work order must not write accepted evidence")
    work_order_page = (ROOT / "site" / "research" / "sky130-frontend-preamp-interface-work-order.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Frontend Preamp Interface Work Order", "frontend_preamp_interface_work_order_ready_not_design_proof", "candidate count: <code>3</code>", "lower_waste_sense_node", "stronger_useful_coupling", "low_input_capacitance_isolation", "The preamp cannot repair a voltage that was lost before the gate", "does not edit layout"]:
        if marker not in work_order_page:
            return fail(f"site/research/sky130-frontend-preamp-interface-work-order.html missing marker {marker!r}")

    interface_candidate = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-frontend-preamp-interface-candidate.json").read_text(encoding="utf-8"))
    if interface_candidate.get("result_type") != "sky130_frontend_preamp_interface_candidate":
        return fail("Sky130 frontend preamp interface candidate has wrong result_type")
    if interface_candidate.get("status") != "frontend_preamp_interface_candidate_ranked_not_yet_layout_proven":
        return fail("Sky130 frontend preamp interface candidate should be ranked but not layout-proven")
    if interface_candidate.get("candidate_count") != 3:
        return fail("Sky130 frontend preamp interface candidate should rank three candidates")
    if interface_candidate.get("recommended_first_candidate") not in {"lower_waste_sense_node", "stronger_useful_coupling"}:
        return fail("Sky130 frontend preamp interface candidate should recommend a capacitance move first")
    if float(interface_candidate.get("required_transfer_improvement_x", 0.0)) <= 9.0:
        return fail("Sky130 frontend preamp interface candidate should carry the transfer target")
    if float(interface_candidate.get("current_best_output_margin_v", 0.0)) >= float(interface_candidate.get("output_margin_target_v", 0.0)):
        return fail("Sky130 frontend preamp interface candidate should remain below output margin")
    if interface_candidate.get("accepted_post_layout_written") is not False:
        return fail("Sky130 frontend preamp interface candidate must not write accepted evidence")
    candidate_names = {item.get("name") for item in interface_candidate.get("candidate_results", [])}
    if candidate_names != {"lower_waste_sense_node", "stronger_useful_coupling", "low_input_capacitance_isolation"}:
        return fail("Sky130 frontend preamp interface candidate has wrong candidate names")
    candidate_page = (ROOT / "site" / "research" / "sky130-frontend-preamp-interface-candidate.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Frontend Preamp Interface Candidate", "frontend_preamp_interface_candidate_ranked_not_yet_layout_proven", "recommended first candidate", "current best output margin V", "change needed x", "The interface has one job", "does not edit layout"]:
        if marker not in candidate_page:
            return fail(f"site/research/sky130-frontend-preamp-interface-candidate.html missing marker {marker!r}")

    lower_waste = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-lower-waste-frontend-preamp-candidate.json").read_text(encoding="utf-8"))
    if lower_waste.get("result_type") != "sky130_lower_waste_frontend_preamp_candidate":
        return fail("Sky130 lower-waste frontend preamp candidate has wrong result_type")
    if lower_waste.get("status") != "lower_waste_frontend_preamp_candidate_failed_scaled_rc_margin":
        return fail("Sky130 lower-waste frontend preamp candidate should record the scaled-RC margin failure")
    if lower_waste.get("case_count") != 2 or lower_waste.get("measured_case_count") != 2:
        return fail("Sky130 lower-waste frontend preamp candidate should measure both reset-pulse cases")
    if lower_waste.get("sign_pass_count") != 2:
        return fail("Sky130 lower-waste frontend preamp candidate should preserve both signs")
    if lower_waste.get("output_margin_pass_count") != 0:
        return fail("Sky130 lower-waste frontend preamp candidate must not claim output margin")
    if float(lower_waste.get("candidate_average_sense_cap_ff", 0.0)) > float(lower_waste.get("target_average_sense_cap_ff", 0.0)) * 1.001:
        return fail("Sky130 lower-waste frontend preamp candidate should scale sense capacitance to target")
    if float(lower_waste.get("minimum_abs_preamp_output_diff_v", 0.0)) >= float(lower_waste.get("output_margin_target_v", 0.0)):
        return fail("Sky130 lower-waste frontend preamp candidate output should remain below margin target")
    if lower_waste.get("accepted_post_layout_written") is not False:
        return fail("Sky130 lower-waste frontend preamp candidate must not write accepted evidence")
    for path_field in ["candidate_netlist", "generated_deck", "csv"]:
        path_value = lower_waste.get(path_field)
        if not path_value or not (ROOT / str(path_value)).exists():
            return fail(f"Sky130 lower-waste frontend preamp candidate missing {path_field}")
    lower_waste_page = (ROOT / "site" / "research" / "sky130-lower-waste-frontend-preamp-candidate.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Lower-Waste Frontend Preamp Candidate", "lower_waste_frontend_preamp_candidate_failed_scaled_rc_margin", "scaled nonuseful sense cap count", "output margin pass count: <code>0</code>", "This experiment asks one narrow question", "does not prove a drawn layout"]:
        if marker not in lower_waste_page:
            return fail(f"site/research/sky130-lower-waste-frontend-preamp-candidate.html missing marker {marker!r}")

    combined_candidate = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-combined-coupling-waste-frontend-preamp-candidate.json").read_text(encoding="utf-8"))
    if combined_candidate.get("result_type") != "sky130_combined_coupling_waste_frontend_preamp_candidate":
        return fail("Sky130 combined coupling/waste frontend preamp candidate has wrong result_type")
    if combined_candidate.get("status") != "combined_coupling_waste_frontend_preamp_candidate_failed_scaled_rc_margin":
        return fail("Sky130 combined coupling/waste frontend preamp candidate should record the scaled-RC margin failure")
    if combined_candidate.get("case_count") != 2 or combined_candidate.get("measured_case_count") != 2:
        return fail("Sky130 combined coupling/waste frontend preamp candidate should measure both reset-pulse cases")
    if combined_candidate.get("sign_pass_count") != 2:
        return fail("Sky130 combined coupling/waste frontend preamp candidate should preserve both signs")
    if combined_candidate.get("output_margin_pass_count") != 0:
        return fail("Sky130 combined coupling/waste frontend preamp candidate must not claim output margin")
    if float(combined_candidate.get("minimum_abs_preamp_output_diff_v", 0.0)) >= float(combined_candidate.get("output_margin_target_v", 0.0)):
        return fail("Sky130 combined coupling/waste frontend preamp candidate output should remain below margin target")
    if combined_candidate.get("accepted_post_layout_written") is not False:
        return fail("Sky130 combined coupling/waste frontend preamp candidate must not write accepted evidence")
    for path_field in ["candidate_netlist", "generated_deck", "csv"]:
        path_value = combined_candidate.get(path_field)
        if not path_value or not (ROOT / str(path_value)).exists():
            return fail(f"Sky130 combined coupling/waste frontend preamp candidate missing {path_field}")
    combined_page = (ROOT / "site" / "research" / "sky130-combined-coupling-waste-frontend-preamp-candidate.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Combined Coupling/Waste Frontend Preamp Candidate", "combined_coupling_waste_frontend_preamp_candidate_failed_scaled_rc_margin", "output margin pass count: <code>0</code>", "useful sample-to-sense coupling rises", "does not prove a drawn layout"]:
        if marker not in combined_page:
            return fail(f"site/research/sky130-combined-coupling-waste-frontend-preamp-candidate.html missing marker {marker!r}")

    active_target = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-active-isolation-preamp-target.json").read_text(encoding="utf-8"))
    if active_target.get("result_type") != "sky130_active_isolation_preamp_target":
        return fail("Sky130 active isolation preamp target has wrong result_type")
    if active_target.get("status") != "active_isolation_preamp_target_ready_after_passive_and_source_follower_failures":
        return fail("Sky130 active isolation preamp target should be ready after passive and source-follower failures")
    if active_target.get("passive_combined_margin_pass_count") != 0:
        return fail("Sky130 active isolation preamp target should record combined passive margin failure")
    if active_target.get("source_follower_sign_pass_count") != 0:
        return fail("Sky130 active isolation preamp target should record source-follower sign failure")
    if float(active_target.get("best_passive_output_to_target_ratio", 1.0)) >= 0.2:
        return fail("Sky130 active isolation preamp target should record a large passive margin gap")
    if float(active_target.get("attached_sense_loss_target_x", 0.0)) != 2.0:
        return fail("Sky130 active isolation preamp target should require 2x or better attached sense loss")
    if active_target.get("accepted_post_layout_written") is not False:
        return fail("Sky130 active isolation preamp target must not write accepted evidence")
    requirement_names = {item.get("name") for item in active_target.get("active_isolation_requirements", [])}
    if requirement_names != {"low_input_capacitance", "differential_preservation", "usable_output_margin", "bounded_power_cost"}:
        return fail("Sky130 active isolation preamp target has wrong requirement names")
    active_target_page = (ROOT / "site" / "research" / "sky130-active-isolation-preamp-target.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Active Isolation Preamp Target", "active_isolation_preamp_target_ready_after_passive_and_source_follower_failures", "best passive output to target ratio", "low_input_capacitance", "bounded_power_cost", "touch the frontend lightly", "does not prove an active isolation circuit"]:
        if marker not in active_target_page:
            return fail(f"site/research/sky130-active-isolation-preamp-target.html missing marker {marker!r}")

    active_candidate = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-active-isolation-preamp-candidate.json").read_text(encoding="utf-8"))
    if active_candidate.get("result_type") != "sky130_active_isolation_preamp_candidate":
        return fail("Sky130 active isolation preamp candidate has wrong result_type")
    if active_candidate.get("status") != "active_isolation_macro_candidate_failed_margin_or_runability":
        return fail("Sky130 active isolation preamp candidate should record no fully passing macro setting")
    if active_candidate.get("setting_count") != 4 or active_candidate.get("case_count") != 8:
        return fail("Sky130 active isolation preamp candidate should run four settings and eight cases")
    if active_candidate.get("measured_case_count") != 8 or active_candidate.get("timed_out_case_count") != 0:
        return fail("Sky130 active isolation preamp candidate should measure all cases without timeout")
    if active_candidate.get("passing_setting_count") != 0:
        return fail("Sky130 active isolation preamp candidate must not claim a passing setting")
    best = active_candidate.get("best_setting", {})
    if float(best.get("minimum_abs_preamp_output_diff_v", 0.0)) <= float(active_candidate.get("output_margin_target_v", 0.0)):
        return fail("Sky130 active isolation preamp candidate should show active macro output can exceed margin")
    if int(best.get("sign_pass_count", 0)) >= int(best.get("case_count", 0)):
        return fail("Sky130 active isolation preamp candidate should still expose incomplete sign preservation")
    if float(best.get("minimum_sample_to_sense_transfer_ratio", 0.0)) <= 0.4:
        return fail("Sky130 active isolation preamp candidate should preserve frontend sense transfer with low input capacitance")
    if active_candidate.get("accepted_post_layout_written") is not False:
        return fail("Sky130 active isolation preamp candidate must not write accepted evidence")
    for path_field in ["generated_deck", "csv"]:
        path_value = active_candidate.get(path_field)
        if not path_value or not (ROOT / str(path_value)).exists():
            return fail(f"Sky130 active isolation preamp candidate missing {path_field}")
    active_candidate_page = (ROOT / "site" / "research" / "sky130-active-isolation-preamp-candidate.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Active Isolation Preamp Candidate", "active_isolation_macro_candidate_failed_margin_or_runability", "passing setting count: <code>0</code>", "best setting", "low input capacitance", "does not prove a transistor isolation circuit"]:
        if marker not in active_candidate_page:
            return fail(f"site/research/sky130-active-isolation-preamp-candidate.html missing marker {marker!r}")

    offset_calibrated = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-offset-calibrated-active-isolation-preamp.json").read_text(encoding="utf-8"))
    if offset_calibrated.get("result_type") != "sky130_offset_calibrated_active_isolation_preamp":
        return fail("Sky130 offset-calibrated active isolation preamp has wrong result_type")
    if offset_calibrated.get("status") != "offset_calibrated_active_isolation_macro_passed_not_transistor_layout_or_strict":
        return fail("Sky130 offset-calibrated active isolation preamp should pass only as a macro")
    if offset_calibrated.get("setting_count") != 4 or offset_calibrated.get("case_count") != 8:
        return fail("Sky130 offset-calibrated active isolation preamp should run four settings and eight signal cases")
    if offset_calibrated.get("measured_case_count") != 8:
        return fail("Sky130 offset-calibrated active isolation preamp should measure all signal cases")
    if offset_calibrated.get("passing_setting_count") < 1:
        return fail("Sky130 offset-calibrated active isolation preamp should find at least one passing macro setting")
    if offset_calibrated.get("first_passing_setting") != "unity_noninverting_low_cin":
        return fail("Sky130 offset-calibrated active isolation preamp should first pass at unity low-cap setting")
    best = offset_calibrated.get("best_setting", {})
    if float(best.get("minimum_abs_corrected_preamp_output_diff_v", 0.0)) <= float(offset_calibrated.get("output_margin_target_v", 0.0)):
        return fail("Sky130 offset-calibrated active isolation preamp should exceed corrected margin target")
    if offset_calibrated.get("accepted_post_layout_written") is not False:
        return fail("Sky130 offset-calibrated active isolation preamp must not write accepted evidence")
    for path_field in ["generated_deck", "csv"]:
        path_value = offset_calibrated.get(path_field)
        if not path_value or not (ROOT / str(path_value)).exists():
            return fail(f"Sky130 offset-calibrated active isolation preamp missing {path_field}")
    offset_calibrated_page = (ROOT / "site" / "research" / "sky130-offset-calibrated-active-isolation-preamp.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Offset-Calibrated Active Isolation Preamp", "offset_calibrated_active_isolation_macro_passed_not_transistor_layout_or_strict", "passing setting count: <code>1</code>", "first passing setting: <code>unity_noninverting_low_cin</code>", "zero-input output", "does not prove a transistor isolation circuit"]:
        if marker not in offset_calibrated_page:
            return fail(f"site/research/sky130-offset-calibrated-active-isolation-preamp.html missing marker {marker!r}")

    transistor_isolation = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-transistor-active-isolation-preamp.json").read_text(encoding="utf-8"))
    if transistor_isolation.get("result_type") != "sky130_transistor_active_isolation_preamp":
        return fail("Sky130 transistor active isolation preamp has wrong result_type")
    # The current canonical run uses the extracted isolation pair with its
    # explicitly corrected sense-pin convention.  Keep accepting the older
    # three-setting failure artifact when validating a historical checkout,
    # but do not require the old failure after the corrected bounded handoff
    # has been measured and published.
    transistor_passed = transistor_isolation.get("status") == "transistor_active_isolation_preamp_passed_schematic_not_layout_or_strict"
    transistor_failed = transistor_isolation.get("status") == "transistor_active_isolation_preamp_failed_schematic"
    if not (transistor_passed or transistor_failed):
        return fail("Sky130 transistor active isolation preamp has an unsupported status")
    expected_setting_count = 1 if transistor_passed else 3
    expected_case_count = 2 if transistor_passed else 6
    if transistor_isolation.get("setting_count") != expected_setting_count or transistor_isolation.get("case_count") != expected_case_count:
        return fail("Sky130 transistor active isolation preamp has an unexpected setting or case count")
    if transistor_isolation.get("measured_case_count") != expected_case_count:
        return fail("Sky130 transistor active isolation preamp should measure all signal cases")
    if transistor_isolation.get("timed_out_case_count") != 0:
        return fail("Sky130 transistor active isolation preamp should not time out")
    expected_passing_setting_count = 1 if transistor_passed else 0
    if transistor_isolation.get("passing_setting_count") != expected_passing_setting_count:
        return fail("Sky130 transistor active isolation preamp has an unexpected passing-setting count")
    best = transistor_isolation.get("best_setting", {})
    expected_best_name = "extracted_560k_4ua" if transistor_passed else "medium_iso_pair_8ua"
    if best.get("name") != expected_best_name:
        return fail("Sky130 transistor active isolation preamp should identify the expected best setting")
    if float(best.get("minimum_abs_corrected_preamp_output_diff_v", 0.0)) <= float(transistor_isolation.get("output_margin_target_v", 0.0)):
        return fail("Sky130 transistor active isolation preamp should exceed magnitude target while still failing sign")
    if transistor_failed and int(best.get("corrected_sign_pass_count", -1)) != 0:
        return fail("Sky130 transistor active isolation preamp should expose the remaining polarity failure")
    if transistor_passed and int(best.get("corrected_sign_pass_count", -1)) != expected_case_count:
        return fail("Sky130 transistor active isolation preamp should preserve corrected polarity")
    if transistor_isolation.get("accepted_post_layout_written") is not False:
        return fail("Sky130 transistor active isolation preamp must not write accepted evidence")
    for path_field in ["generated_deck", "csv"]:
        path_value = transistor_isolation.get(path_field)
        if not path_value or not (ROOT / str(path_value)).exists():
            return fail(f"Sky130 transistor active isolation preamp missing {path_field}")
    transistor_isolation_page = (ROOT / "site" / "research" / "sky130-transistor-active-isolation-preamp.html").read_text(encoding="utf-8")
    markers = ["Sky130 Transistor Active Isolation Preamp", "corrected margin pass", "does not prove layout"]
    if transistor_passed:
        markers.extend(["transistor_active_isolation_preamp_passed_schematic_not_layout_or_strict", "passing setting count: <code>1</code>", "extracted_560k_4ua"])
    else:
        markers.extend(["transistor_active_isolation_preamp_failed_schematic", "passing setting count: <code>0</code>", "medium_iso_pair_8ua"])
    for marker in markers:
        if marker not in transistor_isolation_page:
            return fail(f"site/research/sky130-transistor-active-isolation-preamp.html missing marker {marker!r}")

    swapped_isolation = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-swapped-transistor-active-isolation-preamp.json").read_text(encoding="utf-8"))
    if swapped_isolation.get("result_type") != "sky130_swapped_transistor_active_isolation_preamp":
        return fail("Sky130 swapped transistor active isolation preamp has wrong result_type")
    if swapped_isolation.get("status") != "swapped_transistor_active_isolation_preamp_passed_schematic_not_layout_or_strict":
        return fail("Sky130 swapped transistor active isolation preamp should pass the targeted schematic handoff")
    if swapped_isolation.get("setting_count") != 1 or swapped_isolation.get("case_count") != 2:
        return fail("Sky130 swapped transistor active isolation preamp should be the targeted medium-setting test")
    if swapped_isolation.get("measured_case_count") != 2:
        return fail("Sky130 swapped transistor active isolation preamp should report both measured signal cases")
    if swapped_isolation.get("timed_out_case_count") != 0:
        return fail("Sky130 swapped transistor active isolation preamp should complete without signal-case timeout")
    if swapped_isolation.get("passing_setting_count") != 1:
        return fail("Sky130 swapped transistor active isolation preamp should report one passing setting")
    if swapped_isolation.get("best_setting", {}).get("name") != "medium_iso_pair_8ua":
        return fail("Sky130 swapped transistor active isolation preamp should test the prior best setting")
    if swapped_isolation.get("accepted_post_layout_written") is not False:
        return fail("Sky130 swapped transistor active isolation preamp must not write accepted evidence")
    for path_field in ["generated_deck", "csv"]:
        path_value = swapped_isolation.get(path_field)
        if not path_value or not (ROOT / str(path_value)).exists():
            return fail(f"Sky130 swapped transistor active isolation preamp missing {path_field}")
    swapped_isolation_page = (ROOT / "site" / "research" / "sky130-swapped-transistor-active-isolation-preamp.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Swapped Transistor Active Isolation Preamp", "swapped_transistor_active_isolation_preamp_passed_schematic_not_layout_or_strict", "timed-out case count: <code>0</code>", "passing setting count: <code>1</code>", "medium_iso_pair_8ua", "does not prove layout"]:
        if marker not in swapped_isolation_page:
            return fail(f"site/research/sky130-swapped-transistor-active-isolation-preamp.html missing marker {marker!r}")

    polarity_handoff = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-polarity-corrected-transistor-handoff.json").read_text(encoding="utf-8"))
    if polarity_handoff.get("result_type") != "sky130_polarity_corrected_transistor_handoff":
        return fail("Sky130 polarity-corrected transistor handoff has wrong result_type")
    if polarity_handoff.get("status") != "polarity_corrected_transistor_handoff_passed_schematic_sign_map_not_layout_or_strict":
        return fail("Sky130 polarity-corrected transistor handoff should pass only as a schematic sign-map")
    if polarity_handoff.get("setting_count") != 3 or polarity_handoff.get("case_count") != 6:
        return fail("Sky130 polarity-corrected transistor handoff should analyze the full measured transistor sweep")
    if polarity_handoff.get("passing_setting_count") != 2:
        return fail("Sky130 polarity-corrected transistor handoff should find two passing transistor settings")
    if polarity_handoff.get("first_passing_setting") != "medium_iso_pair_8ua":
        return fail("Sky130 polarity-corrected transistor handoff should first pass at medium isolation setting")
    if polarity_handoff.get("polarity_contract") != "converter_positive_input_is_negative_raw_preamp_output_diff":
        return fail("Sky130 polarity-corrected transistor handoff should name the converter polarity contract")
    best = polarity_handoff.get("best_setting", {})
    if best.get("name") != "medium_iso_pair_8ua":
        return fail("Sky130 polarity-corrected transistor handoff should keep medium isolation as best")
    if float(best.get("minimum_abs_polarity_corrected_output_diff_v", 0.0)) <= float(polarity_handoff.get("output_margin_target_v", 0.0)):
        return fail("Sky130 polarity-corrected transistor handoff should exceed output margin target")
    if polarity_handoff.get("reruns_ngspice") is not False:
        return fail("Sky130 polarity-corrected transistor handoff must not imply a new ngspice run")
    if polarity_handoff.get("accepted_post_layout_written") is not False:
        return fail("Sky130 polarity-corrected transistor handoff must not write accepted evidence")
    polarity_handoff_page = (ROOT / "site" / "research" / "sky130-polarity-corrected-transistor-handoff.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Polarity-Corrected Transistor Handoff", "polarity_corrected_transistor_handoff_passed_schematic_sign_map_not_layout_or_strict", "converter_positive_input_is_negative_raw_preamp_output_diff", "passing setting count: <code>2</code>", "first passing setting: <code>medium_iso_pair_8ua</code>", "does not prove a new circuit"]:
        if marker not in polarity_handoff_page:
            return fail(f"site/research/sky130-polarity-corrected-transistor-handoff.html missing marker {marker!r}")

    latch_sar_risk = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-polarity-contract-latch-sar-risk.json").read_text(encoding="utf-8"))
    if latch_sar_risk.get("result_type") != "sky130_polarity_contract_latch_sar_risk":
        return fail("Sky130 polarity contract latch/SAR risk has wrong result_type")
    if latch_sar_risk.get("status") != "polarity_contract_ready_for_isolated_latch_design_not_strict":
        return fail("Sky130 polarity contract latch/SAR risk should be ready only for isolated latch design")
    if latch_sar_risk.get("polarity_contract") != "converter_positive_input_is_negative_raw_preamp_output_diff":
        return fail("Sky130 polarity contract latch/SAR risk should preserve the converter polarity contract")
    if latch_sar_risk.get("best_transistor_setting") != "medium_iso_pair_8ua":
        return fail("Sky130 polarity contract latch/SAR risk should use the medium transistor setting")
    if float(latch_sar_risk.get("output_margin_over_target_x", 0.0)) <= 1.0:
        return fail("Sky130 polarity contract latch/SAR risk should have output margin over target")
    if float(latch_sar_risk.get("best_latch_kickback_over_half_lsb_x", 0.0)) <= 1.0:
        return fail("Sky130 polarity contract latch/SAR risk should keep kickback as a blocker")
    if latch_sar_risk.get("kickback_still_blocks_sar_contract") is not True:
        return fail("Sky130 polarity contract latch/SAR risk should explicitly block SAR contract on kickback")
    if "latch_kickback_above_half_lsb" not in set(latch_sar_risk.get("blockers", [])):
        return fail("Sky130 polarity contract latch/SAR risk should list latch kickback blocker")
    if latch_sar_risk.get("accepted_post_layout_written") is not False:
        return fail("Sky130 polarity contract latch/SAR risk must not write accepted evidence")
    latch_sar_risk_page = (ROOT / "site" / "research" / "sky130-polarity-contract-latch-sar-risk.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Polarity Contract Latch/SAR Risk", "polarity_contract_ready_for_isolated_latch_design_not_strict", "kickback still blocks SAR contract: <code>True</code>", "latch_kickback_above_half_lsb", "polarity_named_isolated_latch_input", "does not prove a latch connected to the transistor handoff"]:
        if marker not in latch_sar_risk_page:
            return fail(f"site/research/sky130-polarity-contract-latch-sar-risk.html missing marker {marker!r}")

    isolated_latch_order = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-polarity-named-isolated-latch-work-order.json").read_text(encoding="utf-8"))
    if isolated_latch_order.get("result_type") != "sky130_polarity_named_isolated_latch_work_order":
        return fail("Sky130 polarity-named isolated latch work order has wrong result_type")
    if isolated_latch_order.get("status") != "polarity_named_isolated_latch_work_order_ready_not_circuit_proof":
        return fail("Sky130 polarity-named isolated latch work order should be a work order, not a circuit proof")
    if isolated_latch_order.get("polarity_contract") != "converter_positive_input_is_negative_raw_preamp_output_diff":
        return fail("Sky130 polarity-named isolated latch work order should preserve polarity contract")
    if float(isolated_latch_order.get("additional_kickback_reduction_needed_to_half_lsb_x", 0.0)) <= 1.0:
        return fail("Sky130 polarity-named isolated latch work order should require more kickback reduction")
    if float(isolated_latch_order.get("additional_kickback_reduction_needed_to_design_target_x", 0.0)) <= float(isolated_latch_order.get("additional_kickback_reduction_needed_to_half_lsb_x", 0.0)):
        return fail("Sky130 polarity-named isolated latch work order should make design target stricter than half-LSB")
    move_names = {item.get("name") for item in isolated_latch_order.get("candidate_moves", [])}
    for required_move in {"source_follower_input_buffer", "sampled_internal_decision_capacitor", "two_phase_preamp_then_latch", "delayed_or_bottom_plate_latch_clock"}:
        if required_move not in move_names:
            return fail(f"Sky130 polarity-named isolated latch work order missing move {required_move}")
    test_names = {item.get("name") for item in isolated_latch_order.get("acceptance_tests", [])}
    for required_test in {"polarity_contract_preserved", "both_signs_resolve", "kickback_hard_line", "wrong_code_proxy", "no_strict_claim"}:
        if required_test not in test_names:
            return fail(f"Sky130 polarity-named isolated latch work order missing test {required_test}")
    if isolated_latch_order.get("accepted_post_layout_written") is not False:
        return fail("Sky130 polarity-named isolated latch work order must not write accepted evidence")
    isolated_latch_order_page = (ROOT / "site" / "research" / "sky130-polarity-named-isolated-latch-work-order.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Polarity-Named Isolated Latch Work Order", "polarity_named_isolated_latch_work_order_ready_not_circuit_proof", "source_follower_input_buffer", "sampled_internal_decision_capacitor", "wrong_code_proxy", "does not prove the isolated latch circuit"]:
        if marker not in isolated_latch_order_page:
            return fail(f"site/research/sky130-polarity-named-isolated-latch-work-order.html missing marker {marker!r}")

    source_follower_latch = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-source-follower-isolated-latch-candidate.json").read_text(encoding="utf-8"))
    if source_follower_latch.get("result_type") != "sky130_source_follower_isolated_latch_candidate":
        return fail("Sky130 source-follower isolated latch candidate has wrong result_type")
    if source_follower_latch.get("status") != "source_follower_isolated_latch_candidate_characterized_not_accepted":
        return fail("Sky130 source-follower isolated latch candidate should be characterized, not accepted")
    if source_follower_latch.get("case_count") != 4:
        return fail("Sky130 source-follower isolated latch candidate should run four targeted cases")
    if source_follower_latch.get("measured_case_count") != 0:
        return fail("Sky130 source-follower isolated latch candidate should not report measured cases")
    if source_follower_latch.get("timed_out_case_count") != 4:
        return fail("Sky130 source-follower isolated latch candidate should expose timeouts")
    if source_follower_latch.get("passing_setting_count") != 0:
        return fail("Sky130 source-follower isolated latch candidate should not report passing settings")
    if source_follower_latch.get("accepted_post_layout_written") is not False:
        return fail("Sky130 source-follower isolated latch candidate must not write accepted evidence")
    for path_field in ["generated_deck", "csv"]:
        path_value = source_follower_latch.get(path_field)
        if not path_value or not (ROOT / str(path_value)).exists():
            return fail(f"Sky130 source-follower isolated latch candidate missing {path_field}")
    source_follower_latch_page = (ROOT / "site" / "research" / "sky130-source-follower-isolated-latch-candidate.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Source-Follower Isolated Latch Candidate", "source_follower_isolated_latch_candidate_characterized_not_accepted", "timed-out case count: <code>4</code>", "passing setting count: <code>0</code>", "source follower", "does not prove noise"]:
        if marker not in source_follower_latch_page:
            return fail(f"site/research/sky130-source-follower-isolated-latch-candidate.html missing marker {marker!r}")

    sampled_decision_latch = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-sampled-internal-decision-cap-latch-candidate.json").read_text(encoding="utf-8"))
    if sampled_decision_latch.get("result_type") != "sky130_sampled_internal_decision_cap_latch_candidate":
        return fail("Sky130 sampled internal decision-cap latch candidate has wrong result_type")
    if sampled_decision_latch.get("status") != "sampled_internal_decision_cap_latch_candidate_characterized_not_accepted":
        return fail("Sky130 sampled internal decision-cap latch candidate should be characterized, not accepted")
    if sampled_decision_latch.get("case_count") != 4:
        return fail("Sky130 sampled internal decision-cap latch candidate should run four targeted cases")
    if sampled_decision_latch.get("measured_case_count") != 0:
        return fail("Sky130 sampled internal decision-cap latch candidate should not report measured cases")
    if int(sampled_decision_latch.get("timed_out_case_count", 0)) < 3:
        return fail("Sky130 sampled internal decision-cap latch candidate should expose timeout-heavy failure")
    if sampled_decision_latch.get("passing_setting_count") != 0:
        return fail("Sky130 sampled internal decision-cap latch candidate should not report passing settings")
    if sampled_decision_latch.get("accepted_post_layout_written") is not False:
        return fail("Sky130 sampled internal decision-cap latch candidate must not write accepted evidence")
    for path_field in ["generated_deck", "csv"]:
        path_value = sampled_decision_latch.get(path_field)
        if not path_value or not (ROOT / str(path_value)).exists():
            return fail(f"Sky130 sampled internal decision-cap latch candidate missing {path_field}")
    sampled_decision_latch_page = (ROOT / "site" / "research" / "sky130-sampled-internal-decision-cap-latch-candidate.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Sampled Internal Decision-Cap Latch Candidate", "sampled_internal_decision_cap_latch_candidate_characterized_not_accepted", "measured case count: <code>0</code>", "passing setting count: <code>0</code>", "internal decision capacitor", "does not prove noise"]:
        if marker not in sampled_decision_latch_page:
            return fail(f"site/research/sky130-sampled-internal-decision-cap-latch-candidate.html missing marker {marker!r}")

    two_phase_latch = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-two-phase-preamp-latch-candidate.json").read_text(encoding="utf-8"))
    if two_phase_latch.get("result_type") != "sky130_two_phase_preamp_latch_candidate":
        return fail("Sky130 two-phase preamp latch candidate has wrong result_type")
    allowed_two_phase_statuses = {
        "two_phase_preamp_latch_candidate_characterized_not_accepted",
        "two_phase_preamp_latch_candidate_passed_schematic_not_noise_layout_or_strict",
    }
    if two_phase_latch.get("status") not in allowed_two_phase_statuses:
        return fail("Sky130 two-phase preamp latch candidate has an unsupported status")
    if two_phase_latch.get("case_count") != 2:
        return fail("Sky130 two-phase preamp latch candidate should run two target-edge cases")
    if two_phase_latch.get("status") == "two_phase_preamp_latch_candidate_passed_schematic_not_noise_layout_or_strict":
        if two_phase_latch.get("measured_case_count") != 2 or two_phase_latch.get("timed_out_case_count") != 0:
            return fail("Sky130 two-phase preamp latch candidate pass must measure both edge cases")
        if two_phase_latch.get("resolved_correct_polarity_count") != 2 or two_phase_latch.get("kickback_below_half_lsb_count") != 2:
            return fail("Sky130 two-phase preamp latch candidate pass must resolve both signs and kickback checks")
    else:
        if two_phase_latch.get("measured_case_count") != 0 or two_phase_latch.get("timed_out_case_count") != 2:
            return fail("Sky130 two-phase preamp latch candidate incomplete state must expose both timeouts")
        if two_phase_latch.get("resolved_correct_polarity_count") != 0 or two_phase_latch.get("kickback_below_half_lsb_count") != 0:
            return fail("Sky130 two-phase preamp latch candidate should not claim resolution after timeout")
    if two_phase_latch.get("accepted_post_layout_written") is not False:
        return fail("Sky130 two-phase preamp latch candidate must not write accepted evidence")
    for path_field in ["generated_deck", "csv"]:
        path_value = two_phase_latch.get(path_field)
        if not path_value or not (ROOT / str(path_value)).exists():
            return fail(f"Sky130 two-phase preamp latch candidate missing {path_field}")
    two_phase_latch_page = (ROOT / "site" / "research" / "sky130-two-phase-preamp-latch-candidate.html").read_text(encoding="utf-8")
    expected_two_phase_markers = ["Sky130 Two-Phase Preamp-Then-Latch Candidate", two_phase_latch["status"], "preamp-then-latch", "does not prove noise"]
    if two_phase_latch["status"] == "two_phase_preamp_latch_candidate_passed_schematic_not_noise_layout_or_strict":
        expected_two_phase_markers.extend(["timed-out case count: <code>0</code>", "resolved correct polarity count: <code>2</code>"])
    else:
        expected_two_phase_markers.extend(["timed-out case count: <code>2</code>", "resolved correct polarity count: <code>0</code>"])
    for marker in expected_two_phase_markers:
        if marker not in two_phase_latch_page:
            return fail(f"site/research/sky130-two-phase-preamp-latch-candidate.html missing marker {marker!r}")

    debug_ladder = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-isolated-latch-debug-ladder.json").read_text(encoding="utf-8"))
    if debug_ladder.get("result_type") != "sky130_isolated_latch_debug_ladder":
        return fail("Sky130 isolated latch debug ladder has wrong result_type")
    if debug_ladder.get("status") != "isolated_latch_debug_ladder_ready_after_timeout_failures":
        return fail("Sky130 isolated latch debug ladder should be ready after timeout failures")
    if debug_ladder.get("failed_candidate_count") != 3:
        return fail("Sky130 isolated latch debug ladder should summarize three failed candidates")
    if debug_ladder.get("failed_candidate_measured_case_count") != 0:
        return fail("Sky130 isolated latch debug ladder should show zero measured failed-candidate cases")
    if int(debug_ladder.get("failed_candidate_timed_out_case_count", 0)) < 9:
        return fail("Sky130 isolated latch debug ladder should capture timeout-heavy failure pattern")
    step_names = {item.get("name") for item in debug_ladder.get("debug_ladder", [])}
    for required_step in {"preamp_alone_dc_and_transient", "latch_alone_from_measured_preamp_voltages", "clock_timing_ladder", "coupled_kickback_rejoin", "sar_threshold_wrong_code_proxy"}:
        if required_step not in step_names:
            return fail(f"Sky130 isolated latch debug ladder missing step {required_step}")
    if debug_ladder.get("accepted_post_layout_written") is not False:
        return fail("Sky130 isolated latch debug ladder must not write accepted evidence")
    debug_ladder_page = (ROOT / "site" / "research" / "sky130-isolated-latch-debug-ladder.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Isolated Latch Debug Ladder", "isolated_latch_debug_ladder_ready_after_timeout_failures", "failed candidate count: <code>3</code>", "timed-out failed-candidate cases: <code>9</code>", "preamp_alone_dc_and_transient", "sar_threshold_wrong_code_proxy", "does not prove a new circuit"]:
        if marker not in debug_ladder_page:
            return fail(f"site/research/sky130-isolated-latch-debug-ladder.html missing marker {marker!r}")

    preamp_debug = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-preamp-alone-latch-debug.json").read_text(encoding="utf-8"))
    if preamp_debug.get("result_type") != "sky130_preamp_alone_latch_debug":
        return fail("Sky130 preamp-alone latch debug has wrong result_type")
    if preamp_debug.get("status") != "preamp_alone_latch_debug_failed":
        return fail("Sky130 preamp-alone latch debug should currently fail")
    if preamp_debug.get("case_count") != 2:
        return fail("Sky130 preamp-alone latch debug should run two target-edge cases")
    if preamp_debug.get("measured_case_count") != 0:
        return fail("Sky130 preamp-alone latch debug should not report measured transient cases")
    if preamp_debug.get("timed_out_case_count") != 2:
        return fail("Sky130 preamp-alone latch debug should expose two timeouts")
    if preamp_debug.get("uses_regenerative_latch") is not False:
        return fail("Sky130 preamp-alone latch debug must remove the regenerative latch")
    if preamp_debug.get("accepted_post_layout_written") is not False:
        return fail("Sky130 preamp-alone latch debug must not write accepted evidence")
    for path_field in ["generated_deck", "csv"]:
        path_value = preamp_debug.get(path_field)
        if not path_value or not (ROOT / str(path_value)).exists():
            return fail(f"Sky130 preamp-alone latch debug missing {path_field}")
    preamp_debug_page = (ROOT / "site" / "research" / "sky130-preamp-alone-latch-debug.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Preamp-Alone Latch Debug", "preamp_alone_latch_debug_failed", "timed-out case count: <code>2</code>", "uses regenerative latch: <code>False</code>", "preamp itself can turn", "does not prove latch resolution"]:
        if marker not in preamp_debug_page:
            return fail(f"site/research/sky130-preamp-alone-latch-debug.html missing marker {marker!r}")

    preamp_op_debug = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-preamp-op-latch-debug.json").read_text(encoding="utf-8"))
    if preamp_op_debug.get("result_type") != "sky130_preamp_op_latch_debug":
        return fail("Sky130 preamp OP latch debug has wrong result_type")
    if preamp_op_debug.get("status") != "preamp_op_latch_debug_failed":
        return fail("Sky130 preamp OP latch debug should currently fail")
    if preamp_op_debug.get("case_count") != 2:
        return fail("Sky130 preamp OP latch debug should run two target-edge cases")
    if preamp_op_debug.get("op_measured_case_count") != 0:
        return fail("Sky130 preamp OP latch debug should not report measured OP cases")
    if preamp_op_debug.get("timed_out_case_count") != 2:
        return fail("Sky130 preamp OP latch debug should expose two OP timeouts")
    if preamp_op_debug.get("uses_transient") is not False or preamp_op_debug.get("uses_regenerative_latch") is not False:
        return fail("Sky130 preamp OP latch debug must remove transient and latch")
    if preamp_op_debug.get("accepted_post_layout_written") is not False:
        return fail("Sky130 preamp OP latch debug must not write accepted evidence")
    for path_field in ["generated_deck", "csv"]:
        path_value = preamp_op_debug.get(path_field)
        if not path_value or not (ROOT / str(path_value)).exists():
            return fail(f"Sky130 preamp OP latch debug missing {path_field}")
    preamp_op_debug_page = (ROOT / "site" / "research" / "sky130-preamp-op-latch-debug.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Preamp OP Latch Debug", "preamp_op_latch_debug_failed", "OP measured case count: <code>0</code>", "uses transient: <code>False</code>", "uses regenerative latch: <code>False</code>", "does not prove transient settling"]:
        if marker not in preamp_op_debug_page:
            return fail(f"site/research/sky130-preamp-op-latch-debug.html missing marker {marker!r}")

    known_shape_op = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-known-good-shape-preamp-op-latch-debug.json").read_text(encoding="utf-8"))
    if known_shape_op.get("result_type") != "sky130_known_good_shape_preamp_op_latch_debug":
        return fail("Sky130 known-good-shape preamp OP latch debug has wrong result_type")
    if known_shape_op.get("status") != "known_good_shape_preamp_op_debug_passed_both_signs":
        return fail("Sky130 known-good-shape preamp OP latch debug should pass both signs")
    if known_shape_op.get("op_measured_case_count") != 2 or known_shape_op.get("timed_out_case_count") != 0:
        return fail("Sky130 known-good-shape preamp OP latch debug should measure both OP cases without timeout")
    if known_shape_op.get("sign_pass_count") != 2 or known_shape_op.get("output_margin_pass_count") != 2:
        return fail("Sky130 known-good-shape preamp OP latch debug should pass sign and margin")
    if known_shape_op.get("uses_known_good_deck_shape") is not True:
        return fail("Sky130 known-good-shape preamp OP latch debug should use known-good deck shape")
    if known_shape_op.get("accepted_post_layout_written") is not False:
        return fail("Sky130 known-good-shape preamp OP latch debug must not write accepted evidence")
    known_shape_page = (ROOT / "site" / "research" / "sky130-known-good-shape-preamp-op-latch-debug.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Known-Good-Shape Preamp OP Latch Debug", "known_good_shape_preamp_op_debug_passed_both_signs", "uses known-good deck shape: <code>True</code>", "timed-out case count: <code>0</code>", "known-good OP preamp shape", "does not prove transient settling"]:
        if marker not in known_shape_page:
            return fail(f"site/research/sky130-known-good-shape-preamp-op-latch-debug.html missing marker {marker!r}")

    op_diagnosis = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-preamp-op-deck-diff-diagnosis.json").read_text(encoding="utf-8"))
    if op_diagnosis.get("result_type") != "sky130_preamp_op_deck_diff_diagnosis":
        return fail("Sky130 preamp OP deck-diff diagnosis has wrong result_type")
    if op_diagnosis.get("status") != "current_preamp_op_rerun_confirms_known_good_shape_after_timeout_fix":
        return fail("Sky130 preamp OP deck-diff diagnosis should confirm known-good shape after timeout fix")
    if op_diagnosis.get("current_rerun_op_measured_case_count") != 2 or op_diagnosis.get("current_rerun_timed_out_case_count") != 0:
        return fail("Sky130 preamp OP deck-diff diagnosis should summarize current rerun success")
    if "measure transient startup from the known-good OP initial point" not in op_diagnosis.get("next_debug_steps", []):
        return fail("Sky130 preamp OP deck-diff diagnosis should move next to transient startup")
    if op_diagnosis.get("accepted_post_layout_written") is not False:
        return fail("Sky130 preamp OP deck-diff diagnosis must not write accepted evidence")
    op_diagnosis_page = (ROOT / "site" / "research" / "sky130-preamp-op-deck-diff-diagnosis.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Preamp OP Deck-Diff Diagnosis", "current_preamp_op_rerun_confirms_known_good_shape_after_timeout_fix", "current known-good-shape OP measured cases: <code>2</code>", "current known-good-shape timed-out cases: <code>0</code>", "measure transient startup from the known-good OP initial point", "does not prove or disprove the physical preamp design"]:
        if marker not in op_diagnosis_page:
            return fail(f"site/research/sky130-preamp-op-deck-diff-diagnosis.html missing marker {marker!r}")

    preamp_transient = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-known-good-shape-preamp-transient-latch-debug.json").read_text(encoding="utf-8"))
    if preamp_transient.get("result_type") != "sky130_known_good_shape_preamp_transient_latch_debug":
        return fail("Sky130 known-good-shape preamp transient latch debug has wrong result_type")
    if preamp_transient.get("status") != "known_good_shape_preamp_transient_passed_ready_for_latch_alone":
        return fail("Sky130 known-good-shape preamp transient latch debug should pass")
    if preamp_transient.get("measured_case_count") != 2 or preamp_transient.get("timed_out_case_count") != 0:
        return fail("Sky130 known-good-shape preamp transient latch debug should measure both cases")
    if preamp_transient.get("sign_pass_count") != 2 or preamp_transient.get("output_margin_pass_count") != 2:
        return fail("Sky130 known-good-shape preamp transient latch debug should pass sign and margin")
    if preamp_transient.get("settled_case_count") != 2:
        return fail("Sky130 known-good-shape preamp transient latch debug should settle both cases")
    if preamp_transient.get("uses_known_good_op_initial_point") is not True or preamp_transient.get("uses_regenerative_latch") is not False:
        return fail("Sky130 known-good-shape preamp transient latch debug should use OP initial point and no latch")
    if preamp_transient.get("accepted_post_layout_written") is not False:
        return fail("Sky130 known-good-shape preamp transient latch debug must not write accepted evidence")
    preamp_transient_page = (ROOT / "site" / "research" / "sky130-known-good-shape-preamp-transient-latch-debug.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Known-Good-Shape Preamp Transient Latch Debug", "known_good_shape_preamp_transient_passed_ready_for_latch_alone", "measured case count: <code>2</code>", "settled case count: <code>2</code>", "uses known-good OP initial point: <code>True</code>", "does not prove latch resolution"]:
        if marker not in preamp_transient_page:
            return fail(f"site/research/sky130-known-good-shape-preamp-transient-latch-debug.html missing marker {marker!r}")

    latch_alone = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-latch-alone-from-preamp-voltage-debug.json").read_text(encoding="utf-8"))
    if latch_alone.get("result_type") != "sky130_latch_alone_from_preamp_voltage_debug":
        return fail("Sky130 latch-alone from preamp voltage debug has wrong result_type")
    if latch_alone.get("status") != "latch_alone_from_preamp_voltage_passed_ready_for_clock_timing":
        return fail("Sky130 latch-alone from preamp voltage debug should pass the isolated latch test")
    if latch_alone.get("measured_case_count") != 2 or latch_alone.get("timed_out_case_count") != 0:
        return fail("Sky130 latch-alone from preamp voltage debug should measure both cases without timeout")
    if latch_alone.get("resolved_correct_polarity_count") != 2:
        return fail("Sky130 latch-alone from preamp voltage debug should resolve both isolated cases")
    if latch_alone.get("uses_ideal_sources_from_measured_preamp_voltages") is not True or latch_alone.get("uses_sampled_nodes") is not False:
        return fail("Sky130 latch-alone from preamp voltage debug should isolate latch from sampled nodes")
    if latch_alone.get("accepted_post_layout_written") is not False:
        return fail("Sky130 latch-alone from preamp voltage debug must not write accepted evidence")
    latch_alone_page = (ROOT / "site" / "research" / "sky130-latch-alone-from-preamp-voltage-debug.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Latch-Alone From Preamp Voltage Debug", "latch_alone_from_preamp_voltage_passed_ready_for_clock_timing", "measured case count: <code>2</code>", "resolved correct polarity count: <code>2</code>", "uses sampled nodes: <code>False</code>", "does not prove sampled-node kickback"]:
        if marker not in latch_alone_page:
            return fail(f"site/research/sky130-latch-alone-from-preamp-voltage-debug.html missing marker {marker!r}")

    swapped_latch = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-latch-alone-swapped-preamp-voltage-debug.json").read_text(encoding="utf-8"))
    if swapped_latch.get("result_type") != "sky130_latch_alone_swapped_preamp_voltage_debug":
        return fail("Sky130 latch-alone swapped preamp voltage debug has wrong result_type")
    if swapped_latch.get("status") != "latch_alone_swapped_preamp_voltage_passed_ready_for_clock_timing":
        return fail("Sky130 latch-alone swapped preamp voltage debug should pass")
    if swapped_latch.get("measured_case_count") != 2 or swapped_latch.get("timed_out_case_count") != 0:
        return fail("Sky130 latch-alone swapped preamp voltage debug should measure both cases without timeout")
    if swapped_latch.get("resolved_correct_polarity_count") != 2:
        return fail("Sky130 latch-alone swapped preamp voltage debug should resolve both cases")
    if swapped_latch.get("uses_swapped_preamp_voltage_mapping") is not True:
        return fail("Sky130 latch-alone swapped preamp voltage debug should use swapped mapping")
    if swapped_latch.get("accepted_post_layout_written") is not False:
        return fail("Sky130 latch-alone swapped preamp voltage debug must not write accepted evidence")
    swapped_latch_page = (ROOT / "site" / "research" / "sky130-latch-alone-swapped-preamp-voltage-debug.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Latch-Alone Swapped Preamp Voltage Debug", "latch_alone_swapped_preamp_voltage_passed_ready_for_clock_timing", "measured case count: <code>2</code>", "resolved correct polarity count: <code>2</code>", "uses swapped preamp voltage mapping: <code>True</code>", "does not prove sampled-node kickback"]:
        if marker not in swapped_latch_page:
            return fail(f"site/research/sky130-latch-alone-swapped-preamp-voltage-debug.html missing marker {marker!r}")

    swapped_clock = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-swapped-latch-clock-timing-debug.json").read_text(encoding="utf-8"))
    if swapped_clock.get("result_type") != "sky130_swapped_latch_clock_timing_debug":
        return fail("Sky130 swapped latch clock timing debug has wrong result_type")
    if swapped_clock.get("status") != "swapped_latch_clock_timing_characterized_not_ready":
        return fail("Sky130 swapped latch clock timing debug should remain not ready")
    if swapped_clock.get("measured_case_count") != 6 or swapped_clock.get("timed_out_case_count") != 0:
        return fail("Sky130 swapped latch clock timing debug should measure six cases without timeout")
    if swapped_clock.get("resolved_correct_polarity_count") != 0:
        return fail("Sky130 swapped latch clock timing debug should expose zero correct-polarity resolutions")
    if swapped_clock.get("clock_setting_count") != 3 or swapped_clock.get("passing_clock_setting_count") != 0:
        return fail("Sky130 swapped latch clock timing debug should test three clock settings and pass none")
    if swapped_clock.get("uses_swapped_preamp_voltage_mapping") is not True or swapped_clock.get("uses_sampled_nodes") is not False:
        return fail("Sky130 swapped latch clock timing debug should use swapped mapping while sampled nodes are removed")
    if swapped_clock.get("accepted_post_layout_written") is not False:
        return fail("Sky130 swapped latch clock timing debug must not write accepted evidence")
    swapped_clock_page = (ROOT / "site" / "research" / "sky130-swapped-latch-clock-timing-debug.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Swapped Latch Clock Timing Debug", "swapped_latch_clock_timing_characterized_not_ready", "measured case count: <code>6</code>", "timed-out case count: <code>0</code>", "resolved correct polarity count: <code>0</code>", "passing clock setting count: <code>0</code>", "uses sampled nodes: <code>False</code>", "does not prove sampled-node kickback"]:
        if marker not in swapped_clock_page:
            return fail(f"site/research/sky130-swapped-latch-clock-timing-debug.html missing marker {marker!r}")

    latch_convention = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-clocked-latch-output-convention-diagnostic.json").read_text(encoding="utf-8"))
    if latch_convention.get("result_type") != "sky130_clocked_latch_output_convention_diagnostic":
        return fail("Sky130 clocked latch output convention diagnostic has wrong result_type")
    if latch_convention.get("status") != "clocked_latch_output_convention_inversion_confirmed":
        return fail("Sky130 clocked latch output convention diagnostic should confirm inversion")
    if latch_convention.get("case_count") != 6:
        return fail("Sky130 clocked latch output convention diagnostic should inspect six cases")
    if latch_convention.get("outn_minus_outp_contract_match_count") != 0:
        return fail("Sky130 clocked latch output convention diagnostic should reject outn-minus-outp")
    if latch_convention.get("outp_minus_outn_contract_match_count") != 6:
        return fail("Sky130 clocked latch output convention diagnostic should accept outp-minus-outn")
    if latch_convention.get("inferred_clocked_latch_output_contract") != "digital_bit_positive_when_outp_exceeds_outn":
        return fail("Sky130 clocked latch output convention diagnostic should name the output contract")
    if latch_convention.get("requires_new_ngspice_run") is not False or latch_convention.get("uses_existing_same_run_measurements") is not True:
        return fail("Sky130 clocked latch output convention diagnostic should only reinterpret existing measurements")
    if latch_convention.get("accepted_post_layout_written") is not False:
        return fail("Sky130 clocked latch output convention diagnostic must not write accepted evidence")
    latch_convention_page = (ROOT / "site" / "research" / "sky130-clocked-latch-output-convention-diagnostic.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Clocked Latch Output Convention Diagnostic", "clocked_latch_output_convention_inversion_confirmed", "outn-minus-outp contract match count: <code>0</code>", "outp-minus-outn contract match count: <code>6</code>", "digital_bit_positive_when_outp_exceeds_outn", "does not change the circuit", "does not create accepted post-layout converter evidence"]:
        if marker not in latch_convention_page:
            return fail(f"site/research/sky130-clocked-latch-output-convention-diagnostic.html missing marker {marker!r}")

    corrected_coupled = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-corrected-convention-sample-hold-latch-kickback.json").read_text(encoding="utf-8"))
    if corrected_coupled.get("result_type") != "sky130_corrected_convention_sample_hold_latch_kickback":
        return fail("Sky130 corrected-convention sample-hold latch kickback has wrong result_type")
    if corrected_coupled.get("status") != "corrected_convention_coupled_kickback_characterized_not_ready":
        return fail("Sky130 corrected-convention sample-hold latch kickback should remain not ready")
    if corrected_coupled.get("measured_case_count") != 2 or corrected_coupled.get("timed_out_case_count") != 0:
        return fail("Sky130 corrected-convention sample-hold latch kickback should measure two cases without timeout")
    if corrected_coupled.get("resolved_correct_polarity_count") != 0:
        return fail("Sky130 corrected-convention sample-hold latch kickback should expose zero polarity passes")
    if corrected_coupled.get("kickback_below_half_lsb_count") != 0:
        return fail("Sky130 corrected-convention sample-hold latch kickback should expose zero kickback passes")
    if corrected_coupled.get("all_cases_pass_coupled_gate") is not False:
        return fail("Sky130 corrected-convention sample-hold latch kickback should fail coupled gate")
    if corrected_coupled.get("output_definition") != "outp_minus_outn":
        return fail("Sky130 corrected-convention sample-hold latch kickback should use outp-minus-outn output definition")
    if corrected_coupled.get("uses_sampled_nodes") is not True or corrected_coupled.get("uses_corrected_latch_output_convention") is not True:
        return fail("Sky130 corrected-convention sample-hold latch kickback should reconnect sampled nodes with corrected convention")
    if corrected_coupled.get("accepted_post_layout_written") is not False:
        return fail("Sky130 corrected-convention sample-hold latch kickback must not write accepted evidence")
    worst_kickback = corrected_coupled.get("worst_sampled_diff_kickback_v")
    if not isinstance(worst_kickback, (float, int)) or worst_kickback < 0.011:
        return fail("Sky130 corrected-convention sample-hold latch kickback should record large coupled kickback")
    corrected_coupled_page = (ROOT / "site" / "research" / "sky130-corrected-convention-sample-hold-latch-kickback.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Corrected-Convention Sample-Hold Latch Kickback", "corrected_convention_coupled_kickback_characterized_not_ready", "output definition: <code>outp_minus_outn</code>", "measured case count: <code>2</code>", "resolved correct polarity count: <code>0</code>", "kickback below half LSB count: <code>0</code>", "worst sampled differential kickback V: <code>1.197690000e-02</code>", "uses sampled nodes: <code>True</code>", "does not prove comparator noise"]:
        if marker not in corrected_coupled_page:
            return fail(f"site/research/sky130-corrected-convention-sample-hold-latch-kickback.html missing marker {marker!r}")

    corrected_isolation = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-corrected-convention-capacitive-isolation-confirm.json").read_text(encoding="utf-8"))
    if corrected_isolation.get("result_type") != "sky130_corrected_convention_capacitive_isolation_confirm":
        return fail("Sky130 corrected-convention capacitive isolation confirm has wrong result_type")
    if corrected_isolation.get("status") != "corrected_convention_capacitive_isolation_confirmed_not_noise_or_layout_proof":
        return fail("Sky130 corrected-convention capacitive isolation confirm should pass as bounded schematic evidence")
    if corrected_isolation.get("case_count") != 4 or corrected_isolation.get("measured_case_count") != 4:
        return fail("Sky130 corrected-convention capacitive isolation confirm should measure four cases")
    if corrected_isolation.get("timed_out_case_count") != 0 or corrected_isolation.get("passing_case_count") != 4:
        return fail("Sky130 corrected-convention capacitive isolation confirm should pass all cases without timeout")
    if corrected_isolation.get("output_definition") != "outp_minus_outn":
        return fail("Sky130 corrected-convention capacitive isolation confirm should use outp-minus-outn")
    if corrected_isolation.get("uses_capacitive_input_isolation") is not True or corrected_isolation.get("uses_sampled_nodes") is not True:
        return fail("Sky130 corrected-convention capacitive isolation confirm should use sampled nodes with capacitive isolation")
    if corrected_isolation.get("uses_corrected_latch_output_convention") is not True:
        return fail("Sky130 corrected-convention capacitive isolation confirm should carry corrected latch convention")
    if corrected_isolation.get("accepted_post_layout_written") is not False:
        return fail("Sky130 corrected-convention capacitive isolation confirm must not write accepted evidence")
    if corrected_isolation.get("worst_sampled_diff_kickback_v", 1.0) >= corrected_isolation.get("half_lsb_12b_v", 0.0):
        return fail("Sky130 corrected-convention capacitive isolation confirm should keep worst kickback below half-LSB")
    if corrected_isolation.get("minimum_abs_output_diff_v", 0.0) < 1.3:
        return fail("Sky130 corrected-convention capacitive isolation confirm should have strong output separation")
    corrected_isolation_page = (ROOT / "site" / "research" / "sky130-corrected-convention-capacitive-isolation-confirm.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Corrected-Convention Capacitive Isolation Confirm", "corrected_convention_capacitive_isolation_confirmed_not_noise_or_layout_proof", "output definition: <code>outp_minus_outn</code>", "measured case count: <code>4</code>", "passing case count: <code>4</code>", "confirmed coupling caps fF: <code>0.1, 0.2</code>", "worst sampled differential kickback V: <code>2.022000000e-04</code>", "uses capacitive input isolation: <code>True</code>", "does not prove comparator noise"]:
        if marker not in corrected_isolation_page:
            return fail(f"site/research/sky130-corrected-convention-capacitive-isolation-confirm.html missing marker {marker!r}")

    range_stress = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-corrected-convention-isolation-range-stress.json").read_text(encoding="utf-8"))
    if range_stress.get("result_type") != "sky130_corrected_convention_isolation_range_stress":
        return fail("Sky130 corrected-convention isolation range stress has wrong result_type")
    if range_stress.get("status") != "corrected_convention_isolation_range_stress_passed_not_noise_or_layout_proof":
        return fail("Sky130 corrected-convention isolation range stress should pass as bounded schematic evidence")
    if range_stress.get("case_count") != 12 or range_stress.get("measured_case_count") != 12:
        return fail("Sky130 corrected-convention isolation range stress should measure twelve cases")
    if range_stress.get("timed_out_case_count") != 0 or range_stress.get("passing_case_count") != 12:
        return fail("Sky130 corrected-convention isolation range stress should pass all cases without timeout")
    if range_stress.get("output_definition") != "outp_minus_outn":
        return fail("Sky130 corrected-convention isolation range stress should use outp-minus-outn")
    if range_stress.get("uses_capacitive_input_isolation") is not True or range_stress.get("uses_sampled_nodes") is not True:
        return fail("Sky130 corrected-convention isolation range stress should use sampled nodes with capacitive isolation")
    if range_stress.get("uses_corrected_latch_output_convention") is not True:
        return fail("Sky130 corrected-convention isolation range stress should carry corrected convention")
    if range_stress.get("accepted_post_layout_written") is not False:
        return fail("Sky130 corrected-convention isolation range stress must not write accepted evidence")
    if range_stress.get("worst_sampled_diff_kickback_v", 1.0) >= range_stress.get("half_lsb_12b_v", 0.0):
        return fail("Sky130 corrected-convention isolation range stress should keep worst kickback below half-LSB")
    if range_stress.get("minimum_abs_output_diff_v", 0.0) < 1.3:
        return fail("Sky130 corrected-convention isolation range stress should preserve strong latch output")
    range_stress_page = (ROOT / "site" / "research" / "sky130-corrected-convention-isolation-range-stress.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Corrected-Convention Isolation Range Stress", "corrected_convention_isolation_range_stress_passed_not_noise_or_layout_proof", "case count: <code>12</code>", "measured case count: <code>12</code>", "passing case count: <code>12</code>", "tested coupling caps fF: <code>0.1, 0.2</code>", "worst sampled differential kickback V: <code>2.023000000e-04</code>", "minimum abs output diff V: <code>1.373291900e+00</code>", "does not prove comparator noise"]:
        if marker not in range_stress_page:
            return fail(f"site/research/sky130-corrected-convention-isolation-range-stress.html missing marker {marker!r}")

    converter_ladder_page = (ROOT / "site" / "research" / "converter-evidence-ladder.html").read_text(encoding="utf-8")
    for marker in ["Converter Evidence Ladder", "what object did this artifact actually measure?", "schematic SPICE", "extracted RC", "DRC", "LVS", "measured silicon", "same-run package", "does not create accepted post-layout converter evidence"]:
        if marker not in converter_ladder_page:
            return fail(f"site/research/converter-evidence-ladder.html missing marker {marker!r}")

    error_flow_page = (ROOT / "site" / "research" / "analog-to-digital-to-model-error-flow.html").read_text(encoding="utf-8")
    for marker in ["Analog-To-Digital-To-Model Error Flow", "analog voltage error", "ADC code error", "corrected digital value error", "residual_abs", "residual_budget", "Placement says", "Acceptance says", "does not create accepted post-layout converter evidence"]:
        if marker not in error_flow_page:
            return fail(f"site/research/analog-to-digital-to-model-error-flow.html missing marker {marker!r}")

    final_converter_gate_page = (ROOT / "site" / "research" / "final-accepted-converter-gate.html").read_text(encoding="utf-8")
    for marker in ["Final Accepted Converter Gate", "one converter", "one run", "10-bit DAC input", "12-bit ADC output", "blocker count: 45", "Done Means Done", "accepted evidence is written by the strict submitter", "does not create accepted post-layout converter evidence"]:
        if marker not in final_converter_gate_page:
            return fail(f"site/research/final-accepted-converter-gate.html missing marker {marker!r}")

    first_converter_plan_page = (ROOT / "site" / "research" / "first-real-converter-candidate-execution-plan.html").read_text(encoding="utf-8")
    for marker in ["First Real Converter Candidate Execution Plan", "status: not_ready_for_strict_submission", "issue count: 22", "candidate non-scaffold files: 2", "row_90_when_s = 1.199360e-10", "aimc_readout_candidate_001", "energy = integral", "output_noise_rms &lt;= 0.004", "does not write accepted post-layout evidence"]:
        if marker not in first_converter_plan_page:
            return fail(f"site/research/first-real-converter-candidate-execution-plan.html missing marker {marker!r}")

    first_converter_packet = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-candidate-packet.json").read_text(encoding="utf-8"))
    if first_converter_packet.get("result_type") != "first_real_converter_candidate_packet":
        return fail("first real converter candidate packet has wrong result_type")
    if first_converter_packet.get("status") != "partial_measurement_packet_ready_not_strict_submission_ready":
        return fail("first real converter candidate packet has unexpected status")
    if first_converter_packet.get("ready_for_strict_submission") is not False:
        return fail("first real converter candidate packet must not be ready for strict submission")
    if first_converter_packet.get("accepted_post_layout_written") is not False:
        return fail("first real converter candidate packet must not write accepted evidence")
    measured_terms = first_converter_packet.get("measured_terms") if isinstance(first_converter_packet.get("measured_terms"), dict) else {}
    if measured_terms.get("ultra_frontend_transfer_ratio", 0) < 0.43:
        return fail("first real converter candidate packet should include ultra frontend transfer evidence")
    if first_converter_packet.get("current_preflight_issue_count") != 22:
        return fail("first real converter candidate packet should record current 22 preflight issues")
    first_converter_packet_page = (ROOT / "site" / "research" / "first-real-converter-candidate-packet.html").read_text(encoding="utf-8")
    for marker in ["First Real Converter Candidate Packet", "partial_measurement_packet_ready_not_strict_submission_ready", "ready for strict submission: <code>False</code>", "current preflight issue count: <code>22</code>", "starter row final V", "ultra frontend transfer ratio", "Payload Terms Still Missing", "does not write accepted post-layout evidence"]:
        if marker not in first_converter_packet_page:
            return fail(f"site/research/first-real-converter-candidate-packet.html missing marker {marker!r}")

    rehearsal_payload = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-rehearsal-payload.json").read_text(encoding="utf-8"))
    if rehearsal_payload.get("result_type") != "first_real_converter_rehearsal_payload":
        return fail("first real converter rehearsal payload has wrong result_type")
    if rehearsal_payload.get("status") != "rehearsal_payload_written_still_rejected":
        return fail("first real converter rehearsal payload has unexpected status")
    if rehearsal_payload.get("canonical_candidate_payload_touched") is not False:
        return fail("first real converter rehearsal payload must not touch canonical candidate payload")
    if rehearsal_payload.get("ready_for_strict_submission") is not False:
        return fail("first real converter rehearsal payload must remain rejected")
    if rehearsal_payload.get("strict_issue_count") != 15:
        return fail("first real converter rehearsal payload should reduce strict issues to 15")
    if rehearsal_payload.get("preview_would_write_accepted_evidence") is not False:
        return fail("first real converter rehearsal payload must not preview accepted evidence writes")
    rehearsal_page = (ROOT / "site" / "research" / "first-real-converter-rehearsal-payload.html").read_text(encoding="utf-8")
    for marker in ["First Real Converter Rehearsal Payload", "rehearsal_payload_written_still_rejected", "canonical candidate payload touched: <code>False</code>", "strict issue count: <code>15</code>", "Blockers Removed Compared With The Canonical Scaffold", "Remaining Real Blockers", "does not modify the canonical candidate payload"]:
        if marker not in rehearsal_page:
            return fail(f"site/research/first-real-converter-rehearsal-payload.html missing marker {marker!r}")

    blocker_work_order = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-blocker-work-order.json").read_text(encoding="utf-8"))
    if blocker_work_order.get("result_type") != "first_real_converter_blocker_work_order":
        return fail("first real converter blocker work order has wrong result_type")
    if blocker_work_order.get("status") != "six_experiment_work_order_ready":
        return fail("first real converter blocker work order has unexpected status")
    if blocker_work_order.get("rehearsal_strict_issue_count") != 15:
        return fail("first real converter blocker work order should record 15 rehearsal issues")
    if blocker_work_order.get("work_item_count") != 6:
        return fail("first real converter blocker work order should have six work items")
    blocker_names = {item.get("blocker") for item in blocker_work_order.get("work_items", []) if isinstance(item, dict)}
    if blocker_names != {"converter_object", "adc_energy", "conversion_latency", "noise", "area", "break_even"}:
        return fail("first real converter blocker work order has wrong blocker set")
    blocker_page = (ROOT / "site" / "research" / "first-real-converter-blocker-work-order.html").read_text(encoding="utf-8")
    for marker in ["First Real Converter Blocker Work Order", "six_experiment_work_order_ready", "work item count: <code>6</code>", "B1. converter_object", "B2. adc_energy", "B3. conversion_latency", "B4. noise", "B5. area", "B6. break_even", "output artifact", "does not write accepted post-layout evidence"]:
        if marker not in blocker_page:
            return fail(f"site/research/first-real-converter-blocker-work-order.html missing marker {marker!r}")

    physical_object_assembly = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-physical-object-assembly.json").read_text(encoding="utf-8"))
    if physical_object_assembly.get("result_type") != "first_real_converter_physical_object_assembly":
        return fail("first real converter physical object assembly has wrong result_type")
    if physical_object_assembly.get("status") != "b1_physical_object_assembled_from_starter_extractions_not_accepted_evidence":
        return fail("first real converter physical object assembly has unexpected status")
    assembly_netlist = ROOT / str(physical_object_assembly.get("netlist", ""))
    if not assembly_netlist.exists():
        return fail("first real converter physical object assembly netlist is missing")
    assembly_text = assembly_netlist.read_text(encoding="utf-8")
    for marker in ["row_dac", "sar_readout", "shared_mux", "references", "sample_path", ".subckt aimc_readout_candidate_001"]:
        if marker not in assembly_text:
            return fail(f"first real converter physical object assembly netlist missing marker {marker!r}")
    assembly_page = (ROOT / "site" / "research" / "first-real-converter-physical-object-assembly.html").read_text(encoding="utf-8")
    for marker in ["First Real Converter Physical Object Assembly", "b1_physical_object_assembled_from_starter_extractions_not_accepted_evidence", "The first converter blocker asks for one object", "row_dac_10b_layout_smoke.spice", "does not prove energy, latency, noise, area"]:
        if marker not in assembly_page:
            return fail(f"site/research/first-real-converter-physical-object-assembly.html missing marker {marker!r}")

    physical_object_audit = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-physical-object-audit.json").read_text(encoding="utf-8"))
    if physical_object_audit.get("result_type") != "first_real_converter_physical_object_audit":
        return fail("first real converter physical object audit has wrong result_type")
    if physical_object_audit.get("status") != "b1_physical_object_ready_not_accepted_evidence":
        return fail("first real converter physical object audit should record B1 ready")
    if physical_object_audit.get("ready_for_b1") is not True:
        return fail("first real converter physical object audit should claim B1 is ready")
    if physical_object_audit.get("expected_extracted_netlist_exists") is not True:
        return fail("first real converter physical object audit should see the expected netlist")
    if physical_object_audit.get("candidate_file_count", 0) < 2:
        return fail("first real converter physical object audit should see current candidate files")
    for part in ["row_dac", "sar_readout", "shared_mux", "references", "sample_path"]:
        if part not in physical_object_audit.get("present_parts", []):
            return fail(f"first real converter physical object audit should mark {part} present")
    physical_object_page = (ROOT / "site" / "research" / "first-real-converter-physical-object-audit.html").read_text(encoding="utf-8")
    for marker in ["First Real Converter Physical Object Audit", "b1_physical_object_ready_not_accepted_evidence", "ready for B1: <code>True</code>", "A converter claim starts with an object", "expected extracted netlist", "does not measure energy, latency, noise, or area", "does not write accepted post-layout evidence"]:
        if marker not in physical_object_page:
            return fail(f"site/research/first-real-converter-physical-object-audit.html missing marker {marker!r}")

    energy_candidate = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-energy-candidate.json").read_text(encoding="utf-8"))
    if energy_candidate.get("result_type") != "first_real_converter_energy_candidate":
        return fail("first real converter energy candidate has wrong result_type")
    if energy_candidate.get("status") != "b2_energy_candidate_written_not_strict_extracted_energy":
        return fail("first real converter energy candidate has unexpected status")
    if energy_candidate.get("strict_payload_ready") is not False:
        return fail("first real converter energy candidate must not claim strict readiness")
    for field in ["adc_energy_per_conversion", "dac_energy_per_row_drive", "mux_energy_per_conversion", "total_energy_per_conversion"]:
        value = energy_candidate.get(field)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
            return fail(f"first real converter energy candidate has invalid {field}")
    measurement_path = ROOT / str(energy_candidate.get("measurement_artifact", ""))
    if not measurement_path.exists():
        return fail("first real converter energy candidate measurement artifact is missing")
    measurement = json.loads(measurement_path.read_text(encoding="utf-8"))
    if measurement.get("energy_level") != "simple_load_spice_tied_to_named_candidate_not_extracted_power":
        return fail("first real converter energy candidate measurement should remain simple-load level")
    if measurement.get("strict_payload_ready") is not False:
        return fail("first real converter energy measurement must not claim strict readiness")
    energy_page = (ROOT / "site" / "research" / "first-real-converter-energy-candidate.html").read_text(encoding="utf-8")
    for marker in ["First Real Converter Energy Candidate", "b2_energy_candidate_written_not_strict_extracted_energy", "Energy is charge moved through a voltage", "strict payload ready: <code>False</code>", "does not replace extracted converter energy", "does not write accepted post-layout evidence"]:
        if marker not in energy_page:
            return fail(f"site/research/first-real-converter-energy-candidate.html missing marker {marker!r}")

    latency_candidate = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-latency-candidate.json").read_text(encoding="utf-8"))
    if latency_candidate.get("result_type") != "first_real_converter_latency_candidate":
        return fail("first real converter latency candidate has wrong result_type")
    if latency_candidate.get("status") != "b3_latency_candidate_written_not_strict_extracted_timing":
        return fail("first real converter latency candidate has unexpected status")
    if latency_candidate.get("strict_payload_ready") is not False:
        return fail("first real converter latency candidate must not claim strict readiness")
    if latency_candidate.get("settling_time_ns") != 4.0:
        return fail("first real converter latency candidate should use 4 ns settling")
    if latency_candidate.get("conversion_time_ns") != 12.0:
        return fail("first real converter latency candidate should use 12 ns conversion")
    if latency_candidate.get("total_before_digital_value_ns") != 16.0:
        return fail("first real converter latency candidate should total 16 ns")
    latency_measurement_path = ROOT / str(latency_candidate.get("measurement_artifact", ""))
    if not latency_measurement_path.exists():
        return fail("first real converter latency candidate measurement artifact is missing")
    latency_measurement = json.loads(latency_measurement_path.read_text(encoding="utf-8"))
    if latency_measurement.get("latency_level") != "simple_load_spice_tied_to_named_candidate_not_extracted_timing":
        return fail("first real converter latency candidate measurement should remain simple-load level")
    latency_page = (ROOT / "site" / "research" / "first-real-converter-latency-candidate.html").read_text(encoding="utf-8")
    for marker in ["First Real Converter Latency Candidate", "b3_latency_candidate_written_not_strict_extracted_timing", "Latency is the wait", "settling time: <code>4.0</code> ns", "conversion time: <code>12.0</code> ns", "total time before digital value: <code>16.0</code> ns", "does not replace extracted converter timing", "does not write accepted post-layout evidence"]:
        if marker not in latency_page:
            return fail(f"site/research/first-real-converter-latency-candidate.html missing marker {marker!r}")

    noise_candidate = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-noise-candidate.json").read_text(encoding="utf-8"))
    if noise_candidate.get("result_type") != "first_real_converter_noise_candidate":
        return fail("first real converter noise candidate has wrong result_type")
    if noise_candidate.get("status") != "b4_noise_candidate_written_not_strict_extracted_noise":
        return fail("first real converter noise candidate has unexpected status")
    if noise_candidate.get("strict_payload_ready") is not False:
        return fail("first real converter noise candidate must not claim strict readiness")
    if noise_candidate.get("output_noise_rms") != 0.000851121:
        return fail("first real converter noise candidate should use the behavioral output noise")
    if noise_candidate.get("input_referred_noise") != 0.000531011:
        return fail("first real converter noise candidate should use the behavioral input-referred noise")
    if noise_candidate.get("output_noise_budget") != 0.004:
        return fail("first real converter noise candidate should use the 0.004 output-noise budget")
    if noise_candidate.get("meets_output_noise_budget") is not True:
        return fail("first real converter noise candidate should remain inside the output-noise budget")
    noise_measurement_path = ROOT / str(noise_candidate.get("measurement_artifact", ""))
    if not noise_measurement_path.exists():
        return fail("first real converter noise candidate measurement artifact is missing")
    noise_measurement = json.loads(noise_measurement_path.read_text(encoding="utf-8"))
    if noise_measurement.get("noise_level") != "behavioral_circuit_estimate_tied_to_named_candidate_not_extracted_noise":
        return fail("first real converter noise candidate measurement should remain behavioral level")
    noise_page = (ROOT / "site" / "research" / "first-real-converter-noise-candidate.html").read_text(encoding="utf-8")
    for marker in ["First Real Converter Noise Candidate", "b4_noise_candidate_written_not_strict_extracted_noise", "Noise is uncertainty", "output noise RMS: <code>0.000851121</code>", "input-referred noise: <code>0.000531011</code>", "meets output noise budget: <code>True</code>", "does not replace extracted converter noise", "does not write accepted post-layout evidence"]:
        if marker not in noise_page:
            return fail(f"site/research/first-real-converter-noise-candidate.html missing marker {marker!r}")

    area_candidate = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-area-candidate.json").read_text(encoding="utf-8"))
    if area_candidate.get("result_type") != "first_real_converter_area_candidate":
        return fail("first real converter area candidate has wrong result_type")
    if area_candidate.get("status") != "b5_area_candidate_written_not_strict_extracted_area":
        return fail("first real converter area candidate has unexpected status")
    if area_candidate.get("strict_payload_ready") is not False:
        return fail("first real converter area candidate must not claim strict readiness")
    if area_candidate.get("adc_area_um2") != 1200.0:
        return fail("first real converter area candidate should use the starter ADC area")
    if area_candidate.get("dac_area_um2") != 700.0:
        return fail("first real converter area candidate should use the starter DAC area")
    if area_candidate.get("total_readout_area_um2") != 1900.0:
        return fail("first real converter area candidate should total 1900 um2")
    area_measurement_path = ROOT / str(area_candidate.get("measurement_artifact", ""))
    if not area_measurement_path.exists():
        return fail("first real converter area candidate measurement artifact is missing")
    area_measurement = json.loads(area_measurement_path.read_text(encoding="utf-8"))
    if area_measurement.get("area_level") != "starter_layout_boundary_estimate_tied_to_named_candidate_not_extracted_signoff_area":
        return fail("first real converter area candidate measurement should remain starter boundary level")
    area_page = (ROOT / "site" / "research" / "first-real-converter-area-candidate.html").read_text(encoding="utf-8")
    for marker in ["First Real Converter Area Candidate", "b5_area_candidate_written_not_strict_extracted_area", "Area is chip space", "ADC area: <code>1200.0</code> um2", "DAC area: <code>700.0</code> um2", "total readout area: <code>1900.0</code> um2", "does not replace extracted signoff area", "does not write accepted post-layout evidence"]:
        if marker not in area_page:
            return fail(f"site/research/first-real-converter-area-candidate.html missing marker {marker!r}")

    break_even_candidate = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-break-even-candidate.json").read_text(encoding="utf-8"))
    if break_even_candidate.get("result_type") != "first_real_converter_break_even_candidate":
        return fail("first real converter break-even candidate has wrong result_type")
    if break_even_candidate.get("status") != "b6_break_even_candidate_written_not_strict_replacement":
        return fail("first real converter break-even candidate has unexpected status")
    if break_even_candidate.get("claim_ready_to_replace_break_even") is not False:
        return fail("first real converter break-even candidate must not claim replacement readiness")
    if break_even_candidate.get("replacement_decision") != "candidate_would_replace_under_sharing_rule":
        return fail("first real converter break-even candidate should record the candidate sharing decision")
    rerun_path = ROOT / str(break_even_candidate.get("rerun_artifact", ""))
    if not rerun_path.exists():
        return fail("first real converter break-even rerun artifact is missing")
    rerun = json.loads(rerun_path.read_text(encoding="utf-8"))
    if rerun.get("rerun_level") != "candidate_values_mixed_evidence_levels_not_strict_extracted_rerun":
        return fail("first real converter break-even rerun should remain candidate level")
    if rerun.get("summary", {}).get("claim_ready_to_replace_break_even") is not False:
        return fail("first real converter break-even rerun must not claim replacement readiness")
    if len(rerun.get("scenarios", [])) != 2:
        return fail("first real converter break-even rerun should include two scenarios")
    break_even_page = (ROOT / "site" / "research" / "first-real-converter-break-even-candidate.html").read_text(encoding="utf-8")
    for marker in ["First Real Converter Break-Even Candidate", "b6_break_even_candidate_written_not_strict_replacement", "Break-even asks whether the analog path", "candidate_would_replace_under_sharing_rule", "claim ready to replace break-even: <code>False</code>", "does not use strict extracted energy, latency, noise, and area", "does not write accepted post-layout evidence"]:
        if marker not in break_even_page:
            return fail(f"site/research/first-real-converter-break-even-candidate.html missing marker {marker!r}")

    loop_readiness = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-candidate-loop-strict-readiness.json").read_text(encoding="utf-8"))
    if loop_readiness.get("result_type") != "first_real_converter_candidate_loop_strict_readiness":
        return fail("first real converter candidate loop strict readiness has wrong result_type")
    if loop_readiness.get("status") != "candidate_loop_complete_not_strict_accepted_evidence":
        return fail("first real converter candidate loop strict readiness has unexpected status")
    if loop_readiness.get("candidate_loop_complete") is not True:
        return fail("first real converter candidate loop should be complete")
    if loop_readiness.get("same_candidate") is not True:
        return fail("first real converter candidate loop should use one candidate")
    if loop_readiness.get("same_run") is not False:
        return fail("first real converter candidate loop should not claim one strict run")
    if loop_readiness.get("strict_ready") is not False:
        return fail("first real converter candidate loop must not claim strict readiness")
    if loop_readiness.get("accepted_post_layout_ready") is not False:
        return fail("first real converter candidate loop must not claim accepted readiness")
    if len(loop_readiness.get("strict_blockers", [])) < 5:
        return fail("first real converter candidate loop should list strict blockers")
    loop_page = (ROOT / "site" / "research" / "first-real-converter-candidate-loop-strict-readiness.html").read_text(encoding="utf-8")
    for marker in ["First Real Converter Candidate Loop Strict Readiness", "candidate_loop_complete_not_strict_accepted_evidence", "candidate loop complete: <code>True</code>", "same run: <code>False</code>", "strict ready: <code>False</code>", "An end-to-end candidate loop is not the same as accepted evidence", "does not fill the canonical strict payload", "does not write accepted post-layout evidence"]:
        if marker not in loop_page:
            return fail(f"site/research/first-real-converter-candidate-loop-strict-readiness.html missing marker {marker!r}")

    same_candidate_rc = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-same-candidate-extracted-rc.json").read_text(encoding="utf-8"))
    if same_candidate_rc.get("result_type") != "first_real_converter_same_candidate_extracted_rc":
        return fail("first real converter same-candidate extracted RC has wrong result_type")
    if same_candidate_rc.get("status") != "same_candidate_extracted_rc_passed_not_strict_accepted_evidence":
        return fail("first real converter same-candidate extracted RC has unexpected status")
    if same_candidate_rc.get("candidate_id") != "aimc_readout_candidate_001":
        return fail("first real converter same-candidate extracted RC has wrong candidate id")
    if same_candidate_rc.get("uses_assembled_candidate_netlist") is not True:
        return fail("first real converter same-candidate extracted RC should use the assembled candidate netlist")
    if same_candidate_rc.get("uses_transistor_converter_behavior") is not False:
        return fail("first real converter same-candidate extracted RC must not claim transistor converter behavior")
    if same_candidate_rc.get("same_run_strict_payload_ready") is not False:
        return fail("first real converter same-candidate extracted RC must not claim strict payload readiness")
    if same_candidate_rc.get("accepted_post_layout_written") is not False:
        return fail("first real converter same-candidate extracted RC must not write accepted evidence")
    if same_candidate_rc.get("ngspice_returncode") != 0:
        return fail("first real converter same-candidate extracted RC ngspice run failed")
    if same_candidate_rc.get("row_final_v", 0) <= 1.7:
        return fail("first real converter same-candidate extracted RC row did not settle high enough")
    if same_candidate_rc.get("sense_delta_v", 1) >= 0.01:
        return fail("first real converter same-candidate extracted RC sense node did not settle close enough")
    if len(same_candidate_rc.get("strict_blockers", [])) < 3:
        return fail("first real converter same-candidate extracted RC should list strict blockers")
    for path_field in ["source_netlist", "generated_deck", "csv"]:
        path_value = same_candidate_rc.get(path_field)
        if not path_value or not (ROOT / str(path_value)).exists():
            return fail(f"first real converter same-candidate extracted RC missing {path_field}")
    same_candidate_rc_page = (ROOT / "site" / "research" / "first-real-converter-same-candidate-extracted-rc.html").read_text(encoding="utf-8")
    for marker in ["First Real Converter Same-Candidate Extracted RC", "same_candidate_extracted_rc_passed_not_strict_accepted_evidence", "candidate id: <code>aimc_readout_candidate_001</code>", "same-run strict payload ready: <code>False</code>", "accepted post-layout written: <code>False</code>", "one named extracted object", "charge movement through extracted capacitance", "It is still not enough to accept the converter", "accepted post-layout converter evidence"]:
        if marker not in same_candidate_rc_page:
            return fail(f"site/research/first-real-converter-same-candidate-extracted-rc.html missing marker {marker!r}")

    frontend_bridge = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-frontend-to-input-stage-proxy.json").read_text(encoding="utf-8"))
    if frontend_bridge.get("result_type") != "first_real_converter_frontend_to_input_stage_proxy":
        return fail("first real converter frontend-to-input-stage proxy has wrong result_type")
    if frontend_bridge.get("status") not in {"frontend_to_input_stage_proxy_passed_not_full_comparator_or_strict_evidence", "frontend_to_input_stage_proxy_timed_out_not_strict_evidence"}:
        return fail("first real converter frontend-to-input-stage proxy has unexpected status")
    if frontend_bridge.get("candidate_id") != "aimc_readout_candidate_001":
        return fail("first real converter frontend-to-input-stage proxy has wrong candidate id")
    if frontend_bridge.get("source_frontend_evidence") != "evidence/aimc-simulator-adapters/sky130-ultra-sense-frontend-candidate.json":
        return fail("first real converter frontend-to-input-stage proxy should use ultra frontend evidence")
    if frontend_bridge.get("uses_measured_extracted_frontend_sense_delta") is not True:
        return fail("first real converter frontend-to-input-stage proxy should use measured frontend sense delta")
    if frontend_bridge.get("uses_sky130_transistor_input_stage") is not True:
        return fail("first real converter frontend-to-input-stage proxy should use Sky130 transistor input stage")
    if frontend_bridge.get("uses_clocked_latch") is not False or frontend_bridge.get("uses_sar_loop") is not False:
        return fail("first real converter frontend-to-input-stage proxy must not claim latch or SAR loop")
    if frontend_bridge.get("same_run_strict_payload_ready") is not False:
        return fail("first real converter frontend-to-input-stage proxy must not claim strict payload readiness")
    if frontend_bridge.get("accepted_post_layout_written") is not False:
        return fail("first real converter frontend-to-input-stage proxy must not write accepted evidence")
    if frontend_bridge.get("case_count") != 4:
        return fail("first real converter frontend-to-input-stage proxy should test four frontend rows")
    if frontend_bridge.get("floor_case_count") != 4:
        return fail("first real converter frontend-to-input-stage proxy should record that all raw frontend rows need the active-stage floor")
    if len(frontend_bridge.get("strict_blockers", [])) < 3:
        return fail("first real converter frontend-to-input-stage proxy should list strict blockers")
    for path_field in ["generated_deck", "csv"]:
        path_value = frontend_bridge.get(path_field)
        if not path_value or not (ROOT / str(path_value)).exists():
            return fail(f"first real converter frontend-to-input-stage proxy missing {path_field}")
    frontend_bridge_page = (ROOT / "site" / "research" / "first-real-converter-frontend-to-input-stage-proxy.html").read_text(encoding="utf-8")
    for marker in ["First Real Converter Frontend To Input-Stage Proxy", "frontend_to_input_stage_proxy_timed_out_not_strict_evidence", "candidate id: <code>aimc_readout_candidate_001</code>", "timed-out case count: <code>4</code>", "active-stage input floor V", "same-run strict payload ready: <code>False</code>", "accepted post-layout written: <code>False</code>", "active block pays power", "This is a bridge, not an accepted converter", "does not prove a full comparator"]:
        if marker not in frontend_bridge_page:
            return fail(f"site/research/first-real-converter-frontend-to-input-stage-proxy.html missing marker {marker!r}")

    active_handoff = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-frontend-active-handoff-estimate.json").read_text(encoding="utf-8"))
    if active_handoff.get("result_type") != "first_real_converter_frontend_active_handoff_estimate":
        return fail("first real converter frontend active handoff estimate has wrong result_type")
    if active_handoff.get("status") != "frontend_active_handoff_estimate_ready_not_same_deck_or_strict_evidence":
        return fail("first real converter frontend active handoff estimate has unexpected status")
    if active_handoff.get("candidate_id") != "aimc_readout_candidate_001":
        return fail("first real converter frontend active handoff estimate has wrong candidate id")
    if active_handoff.get("source_frontend_evidence") != "evidence/aimc-simulator-adapters/sky130-ultra-sense-frontend-candidate.json":
        return fail("first real converter frontend active handoff estimate should use ultra frontend evidence")
    if active_handoff.get("source_input_stage_evidence") != "evidence/aimc-simulator-adapters/sky130-comparator-input-stage-ngspice.json":
        return fail("first real converter frontend active handoff estimate should use input-stage evidence")
    if active_handoff.get("minimum_measured_input_stage_gain_v_per_v", 0) <= 9.0:
        return fail("first real converter frontend active handoff estimate should preserve measured input-stage gain")
    if active_handoff.get("minimum_estimated_output_diff_v", 0) <= 0.0005:
        return fail("first real converter frontend active handoff estimate should produce millivolt-scale output")
    if active_handoff.get("estimated_polarity_pass_count") != active_handoff.get("case_count"):
        return fail("first real converter frontend active handoff estimate should preserve polarity in all cases")
    if active_handoff.get("uses_same_deck_simulation") is not False or active_handoff.get("uses_same_extracted_layout_netlist") is not False:
        return fail("first real converter frontend active handoff estimate must not claim same-deck or same-layout evidence")
    if active_handoff.get("same_run_strict_payload_ready") is not False:
        return fail("first real converter frontend active handoff estimate must not claim strict payload readiness")
    if active_handoff.get("accepted_post_layout_written") is not False:
        return fail("first real converter frontend active handoff estimate must not write accepted evidence")
    if len(active_handoff.get("strict_blockers", [])) < 3:
        return fail("first real converter frontend active handoff estimate should list strict blockers")
    path_value = active_handoff.get("csv")
    if not path_value or not (ROOT / str(path_value)).exists():
        return fail("first real converter frontend active handoff estimate missing csv")
    active_handoff_page = (ROOT / "site" / "research" / "first-real-converter-frontend-active-handoff-estimate.html").read_text(encoding="utf-8")
    for marker in ["First Real Converter Frontend Active Handoff Estimate", "frontend_active_handoff_estimate_ready_not_same_deck_or_strict_evidence", "minimum measured input-stage gain V/V", "minimum estimated output diff V", "uses same-deck simulation: <code>False</code>", "uses same extracted layout netlist: <code>False</code>", "about 0.62 millivolt", "not a new circuit simulation", "does not prove same-deck active handoff"]:
        if marker not in active_handoff_page:
            return fail(f"site/research/first-real-converter-frontend-active-handoff-estimate.html missing marker {marker!r}")

    combined_work_order = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "first-real-converter-combined-active-handoff-work-order.json").read_text(encoding="utf-8"))
    if combined_work_order.get("result_type") != "first_real_converter_combined_active_handoff_work_order":
        return fail("first real converter combined active handoff work order has wrong result_type")
    if combined_work_order.get("status") != "combined_active_handoff_work_order_ready":
        return fail("first real converter combined active handoff work order has unexpected status")
    if combined_work_order.get("candidate_id") != "aimc_readout_candidate_001":
        return fail("first real converter combined active handoff work order has wrong candidate id")
    if combined_work_order.get("accepted_post_layout_written") is not False:
        return fail("first real converter combined active handoff work order must not write accepted evidence")
    if combined_work_order.get("same_run_strict_payload_ready") is not False:
        return fail("first real converter combined active handoff work order must not claim strict payload readiness")
    active_object = combined_work_order.get("new_physical_object") if isinstance(combined_work_order.get("new_physical_object"), dict) else {}
    if active_object.get("name") != "sky130_frontend_input_stage_handoff_candidate":
        return fail("first real converter combined active handoff work order should name the next physical object")
    if len(active_object.get("minimum_contents", [])) < 5:
        return fail("first real converter combined active handoff work order should define minimum contents")
    acceptance_tests = combined_work_order.get("acceptance_tests") if isinstance(combined_work_order.get("acceptance_tests"), list) else []
    if len(acceptance_tests) != 5:
        return fail("first real converter combined active handoff work order should define five acceptance tests")
    acceptance_names = {item.get("name") for item in acceptance_tests if isinstance(item, dict)}
    for name in ["A1. bounded simulator run", "A2. sign handoff", "A3. active output margin", "A4. loading check", "A5. claim boundary"]:
        if name not in acceptance_names:
            return fail(f"first real converter combined active handoff work order missing acceptance test {name!r}")
    outputs = combined_work_order.get("expected_outputs") if isinstance(combined_work_order.get("expected_outputs"), list) else []
    if len(outputs) != 5:
        return fail("first real converter combined active handoff work order should name five expected outputs")
    for fragment in ["sky130_frontend_input_stage_handoff_candidate.sp", "sky130-frontend-input-stage-handoff-candidate.json", "docs/research/sky130-frontend-input-stage-handoff-candidate.md"]:
        if not any(fragment in str(item) for item in outputs):
            return fail(f"first real converter combined active handoff work order missing expected output fragment {fragment!r}")
    why_next = combined_work_order.get("why_this_is_next") if isinstance(combined_work_order.get("why_this_is_next"), dict) else {}
    if why_next.get("direct_proxy_status") != "frontend_to_input_stage_proxy_timed_out_not_strict_evidence":
        return fail("first real converter combined active handoff work order should consume the timed-out direct proxy")
    if why_next.get("estimated_active_output_diff_v", 0) <= 0.0005:
        return fail("first real converter combined active handoff work order should carry the active handoff estimate")
    combined_work_order_page = (ROOT / "site" / "research" / "first-real-converter-combined-active-handoff-work-order.html").read_text(encoding="utf-8")
    for marker in ["First Real Converter Combined Active Handoff Work Order", "combined_active_handoff_work_order_ready", "sky130_frontend_input_stage_handoff_candidate", "A1. bounded simulator run", "A2. sign handoff", "A3. active output margin", "A4. loading check", "A5. claim boundary", "one bounded same-deck handoff candidate", "does not prove the combined active handoff"]:
        if marker not in combined_work_order_page:
            return fail(f"site/research/first-real-converter-combined-active-handoff-work-order.html missing marker {marker!r}")

    handoff_candidate = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-frontend-input-stage-handoff-candidate.json").read_text(encoding="utf-8"))
    if handoff_candidate.get("result_type") != "sky130_frontend_input_stage_handoff_candidate":
        return fail("Sky130 frontend input-stage handoff candidate has wrong result_type")
    if handoff_candidate.get("status") != "active_macro_handoff_passed_not_sky130_transistor_or_strict_evidence":
        return fail("Sky130 frontend input-stage handoff candidate has unexpected status")
    if handoff_candidate.get("candidate_id") != "aimc_readout_candidate_001":
        return fail("Sky130 frontend input-stage handoff candidate has wrong candidate id")
    if handoff_candidate.get("handoff_candidate") != "sky130_frontend_input_stage_handoff_candidate":
        return fail("Sky130 frontend input-stage handoff candidate should name the handoff candidate")
    if handoff_candidate.get("uses_extracted_frontend_netlist") is not True:
        return fail("Sky130 frontend input-stage handoff candidate should use extracted frontend netlist")
    if handoff_candidate.get("uses_active_gain_macro") is not True:
        return fail("Sky130 frontend input-stage handoff candidate should use active gain macro")
    if handoff_candidate.get("uses_sky130_transistor_input_stage") is not False:
        return fail("Sky130 frontend input-stage handoff candidate must not claim transistor input-stage proof")
    if handoff_candidate.get("uses_clocked_latch") is not False or handoff_candidate.get("uses_sar_loop") is not False:
        return fail("Sky130 frontend input-stage handoff candidate must not claim latch or SAR proof")
    if handoff_candidate.get("case_count") != 4 or handoff_candidate.get("measured_case_count") != 4:
        return fail("Sky130 frontend input-stage handoff candidate should measure four cases")
    if handoff_candidate.get("sign_pass_count") != 4:
        return fail("Sky130 frontend input-stage handoff candidate should preserve sign in four cases")
    if handoff_candidate.get("active_output_margin_pass_count") != 4:
        return fail("Sky130 frontend input-stage handoff candidate should pass output margin in four cases")
    if handoff_candidate.get("minimum_output_diff_v", 0) <= 0.0005:
        return fail("Sky130 frontend input-stage handoff candidate should clear output margin")
    if handoff_candidate.get("loading_pass") is not True:
        return fail("Sky130 frontend input-stage handoff candidate should pass loading check")
    tests = handoff_candidate.get("acceptance_tests") if isinstance(handoff_candidate.get("acceptance_tests"), dict) else {}
    for name in ["A1_bounded_simulator_run", "A2_sign_handoff", "A3_active_output_margin", "A4_loading_check", "A5_claim_boundary"]:
        if tests.get(name) is not True:
            return fail(f"Sky130 frontend input-stage handoff candidate failed acceptance test {name}")
    if handoff_candidate.get("same_run_strict_payload_ready") is not False:
        return fail("Sky130 frontend input-stage handoff candidate must not claim strict payload readiness")
    if handoff_candidate.get("accepted_post_layout_written") is not False:
        return fail("Sky130 frontend input-stage handoff candidate must not write accepted evidence")
    for path_field in ["source_frontend_netlist", "generated_deck", "csv"]:
        path_value = handoff_candidate.get(path_field)
        if not path_value or not (ROOT / str(path_value)).exists():
            return fail(f"Sky130 frontend input-stage handoff candidate missing {path_field}")
    handoff_candidate_page = (ROOT / "site" / "research" / "sky130-frontend-input-stage-handoff-candidate.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Frontend Input-Stage Handoff Candidate", "active_macro_handoff_passed_not_sky130_transistor_or_strict_evidence", "uses extracted frontend netlist: <code>True</code>", "uses active gain macro: <code>True</code>", "uses Sky130 transistor input stage: <code>False</code>", "sign pass count: <code>4</code>", "active output margin pass count: <code>4</code>", "A1_bounded_simulator_run", "A5_claim_boundary", "same-deck handoff at the active-macro level", "does not prove Sky130 transistor input-stage handoff"]:
        if marker not in handoff_candidate_page:
            return fail(f"site/research/sky130-frontend-input-stage-handoff-candidate.html missing marker {marker!r}")

    transistor_handoff = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-frontend-transistor-input-stage-handoff-candidate.json").read_text(encoding="utf-8"))
    if transistor_handoff.get("result_type") != "sky130_frontend_transistor_input_stage_handoff_candidate":
        return fail("Sky130 frontend transistor input-stage handoff candidate has wrong result_type")
    if transistor_handoff.get("status") != "transistor_handoff_failed_or_timed_out":
        return fail("Sky130 frontend transistor input-stage handoff candidate should record the current bounded failure")
    if transistor_handoff.get("candidate_id") != "aimc_readout_candidate_001":
        return fail("Sky130 frontend transistor input-stage handoff candidate has wrong candidate id")
    if transistor_handoff.get("handoff_candidate") != "sky130_frontend_transistor_input_stage_handoff_candidate":
        return fail("Sky130 frontend transistor input-stage handoff candidate should name the transistor handoff candidate")
    if transistor_handoff.get("uses_extracted_frontend_netlist") is not True:
        return fail("Sky130 frontend transistor input-stage handoff candidate should use extracted frontend netlist")
    if transistor_handoff.get("uses_active_gain_macro") is not False:
        return fail("Sky130 frontend transistor input-stage handoff candidate must not use active gain macro")
    if transistor_handoff.get("uses_sky130_transistor_input_stage") is not True:
        return fail("Sky130 frontend transistor input-stage handoff candidate should use Sky130 transistor input stage")
    if transistor_handoff.get("uses_clocked_latch") is not False or transistor_handoff.get("uses_sar_loop") is not False:
        return fail("Sky130 frontend transistor input-stage handoff candidate must not claim latch or SAR proof")
    if transistor_handoff.get("case_count") != 4:
        return fail("Sky130 frontend transistor input-stage handoff candidate should test four cases")
    if transistor_handoff.get("measured_case_count") != 0:
        return fail("Sky130 frontend transistor input-stage handoff candidate should currently have zero measured passing cases")
    if transistor_handoff.get("sign_pass_count") != 0 or transistor_handoff.get("active_output_margin_pass_count") != 0:
        return fail("Sky130 frontend transistor input-stage handoff candidate should not pass sign or margin yet")
    tests = transistor_handoff.get("acceptance_tests") if isinstance(transistor_handoff.get("acceptance_tests"), dict) else {}
    if tests.get("T5_claim_boundary") is not True:
        return fail("Sky130 frontend transistor input-stage handoff candidate should preserve claim boundary")
    for name in ["T1_bounded_simulator_run", "T2_sign_handoff", "T3_active_output_margin", "T4_loading_check"]:
        if tests.get(name) is not False:
            return fail(f"Sky130 frontend transistor input-stage handoff candidate should fail acceptance test {name}")
    if transistor_handoff.get("same_run_strict_payload_ready") is not False:
        return fail("Sky130 frontend transistor input-stage handoff candidate must not claim strict payload readiness")
    if transistor_handoff.get("accepted_post_layout_written") is not False:
        return fail("Sky130 frontend transistor input-stage handoff candidate must not write accepted evidence")
    for path_field in ["source_frontend_netlist", "generated_deck", "csv"]:
        path_value = transistor_handoff.get(path_field)
        if not path_value or not (ROOT / str(path_value)).exists():
            return fail(f"Sky130 frontend transistor input-stage handoff candidate missing {path_field}")
    transistor_handoff_page = (ROOT / "site" / "research" / "sky130-frontend-transistor-input-stage-handoff-candidate.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Frontend Transistor Input-Stage Handoff Candidate", "transistor_handoff_failed_or_timed_out", "uses active gain macro: <code>False</code>", "uses Sky130 transistor input stage: <code>True</code>", "measured case count: <code>0</code>", "sign pass count: <code>0</code>", "T1_bounded_simulator_run: <code>False</code>", "T5_claim_boundary: <code>True</code>", "replaces that macro with real Sky130 nfet input devices", "does not prove clocked latch behavior"]:
        if marker not in transistor_handoff_page:
            return fail(f"site/research/sky130-frontend-transistor-input-stage-handoff-candidate.html missing marker {marker!r}")

    simulator_status_page = (ROOT / "site" / "research" / "current-simulator-adapter-status.html").read_text(encoding="utf-8")
    for marker in ["AIHWKIT: available", "CrossSim: available", "broad chip claims are not upgraded", "Refused Claim", "Next Handoff"]:
        if marker not in simulator_status_page:
            return fail(f"site/research/current-simulator-adapter-status.html missing marker {marker!r}")

    simulator_status = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "simulator-adapter-status.json").read_text(encoding="utf-8"))
    if simulator_status.get("run_output_contract") != "sources/evidence/analog-simulator-adapter-output-schema.json":
        return fail("simulator adapter status does not point to the run output contract")
    planned_payloads = simulator_status.get("planned_run_payloads") if isinstance(simulator_status.get("planned_run_payloads"), dict) else {}
    if planned_payloads.get("aihwkit") != "evidence/aimc-simulator-adapters/aihwkit-analog-error-simulation.json":
        return fail("simulator adapter status missing planned AIHWKIT payload path")
    if planned_payloads.get("crosssim") != "evidence/aimc-simulator-adapters/crosssim-analog-error-simulation.json":
        return fail("simulator adapter status missing planned CrossSim payload path")
    tools = simulator_status.get("tools") if isinstance(simulator_status.get("tools"), list) else []
    for tool_name in ["aihwkit", "crosssim"]:
        tool = next((item for item in tools if isinstance(item, dict) and item.get("tool") == tool_name), None)
        if not isinstance(tool, dict) or "planned_payload" not in tool:
            return fail(f"simulator adapter status missing planned payload on {tool_name}")
        if "smoke_report" not in tool:
            return fail(f"simulator adapter status missing smoke report path on {tool_name}")
        smoke_run = tool.get("smoke_run") if isinstance(tool.get("smoke_run"), dict) else {}
        if smoke_run.get("status") not in {"skipped", "ran", "failed"}:
            return fail(f"simulator adapter status missing valid smoke-run status on {tool_name}")

    adapter_contract = json.loads((ROOT / "sources" / "evidence" / "analog-simulator-adapter-output-schema.json").read_text(encoding="utf-8"))
    for field in ["error_model", "temperature_range", "voltage_range", "accuracy_impact", "calibration_profile", "provenance"]:
        if field not in adapter_contract.get("required_top_level_fields", []):
            return fail(f"analog simulator adapter schema missing top-level field {field!r}")
    for field in ["name", "tool", "target_object", "adc_bits", "dac_bits", "final_residual_relative", "device_assumptions", "array_assumptions"]:
        if field not in adapter_contract.get("required_error_model_fields", []):
            return fail(f"analog simulator adapter schema missing error_model field {field!r}")
    for fragment in ["aihwkit", "crosssim"]:
        if fragment not in adapter_contract.get("accepted_tool_name_fragments", []):
            return fail(f"analog simulator adapter schema missing tool fragment {fragment!r}")
    contract_page = (ROOT / "site" / "research" / "analog-simulator-adapter-output-contract.html").read_text(encoding="utf-8")
    for marker in ["A simulator name is not evidence", "target object", "ADC bits", "DAC bits", "Refused Claim"]:
        if marker not in contract_page:
            return fail(f"site/research/analog-simulator-adapter-output-contract.html missing marker {marker!r}")

    simulator_to_post_layout_gap = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "simulator-to-post-layout-gap-audit.json").read_text(encoding="utf-8"))
    if simulator_to_post_layout_gap.get("result_type") != "simulator_to_post_layout_gap_audit":
        return fail("simulator-to-post-layout gap audit has wrong result_type")
    if simulator_to_post_layout_gap.get("status") != "simulator_evidence_present_post_layout_converter_evidence_missing":
        return fail("simulator-to-post-layout gap audit should record missing post-layout converter evidence")
    if simulator_to_post_layout_gap.get("simulator_payload_count", 0) < 2:
        return fail("simulator-to-post-layout gap audit should see simulator payloads")
    if simulator_to_post_layout_gap.get("post_layout_converter_ready_payload_count") != 0:
        return fail("simulator-to-post-layout gap audit should not mark simulator payloads as post-layout ready")
    missing_physical = set(simulator_to_post_layout_gap.get("post_layout_evidence_fields_not_supplied_by_simulator_payloads") if isinstance(simulator_to_post_layout_gap.get("post_layout_evidence_fields_not_supplied_by_simulator_payloads"), list) else [])
    for field in ["extracted_netlist", "parasitic_format", "adc_energy_per_conversion", "conversion_time_ns", "output_noise_rms", "adc_area_um2", "rerun_artifact", "same_run_id"]:
        if field not in missing_physical:
            return fail(f"simulator-to-post-layout gap audit missing physical field {field!r}")
    gap_page = (ROOT / "site" / "research" / "simulator-to-post-layout-gap-audit.html").read_text(encoding="utf-8")
    for marker in ["Simulator To Post-Layout Gap Audit", "simulator_evidence_present_post_layout_converter_evidence_missing", "post-layout converter ready payload count: <code>0</code>", "A simulator run and a post-layout converter run answer different questions", "extracted_netlist", "adc_energy_per_conversion", "does not treat AIHWKIT or CrossSim output residuals as extracted layout"]:
        if marker not in gap_page:
            return fail(f"site/research/simulator-to-post-layout-gap-audit.html missing marker {marker!r}")

    digital_physical_boundary = json.loads((ROOT / "evidence" / "aimc-hardware-lab" / "digital-physical-artifact-boundary.json").read_text(encoding="utf-8"))
    if digital_physical_boundary.get("result_type") != "digital_physical_artifact_boundary":
        return fail("digital physical artifact boundary has wrong result_type")
    if digital_physical_boundary.get("status") != "digital_physical_artifacts_present_analog_converter_post_layout_missing":
        return fail("digital physical artifact boundary should record analog converter post-layout as missing")
    if digital_physical_boundary.get("metrics_files_checked", 0) < 4:
        return fail("digital physical artifact boundary should check multiple OpenLane metrics files")
    if digital_physical_boundary.get("digital_physical_flow_supported_count", 0) < 3:
        return fail("digital physical artifact boundary should find supported digital physical runs")
    if digital_physical_boundary.get("cts_enabled_supported_count", 0) < 2:
        return fail("digital physical artifact boundary should find CTS-enabled supported runs")
    if digital_physical_boundary.get("analog_converter_post_layout_supported") is not False:
        return fail("digital physical artifact boundary must not support analog converter post-layout")
    physical_page = (ROOT / "site" / "research" / "digital-physical-artifact-boundary.html").read_text(encoding="utf-8")
    for marker in ["Digital Physical Artifact Boundary", "digital_physical_artifacts_present_analog_converter_post_layout_missing", "analog converter post-layout supported: <code>False</code>", "A routed digital controller and an extracted analog converter are different physical objects", "does not claim analog converter layout"]:
        if marker not in physical_page:
            return fail(f"site/research/digital-physical-artifact-boundary.html missing marker {marker!r}")

    analog_layout_work_order = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "analog-converter-layout-work-order.json").read_text(encoding="utf-8"))
    if analog_layout_work_order.get("result_type") != "analog_converter_layout_work_order":
        return fail("analog converter layout work order has wrong result_type")
    if analog_layout_work_order.get("status") != "layout_work_order_ready_waiting_for_converter_layout":
        return fail("analog converter layout work order should wait for converter layout")
    if analog_layout_work_order.get("all_starting_spice_decks_exist") is not True:
        return fail("analog converter layout work order should find all starting SPICE decks")
    if analog_layout_work_order.get("deliverable_count") != 5:
        return fail("analog converter layout work order should name five deliverables")
    deliverable_names = {item.get("name") for item in analog_layout_work_order.get("deliverables", []) if isinstance(item, dict)}
    for name in ["row_dac_layout", "sar_readout_layout", "shared_mux_layout", "converter_macro_area", "same_run_break_even_rerun"]:
        if name not in deliverable_names:
            return fail(f"analog converter layout work order missing deliverable {name!r}")
    work_order_page = (ROOT / "site" / "research" / "analog-converter-layout-work-order.html").read_text(encoding="utf-8")
    for marker in ["Analog Converter Layout Work Order", "layout_work_order_ready_waiting_for_converter_layout", "repo-local analog layout file count", "row_dac_layout", "sar_readout_layout", "same_run_break_even_rerun", "The existing SPICE decks test behavior", "does not create layout"]:
        if marker not in work_order_page:
            return fail(f"site/research/analog-converter-layout-work-order.html missing marker {marker!r}")

    analog_layout_starter = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "analog-converter-layout-starter-package.json").read_text(encoding="utf-8"))
    if analog_layout_starter.get("result_type") != "analog_converter_layout_starter_package":
        return fail("analog converter layout starter package has wrong result_type")
    if analog_layout_starter.get("status") != "starter_package_written_not_extracted_evidence":
        return fail("analog converter layout starter package should be marked as starter-only")
    if analog_layout_starter.get("starter_file_count") != 5:
        return fail("analog converter layout starter package should write five files")
    strict_waiting = analog_layout_starter.get("strict_payload_still_waiting_for_real_files")
    if strict_waiting is not True:
        # The candidate workspace may contain explicitly rejected rehearsal
        # artifacts. They are useful physical-object progress, but must not be
        # mistaken for an accepted post-layout converter payload.
        candidate_payload = ROOT / "evidence" / "aimc-simulator-adapters" / "candidate-post-layout" / "payload.json"
        if not candidate_payload.is_file():
            return fail("analog converter layout starter package has candidate counts but no candidate payload")
        candidate = json.loads(candidate_payload.read_text(encoding="utf-8"))
        if candidate.get("template_only") is not True:
            return fail("non-empty candidate converter workspace must remain template_only")
        if "replace-with" not in json.dumps(candidate):
            return fail("non-empty candidate converter workspace must retain placeholder fields")
    for path in [
        "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/README.md",
        "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/converter-layout-plan.json",
        "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/magic-extract-skeleton.tcl",
        "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/xschem-netlist-skeleton.sh",
        "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/post-layout-measurement-record.template.json",
    ]:
        if not (ROOT / path).is_file():
            return fail(f"analog converter layout starter package missing {path}")
    starter_page = (ROOT / "site" / "research" / "analog-converter-layout-starter-package.html").read_text(encoding="utf-8")
    for marker in ["Analog Converter Layout Starter Package", "starter_package_written_not_extracted_evidence", "strict payload still waiting for real files", "magic-extract-skeleton.tcl", "xschem-netlist-skeleton.sh", "A converter layout is not a better paragraph", "does not create layout"]:
        if marker not in starter_page:
            return fail(f"site/research/analog-converter-layout-starter-package.html missing marker {marker!r}")

    analog_layout_tool_readiness = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "analog-converter-layout-tool-readiness.json").read_text(encoding="utf-8"))
    if analog_layout_tool_readiness.get("result_type") != "analog_converter_layout_tool_readiness":
        return fail("analog converter layout tool readiness has wrong result_type")
    readiness_status = analog_layout_tool_readiness.get("status")
    if readiness_status not in {
        "first_starter_layout_present_candidate_evidence_still_empty",
        "starter_layout_present_candidate_rehearsal_artifacts_not_accepted",
    }:
        return fail("analog converter layout tool readiness should show starter or explicitly rejected rehearsal state")
    if analog_layout_tool_readiness.get("all_required_tools_available") is not True:
        return fail("analog converter layout tool readiness should find required tools")
    if analog_layout_tool_readiness.get("starter_files_ready") is not True:
        return fail("analog converter layout tool readiness should find starter files")
    if analog_layout_tool_readiness.get("real_layout_file_count", 0) < 4:
        return fail("analog converter layout tool readiness should find at least the four named starter layout files")
    if readiness_status == "first_starter_layout_present_candidate_evidence_still_empty":
        if analog_layout_tool_readiness.get("candidate_post_layout_still_empty") is not True:
            return fail("empty candidate readiness state must keep candidate post-layout evidence empty")
    elif analog_layout_tool_readiness.get("candidate_post_layout_rehearsal_only") is not True:
        return fail("rehearsal candidate readiness state must remain explicitly non-accepted")
    readiness_page = (ROOT / "site" / "research" / "analog-converter-layout-tool-readiness.html").read_text(encoding="utf-8")
    for marker in ["Analog Converter Layout Tool Readiness", "all required tools available", "real layout file count:", "candidate post-layout", "A ready toolchain is not the same as a ready circuit", "does not draw converter layout"]:
        if marker not in readiness_page:
            return fail(f"site/research/analog-converter-layout-tool-readiness.html missing marker {marker!r}")

    analog_pdk_readiness = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "analog-converter-pdk-readiness.json").read_text(encoding="utf-8"))
    if analog_pdk_readiness.get("result_type") != "analog_converter_pdk_readiness":
        return fail("analog converter PDK readiness has wrong result_type")
    if analog_pdk_readiness.get("status") != "sky130_pdk_ready_first_converter_starter_cell_present":
        return fail("analog converter PDK readiness should show Sky130 ready with the first starter cell present")
    if analog_pdk_readiness.get("all_required_pdk_files_present") is not True:
        return fail("analog converter PDK readiness should find required PDK files")
    if analog_pdk_readiness.get("pdk") != "sky130A":
        return fail("analog converter PDK readiness should select sky130A")
    if analog_pdk_readiness.get("workbench_has_converter_physical_cells") is not True:
        return fail("analog converter PDK readiness should find the first converter starter cell")
    pdk_file_names = {item.get("name") for item in analog_pdk_readiness.get("required_files", []) if isinstance(item, dict)}
    for name in ["magic_tech", "magic_rc", "xschem_rc", "ngspice_model_library", "ngspice_tt_corner"]:
        if name not in pdk_file_names:
            return fail(f"analog converter PDK readiness missing required file record {name!r}")
    pdk_page = (ROOT / "site" / "research" / "analog-converter-pdk-readiness.html").read_text(encoding="utf-8")
    for marker in ["Analog Converter PDK Readiness", "sky130_pdk_ready_first_converter_starter_cell_present", "all required PDK files present", "sky130A.tech", "sky130A.magicrc", "sky130.lib.spice", "A process file gives meaning to drawn shapes", "does not prove converter layout"]:
        if marker not in pdk_page:
            return fail(f"site/research/analog-converter-pdk-readiness.html missing marker {marker!r}")

    magic_smoke = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "magic-sky130-extraction-smoke.json").read_text(encoding="utf-8"))
    if magic_smoke.get("result_type") != "magic_sky130_extraction_smoke":
        return fail("Magic Sky130 extraction smoke has wrong result_type")
    if magic_smoke.get("writes_candidate_post_layout_evidence") is not False:
        return fail("Magic Sky130 extraction smoke must not write candidate post-layout evidence")
    if magic_smoke.get("converter_cell_names_touched") != []:
        return fail("Magic Sky130 extraction smoke must not touch converter cell names")
    if magic_smoke.get("pdk_magic_rc_present") is not True:
        return fail("Magic Sky130 extraction smoke should find the PDK magicrc")
    if magic_smoke.get("status") not in {"magic_sky130_extraction_smoke_passed_not_converter_evidence", "magic_sky130_extraction_smoke_failed"}:
        return fail("Magic Sky130 extraction smoke has unexpected status")
    smoke_page = (ROOT / "site" / "research" / "magic-sky130-extraction-smoke.html").read_text(encoding="utf-8")
    for marker in ["Magic Sky130 Extraction Smoke", "writes candidate post-layout evidence: <code>False</code>", "Before a real converter can be extracted", "tiny metal wire", "does not prove a DAC"]:
        if marker not in smoke_page:
            return fail(f"site/research/magic-sky130-extraction-smoke.html missing marker {marker!r}")

    magic_compat = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "magic-sky130-compatibility.json").read_text(encoding="utf-8"))
    if magic_compat.get("result_type") != "magic_sky130_compatibility":
        return fail("Magic Sky130 compatibility has wrong result_type")
    if magic_compat.get("system_magic_version") != "8.3.105":
        return fail("Magic Sky130 compatibility should record the current system Magic version")
    if magic_compat.get("local_magic_present") not in {True, False}:
        return fail("Magic Sky130 compatibility should record whether local Magic is installed")
    if magic_compat.get("local_magic_present") is True and magic_compat.get("local_magic_version") in {None, "", "missing"}:
        return fail("Magic Sky130 compatibility should record the installed local Magic version")
    if magic_compat.get("smoke_passed") not in {True, False}:
        return fail("Magic Sky130 compatibility should record whether the Sky130 smoke passed")
    if magic_compat.get("status") not in {
        "local_magic_upgrade_needed_for_sky130_extraction",
        "local_magic_installed_sky130_smoke_not_passing",
        "magic_sky130_extraction_path_ready_not_converter_evidence",
    }:
        return fail("Magic Sky130 compatibility has unexpected status")
    if magic_compat.get("install_script") != "scripts/install_local_magic_from_source.sh":
        return fail("Magic Sky130 compatibility should point to the local install script")
    compat_page = (ROOT / "site" / "research" / "magic-sky130-compatibility.html").read_text(encoding="utf-8")
    for marker in ["Magic Sky130 Compatibility", magic_compat["status"], "system Magic version: <code>8.3.105</code>", "local Magic present:", "local Magic version:", "install_local_magic_from_source.sh", "Extraction is a contract", "does not install tools by itself"]:
        if marker not in compat_page:
            return fail(f"site/research/magic-sky130-compatibility.html missing marker {marker!r}")

    row_dac_layout_smoke = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "row-dac-10b-layout-smoke.json").read_text(encoding="utf-8"))
    if row_dac_layout_smoke.get("result_type") != "row_dac_10b_layout_smoke":
        return fail("Row-DAC 10b layout smoke has wrong result_type")
    if row_dac_layout_smoke.get("cell_present") is not True:
        return fail("Row-DAC 10b layout smoke should find the named Magic cell")
    if row_dac_layout_smoke.get("passed") is not True:
        return fail("Row-DAC 10b layout smoke should pass with local Sky130 Magic")
    if row_dac_layout_smoke.get("writes_candidate_post_layout_evidence") is not False:
        return fail("Row-DAC 10b layout smoke must not write candidate post-layout evidence")
    output_paths = {item.get("path") for item in row_dac_layout_smoke.get("outputs", []) if isinstance(item, dict) and item.get("present") is True}
    for path in [
        "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/row_dac_10b.ext",
        "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/row_dac_10b_layout_smoke.spice",
    ]:
        if path not in output_paths:
            return fail(f"Row-DAC 10b layout smoke missing extracted output {path!r}")
    row_dac_layout_page = (ROOT / "site" / "research" / "row-dac-10b-layout-smoke.html").read_text(encoding="utf-8")
    for marker in ["Row DAC 10b Layout Smoke", "row_dac_10b_layout_smoke_passed_not_candidate_evidence", "writes candidate post-layout evidence: <code>False</code>", "first named physical converter starter cell", "not a production DAC proof", "does not prove a production 10-bit DAC"]:
        if marker not in row_dac_layout_page:
            return fail(f"site/research/row-dac-10b-layout-smoke.html missing marker {marker!r}")

    converter_starter_smoke = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-starter-layout-smoke.json").read_text(encoding="utf-8"))
    if converter_starter_smoke.get("result_type") != "converter_starter_layout_smoke":
        return fail("converter starter layout smoke has wrong result_type")
    if converter_starter_smoke.get("passed") is not True:
        return fail("converter starter layout smoke should pass")
    if converter_starter_smoke.get("cell_count") != 4 or converter_starter_smoke.get("passed_cell_count") != 4:
        return fail("converter starter layout smoke should cover and pass four named cells")
    if converter_starter_smoke.get("writes_candidate_post_layout_evidence") is not False:
        return fail("converter starter layout smoke must not write candidate post-layout evidence")
    starter_cell_names = {item.get("name") for item in converter_starter_smoke.get("cells", []) if isinstance(item, dict) and item.get("passed") is True}
    for name in ["row_dac_10b", "sar_readout_12b", "shared_converter_mux", "aimc_converter_macro"]:
        if name not in starter_cell_names:
            return fail(f"converter starter layout smoke missing passed cell {name!r}")
    converter_starter_page = (ROOT / "site" / "research" / "converter-starter-layout-smoke.html").read_text(encoding="utf-8")
    for marker in ["Converter Starter Layout Smoke", "converter_starter_layout_smoke_passed_not_candidate_evidence", "passed cell count: <code>4</code>", "writes candidate post-layout evidence: <code>False</code>", "row_dac_10b", "sar_readout_12b", "shared_converter_mux", "aimc_converter_macro", "does not prove production DAC/ADC/mux quality"]:
        if marker not in converter_starter_page:
            return fail(f"site/research/converter-starter-layout-smoke.html missing marker {marker!r}")

    starter_candidate = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-starter-post-layout-candidate.json").read_text(encoding="utf-8"))
    if starter_candidate.get("result_type") != "converter_starter_post_layout_candidate":
        return fail("converter starter post-layout candidate has wrong result_type")
    if starter_candidate.get("status") != "starter_candidate_packet_ready_not_accepted_evidence":
        return fail("converter starter post-layout candidate should be preflight-ready but not accepted evidence")
    if starter_candidate.get("preflight_status") != "ready_for_strict_submission":
        return fail("converter starter post-layout candidate preflight should be ready")
    if starter_candidate.get("preflight_issue_count") != 0:
        return fail("converter starter post-layout candidate should have zero preflight issues")
    if starter_candidate.get("writes_canonical_candidate_post_layout") is not False:
        return fail("converter starter post-layout candidate must not write canonical candidate evidence")
    if starter_candidate.get("writes_accepted_post_layout") is not False:
        return fail("converter starter post-layout candidate must not write accepted evidence")
    if starter_candidate.get("canonical_accepted_post_layout_exists") is not False:
        return fail("converter starter post-layout candidate must keep canonical accepted evidence absent")
    starter_candidate_page = (ROOT / "site" / "research" / "converter-starter-post-layout-candidate.html").read_text(encoding="utf-8")
    for marker in ["Converter Starter Post-Layout Candidate", "starter_candidate_packet_ready_not_accepted_evidence", "preflight status: <code>ready_for_strict_submission</code>", "preflight issue count: <code>0</code>", "writes accepted post-layout: <code>False</code>", "does not submit accepted evidence", "not production converter physics"]:
        if marker not in starter_candidate_page:
            return fail(f"site/research/converter-starter-post-layout-candidate.html missing marker {marker!r}")

    starter_physical = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-starter-physical-artifacts.json").read_text(encoding="utf-8"))
    if starter_physical.get("result_type") != "converter_starter_physical_artifacts":
        return fail("converter starter physical artifacts has wrong result_type")
    if starter_physical.get("status") != "starter_physical_artifacts_present_not_accepted_evidence":
        return fail("converter starter physical artifacts should be present but not accepted evidence")
    if starter_physical.get("cell_count") != 4 or starter_physical.get("complete_cell_count") != 4:
        return fail("converter starter physical artifacts should cover four complete cells")
    if starter_physical.get("macro_bbox_area_lambda2", 0) <= 0:
        return fail("converter starter physical artifacts should record positive macro bbox area")
    if starter_physical.get("candidate_post_layout_written") is not False:
        return fail("converter starter physical artifacts must not write candidate post-layout")
    if starter_physical.get("accepted_post_layout_written") is not False:
        return fail("converter starter physical artifacts must not write accepted post-layout")
    starter_physical_page = (ROOT / "site" / "research" / "converter-starter-physical-artifacts.html").read_text(encoding="utf-8")
    for marker in ["Converter Starter Physical Artifacts", "starter_physical_artifacts_present_not_accepted_evidence", "complete cell count: <code>4</code>", "candidate post-layout written: <code>False</code>", "accepted post-layout written: <code>False</code>", "A layout artifact is stronger than a paragraph", "does not measure converter energy"]:
        if marker not in starter_physical_page:
            return fail(f"site/research/converter-starter-physical-artifacts.html missing marker {marker!r}")

    parasitic_load = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-starter-parasitic-load-estimate.json").read_text(encoding="utf-8"))
    if parasitic_load.get("result_type") != "converter_starter_parasitic_load_estimate":
        return fail("converter starter parasitic load estimate has wrong result_type")
    if parasitic_load.get("status") != "starter_extracted_parasitic_load_estimated_not_converter_proof":
        return fail("converter starter parasitic load estimate has unexpected status")
    if parasitic_load.get("row_count") != 7:
        return fail("converter starter parasitic load estimate should report seven rows")
    if parasitic_load.get("total_estimated_pin_charge_energy_j", 0) <= 0:
        return fail("converter starter parasitic load estimate should have positive charge energy")
    if parasitic_load.get("max_settle_0p1pct_s", 0) <= 0:
        return fail("converter starter parasitic load estimate should have positive settling estimate")
    for row in parasitic_load.get("rows", []):
        if isinstance(row, dict) and row.get("cap_f", 0) <= 0:
            return fail(f"converter starter parasitic load estimate has non-positive capacitance for {row.get('object')!r}")
    if parasitic_load.get("candidate_post_layout_written") is not False:
        return fail("converter starter parasitic load estimate must not write candidate post-layout")
    if parasitic_load.get("accepted_post_layout_written") is not False:
        return fail("converter starter parasitic load estimate must not write accepted post-layout")
    parasitic_page = (ROOT / "site" / "research" / "converter-starter-parasitic-load-estimate.html").read_text(encoding="utf-8")
    for marker in ["Converter Starter Parasitic Load Estimate", "starter_extracted_parasitic_load_estimated_not_converter_proof", "total estimated pin charge energy J", "max settle 0.1 percent s", "An extracted capacitance tells us", "does not simulate transistor converter behavior"]:
        if marker not in parasitic_page:
            return fail(f"site/research/converter-starter-parasitic-load-estimate.html missing marker {marker!r}")

    parasitic_rerun = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-starter-parasitic-break-even-rerun.json").read_text(encoding="utf-8"))
    if parasitic_rerun.get("result_type") != "converter_starter_parasitic_break_even_rerun":
        return fail("converter starter parasitic break-even rerun has wrong result_type")
    if parasitic_rerun.get("status") != "starter_parasitic_break_even_rerun_complete_not_accepted_evidence":
        return fail("converter starter parasitic break-even rerun has unexpected status")
    if parasitic_rerun.get("scenario_count") != 4:
        return fail("converter starter parasitic break-even rerun should preserve four scenarios")
    if parasitic_rerun.get("starter_total_pin_charge_energy_j", 0) <= 0:
        return fail("converter starter parasitic break-even rerun should carry positive parasitic energy")
    if parasitic_rerun.get("replacement_decision") != "keep_digital_fallback_until_real_converter_post_layout_measurement":
        return fail("converter starter parasitic break-even rerun should keep digital fallback")
    if parasitic_rerun.get("candidate_post_layout_written") is not False or parasitic_rerun.get("accepted_post_layout_written") is not False:
        return fail("converter starter parasitic break-even rerun must not write candidate or accepted post-layout")
    rerun_page = (ROOT / "site" / "research" / "converter-starter-parasitic-break-even-rerun.html").read_text(encoding="utf-8")
    for marker in ["Converter Starter Parasitic Break-Even Rerun", "starter_parasitic_break_even_rerun_complete_not_accepted_evidence", "starter total pin charge energy J", "keep_digital_fallback_until_real_converter_post_layout_measurement", "A parasitic load changes the break-even question", "does not replace real ADC/DAC energy"]:
        if marker not in rerun_page:
            return fail(f"site/research/converter-starter-parasitic-break-even-rerun.html missing marker {marker!r}")

    extracted_rc = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-starter-extracted-rc-ngspice.json").read_text(encoding="utf-8"))
    if extracted_rc.get("result_type") != "converter_starter_extracted_rc_ngspice":
        return fail("converter starter extracted RC ngspice has wrong result_type")
    if extracted_rc.get("status") != "starter_extracted_rc_ngspice_passed_not_converter_proof":
        return fail("converter starter extracted RC ngspice has unexpected status")
    if extracted_rc.get("ngspice_returncode") != 0:
        return fail("converter starter extracted RC ngspice should have return code 0")
    if extracted_rc.get("row_final_v", 0) <= 1.7:
        return fail("converter starter extracted RC ngspice should drive row final voltage above 1.7 V")
    if extracted_rc.get("row_90_when_s", 0) <= 0:
        return fail("converter starter extracted RC ngspice should report positive 90 percent crossing")
    if extracted_rc.get("row_99_when_s", 0) <= extracted_rc.get("row_90_when_s", 0):
        return fail("converter starter extracted RC ngspice should report 99 percent after 90 percent")
    if extracted_rc.get("candidate_post_layout_written") is not False or extracted_rc.get("accepted_post_layout_written") is not False:
        return fail("converter starter extracted RC ngspice must not write candidate or accepted post-layout")
    extracted_rc_page = (ROOT / "site" / "research" / "converter-starter-extracted-rc-ngspice.html").read_text(encoding="utf-8")
    for marker in ["Converter Starter Extracted RC Ngspice", "starter_extracted_rc_ngspice_passed_not_converter_proof", "row final V", "column peak V", "SPICE is now solving time-domain charge movement", "does not simulate transistor converter behavior"]:
        if marker not in extracted_rc_page:
            return fail(f"site/research/converter-starter-extracted-rc-ngspice.html missing marker {marker!r}")

    sample_switch = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-transistor-sample-switch-ngspice.json").read_text(encoding="utf-8"))
    if sample_switch.get("result_type") != "sky130_transistor_sample_switch_ngspice":
        return fail("Sky130 transistor sample switch ngspice has wrong result_type")
    if sample_switch.get("status") != "sky130_transistor_sample_switch_passed_not_converter_proof":
        return fail("Sky130 transistor sample switch ngspice has unexpected status")
    if sample_switch.get("case_count") != 3:
        return fail("Sky130 transistor sample switch ngspice should run three cases")
    for model in ["sky130_fd_pr__nfet_01v8", "sky130_fd_pr__pfet_01v8"]:
        if model not in sample_switch.get("device_models", []):
            return fail(f"Sky130 transistor sample switch ngspice missing device model {model}")
    if sample_switch.get("worst_sample_error_v", 1) > sample_switch.get("half_lsb_12b_v", 0):
        return fail("Sky130 transistor sample switch ngspice should settle within half LSB")
    if sample_switch.get("candidate_post_layout_written") is not False or sample_switch.get("accepted_post_layout_written") is not False:
        return fail("Sky130 transistor sample switch ngspice must not write candidate or accepted post-layout")
    switch_page = (ROOT / "site" / "research" / "sky130-transistor-sample-switch-ngspice.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Transistor Sample Switch Ngspice", "sky130_transistor_sample_switch_passed_not_converter_proof", "worst sample error V", "sky130_fd_pr__nfet_01v8", "A sample switch is a controlled path for charge", "does not prove hold-mode feedthrough"]:
        if marker not in switch_page:
            return fail(f"site/research/sky130-transistor-sample-switch-ngspice.html missing marker {marker!r}")

    hold_mode = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-sample-switch-hold-mode-ngspice.json").read_text(encoding="utf-8"))
    if hold_mode.get("result_type") != "sky130_sample_switch_hold_mode_ngspice":
        return fail("Sky130 sample switch hold mode ngspice has wrong result_type")
    if hold_mode.get("status") != "sky130_sample_switch_hold_mode_characterized_not_converter_proof":
        return fail("Sky130 sample switch hold mode ngspice has unexpected status")
    if hold_mode.get("case_count") != 3:
        return fail("Sky130 sample switch hold mode ngspice should run three cases")
    if hold_mode.get("worst_hold_abs_delta_v", 0) <= 0:
        return fail("Sky130 sample switch hold mode ngspice should report nonzero hold movement")
    if hold_mode.get("hold_delta_pass_count") != 0 or hold_mode.get("total_error_pass_count") != 0:
        return fail("Sky130 sample switch hold mode ngspice should expose the current hold-mode half-LSB failure")
    if hold_mode.get("candidate_post_layout_written") is not False or hold_mode.get("accepted_post_layout_written") is not False:
        return fail("Sky130 sample switch hold mode ngspice must not write candidate or accepted post-layout")
    hold_page = (ROOT / "site" / "research" / "sky130-sample-switch-hold-mode-ngspice.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Sample Switch Hold Mode Ngspice", "sky130_sample_switch_hold_mode_characterized_not_converter_proof", "worst hold abs delta V", "hold delta pass count: <code>0</code>", "A sampled voltage is stored charge", "does not prove an ADC decision"]:
        if marker not in hold_page:
            return fail(f"site/research/sky130-sample-switch-hold-mode-ngspice.html missing marker {marker!r}")

    hold_sweep = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-sample-switch-hold-mitigation-sweep.json").read_text(encoding="utf-8"))
    if hold_sweep.get("result_type") != "sky130_sample_switch_hold_mitigation_sweep":
        return fail("Sky130 sample switch hold mitigation sweep has wrong result_type")
    if hold_sweep.get("status") != "sky130_hold_mitigation_sweep_complete_not_converter_proof":
        return fail("Sky130 sample switch hold mitigation sweep has unexpected status")
    if hold_sweep.get("config_count") != 3 or hold_sweep.get("case_count") != 9:
        return fail("Sky130 sample switch hold mitigation sweep should run three configs and nine cases")
    if hold_sweep.get("measured_case_count", 0) < 6:
        return fail("Sky130 sample switch hold mitigation sweep should measure at least six cases")
    if hold_sweep.get("timed_out_case_count", 0) > 3:
        return fail("Sky130 sample switch hold mitigation sweep should keep bounded timeouts at three cases or fewer")
    if hold_sweep.get("best_improvement_vs_plain_hold_mode_x", 0) <= 1.0:
        return fail("Sky130 sample switch hold mitigation sweep should improve over the separate plain hold-mode reference")
    if hold_sweep.get("plain_hold_mode_reference_worst_hold_abs_delta_v") is None:
        return fail("Sky130 sample switch hold mitigation sweep should record the plain hold-mode reference")
    if hold_sweep.get("best_worst_hold_abs_delta_v", 1) >= hold_sweep.get("plain_hold_mode_reference_worst_hold_abs_delta_v", 0):
        return fail("Sky130 sample switch hold mitigation sweep best config should reduce hold movement versus plain hold mode")
    if hold_sweep.get("candidate_post_layout_written") is not False or hold_sweep.get("accepted_post_layout_written") is not False:
        return fail("Sky130 sample switch hold mitigation sweep must not write candidate or accepted post-layout")
    sweep_page = (ROOT / "site" / "research" / "sky130-sample-switch-hold-mitigation-sweep.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Sample Switch Hold Mitigation Sweep", "sky130_hold_mitigation_sweep_complete_not_converter_proof", "best improvement vs plain hold-mode x", "timed out case count", "The held-node error is charge divided by capacitance", "does not prove a complete sample-and-hold architecture"]:
        if marker not in sweep_page:
            return fail(f"site/research/sky130-sample-switch-hold-mitigation-sweep.html missing marker {marker!r}")

    dummy_cancellation = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-sample-switch-dummy-cancellation-ngspice.json").read_text(encoding="utf-8"))
    if dummy_cancellation.get("result_type") != "sky130_sample_switch_dummy_cancellation_ngspice":
        return fail("Sky130 sample switch dummy cancellation ngspice has wrong result_type")
    if dummy_cancellation.get("status") != "sky130_dummy_cancellation_sweep_complete_not_converter_proof":
        return fail("Sky130 sample switch dummy cancellation ngspice has unexpected status")
    if dummy_cancellation.get("config_count") != 3 or dummy_cancellation.get("case_count") != 9:
        return fail("Sky130 sample switch dummy cancellation ngspice should run three configs and nine cases")
    if dummy_cancellation.get("measured_case_count", 0) < 6:
        return fail("Sky130 sample switch dummy cancellation ngspice should measure at least six cases")
    if dummy_cancellation.get("timed_out_case_count", 0) > 3:
        return fail("Sky130 sample switch dummy cancellation ngspice should keep bounded timeouts at three cases or fewer")
    if dummy_cancellation.get("best_config") not in {"dummy_0p25x_1p0p_2x4", "dummy_0p50x_1p0p_2x4"}:
        return fail("Sky130 sample switch dummy cancellation ngspice should identify a measured dummy case as best")
    if dummy_cancellation.get("best_hold_improvement_x", 0) <= 1.0:
        return fail("Sky130 sample switch dummy cancellation ngspice should show measured improvement over no-dummy baseline")
    if dummy_cancellation.get("best_worst_hold_abs_delta_v", 1) >= dummy_cancellation.get("baseline_worst_hold_abs_delta_v", 0):
        return fail("Sky130 sample switch dummy cancellation best measured case should reduce hold movement")
    if dummy_cancellation.get("candidate_post_layout_written") is not False or dummy_cancellation.get("accepted_post_layout_written") is not False:
        return fail("Sky130 sample switch dummy cancellation ngspice must not write candidate or accepted post-layout")
    dummy_page = (ROOT / "site" / "research" / "sky130-sample-switch-dummy-cancellation-ngspice.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Sample Switch Dummy Cancellation Ngspice", "sky130_dummy_cancellation_sweep_complete_not_converter_proof", "timed out case count", "A dummy device tries to inject charge with the opposite sign", "does not prove a complete sample-and-hold architecture"]:
        if marker not in dummy_page:
            return fail(f"site/research/sky130-sample-switch-dummy-cancellation-ngspice.html missing marker {marker!r}")

    bottom_plate = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-bottom-plate-sampling-ngspice.json").read_text(encoding="utf-8"))
    if bottom_plate.get("result_type") != "sky130_bottom_plate_sampling_ngspice":
        return fail("Sky130 bottom-plate sampling ngspice has wrong result_type")
    if bottom_plate.get("status") != "sky130_bottom_plate_sampling_characterized_not_converter_proof":
        return fail("Sky130 bottom-plate sampling ngspice has unexpected status")
    if bottom_plate.get("config_count") != 3 or bottom_plate.get("case_count") != 9:
        return fail("Sky130 bottom-plate sampling ngspice should run three configs and nine cases")
    if bottom_plate.get("measured_case_count", 0) < 4:
        return fail("Sky130 bottom-plate sampling ngspice should measure at least four cases")
    if bottom_plate.get("timed_out_case_count", 0) > 5:
        return fail("Sky130 bottom-plate sampling ngspice should keep bounded timeouts at five cases or fewer")
    if bottom_plate.get("best_worst_hold_abs_delta_v") is None:
        return fail("Sky130 bottom-plate sampling ngspice should report a measured best hold movement")
    if bottom_plate.get("best_worst_hold_abs_delta_v", 0) <= 0:
        return fail("Sky130 bottom-plate sampling ngspice should report nonzero hold movement")
    if bottom_plate.get("candidate_post_layout_written") is not False or bottom_plate.get("accepted_post_layout_written") is not False:
        return fail("Sky130 bottom-plate sampling ngspice must not write candidate or accepted post-layout")
    bottom_page = (ROOT / "site" / "research" / "sky130-bottom-plate-sampling-ngspice.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Bottom Plate Sampling Ngspice", "sky130_bottom_plate_sampling_characterized_not_converter_proof", "timed out case count", "Bottom-plate sampling stores the voltage across a capacitor", "does not prove comparator behavior"]:
        if marker not in bottom_page:
            return fail(f"site/research/sky130-bottom-plate-sampling-ngspice.html missing marker {marker!r}")

    topology_gate = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-sample-hold-topology-decision-gate.json").read_text(encoding="utf-8"))
    if topology_gate.get("result_type") != "sky130_sample_hold_topology_decision_gate":
        return fail("Sky130 sample-hold topology decision gate has wrong result_type")
    if topology_gate.get("status") != "sky130_sample_hold_topology_gate_requires_buffered_or_bootstrapped_design":
        return fail("Sky130 sample-hold topology decision gate has unexpected status")
    if topology_gate.get("on_state_passes") is not True:
        return fail("Sky130 sample-hold topology decision gate should preserve the on-state pass result")
    if topology_gate.get("plain_hold_passes") is not False:
        return fail("Sky130 sample-hold topology decision gate should preserve the plain hold failure")
    if topology_gate.get("all_existing_hold_topologies_pass") is not False:
        return fail("Sky130 sample-hold topology decision gate must not treat existing hold topologies as passing")
    if topology_gate.get("best_mitigation_worst_hold_abs_delta_v", 0) <= topology_gate.get("half_lsb_12b_v", 0):
        return fail("Sky130 sample-hold topology decision gate should show mitigation still above half LSB")
    for candidate in ["bootstrapped_switch", "buffered_sample_and_hold", "fully_differential_sampling"]:
        if candidate not in topology_gate.get("selected_next_topology_candidates", []):
            return fail(f"Sky130 sample-hold topology decision gate missing next topology {candidate!r}")
    if topology_gate.get("candidate_post_layout_written") is not False or topology_gate.get("accepted_post_layout_written") is not False:
        return fail("Sky130 sample-hold topology decision gate must not write candidate or accepted post-layout")
    topology_page = (ROOT / "site" / "research" / "sky130-sample-hold-topology-decision-gate.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Sample-Hold Topology Decision Gate", "sky130_sample_hold_topology_gate_requires_buffered_or_bootstrapped_design", "all existing hold topologies pass", "voltage movement is charge movement divided by capacitance", "bootstrapped_switch", "does not prove a working ADC"]:
        if marker not in topology_page:
            return fail(f"site/research/sky130-sample-hold-topology-decision-gate.html missing marker {marker!r}")

    buffered_hold = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-buffered-sample-hold-ngspice.json").read_text(encoding="utf-8"))
    if buffered_hold.get("result_type") != "sky130_buffered_sample_hold_ngspice":
        return fail("Sky130 buffered sample-hold ngspice has wrong result_type")
    if buffered_hold.get("status") != "sky130_buffered_sample_hold_characterized_not_converter_proof":
        return fail("Sky130 buffered sample-hold ngspice has unexpected status")
    if buffered_hold.get("topology") != "nfet_source_follower_readout_buffer_after_sample_capacitor":
        return fail("Sky130 buffered sample-hold ngspice should name the tested buffer topology")
    if buffered_hold.get("case_count") != 3:
        return fail("Sky130 buffered sample-hold ngspice should run three input cases")
    if buffered_hold.get("timed_out_case_count", 0) + buffered_hold.get("measured_case_count", 0) != buffered_hold.get("case_count"):
        return fail("Sky130 buffered sample-hold ngspice should account for every case")
    if buffered_hold.get("measured_case_count") != 0:
        return fail("Sky130 buffered sample-hold ngspice currently documents the naive buffer as not numerically stable")
    if buffered_hold.get("candidate_post_layout_written") is not False or buffered_hold.get("accepted_post_layout_written") is not False:
        return fail("Sky130 buffered sample-hold ngspice must not write candidate or accepted post-layout")
    buffered_page = (ROOT / "site" / "research" / "sky130-buffered-sample-hold-ngspice.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Buffered Sample-Hold Ngspice", "sky130_buffered_sample_hold_characterized_not_converter_proof", "source_follower_readout_buffer", "not acceptable evidence", "does not prove a rail-to-rail buffer"]:
        if marker not in buffered_page:
            return fail(f"site/research/sky130-buffered-sample-hold-ngspice.html missing marker {marker!r}")

    bootstrap = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-bootstrapped-switch-ngspice.json").read_text(encoding="utf-8"))
    if bootstrap.get("result_type") != "sky130_bootstrapped_switch_ngspice":
        return fail("Sky130 bootstrapped switch ngspice has wrong result_type")
    if bootstrap.get("status") != "sky130_bootstrapped_switch_characterized_not_converter_proof":
        return fail("Sky130 bootstrapped switch ngspice has unexpected status")
    if bootstrap.get("topology") != "idealized_input_referenced_bootstrapped_nfet_sample_switch":
        return fail("Sky130 bootstrapped switch ngspice should name the tested topology")
    if bootstrap.get("idealized_bootstrap_driver") is not True:
        return fail("Sky130 bootstrapped switch ngspice should mark the bootstrap driver as idealized")
    if bootstrap.get("case_count") != 3:
        return fail("Sky130 bootstrapped switch ngspice should run three input cases")
    if bootstrap.get("timed_out_case_count", 0) + bootstrap.get("measured_case_count", 0) != bootstrap.get("case_count"):
        return fail("Sky130 bootstrapped switch ngspice should account for every case")
    if bootstrap.get("measured_case_count") != 3 or bootstrap.get("timed_out_case_count") != 0:
        return fail("Sky130 bootstrapped switch ngspice should have three converged cases under the calibrated timeout")
    if bootstrap.get("acquisition_pass_count") != 3 or bootstrap.get("hold_delta_pass_count") != 0:
        return fail("Sky130 bootstrapped switch ngspice should preserve its measured acquisition-pass and hold-fail boundary")
    if bootstrap.get("candidate_post_layout_written") is not False or bootstrap.get("accepted_post_layout_written") is not False:
        return fail("Sky130 bootstrapped switch ngspice must not write candidate or accepted post-layout")
    bootstrap_page = (ROOT / "site" / "research" / "sky130-bootstrapped-switch-ngspice.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Bootstrapped Switch Ngspice", "sky130_bootstrapped_switch_characterized_not_converter_proof", "idealized_input_referenced_bootstrapped", "constant gate-to-source voltage", "does not prove a real bootstrap charge pump"]:
        if marker not in bootstrap_page:
            return fail(f"site/research/sky130-bootstrapped-switch-ngspice.html missing marker {marker!r}")

    differential = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-fully-differential-sampling-ngspice.json").read_text(encoding="utf-8"))
    if differential.get("result_type") != "sky130_fully_differential_sampling_ngspice":
        return fail("Sky130 fully differential sampling ngspice has wrong result_type")
    if differential.get("status") != "sky130_fully_differential_sampling_characterized_not_converter_proof":
        return fail("Sky130 fully differential sampling ngspice has unexpected status")
    if differential.get("topology") != "matched_transmission_gate_differential_sample_hold_from_baseline":
        return fail("Sky130 fully differential sampling ngspice should name the tested topology")
    if differential.get("case_count") != 1:
        return fail("Sky130 fully differential sampling ngspice should run the current one-case differential input gate")
    if differential.get("timed_out_case_count", 0) + differential.get("measured_case_count", 0) != differential.get("case_count"):
        return fail("Sky130 fully differential sampling ngspice should account for every case")
    if differential.get("measured_case_count") != 1:
        return fail("Sky130 fully differential sampling ngspice should measure the one-case transmission-gate fixture")
    if differential.get("worst_diff_hold_abs_delta_v") is None:
        return fail("Sky130 fully differential sampling ngspice should report a differential hold movement")
    if differential.get("candidate_post_layout_written") is not False or differential.get("accepted_post_layout_written") is not False:
        return fail("Sky130 fully differential sampling ngspice must not write candidate or accepted post-layout")
    differential_page = (ROOT / "site" / "research" / "sky130-fully-differential-sampling-ngspice.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Fully Differential Sampling Ngspice", "sky130_fully_differential_sampling_characterized_not_converter_proof", "matched_transmission_gate_differential_sample_hold_from_baseline", "A comparator does not care about one stored node by itself", "does not prove comparator offset"]:
        if marker not in differential_page:
            return fail(f"site/research/sky130-fully-differential-sampling-ngspice.html missing marker {marker!r}")

    differential_dummy = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-differential-dummy-cancellation-ngspice.json").read_text(encoding="utf-8"))
    if differential_dummy.get("result_type") != "sky130_differential_dummy_cancellation_ngspice":
        return fail("Sky130 differential dummy cancellation ngspice has wrong result_type")
    if differential_dummy.get("status") != "sky130_differential_dummy_cancellation_characterized_not_converter_proof":
        return fail("Sky130 differential dummy cancellation ngspice has unexpected status")
    if differential_dummy.get("topology") != "matched_transmission_gate_differential_sample_hold_with_opposite_clock_dummy_devices":
        return fail("Sky130 differential dummy cancellation ngspice should name the tested topology")
    if differential_dummy.get("case_count") != 3:
        return fail("Sky130 differential dummy cancellation ngspice should run three dummy-size cases")
    if differential_dummy.get("timed_out_case_count", 0) + differential_dummy.get("measured_case_count", 0) != differential_dummy.get("case_count"):
        return fail("Sky130 differential dummy cancellation ngspice should account for every case")
    if differential_dummy.get("measured_case_count", 0) < 1:
        return fail("Sky130 differential dummy cancellation ngspice should measure at least one dummy-size case")
    if differential_dummy.get("best_diff_hold_abs_delta_v") is None:
        return fail("Sky130 differential dummy cancellation ngspice should report a best differential hold movement")
    if differential_dummy.get("candidate_post_layout_written") is not False or differential_dummy.get("accepted_post_layout_written") is not False:
        return fail("Sky130 differential dummy cancellation ngspice must not write candidate or accepted post-layout")
    differential_dummy_page = (ROOT / "site" / "research" / "sky130-differential-dummy-cancellation-ngspice.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Differential Dummy Cancellation Ngspice", "sky130_differential_dummy_cancellation_characterized_not_converter_proof", "opposite_clock_dummy_devices", "controlled error source", "does not prove comparator offset"]:
        if marker not in differential_dummy_page:
            return fail(f"site/research/sky130-differential-dummy-cancellation-ngspice.html missing marker {marker!r}")

    differential_input_sweep = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-differential-dummy-candidate-input-sweep.json").read_text(encoding="utf-8"))
    if differential_input_sweep.get("result_type") != "sky130_differential_dummy_candidate_input_sweep":
        return fail("Sky130 differential dummy candidate input sweep has wrong result_type")
    if differential_input_sweep.get("status") != "sky130_differential_dummy_candidate_input_sweep_characterized_not_converter_proof":
        return fail("Sky130 differential dummy candidate input sweep has unexpected status")
    if differential_input_sweep.get("topology") != "fixed_dummy_0p50x_differential_transmission_gate_sample_hold":
        return fail("Sky130 differential dummy candidate input sweep should name the fixed candidate topology")
    if differential_input_sweep.get("case_count") != 3:
        return fail("Sky130 differential dummy candidate input sweep should cover low, mid, and high cases")
    if differential_input_sweep.get("timed_out_case_count", 0) + differential_input_sweep.get("measured_case_count", 0) != differential_input_sweep.get("case_count"):
        return fail("Sky130 differential dummy candidate input sweep should account for every case")
    if differential_input_sweep.get("measured_case_count", 0) < 1:
        return fail("Sky130 differential dummy candidate input sweep should measure at least one case")
    if differential_input_sweep.get("worst_diff_hold_abs_delta_v") is None:
        return fail("Sky130 differential dummy candidate input sweep should report worst differential hold movement")
    if differential_input_sweep.get("candidate_post_layout_written") is not False or differential_input_sweep.get("accepted_post_layout_written") is not False:
        return fail("Sky130 differential dummy candidate input sweep must not write candidate or accepted post-layout")
    differential_input_page = (ROOT / "site" / "research" / "sky130-differential-dummy-candidate-input-sweep.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Differential Dummy Candidate Input Sweep", "fixed_dummy_0p50x_differential_transmission_gate_sample_hold", "low, mid, and high", "next proof is mismatch and noise", "does not prove comparator offset"]:
        if marker not in differential_input_page:
            return fail(f"site/research/sky130-differential-dummy-candidate-input-sweep.html missing marker {marker!r}")

    differential_mismatch_sweep = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-differential-dummy-candidate-mismatch-sweep.json").read_text(encoding="utf-8"))
    if differential_mismatch_sweep.get("result_type") != "sky130_differential_dummy_candidate_mismatch_sweep":
        return fail("Sky130 differential dummy candidate mismatch sweep has wrong result_type")
    if differential_mismatch_sweep.get("status") != "sky130_differential_dummy_candidate_mismatch_sweep_characterized_not_converter_proof":
        return fail("Sky130 differential dummy candidate mismatch sweep has unexpected status")
    if differential_mismatch_sweep.get("topology") != "fixed_dummy_0p50x_differential_transmission_gate_sample_hold_with_width_mismatch":
        return fail("Sky130 differential dummy candidate mismatch sweep should name the mismatched candidate topology")
    if differential_mismatch_sweep.get("case_count") != 5:
        return fail("Sky130 differential dummy candidate mismatch sweep should run five mismatch cases")
    if differential_mismatch_sweep.get("timed_out_case_count", 0) + differential_mismatch_sweep.get("measured_case_count", 0) != differential_mismatch_sweep.get("case_count"):
        return fail("Sky130 differential dummy candidate mismatch sweep should account for every case")
    if differential_mismatch_sweep.get("measured_case_count", 0) < 1:
        return fail("Sky130 differential dummy candidate mismatch sweep should measure at least one case")
    if differential_mismatch_sweep.get("worst_diff_hold_abs_delta_v") is None:
        return fail("Sky130 differential dummy candidate mismatch sweep should report worst differential hold movement")
    if differential_mismatch_sweep.get("candidate_post_layout_written") is not False or differential_mismatch_sweep.get("accepted_post_layout_written") is not False:
        return fail("Sky130 differential dummy candidate mismatch sweep must not write candidate or accepted post-layout")
    differential_mismatch_page = (ROOT / "site" / "research" / "sky130-differential-dummy-candidate-mismatch-sweep.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Differential Dummy Candidate Mismatch Sweep", "width mismatch", "controlled stress test", "next stress is noise", "does not prove random mismatch statistics"]:
        if marker not in differential_mismatch_page:
            return fail(f"site/research/sky130-differential-dummy-candidate-mismatch-sweep.html missing marker {marker!r}")

    decision_margin = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-differential-dummy-candidate-decision-margin.json").read_text(encoding="utf-8"))
    if decision_margin.get("result_type") != "sky130_differential_dummy_candidate_decision_margin":
        return fail("Sky130 differential dummy candidate decision margin has wrong result_type")
    if decision_margin.get("status") != "sky130_differential_dummy_candidate_decision_margin_defined_not_converter_proof":
        return fail("Sky130 differential dummy candidate decision margin has unexpected status")
    if decision_margin.get("remaining_comparator_offset_or_noise_budget_mv", 0) <= 0:
        return fail("Sky130 differential dummy candidate decision margin should leave positive comparator/noise budget")
    if decision_margin.get("max_passing_tested_comparator_offset_mv") is None:
        return fail("Sky130 differential dummy candidate decision margin should identify a passing tested offset")
    if decision_margin.get("candidate_post_layout_written") is not False or decision_margin.get("accepted_post_layout_written") is not False:
        return fail("Sky130 differential dummy candidate decision margin must not write candidate or accepted post-layout")
    decision_margin_page = (ROOT / "site" / "research" / "sky130-differential-dummy-candidate-decision-margin.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Differential Dummy Candidate Decision Margin", "remaining comparator offset or noise budget", "arithmetic gate", "Offset Budget Table", "does not simulate comparator transistors"]:
        if marker not in decision_margin_page:
            return fail(f"site/research/sky130-differential-dummy-candidate-decision-margin.html missing marker {marker!r}")

    offset_noise = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-differential-dummy-candidate-offset-noise-stress.json").read_text(encoding="utf-8"))
    if offset_noise.get("result_type") != "sky130_differential_dummy_candidate_offset_noise_stress":
        return fail("Sky130 differential dummy candidate offset/noise stress has wrong result_type")
    if offset_noise.get("status") != "sky130_differential_dummy_candidate_offset_noise_stress_defined_not_comparator_proof":
        return fail("Sky130 differential dummy candidate offset/noise stress has unexpected status")
    if offset_noise.get("case_count") != 20:
        return fail("Sky130 differential dummy candidate offset/noise stress should cover 20 budget cases")
    if offset_noise.get("passing_case_count", 0) <= 0 or offset_noise.get("failing_case_count", 0) <= 0:
        return fail("Sky130 differential dummy candidate offset/noise stress should include passing and failing budget cases")
    if offset_noise.get("candidate_post_layout_written") is not False or offset_noise.get("accepted_post_layout_written") is not False:
        return fail("Sky130 differential dummy candidate offset/noise stress must not write candidate or accepted post-layout")
    offset_noise_page = (ROOT / "site" / "research" / "sky130-differential-dummy-candidate-offset-noise-stress.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Differential Dummy Candidate Offset Noise Stress", "combined uncertainty", "budget stress test", "Stress Table", "does not simulate comparator devices"]:
        if marker not in offset_noise_page:
            return fail(f"site/research/sky130-differential-dummy-candidate-offset-noise-stress.html missing marker {marker!r}")

    comparator_spec = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-comparator-acceptance-fixture-spec.json").read_text(encoding="utf-8"))
    if comparator_spec.get("result_type") != "sky130_comparator_acceptance_fixture_spec":
        return fail("Sky130 comparator acceptance fixture spec has wrong result_type")
    if comparator_spec.get("status") != "sky130_comparator_acceptance_fixture_spec_ready_not_comparator_proof":
        return fail("Sky130 comparator acceptance fixture spec has unexpected status")
    comparator_budget = comparator_spec.get("derived_budget") if isinstance(comparator_spec.get("derived_budget"), dict) else {}
    if comparator_budget.get("target_combined_offset_noise_mv", 0) <= 0:
        return fail("Sky130 comparator acceptance fixture spec should carry a positive target offset/noise budget")
    if comparator_budget.get("target_combined_offset_noise_mv", 1) >= comparator_budget.get("first_known_failing_combined_offset_noise_mv", 0):
        return fail("Sky130 comparator acceptance fixture spec should keep passing target below first failing case")
    if len(comparator_spec.get("required_measurements", [])) < 5:
        return fail("Sky130 comparator acceptance fixture spec should define required measurements")
    if len(comparator_spec.get("stimulus_cases", [])) < 5:
        return fail("Sky130 comparator acceptance fixture spec should define stimulus cases")
    if comparator_spec.get("candidate_post_layout_written") is not False or comparator_spec.get("accepted_post_layout_written") is not False:
        return fail("Sky130 comparator acceptance fixture spec must not write candidate or accepted post-layout")
    comparator_spec_page = (ROOT / "site" / "research" / "sky130-comparator-acceptance-fixture-spec.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Comparator Acceptance Fixture Spec", "target combined offset/noise", "Required Measurements", "Stimulus Cases", "does not simulate comparator transistors"]:
        if marker not in comparator_spec_page:
            return fail(f"site/research/sky130-comparator-acceptance-fixture-spec.html missing marker {marker!r}")

    comparator_input = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-comparator-input-stage-ngspice.json").read_text(encoding="utf-8"))
    if comparator_input.get("result_type") != "sky130_comparator_input_stage_ngspice":
        return fail("Sky130 comparator input-stage ngspice has wrong result_type")
    if comparator_input.get("status") != "sky130_comparator_input_stage_polarity_proxy_passed_not_latch_or_noise_proof":
        return fail("Sky130 comparator input-stage ngspice has unexpected status")
    if comparator_input.get("case_count") != 6 or comparator_input.get("measured_case_count") != 6:
        return fail("Sky130 comparator input-stage ngspice should measure six cases")
    if comparator_input.get("polarity_pass_count") != 6 or comparator_input.get("all_cases_correct_polarity") is not True:
        return fail("Sky130 comparator input-stage ngspice should pass polarity on all cases")
    if comparator_input.get("offset_proxy_passes_target") is not True:
        return fail("Sky130 comparator input-stage ngspice should pass the static offset proxy target")
    if comparator_input.get("candidate_post_layout_written") is not False or comparator_input.get("accepted_post_layout_written") is not False:
        return fail("Sky130 comparator input-stage ngspice must not write candidate or accepted post-layout")
    comparator_input_page = (ROOT / "site" / "research" / "sky130-comparator-input-stage-ngspice.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Comparator Input-Stage Ngspice", "polarity pass count", "estimated static zero crossing", "not a clocked latch", "does not prove a clocked comparator latch"]:
        if marker not in comparator_input_page:
            return fail(f"site/research/sky130-comparator-input-stage-ngspice.html missing marker {marker!r}")

    comparator_latch = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-clocked-comparator-latch-ngspice.json").read_text(encoding="utf-8"))
    if comparator_latch.get("result_type") != "sky130_clocked_comparator_latch_ngspice":
        return fail("Sky130 clocked comparator latch ngspice has wrong result_type")
    if comparator_latch.get("status") != "sky130_clocked_comparator_latch_proxy_passed_not_noise_or_layout_proof":
        return fail("Sky130 clocked comparator latch ngspice has unexpected status")
    if comparator_latch.get("case_count") != 2 or comparator_latch.get("measured_case_count") != 2:
        return fail("Sky130 clocked comparator latch ngspice should measure two target-edge cases")
    if comparator_latch.get("resolved_correct_polarity_count") != 2 or comparator_latch.get("all_cases_resolve_correct_polarity") is not True:
        return fail("Sky130 clocked comparator latch ngspice should resolve both target-edge cases")
    if comparator_latch.get("candidate_post_layout_written") is not False or comparator_latch.get("accepted_post_layout_written") is not False:
        return fail("Sky130 clocked comparator latch ngspice must not write candidate or accepted post-layout")
    comparator_latch_page = (ROOT / "site" / "research" / "sky130-clocked-comparator-latch-ngspice.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Clocked Comparator Latch Ngspice", "resolved correct polarity count", "target-edge input difference", "does not yet measure kickback", "does not prove comparator noise"]:
        if marker not in comparator_latch_page:
            return fail(f"site/research/sky130-clocked-comparator-latch-ngspice.html missing marker {marker!r}")

    latch_kickback = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-sample-hold-latch-kickback-ngspice.json").read_text(encoding="utf-8"))
    if latch_kickback.get("result_type") != "sky130_sample_hold_latch_kickback_ngspice":
        return fail("Sky130 sample-hold latch kickback ngspice has wrong result_type")
    if latch_kickback.get("status") != "sky130_sample_hold_latch_kickback_proxy_characterized_not_accepted":
        return fail("Sky130 sample-hold latch kickback ngspice should remain characterized-not-accepted until kickback is fixed")
    if latch_kickback.get("case_count") != 2 or latch_kickback.get("measured_case_count") != 2:
        return fail("Sky130 sample-hold latch kickback ngspice should measure two target-edge cases")
    if latch_kickback.get("resolved_correct_polarity_count") != 2:
        return fail("Sky130 sample-hold latch kickback ngspice should still resolve both target-edge cases")
    if latch_kickback.get("kickback_below_half_lsb_count") != 0 or latch_kickback.get("all_cases_pass_coupled_gate") is not False:
        return fail("Sky130 sample-hold latch kickback ngspice should expose kickback failure")
    if latch_kickback.get("worst_sampled_diff_kickback_v", 0) <= latch_kickback.get("half_lsb_12b_v", 0):
        return fail("Sky130 sample-hold latch kickback ngspice should show kickback above half LSB")
    if latch_kickback.get("candidate_post_layout_written") is not False or latch_kickback.get("accepted_post_layout_written") is not False:
        return fail("Sky130 sample-hold latch kickback ngspice must not write candidate or accepted post-layout")
    latch_kickback_page = (ROOT / "site" / "research" / "sky130-sample-hold-latch-kickback-ngspice.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Sample-Hold Latch Kickback Ngspice", "kickback below half LSB count", "all cases pass coupled gate", "A latch is not only a reader", "does not prove comparator noise"]:
        if marker not in latch_kickback_page:
            return fail(f"site/research/sky130-sample-hold-latch-kickback-ngspice.html missing marker {marker!r}")

    input_size_sweep = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-latch-input-size-kickback-sweep.json").read_text(encoding="utf-8"))
    if input_size_sweep.get("result_type") != "sky130_latch_input_size_kickback_sweep":
        return fail("Sky130 latch input-size kickback sweep has wrong result_type")
    if input_size_sweep.get("status") != "sky130_latch_input_size_sweep_characterized_no_passing_width":
        return fail("Sky130 latch input-size kickback sweep should remain no-passing-width until isolation is added")
    if input_size_sweep.get("case_count") != 5 or input_size_sweep.get("measured_case_count") != 5:
        return fail("Sky130 latch input-size kickback sweep should measure five widths")
    if input_size_sweep.get("best_width_um") != 0.5:
        return fail("Sky130 latch input-size kickback sweep should identify 0.5um as the lowest-kickback tested width")
    if input_size_sweep.get("passing_width_count") != 0:
        return fail("Sky130 latch input-size kickback sweep should have no passing width")
    if input_size_sweep.get("best_kickback_v", 0) <= input_size_sweep.get("half_lsb_12b_v", 0):
        return fail("Sky130 latch input-size kickback sweep should still miss half LSB")
    if input_size_sweep.get("candidate_post_layout_written") is not False or input_size_sweep.get("accepted_post_layout_written") is not False:
        return fail("Sky130 latch input-size kickback sweep must not write candidate or accepted post-layout")
    input_size_sweep_page = (ROOT / "site" / "research" / "sky130-latch-input-size-kickback-sweep.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Latch Input-Size Kickback Sweep", "passing width count", "best kickback", "Shrinking it should reduce kickback", "does not prove comparator noise"]:
        if marker not in input_size_sweep_page:
            return fail(f"site/research/sky130-latch-input-size-kickback-sweep.html missing marker {marker!r}")

    isolation_target = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-comparator-isolation-target.json").read_text(encoding="utf-8"))
    if isolation_target.get("result_type") != "sky130_comparator_isolation_target":
        return fail("Sky130 comparator isolation target has wrong result_type")
    if isolation_target.get("status") != "sky130_comparator_isolation_target_defined_not_circuit_proof":
        return fail("Sky130 comparator isolation target should be target-only")
    measured_boundary = isolation_target.get("measured_boundary") if isinstance(isolation_target.get("measured_boundary"), dict) else {}
    target = isolation_target.get("target") if isinstance(isolation_target.get("target"), dict) else {}
    if measured_boundary.get("additional_reduction_needed_to_reach_half_lsb_x", 0) <= 2.9:
        return fail("Sky130 comparator isolation target should require about 3x additional reduction")
    if measured_boundary.get("additional_reduction_needed_to_reach_half_lsb_half_margin_x", 0) <= 5.8:
        return fail("Sky130 comparator isolation target should define a stronger margin target")
    if target.get("recommended_kickback_target_v", 1) >= target.get("hard_kickback_limit_v", 0):
        return fail("Sky130 comparator isolation target should recommend margin below the hard limit")
    if len(isolation_target.get("candidate_options", [])) < 4 or len(isolation_target.get("next_acceptance_tests", [])) < 4:
        return fail("Sky130 comparator isolation target should define candidate moves and next tests")
    if isolation_target.get("candidate_post_layout_written") is not False or isolation_target.get("accepted_post_layout_written") is not False:
        return fail("Sky130 comparator isolation target must not write candidate or accepted post-layout")
    isolation_page = (ROOT / "site" / "research" / "sky130-comparator-isolation-target.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Comparator Isolation Target", "additional reduction needed", "Candidate Isolation Moves", "sampled capacitor stores the decision voltage", "does not prove an isolated comparator"]:
        if marker not in isolation_page:
            return fail(f"site/research/sky130-comparator-isolation-target.html missing marker {marker!r}")

    capacitive_isolation = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-capacitive-latch-input-isolation-sweep.json").read_text(encoding="utf-8"))
    if capacitive_isolation.get("result_type") != "sky130_capacitive_latch_input_isolation_sweep":
        return fail("Sky130 capacitive latch input isolation sweep has wrong result_type")
    if capacitive_isolation.get("status") != "sky130_capacitive_latch_input_isolation_found_candidate_not_noise_or_layout_proof":
        return fail("Sky130 capacitive latch input isolation sweep should find a schematic candidate")
    if capacitive_isolation.get("case_count") != 5 or capacitive_isolation.get("measured_case_count") != 5:
        return fail("Sky130 capacitive latch input isolation sweep should measure five capacitor cases")
    if capacitive_isolation.get("passing_candidate_count", 0) <= 0:
        return fail("Sky130 capacitive latch input isolation sweep should find passing candidates")
    if capacitive_isolation.get("best_kickback_v", 1) >= capacitive_isolation.get("hard_kickback_limit_v", 0):
        return fail("Sky130 capacitive latch input isolation sweep best kickback should pass the hard limit")
    if capacitive_isolation.get("best_resolved_correct_polarity") is not True:
        return fail("Sky130 capacitive latch input isolation sweep best candidate should still resolve")
    if capacitive_isolation.get("candidate_post_layout_written") is not False or capacitive_isolation.get("accepted_post_layout_written") is not False:
        return fail("Sky130 capacitive latch input isolation sweep must not write candidate or accepted post-layout")
    capacitive_isolation_page = (ROOT / "site" / "research" / "sky130-capacitive-latch-input-isolation-sweep.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Capacitive Latch Input Isolation Sweep", "passing candidate count", "coupling capacitor", "sample-and-hold keeps the original charge", "does not prove comparator noise"]:
        if marker not in capacitive_isolation_page:
            return fail(f"site/research/sky130-capacitive-latch-input-isolation-sweep.html missing marker {marker!r}")

    both_polarity = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-capacitive-isolation-both-polarity-confirm.json").read_text(encoding="utf-8"))
    if both_polarity.get("result_type") != "sky130_capacitive_isolation_both_polarity_confirm":
        return fail("Sky130 capacitive isolation both-polarity confirm has wrong result_type")
    if both_polarity.get("status") != "sky130_capacitive_isolation_both_polarity_confirmed_not_noise_or_layout_proof":
        return fail("Sky130 capacitive isolation both-polarity confirm should confirm both input signs")
    if both_polarity.get("case_count") != 4 or both_polarity.get("measured_case_count") != 4:
        return fail("Sky130 capacitive isolation both-polarity confirm should measure four cases")
    if both_polarity.get("passing_case_count") != 4 or both_polarity.get("all_cases_pass") is not True:
        return fail("Sky130 capacitive isolation both-polarity confirm should pass all cases")
    if both_polarity.get("worst_kickback_v", 1) >= both_polarity.get("hard_kickback_limit_v", 0):
        return fail("Sky130 capacitive isolation both-polarity confirm worst kickback should pass the hard limit")
    if both_polarity.get("candidate_post_layout_written") is not False or both_polarity.get("accepted_post_layout_written") is not False:
        return fail("Sky130 capacitive isolation both-polarity confirm must not write candidate or accepted post-layout")
    both_polarity_page = (ROOT / "site" / "research" / "sky130-capacitive-isolation-both-polarity-confirm.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Capacitive Isolation Both-Polarity Confirm", "passing case count", "either sign of the input difference", "one-sided accident", "does not prove comparator noise"]:
        if marker not in both_polarity_page:
            return fail(f"site/research/sky130-capacitive-isolation-both-polarity-confirm.html missing marker {marker!r}")

    isolation_handoff = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-capacitive-isolation-post-layout-handoff.json").read_text(encoding="utf-8"))
    if isolation_handoff.get("result_type") != "sky130_capacitive_isolation_post_layout_handoff":
        return fail("Sky130 capacitive isolation post-layout handoff has wrong result_type")
    if isolation_handoff.get("status") != "confirmed_schematic_candidate_waiting_for_extracted_layout":
        return fail("Sky130 capacitive isolation post-layout handoff should wait for extracted layout")
    schematic = isolation_handoff.get("schematic_confirmation") if isinstance(isolation_handoff.get("schematic_confirmation"), dict) else {}
    if schematic.get("all_cases_pass") is not True or schematic.get("passing_case_count") != 4:
        return fail("Sky130 capacitive isolation post-layout handoff should consume confirmed schematic evidence")
    gate = isolation_handoff.get("post_layout_gate") if isinstance(isolation_handoff.get("post_layout_gate"), dict) else {}
    if gate.get("accepted_ready_now") is not False:
        return fail("Sky130 capacitive isolation post-layout handoff must not be accepted-ready")
    if gate.get("candidate_post_layout_written") is not False or gate.get("accepted_post_layout_written") is not False:
        return fail("Sky130 capacitive isolation post-layout handoff must not write post-layout evidence")
    if len(isolation_handoff.get("required_layout_objects", [])) < 7:
        return fail("Sky130 capacitive isolation post-layout handoff should name required physical objects")
    isolation_handoff_page = (ROOT / "site" / "research" / "sky130-capacitive-isolation-post-layout-handoff.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Capacitive Isolation Post-Layout Handoff", "confirmed schematic candidate", "Required Layout Objects", "Layout changes the object being measured", "does not create extracted layout"]:
        if marker not in isolation_handoff_page:
            return fail(f"site/research/sky130-capacitive-isolation-post-layout-handoff.html missing marker {marker!r}")

    physical_gap = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-capacitive-isolation-physical-cell-gap.json").read_text(encoding="utf-8"))
    if physical_gap.get("result_type") != "sky130_capacitive_isolation_physical_cell_gap":
        return fail("Sky130 capacitive isolation physical cell gap has wrong result_type")
    if physical_gap.get("status") != "physical_cell_gap_blocks_post_layout_candidate":
        return fail("Sky130 capacitive isolation physical cell gap should currently block post-layout candidate evidence")
    if physical_gap.get("required_object_count") != 6 or physical_gap.get("missing_object_count") != 2:
        return fail("Sky130 capacitive isolation physical cell gap should name two remaining physical proof gaps")
    if physical_gap.get("present_object_count") != 4 or physical_gap.get("accepted_ready_now") is not False:
        return fail("Sky130 capacitive isolation physical cell gap should have only starter physical objects ready")
    if physical_gap.get("candidate_post_layout_written") is not False or physical_gap.get("accepted_post_layout_written") is not False:
        return fail("Sky130 capacitive isolation physical cell gap must not write post-layout evidence")
    physical_gap_page = (ROOT / "site" / "research" / "sky130-capacitive-isolation-physical-cell-gap.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Capacitive Isolation Physical Cell Gap", "missing object count", "The confirmed schematic is a behavior", "Required Objects", "does not treat the starter layout"]:
        if marker not in physical_gap_page:
            return fail(f"site/research/sky130-capacitive-isolation-physical-cell-gap.html missing marker {marker!r}")

    post_layout_polarity = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "candidate-post-layout" / "rerun" / "sky130-capacitive-isolation-post-layout-both-polarity.json").read_text(encoding="utf-8"))
    if post_layout_polarity.get("result_type") != "sky130_capacitive_isolation_post_layout_both_polarity_rerun":
        return fail("Sky130 capacitive isolation post-layout both-polarity rerun has wrong result_type")
    if post_layout_polarity.get("status") != "extracted_rc_both_polarity_characterized_not_confirmed":
        return fail("Sky130 capacitive isolation post-layout both-polarity rerun should record the current unconfirmed result")
    if post_layout_polarity.get("case_count") != 2 or post_layout_polarity.get("measured_case_count") != 2:
        return fail("Sky130 capacitive isolation post-layout both-polarity rerun should measure two cases")
    if post_layout_polarity.get("passing_case_count") != 1 or post_layout_polarity.get("all_cases_pass") is not False:
        return fail("Sky130 capacitive isolation post-layout both-polarity rerun should pass only one polarity")
    if post_layout_polarity.get("worst_kickback_v", 1) >= post_layout_polarity.get("hard_kickback_limit_v", 0):
        return fail("Sky130 capacitive isolation post-layout both-polarity rerun should keep kickback below the hard limit")
    if post_layout_polarity.get("accepted_ready_now") is not False or post_layout_polarity.get("accepted_post_layout_written") is not False:
        return fail("Sky130 capacitive isolation post-layout both-polarity rerun must not write accepted evidence")
    post_layout_polarity_page = (ROOT / "site" / "research" / "sky130-capacitive-isolation-post-layout-both-polarity.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Capacitive Isolation Post-Layout Both-Polarity Rerun", "Magic-extracted RC", "passing case count", "not accepted comparator evidence", "does not prove comparator offset"]:
        if marker not in post_layout_polarity_page:
            return fail(f"site/research/sky130-capacitive-isolation-post-layout-both-polarity.html missing marker {marker!r}")

    port_diag = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-capacitive-isolation-extracted-port-mapping-diagnostic.json").read_text(encoding="utf-8"))
    if port_diag.get("result_type") != "sky130_capacitive_isolation_extracted_port_mapping_diagnostic":
        return fail("Sky130 capacitive isolation extracted port mapping diagnostic has wrong result_type")
    if port_diag.get("status") != "no_port_mapping_preserves_both_signs":
        return fail("Sky130 capacitive isolation extracted port mapping diagnostic should find no preserving mapping")
    if port_diag.get("row_count") != 6 or port_diag.get("mappings_with_both_signs_preserved") != []:
        return fail("Sky130 capacitive isolation extracted port mapping diagnostic should test six rows with no passing mapping")
    if port_diag.get("accepted_ready_now") is not False or port_diag.get("accepted_post_layout_written") is not False:
        return fail("Sky130 capacitive isolation extracted port mapping diagnostic must not write accepted evidence")
    port_diag_page = (ROOT / "site" / "research" / "sky130-capacitive-isolation-extracted-port-mapping-diagnostic.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Capacitive Isolation Extracted Port-Mapping Diagnostic", "mappings with both signs preserved", "removes the latch", "not a valid differential handoff", "does not prove latch resolution"]:
        if marker not in port_diag_page:
            return fail(f"site/research/sky130-capacitive-isolation-extracted-port-mapping-diagnostic.html missing marker {marker!r}")

    strength = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-capacitive-isolation-extracted-coupling-strength-sweep.json").read_text(encoding="utf-8"))
    if strength.get("result_type") != "sky130_capacitive_isolation_extracted_coupling_strength_sweep":
        return fail("Sky130 capacitive isolation extracted coupling-strength sweep has wrong result_type")
    if strength.get("status") != "no_added_coupling_strength_preserves_both_signs":
        return fail("Sky130 capacitive isolation extracted coupling-strength sweep should show added coupling alone does not preserve both signs")
    if strength.get("row_count") != 24 or strength.get("first_passing_added_cap_ff") is not None:
        return fail("Sky130 capacitive isolation extracted coupling-strength sweep should test 24 rows with no passing capacitor")
    if strength.get("accepted_ready_now") is not False or strength.get("accepted_post_layout_written") is not False:
        return fail("Sky130 capacitive isolation extracted coupling-strength sweep must not write accepted evidence")
    strength_page = (ROOT / "site" / "research" / "sky130-capacitive-isolation-extracted-coupling-strength-sweep.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Capacitive Isolation Extracted Coupling-Strength Sweep", "first passing added capacitor", "fixed capacitance", "sample-to-gate", "does not modify the physical layout"]:
        if marker not in strength_page:
            return fail(f"site/research/sky130-capacitive-isolation-extracted-coupling-strength-sweep.html missing marker {marker!r}")

    redesign = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-extracted-frontend-redesign-target.json").read_text(encoding="utf-8"))
    if redesign.get("result_type") != "sky130_extracted_frontend_redesign_target":
        return fail("Sky130 extracted frontend redesign target has wrong result_type")
    if redesign.get("status") != "redesign_required_before_post_layout_acceptance":
        return fail("Sky130 extracted frontend redesign target has unexpected status")
    if redesign.get("measured_wrong_sign_bias_mv", 0) <= redesign.get("target_differential_signal_mv", 0):
        return fail("Sky130 extracted frontend redesign target should show extracted bias larger than target signal")
    if redesign.get("required_bias_reduction_factor", 0) < 100:
        return fail("Sky130 extracted frontend redesign target should require more than 100x wrong-sign bias reduction")
    if redesign.get("accepted_ready_now") is not False or redesign.get("accepted_post_layout_written") is not False:
        return fail("Sky130 extracted frontend redesign target must not write accepted evidence")
    redesign_page = (ROOT / "site" / "research" / "sky130-extracted-frontend-redesign-target.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Extracted Frontend Redesign Target", "bias-to-signal ratio", "required bias reduction factor", "balanced measuring node", "does not claim a working comparator"]:
        if marker not in redesign_page:
            return fail(f"site/research/sky130-extracted-frontend-redesign-target.html missing marker {marker!r}")

    balanced_work_order = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-balanced-frontend-work-order.json").read_text(encoding="utf-8"))
    if balanced_work_order.get("result_type") != "sky130_balanced_frontend_work_order":
        return fail("Sky130 balanced frontend work order has wrong result_type")
    if balanced_work_order.get("status") != "ready_to_build_balanced_extracted_frontend_candidate":
        return fail("Sky130 balanced frontend work order has unexpected status")
    if balanced_work_order.get("target_cell_name") != "sky130_balanced_capacitive_isolation_frontend":
        return fail("Sky130 balanced frontend work order should name the new balanced frontend cell")
    if balanced_work_order.get("required_bias_reduction_factor", 0) < 100:
        return fail("Sky130 balanced frontend work order should carry the extracted wrong-sign reduction target")
    if len(balanced_work_order.get("ports", [])) < 9 or len(balanced_work_order.get("acceptance_checks", [])) < 7:
        return fail("Sky130 balanced frontend work order should define concrete ports and acceptance checks")
    if balanced_work_order.get("accepted_ready_now") is not False or balanced_work_order.get("accepted_post_layout_written") is not False:
        return fail("Sky130 balanced frontend work order must not write accepted evidence")
    balanced_work_order_page = (ROOT / "site" / "research" / "sky130-balanced-frontend-work-order.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Balanced Frontend Work Order", "sky130_balanced_capacitive_isolation_frontend", "balanced measuring node", "clk_sample", "clk_latch", "do not accept an ideal capacitor overlay"]:
        if marker not in balanced_work_order_page:
            return fail(f"site/research/sky130-balanced-frontend-work-order.html missing marker {marker!r}")

    balanced_extraction = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-balanced-frontend-starter-extraction.json").read_text(encoding="utf-8"))
    if balanced_extraction.get("result_type") != "sky130_balanced_frontend_starter_extraction":
        return fail("Sky130 balanced frontend starter extraction has wrong result_type")
    if balanced_extraction.get("status") != "balanced_frontend_starter_extracted_not_comparator_proof":
        return fail("Sky130 balanced frontend starter extraction has unexpected status")
    if balanced_extraction.get("ports_match_work_order") is not True:
        return fail("Sky130 balanced frontend starter extraction should match the work-order port list")
    if balanced_extraction.get("sense_capacitance_balanced") is not True or balanced_extraction.get("sense_capacitance_delta_ff", 1) > 0.001:
        return fail("Sky130 balanced frontend starter extraction should have matched sense-node capacitance")
    if balanced_extraction.get("accepted_ready_now") is not False or balanced_extraction.get("accepted_post_layout_written") is not False:
        return fail("Sky130 balanced frontend starter extraction must not write accepted evidence")
    balanced_extraction_page = (ROOT / "site" / "research" / "sky130-balanced-frontend-starter-extraction.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Balanced Frontend Starter Extraction", "sense capacitance delta fF", "balanced measuring nodes", "Capacitance Totals", "does not prove sign preservation"]:
        if marker not in balanced_extraction_page:
            return fail(f"site/research/sky130-balanced-frontend-starter-extraction.html missing marker {marker!r}")

    balanced_sign = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-balanced-frontend-sign-preservation.json").read_text(encoding="utf-8"))
    if balanced_sign.get("result_type") != "sky130_balanced_frontend_sign_preservation":
        return fail("Sky130 balanced frontend sign preservation has wrong result_type")
    if balanced_sign.get("status") != "balanced_extracted_frontend_preserves_sign_not_comparator_proof":
        return fail("Sky130 balanced frontend sign preservation has unexpected status")
    if balanced_sign.get("case_count") != 4 or balanced_sign.get("passing_case_count") != 4:
        return fail("Sky130 balanced frontend sign preservation should pass four extracted sense-node cases")
    if not all(row.get("sign_preserved") is True for row in balanced_sign.get("rows", [])):
        return fail("Sky130 balanced frontend sign preservation should preserve every measured sign")
    if balanced_sign.get("accepted_ready_now") is not False or balanced_sign.get("accepted_post_layout_written") is not False:
        return fail("Sky130 balanced frontend sign preservation must not write accepted evidence")
    balanced_sign_page = (ROOT / "site" / "research" / "sky130-balanced-frontend-sign-preservation.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Balanced Frontend Sign Preservation", "passing case count", "sense-node handoff", "does not prove active reset devices", "accepted post-layout converter evidence"]:
        if marker not in balanced_sign_page:
            return fail(f"site/research/sky130-balanced-frontend-sign-preservation.html missing marker {marker!r}")

    balanced_latch = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-balanced-frontend-latch-decision.json").read_text(encoding="utf-8"))
    if balanced_latch.get("result_type") != "sky130_balanced_frontend_latch_decision":
        return fail("Sky130 balanced frontend latch decision has wrong result_type")
    if balanced_latch.get("status") != "balanced_frontend_latch_decision_open_sense_signal_too_small":
        return fail("Sky130 balanced frontend latch decision should remain open because the sense signal is small")
    if balanced_latch.get("case_count") != 4 or balanced_latch.get("sign_preserved_case_count") != 4:
        return fail("Sky130 balanced frontend latch decision should preserve sign in four source cases")
    if balanced_latch.get("minimum_sense_to_latch_input_ratio", 1) >= 0.2:
        return fail("Sky130 balanced frontend latch decision should show the sense signal is far below the latch proxy input")
    if balanced_latch.get("latch_decision_proven") is not False:
        return fail("Sky130 balanced frontend latch decision must not prove latch decision")
    if balanced_latch.get("accepted_ready_now") is not False or balanced_latch.get("accepted_post_layout_written") is not False:
        return fail("Sky130 balanced frontend latch decision must not write accepted evidence")
    balanced_latch_page = (ROOT / "site" / "research" / "sky130-balanced-frontend-latch-decision.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Balanced Frontend Latch Decision", "sense-to-latch-input ratio", "sign is not the same as a digital decision", "latch decision remains an open gate", "does not prove latch resolution"]:
        if marker not in balanced_latch_page:
            return fail(f"site/research/sky130-balanced-frontend-latch-decision.html missing marker {marker!r}")

    sense_gain = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-balanced-frontend-sense-gain-target.json").read_text(encoding="utf-8"))
    if sense_gain.get("result_type") != "sky130_balanced_frontend_sense_gain_target":
        return fail("Sky130 balanced frontend sense-gain target has wrong result_type")
    if sense_gain.get("status") != "sense_gain_target_ready_before_latch_rerun":
        return fail("Sky130 balanced frontend sense-gain target has unexpected status")
    if sense_gain.get("required_sense_gain_improvement_x", 0) <= 10:
        return fail("Sky130 balanced frontend sense-gain target should require more than 10x improvement")
    if sense_gain.get("current_minimum_sample_to_sense_transfer_ratio", 1) >= 0.2:
        return fail("Sky130 balanced frontend sense-gain target should show weak current transfer")
    if sense_gain.get("accepted_ready_now") is not False or sense_gain.get("accepted_post_layout_written") is not False:
        return fail("Sky130 balanced frontend sense-gain target must not write accepted evidence")
    sense_gain_page = (ROOT / "site" / "research" / "sky130-balanced-frontend-sense-gain-target.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Balanced Frontend Sense-Gain Target", "required sense gain improvement", "sample-to-sense transfer", "one tenth of the needed latch input", "does not prove latch resolution"]:
        if marker not in sense_gain_page:
            return fail(f"site/research/sky130-balanced-frontend-sense-gain-target.html missing marker {marker!r}")

    strong_sense = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-strong-sense-frontend-candidate.json").read_text(encoding="utf-8"))
    if strong_sense.get("result_type") != "sky130_strong_sense_frontend_candidate":
        return fail("Sky130 strong sense frontend candidate has wrong result_type")
    if strong_sense.get("status") != "strong_sense_candidate_improves_coupling_but_transfer_still_below_latch_target":
        return fail("Sky130 strong sense frontend candidate has unexpected status")
    if strong_sense.get("direct_coupling_improvement_x", 0) <= 5:
        return fail("Sky130 strong sense frontend candidate should improve direct sample-to-sense coupling by more than 5x")
    if strong_sense.get("minimum_sample_to_sense_transfer_ratio", 0) <= 0.3:
        return fail("Sky130 strong sense frontend candidate should improve transfer beyond the first balanced starter")
    if strong_sense.get("remaining_transfer_improvement_x", 0) <= 2:
        return fail("Sky130 strong sense frontend candidate should still show a remaining transfer gap")
    if strong_sense.get("passing_sign_case_count") != strong_sense.get("case_count"):
        return fail("Sky130 strong sense frontend candidate should preserve every measured sign")
    if strong_sense.get("accepted_ready_now") is not False or strong_sense.get("accepted_post_layout_written") is not False:
        return fail("Sky130 strong sense frontend candidate must not write accepted evidence")
    strong_sense_page = (ROOT / "site" / "research" / "sky130-strong-sense-frontend-candidate.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Strong Sense Frontend Candidate", "direct coupling improvement", "minimum sample-to-sense transfer ratio", "still below the latch target", "does not prove latch resolution"]:
        if marker not in strong_sense_page:
            return fail(f"site/research/sky130-strong-sense-frontend-candidate.html missing marker {marker!r}")

    ultra_sense = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-ultra-sense-frontend-candidate.json").read_text(encoding="utf-8"))
    if ultra_sense.get("result_type") != "sky130_ultra_sense_frontend_candidate":
        return fail("Sky130 ultra sense frontend candidate has wrong result_type")
    if ultra_sense.get("status") != "ultra_sense_candidate_transfer_still_below_latch_target":
        return fail("Sky130 ultra sense frontend candidate should remain below latch target")
    if ultra_sense.get("direct_coupling_improvement_x", 0) <= strong_sense.get("direct_coupling_improvement_x", 0):
        return fail("Sky130 ultra sense frontend candidate should improve direct coupling beyond strong candidate")
    if ultra_sense.get("minimum_sample_to_sense_transfer_ratio", 0) <= strong_sense.get("minimum_sample_to_sense_transfer_ratio", 0):
        return fail("Sky130 ultra sense frontend candidate should improve transfer beyond strong candidate")
    if ultra_sense.get("remaining_transfer_improvement_x", 0) <= 2:
        return fail("Sky130 ultra sense frontend candidate should still show a meaningful remaining transfer gap")
    if ultra_sense.get("passing_sign_case_count") != ultra_sense.get("case_count"):
        return fail("Sky130 ultra sense frontend candidate should preserve every measured sign")
    if ultra_sense.get("accepted_ready_now") is not False or ultra_sense.get("accepted_post_layout_written") is not False:
        return fail("Sky130 ultra sense frontend candidate must not write accepted evidence")
    ultra_sense_page = (ROOT / "site" / "research" / "sky130-ultra-sense-frontend-candidate.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Ultra Sense Frontend Candidate", "direct coupling improvement", "minimum sample-to-sense transfer ratio", "still below the latch target", "does not prove latch resolution"]:
        if marker not in ultra_sense_page:
            return fail(f"site/research/sky130-ultra-sense-frontend-candidate.html missing marker {marker!r}")

    sense_efficiency = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-frontend-sense-efficiency-audit.json").read_text(encoding="utf-8"))
    if sense_efficiency.get("result_type") != "sky130_frontend_sense_efficiency_audit":
        return fail("Sky130 frontend sense efficiency audit has wrong result_type")
    if sense_efficiency.get("status") != "sense_efficiency_audit_shows_transfer_plateau_before_latch_target":
        return fail("Sky130 frontend sense efficiency audit has unexpected status")
    rows_by_candidate = {row.get("candidate"): row for row in sense_efficiency.get("rows", [])}
    for candidate in ["balanced", "strong", "ultra"]:
        if candidate not in rows_by_candidate:
            return fail(f"Sky130 frontend sense efficiency audit missing {candidate} row")
    if rows_by_candidate["balanced"].get("minimum_sample_to_sense_transfer_ratio", 1) >= rows_by_candidate["strong"].get("minimum_sample_to_sense_transfer_ratio", 0):
        return fail("Sky130 frontend sense efficiency audit should show strong improves beyond balanced")
    if rows_by_candidate["strong"].get("minimum_sample_to_sense_transfer_ratio", 1) >= rows_by_candidate["ultra"].get("minimum_sample_to_sense_transfer_ratio", 0):
        return fail("Sky130 frontend sense efficiency audit should show ultra improves beyond strong")
    if sense_efficiency.get("best_measured_transfer_ratio", 0) >= sense_efficiency.get("target_sample_to_sense_transfer_ratio", 1):
        return fail("Sky130 frontend sense efficiency audit must remain below latch target")
    if sense_efficiency.get("remaining_transfer_improvement_x", 0) <= 2:
        return fail("Sky130 frontend sense efficiency audit should retain a meaningful remaining transfer gap")
    if sense_efficiency.get("accepted_ready_now") is not False or sense_efficiency.get("accepted_post_layout_written") is not False:
        return fail("Sky130 frontend sense efficiency audit must not write accepted evidence")
    sense_efficiency_page = (ROOT / "site" / "research" / "sky130-frontend-sense-efficiency-audit.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Frontend Sense Efficiency Audit", "The comparator does not see capacitance. It sees voltage.", "pipe grows faster than the bucket", "0.437908", "2.28x", "does not prove latch resolution"]:
        if marker not in sense_efficiency_page:
            return fail(f"site/research/sky130-frontend-sense-efficiency-audit.html missing marker {marker!r}")

    differential_control = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "differential-sampling-control-proof-ngspice.json").read_text(encoding="utf-8"))
    if differential_control.get("result_type") != "differential_sampling_control_proof_ngspice":
        return fail("differential sampling control proof ngspice has wrong result_type")
    if differential_control.get("status") != "differential_sampling_control_proof_passed_topology_only_not_converter_proof":
        return fail("differential sampling control proof ngspice has unexpected status")
    if differential_control.get("sky130_transistor_model_used") is not False:
        return fail("differential sampling control proof ngspice should be marked as a non-Sky130 topology control")
    if differential_control.get("case_count") != 3 or differential_control.get("measured_case_count") != 3:
        return fail("differential sampling control proof ngspice should measure all three cases")
    if differential_control.get("diff_hold_pass_count") != 2:
        return fail("differential sampling control proof ngspice should pass only the common-injection cases")
    if differential_control.get("worst_diff_hold_abs_delta_v", 0) <= differential_control.get("half_lsb_12b_v", 0):
        return fail("differential sampling control proof ngspice should show mismatch remains above half LSB")
    if differential_control.get("candidate_post_layout_written") is not False or differential_control.get("accepted_post_layout_written") is not False:
        return fail("differential sampling control proof ngspice must not write candidate or accepted post-layout")
    differential_control_page = (ROOT / "site" / "research" / "differential-sampling-control-proof-ngspice.html").read_text(encoding="utf-8")
    for marker in ["Differential Sampling Control Proof Ngspice", "differential_sampling_control_proof_passed_topology_only_not_converter_proof", "Sky130 transistor model used", "the decision voltage barely moves", "does not prove Sky130 transistor behavior"]:
        if marker not in differential_control_page:
            return fail(f"site/research/differential-sampling-control-proof-ngspice.html missing marker {marker!r}")

    single_device_injection = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-single-device-charge-injection-ngspice.json").read_text(encoding="utf-8"))
    if single_device_injection.get("result_type") != "sky130_single_device_charge_injection_ngspice":
        return fail("Sky130 single-device charge injection ngspice has wrong result_type")
    if single_device_injection.get("status") != "sky130_single_device_charge_injection_characterized_not_converter_proof":
        return fail("Sky130 single-device charge injection ngspice has unexpected status")
    if single_device_injection.get("topology") != "single_sky130_nfet_sample_path_to_hold_capacitor":
        return fail("Sky130 single-device charge injection ngspice should name the tested topology")
    if single_device_injection.get("case_count") != 3:
        return fail("Sky130 single-device charge injection ngspice should run three sizing/capacitance cases")
    if single_device_injection.get("measured_case_count") != 0:
        return fail("Sky130 single-device charge injection ngspice currently documents the single-device edge fixture as not numerically stable")
    if single_device_injection.get("timed_out_case_count") != 3:
        return fail("Sky130 single-device charge injection ngspice should account for all three bounded timeouts")
    if single_device_injection.get("candidate_post_layout_written") is not False or single_device_injection.get("accepted_post_layout_written") is not False:
        return fail("Sky130 single-device charge injection ngspice must not write candidate or accepted post-layout")
    single_device_page = (ROOT / "site" / "research" / "sky130-single-device-charge-injection-ngspice.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Single-Device Charge Injection Ngspice", "sky130_single_device_charge_injection_characterized_not_converter_proof", "single_sky130_nfet_sample_path", "smallest normal-switch unit", "does not prove a complete sampling switch"]:
        if marker not in single_device_page:
            return fail(f"site/research/sky130-single-device-charge-injection-ngspice.html missing marker {marker!r}")

    clock_edge = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-sample-switch-clock-edge-sweep.json").read_text(encoding="utf-8"))
    if clock_edge.get("result_type") != "sky130_sample_switch_clock_edge_sweep":
        return fail("Sky130 sample switch clock edge sweep has wrong result_type")
    if clock_edge.get("status") != "sky130_sample_switch_clock_edge_pair_characterized_not_converter_proof":
        return fail("Sky130 sample switch clock edge sweep has unexpected status")
    if clock_edge.get("config_count") != 2 or clock_edge.get("case_count") != 2:
        return fail("Sky130 sample switch clock edge sweep should run two mid-input edge cases")
    if clock_edge.get("measured_case_count") != 2 or clock_edge.get("timed_out_case_count") != 0:
        return fail("Sky130 sample switch clock edge sweep should measure both edge cases")
    if clock_edge.get("best_config") != "baseline_20ps_mid_input":
        return fail("Sky130 sample switch clock edge sweep should show 100 ps does not beat the 20 ps baseline")
    if clock_edge.get("best_worst_hold_abs_delta_v", 0) <= clock_edge.get("half_lsb_12b_v", 0):
        return fail("Sky130 sample switch clock edge sweep should preserve the baseline hold failure")
    if clock_edge.get("candidate_post_layout_written") is not False or clock_edge.get("accepted_post_layout_written") is not False:
        return fail("Sky130 sample switch clock edge sweep must not write candidate or accepted post-layout")
    clock_edge_page = (ROOT / "site" / "research" / "sky130-sample-switch-clock-edge-sweep.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Sample Switch Clock Edge Sweep", "sky130_sample_switch_clock_edge_pair_characterized_not_converter_proof", "20 ps edge", "100 ps edge", "does not prove a complete sample-and-hold architecture"]:
        if marker not in clock_edge_page:
            return fail(f"site/research/sky130-sample-switch-clock-edge-sweep.html missing marker {marker!r}")

    design_target = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-sample-hold-design-target.json").read_text(encoding="utf-8"))
    if design_target.get("result_type") != "sky130_sample_hold_design_target":
        return fail("Sky130 sample-hold design target has wrong result_type")
    if design_target.get("status") != "sky130_sample_hold_design_target_has_one_passing_decision_voltage_not_converter_proof":
        return fail("Sky130 sample-hold design target has unexpected status")
    if design_target.get("best_measured_hold_error_v", 1) > design_target.get("half_lsb_12b_v", 0):
        return fail("Sky130 sample-hold design target should reflect the first measured passing decision-voltage case")
    if design_target.get("best_measured_source") != "sky130-differential-dummy-candidate-input-sweep":
        return fail("Sky130 sample-hold design target should choose the broader differential dummy input sweep as the best measured source")
    if design_target.get("remaining_margin_x_from_best_measured", 0) <= 1.0:
        return fail("Sky130 sample-hold design target should report positive margin for the best measured case")
    if design_target.get("candidate_post_layout_written") is not False or design_target.get("accepted_post_layout_written") is not False:
        return fail("Sky130 sample-hold design target must not write candidate or accepted post-layout")
    design_target_page = (ROOT / "site" / "research" / "sky130-sample-hold-design-target.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Sample-Hold Design Target", "sky130_sample_hold_design_target_has_one_passing_decision_voltage_not_converter_proof", "best measured passes half LSB 12b", "cleared the nominal low, mid, and high input gate", "does not prove comparator behavior"]:
        if marker not in design_target_page:
            return fail(f"site/research/sky130-sample-hold-design-target.html missing marker {marker!r}")

    matching_requirement = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-differential-matching-requirement.json").read_text(encoding="utf-8"))
    if matching_requirement.get("result_type") != "sky130_differential_matching_requirement":
        return fail("Sky130 differential matching requirement has wrong result_type")
    if matching_requirement.get("status") != "sky130_differential_matching_requirement_defined_not_converter_proof":
        return fail("Sky130 differential matching requirement has unexpected status")
    if matching_requirement.get("max_allowed_differential_mismatch_v", 1) > matching_requirement.get("half_lsb_12b_v", 0):
        return fail("Sky130 differential matching requirement should cap mismatch at the half-LSB line")
    if matching_requirement.get("best_measured_margin_x", 0) <= 1.0:
        return fail("Sky130 differential matching requirement should report margin for the passing dummy case")
    if matching_requirement.get("required_common_rejection_percent", 0) < 85.0:
        return fail("Sky130 differential matching requirement should still require high rejection from the uncancelled reference")
    if matching_requirement.get("control_mismatch_case_over_limit_x", 0) <= 1.0:
        return fail("Sky130 differential matching requirement should show the 0.3 mV mismatch case is over limit")
    if matching_requirement.get("candidate_post_layout_written") is not False or matching_requirement.get("accepted_post_layout_written") is not False:
        return fail("Sky130 differential matching requirement must not write candidate or accepted post-layout")
    matching_page = (ROOT / "site" / "research" / "sky130-differential-matching-requirement.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Differential Matching Requirement", "sky130_differential_matching_requirement_defined_not_converter_proof", "best measured margin", "required common rejection", "does not prove Sky130 transistor matching"]:
        if marker not in matching_page:
            return fail(f"site/research/sky130-differential-matching-requirement.html missing marker {marker!r}")

    fixture_work_order = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-next-transistor-fixture-work-order.json").read_text(encoding="utf-8"))
    if fixture_work_order.get("result_type") != "sky130_next_transistor_fixture_work_order":
        return fail("Sky130 next transistor fixture work order has wrong result_type")
    if fixture_work_order.get("status") != "sky130_next_transistor_fixture_work_order_ready_not_converter_proof":
        return fail("Sky130 next transistor fixture work order has unexpected status")
    if fixture_work_order.get("recommended_next_topology") != "broaden_differential_dummy_cancellation_candidate":
        return fail("Sky130 next transistor fixture work order should recommend broadening the passing differential dummy candidate")
    if fixture_work_order.get("remaining_margin_x", 0) <= 1.0:
        return fail("Sky130 next transistor fixture work order should preserve the passing candidate margin")
    if fixture_work_order.get("remaining_comparator_offset_or_noise_budget_mv", 0) <= 0:
        return fail("Sky130 next transistor fixture work order should carry the comparator/noise budget")
    if fixture_work_order.get("max_passing_tested_decision_uncertainty_mv", 0) <= 0:
        return fail("Sky130 next transistor fixture work order should carry the tested decision uncertainty target")
    if fixture_work_order.get("max_allowed_differential_mismatch_mv", 1) > 0.22:
        return fail("Sky130 next transistor fixture work order should preserve the mismatch limit")
    if len(fixture_work_order.get("acceptance_tests", [])) < 6:
        return fail("Sky130 next transistor fixture work order should define acceptance tests")
    if fixture_work_order.get("candidate_post_layout_written") is not False or fixture_work_order.get("accepted_post_layout_written") is not False:
        return fail("Sky130 next transistor fixture work order must not write candidate or accepted post-layout")
    fixture_work_order_page = (ROOT / "site" / "research" / "sky130-next-transistor-fixture-work-order.html").read_text(encoding="utf-8")
    for marker in ["Sky130 Next Transistor Fixture Work Order", "sky130_next_transistor_fixture_work_order_ready_not_converter_proof", "Acceptance Tests", "copy the known-running transmission-gate hold-mode deck exactly", "does not prove a new circuit"]:
        if marker not in fixture_work_order_page:
            return fail(f"site/research/sky130-next-transistor-fixture-work-order.html missing marker {marker!r}")

    sky130_env = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "analog-converter-sky130-workbench-env.json").read_text(encoding="utf-8"))
    if sky130_env.get("result_type") != "analog_converter_sky130_workbench_env":
        return fail("analog converter Sky130 workbench environment has wrong result_type")
    if sky130_env.get("status") != "sky130_workbench_environment_ready_not_layout":
        return fail("analog converter Sky130 workbench environment should be setup-only")
    if sky130_env.get("env_file_count") != 4:
        return fail("analog converter Sky130 workbench environment should write four files")
    if sky130_env.get("all_pdk_files_present") is not True:
        return fail("analog converter Sky130 workbench environment should find PDK files")
    if sky130_env.get("physical_converter_cell_count") != 4:
        return fail("analog converter Sky130 workbench environment should find four named converter starter cells")
    if sky130_env.get("candidate_evidence_written") is not False:
        return fail("analog converter Sky130 workbench environment should not write candidate evidence")
    for path in [
        "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/.magicrc",
        "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/xschemrc.local",
        "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/sky130-ngspice.includes",
        "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/run-layout-env-check.sh",
    ]:
        if not (ROOT / path).is_file():
            return fail(f"analog converter Sky130 workbench environment missing {path}")
    env_page = (ROOT / "site" / "research" / "analog-converter-sky130-workbench-env.html").read_text(encoding="utf-8")
    for marker in ["Analog Converter Sky130 Workbench Environment", "sky130_workbench_environment_ready_not_layout", "environment file count", "physical converter cell count: <code>4</code>", "candidate evidence written: <code>False</code>", "run-layout-env-check.sh", "The PDK tells the tools how to read process-specific shapes", "does not draw converter cells"]:
        if marker not in env_page:
            return fail(f"site/research/analog-converter-sky130-workbench-env.html missing marker {marker!r}")

    physical_cell_gate = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "analog-converter-physical-cell-gate.json").read_text(encoding="utf-8"))
    if physical_cell_gate.get("result_type") != "analog_converter_physical_cell_gate":
        return fail("analog converter physical cell gate has wrong result_type")
    if physical_cell_gate.get("status") != "physical_cells_present_waiting_for_extracted_artifacts":
        return fail("analog converter physical cell gate should remain open until all candidate artifacts exist")
    if physical_cell_gate.get("required_cell_count") != 4:
        return fail("analog converter physical cell gate should require four named cells")
    if physical_cell_gate.get("present_cell_count") != 4:
        return fail("analog converter physical cell gate should find four physical starter cells")
    if physical_cell_gate.get("missing_cell_count") != 0:
        return fail("analog converter physical cell gate should report no missing physical starter cells")
    if physical_cell_gate.get("present_extracted_artifact_count") != 3:
        return fail("analog converter physical cell gate should find the three extracted starter cell artifacts")
    if physical_cell_gate.get("ready_for_candidate_post_layout_payload") is not False:
        return fail("analog converter physical cell gate should not be candidate-ready yet")
    gate_cell_names = {item.get("name") for item in physical_cell_gate.get("required_cells", []) if isinstance(item, dict)}
    for name in ["row_dac_10b", "sar_readout_12b", "shared_converter_mux", "aimc_converter_macro"]:
        if name not in gate_cell_names:
            return fail(f"analog converter physical cell gate missing cell {name!r}")
    gate_page = (ROOT / "site" / "research" / "analog-converter-physical-cell-gate.html").read_text(encoding="utf-8")
    for marker in ["Analog Converter Physical Cell Gate", "physical_cells_present_waiting_for_extracted_artifacts", "present cell count: <code>4</code>", "missing cell count: <code>0</code>", "present extracted artifact count: <code>3</code>", "row_dac_10b", "sar_readout_12b", "shared_converter_mux", "aimc_converter_macro", "A converter is not proven by having the right tools", "does not count environment files"]:
        if marker not in gate_page:
            return fail(f"site/research/analog-converter-physical-cell-gate.html missing marker {marker!r}")

    physical_flow_run = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "analog-converter-physical-flow-run.json").read_text(encoding="utf-8"))
    if physical_flow_run.get("result_type") != "analog_converter_physical_flow_run":
        return fail("analog converter physical flow run has wrong result_type")
    if physical_flow_run.get("status") != "physical_flow_ready_for_manual_extraction_commands":
        return fail("analog converter physical flow run should be ready for extraction commands after starter cells exist")
    if physical_flow_run.get("present_cell_count") != 4:
        return fail("analog converter physical flow run should find four physical starter cells")
    if physical_flow_run.get("missing_cell_count") != 0:
        return fail("analog converter physical flow run should report no missing cells")
    if physical_flow_run.get("blocked_command_count") != 0:
        return fail("analog converter physical flow run should not block extraction commands after starter cells exist")
    if physical_flow_run.get("runnable_command_count") != 4:
        return fail("analog converter physical flow run should have four runnable extraction commands")
    flow_page = (ROOT / "site" / "research" / "analog-converter-physical-flow-run.html").read_text(encoding="utf-8")
    for marker in ["Analog Converter Physical Flow Run", "physical_flow_ready_for_manual_extraction_commands", "blocked command count: <code>0</code>", "runnable command count: <code>4</code>", "magic -dnull -noconsole", "row_dac_10b.mag", "A physical flow has to start from shapes", "does not fabricate Magic output"]:
        if marker not in flow_page:
            return fail(f"site/research/analog-converter-physical-flow-run.html missing marker {marker!r}")

    guarded_import_page = (ROOT / "site" / "research" / "guarded-simulator-payload-import.html").read_text(encoding="utf-8")
    for marker in ["reject <code>dry_run: true</code>", "aihwkit-analog-error-simulation.json", "crosssim-analog-error-simulation.json", "--expect-reject", "backend strict-tool readiness", "Refused Claim"]:
        if marker not in guarded_import_page:
            return fail(f"site/research/guarded-simulator-payload-import.html missing marker {marker!r}")

    tool_check = (ROOT / "scripts" / "check_tools.sh").read_text(encoding="utf-8")
    for marker in ["Optional simulator adapter checks", "aihwkit python module", "crosssim python module", "Optional missing simulator adapters"]:
        if marker not in tool_check:
            return fail(f"scripts/check_tools.sh missing optional simulator adapter marker {marker!r}")

    optional_install = (ROOT / "scripts" / "install_optional_aimc_simulators.sh").read_text(encoding="utf-8")
    for marker in ["pip install aihwkit", "github.com/sandialabs/cross-sim", "aimc-simulators-venv", "check_aimc_simulator_adapters.py"]:
        if marker not in optional_install:
            return fail(f"scripts/install_optional_aimc_simulators.sh missing marker {marker!r}")
    optional_install_page = (ROOT / "site" / "research" / "optional-aimc-simulator-install-path.html").read_text(encoding="utf-8")
    for marker in ["Installation is not evidence", "pip install aihwkit", "github.com/sandialabs/cross-sim", "Refused Claim", "strict simulator payload"]:
        if marker not in optional_install_page:
            return fail(f"site/research/optional-aimc-simulator-install-path.html missing marker {marker!r}")
    optional_run = (ROOT / "scripts" / "run_optional_aimc_simulator_payloads.py").read_text(encoding="utf-8")
    for marker in ["AIHWKIT_OUT", "CROSSSIM_OUT", "optional-simulator-payload-run-summary.json", "external_simulator_small_fixture"]:
        if marker not in optional_run:
            return fail(f"scripts/run_optional_aimc_simulator_payloads.py missing marker {marker!r}")
    optional_run_summary = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "optional-simulator-payload-run-summary.json").read_text(encoding="utf-8"))
    if optional_run_summary.get("result_type") != "optional_aimc_simulator_payload_run_summary":
        return fail("optional simulator payload summary has wrong result_type")
    optional_run_page = (ROOT / "site" / "research" / "optional-simulator-payload-run-path.html").read_text(encoding="utf-8")
    for marker in ["package import alone is not a run", "strict simulator payload", "writes the matching strict payload path", "Refused Claim"]:
        if marker not in optional_run_page:
            return fail(f"site/research/optional-simulator-payload-run-path.html missing marker {marker!r}")
    workload_run = (ROOT / "scripts" / "run_workload_aimc_simulator_payloads.py").read_text(encoding="utf-8")
    for marker in ["AIHWKIT_OUT", "CROSSSIM_OUT", "workload-simulator-payload-run-summary.json", "external_simulator_backend_candidate_workload"]:
        if marker not in workload_run:
            return fail(f"scripts/run_workload_aimc_simulator_payloads.py missing marker {marker!r}")
    workload_summary = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "workload-simulator-payload-run-summary.json").read_text(encoding="utf-8"))
    if workload_summary.get("result_type") != "workload_aimc_simulator_payload_run_summary":
        return fail("workload simulator payload summary has wrong result_type")
    if workload_summary.get("candidate_count") != 3:
        return fail("workload simulator payload summary should cover 3 allowed analog candidates")
    workload_page = (ROOT / "site" / "research" / "workload-shaped-simulator-evidence.html").read_text(encoding="utf-8")
    for marker in ["backend-selected analog candidate", "measured_fixed_projection_tile", "backend_dense1.matmul", "backend_dense2.matmul", "Refused Claim"]:
        if marker not in workload_page:
            return fail(f"site/research/workload-shaped-simulator-evidence.html missing marker {marker!r}")
    tensor_run = (ROOT / "scripts" / "run_tensor_shape_aimc_simulator_payloads.py").read_text(encoding="utf-8")
    for marker in ["AIHWKIT_OUT", "CROSSSIM_OUT", "tensor-shape-simulator-payload-run-summary.json", "external_simulator_backend_tensor_shape_replay"]:
        if marker not in tensor_run:
            return fail(f"scripts/run_tensor_shape_aimc_simulator_payloads.py missing marker {marker!r}")
    tensor_summary = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "tensor-shape-simulator-payload-run-summary.json").read_text(encoding="utf-8"))
    if tensor_summary.get("result_type") != "tensor_shape_aimc_simulator_payload_run_summary":
        return fail("tensor-shape simulator payload summary has wrong result_type")
    if tensor_summary.get("candidate_count") != 2:
        return fail("tensor-shape simulator payload summary should cover 2 backend analog MatMul candidates")
    tensor_page = (ROOT / "site" / "research" / "tensor-shaped-simulator-evidence.html").read_text(encoding="utf-8")
    for marker in ["dense1.matmul", "dense2.matmul", "deterministic fixture weights", "Refused Claim", "trained package weights"]:
        if marker not in tensor_page:
            return fail(f"site/research/tensor-shaped-simulator-evidence.html missing marker {marker!r}")
    trained_run = (ROOT / "scripts" / "run_trained_weight_aimc_simulator_payloads.py").read_text(encoding="utf-8")
    for marker in ["AIHWKIT_OUT", "CROSSSIM_OUT", "trained-weight-simulator-payload-run-summary.json", "external_simulator_backend_trained_weight_replay"]:
        if marker not in trained_run:
            return fail(f"scripts/run_trained_weight_aimc_simulator_payloads.py missing marker {marker!r}")
    trained_summary = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "trained-weight-simulator-payload-run-summary.json").read_text(encoding="utf-8"))
    if trained_summary.get("result_type") != "trained_weight_aimc_simulator_payload_run_summary":
        return fail("trained-weight simulator payload summary has wrong result_type")
    if trained_summary.get("candidate_count") != 2:
        return fail("trained-weight simulator payload summary should cover 2 backend analog MatMul candidates")
    trained_page = (ROOT / "site" / "research" / "trained-weight-simulator-evidence.html").read_text(encoding="utf-8")
    for marker in ["tiny-mlp.onnx", "w1", "w2", "AIHWKIT and CrossSim", "Refused Claim"]:
        if marker not in trained_page:
            return fail(f"site/research/trained-weight-simulator-evidence.html missing marker {marker!r}")
    projection_run = (ROOT / "scripts" / "run_projection_stack_aimc_simulator_payloads.py").read_text(encoding="utf-8")
    for marker in ["AIHWKIT_OUT", "CROSSSIM_OUT", "projection-stack-simulator-payload-run-summary.json", "external_simulator_projection_stack_trained_weight_replay"]:
        if marker not in projection_run:
            return fail(f"scripts/run_projection_stack_aimc_simulator_payloads.py missing marker {marker!r}")
    projection_summary = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "projection-stack-simulator-payload-run-summary.json").read_text(encoding="utf-8"))
    if projection_summary.get("result_type") != "projection_stack_aimc_simulator_payload_run_summary":
        return fail("projection-stack simulator payload summary has wrong result_type")
    if projection_summary.get("candidate_count") != 4:
        return fail("projection-stack simulator payload summary should cover 4 MatMul candidates")
    projection_page = (ROOT / "site" / "research" / "projection-stack-simulator-evidence.html").read_text(encoding="utf-8")
    for marker in ["projection-stack.onnx", "proj.q.matmul", "proj.k.matmul", "proj.v.matmul", "proj.out.matmul", "Refused Claim"]:
        if marker not in projection_page:
            return fail(f"site/research/projection-stack-simulator-evidence.html missing marker {marker!r}")
    transformer_mlp_run = (ROOT / "scripts" / "run_transformer_mlp_block_aimc_simulator_payloads.py").read_text(encoding="utf-8")
    for marker in ["transformer_mlp_block_aimc_simulator_payloads", "transformer-mlp-block-simulator-payload-run-summary.json", "external_simulator_transformer_mlp_block_trained_weight_replay"]:
        if marker not in transformer_mlp_run:
            return fail(f"scripts/run_transformer_mlp_block_aimc_simulator_payloads.py missing marker {marker!r}")
    transformer_mlp_summary = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "transformer-mlp-block-simulator-payload-run-summary.json").read_text(encoding="utf-8"))
    if transformer_mlp_summary.get("result_type") != "transformer_mlp_block_aimc_simulator_payload_run_summary":
        return fail("transformer MLP block simulator payload summary has wrong result_type")
    if transformer_mlp_summary.get("candidate_count") != 4:
        return fail("transformer MLP block simulator payload summary should cover 4 MatMul candidates")
    transformer_mlp_page = (ROOT / "site" / "research" / "transformer-mlp-block-simulator-evidence.html").read_text(encoding="utf-8")
    for marker in ["transformer-mlp-block.onnx", "digital-only operations", "CrossSim writes a payload", "AIHWKIT writes a payload", "Refused Claim"]:
        if marker not in transformer_mlp_page:
            return fail(f"site/research/transformer-mlp-block-simulator-evidence.html missing marker {marker!r}")
    calibrated_transformer_mlp_run = (ROOT / "scripts" / "run_calibrated_transformer_mlp_block_aimc_simulator_payloads.py").read_text(encoding="utf-8")
    for marker in ["calibrated_transformer_mlp_block_aimc_simulator_payloads", "calibrated-transformer-mlp-block-simulator-payload-run-summary.json", "external_simulator_calibrated_transformer_mlp_block_replay"]:
        if marker not in calibrated_transformer_mlp_run:
            return fail(f"scripts/run_calibrated_transformer_mlp_block_aimc_simulator_payloads.py missing marker {marker!r}")
    calibrated_transformer_mlp_summary = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "calibrated-transformer-mlp-block-simulator-payload-run-summary.json").read_text(encoding="utf-8"))
    if calibrated_transformer_mlp_summary.get("result_type") != "calibrated_transformer_mlp_block_aimc_simulator_payload_run_summary":
        return fail("calibrated transformer MLP block simulator payload summary has wrong result_type")
    if calibrated_transformer_mlp_summary.get("candidate_count") != 4:
        return fail("calibrated transformer MLP block simulator payload summary should cover 4 MatMul candidates")
    calibrated_transformer_mlp_page = (ROOT / "site" / "research" / "calibrated-transformer-mlp-block-simulator-evidence.html").read_text(encoding="utf-8")
    for marker in ["held-out calibration", "CrossSim passes", "AIHWKIT also runs", "nonlinear and residual operations digital", "Refused Claim"]:
        if marker not in calibrated_transformer_mlp_page:
            return fail(f"site/research/calibrated-transformer-mlp-block-simulator-evidence.html missing marker {marker!r}")
    calibrated_deep_mlp_run = (ROOT / "scripts" / "run_calibrated_deep_transformer_mlp_stack_aimc_simulator_payloads.py").read_text(encoding="utf-8")
    for marker in ["calibrated_deep_transformer_mlp_stack_aimc_simulator_payloads", "calibrated-deep-transformer-mlp-stack-simulator-payload-run-summary.json", "external_simulator_calibrated_deep_transformer_mlp_stack_replay"]:
        if marker not in calibrated_deep_mlp_run:
            return fail(f"scripts/run_calibrated_deep_transformer_mlp_stack_aimc_simulator_payloads.py missing marker {marker!r}")
    calibrated_deep_mlp_summary = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "calibrated-deep-transformer-mlp-stack-simulator-payload-run-summary.json").read_text(encoding="utf-8"))
    if calibrated_deep_mlp_summary.get("result_type") != "calibrated_deep_transformer_mlp_stack_aimc_simulator_payload_run_summary":
        return fail("calibrated deep transformer MLP stack simulator payload summary has wrong result_type")
    if calibrated_deep_mlp_summary.get("candidate_count") != 12:
        return fail("calibrated deep transformer MLP stack simulator payload summary should cover 12 MatMul candidates")
    calibrated_deep_mlp_page = (ROOT / "site" / "research" / "calibrated-deep-transformer-mlp-stack-simulator-evidence.html").read_text(encoding="utf-8")
    for marker in ["deep-transformer-mlp-stack.onnx", "twelve fixed-weight MatMul", "CrossSim writes a passing payload", "AIHWKIT writes a payload", "Refused Claim"]:
        if marker not in calibrated_deep_mlp_page:
            return fail(f"site/research/calibrated-deep-transformer-mlp-stack-simulator-evidence.html missing marker {marker!r}")
    attention_run = (ROOT / "scripts" / "run_attention_block_aimc_simulator_payloads.py").read_text(encoding="utf-8")
    for marker in ["AIHWKIT_OUT", "CROSSSIM_OUT", "attention-block-simulator-payload-run-summary.json", "external_simulator_attention_block_trained_weight_replay"]:
        if marker not in attention_run:
            return fail(f"scripts/run_attention_block_aimc_simulator_payloads.py missing marker {marker!r}")
    attention_summary = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "attention-block-simulator-payload-run-summary.json").read_text(encoding="utf-8"))
    if attention_summary.get("result_type") != "attention_block_aimc_simulator_payload_run_summary":
        return fail("attention-block simulator payload summary has wrong result_type")
    if attention_summary.get("candidate_count") != 4:
        return fail("attention-block simulator payload summary should cover 4 static projection candidates")
    attention_page = (ROOT / "site" / "research" / "attention-block-simulator-evidence.html").read_text(encoding="utf-8")
    for marker in ["attention-block.onnx", "attn.q.matmul", "attn.softmax", "dynamic attention operations remain digital", "Refused Claim"]:
        if marker not in attention_page:
            return fail(f"site/research/attention-block-simulator-evidence.html missing marker {marker!r}")
    calibrated_attention_run = (ROOT / "scripts" / "run_calibrated_attention_block_aimc_simulator_payloads.py").read_text(encoding="utf-8")
    for marker in ["AIHWKIT_OUT", "CROSSSIM_OUT", "calibrated-attention-block-simulator-payload-run-summary.json", "external_simulator_calibrated_attention_block_replay"]:
        if marker not in calibrated_attention_run:
            return fail(f"scripts/run_calibrated_attention_block_aimc_simulator_payloads.py missing marker {marker!r}")
    calibrated_attention_summary = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "calibrated-attention-block-simulator-payload-run-summary.json").read_text(encoding="utf-8"))
    if calibrated_attention_summary.get("result_type") != "calibrated_attention_block_aimc_simulator_payload_run_summary":
        return fail("calibrated attention-block simulator payload summary has wrong result_type")
    if calibrated_attention_summary.get("candidate_count") != 4:
        return fail("calibrated attention-block simulator payload summary should cover 4 static projection candidates")
    calibrated_attention_page = (ROOT / "site" / "research" / "calibrated-attention-block-simulator-evidence.html").read_text(encoding="utf-8")
    for marker in ["per-output affine", "held-out input", "CrossSim passes", "AIHWKIT still exceeds", "Refused Claim"]:
        if marker not in calibrated_attention_page:
            return fail(f"site/research/calibrated-attention-block-simulator-evidence.html missing marker {marker!r}")
    calibrated_bridge_run = (ROOT / "scripts" / "run_calibrated_residual_governor_bridge.py").read_text(encoding="utf-8")
    for marker in ["calibrated_residual_governor_bridge", "calibrated-attention-block-simulator-payload-run-summary.json", "calibrated-transformer-mlp-block-simulator-payload-run-summary.json", "calibrated-deep-transformer-mlp-stack-simulator-payload-run-summary.json", "source_summaries", "accepted_as_positive_evidence", "governor_decision"]:
        if marker not in calibrated_bridge_run:
            return fail(f"scripts/run_calibrated_residual_governor_bridge.py missing marker {marker!r}")
    calibrated_bridge = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "calibrated-residual-governor-bridge.json").read_text(encoding="utf-8"))
    if calibrated_bridge.get("result_type") != "calibrated_residual_governor_bridge":
        return fail("calibrated residual governor bridge has wrong result_type")
    calibrated_bridge_rows = calibrated_bridge.get("rows") if isinstance(calibrated_bridge.get("rows"), list) else []
    calibrated_bridge_sources = {row.get("source_id") for row in calibrated_bridge_rows if isinstance(row, dict)}
    if {"attention_block", "transformer_mlp_block", "deep_transformer_mlp_stack"} - calibrated_bridge_sources:
        return fail("calibrated residual governor bridge does not cover attention, transformer MLP, and deep transformer MLP stack sources")
    if not any(isinstance(row, dict) and row.get("accepted_as_positive_evidence") is True for row in calibrated_bridge_rows):
        return fail("calibrated residual governor bridge has no accepted positive-evidence row")
    if not any(isinstance(row, dict) and row.get("governor_decision") == 1 for row in calibrated_bridge_rows):
        return fail("calibrated residual governor bridge has no analog governor decision")
    calibrated_bridge_page = (ROOT / "site" / "research" / "calibrated-residual-governor-bridge.html").read_text(encoding="utf-8")
    for marker in ["Calibrated Residual Governor Bridge", "attention-block", "transformer-MLP", "CrossSim becomes an analog candidate", "AIHWKIT does not become a candidate", "Refused Claim"]:
        if marker not in calibrated_bridge_page:
            return fail(f"site/research/calibrated-residual-governor-bridge.html missing marker {marker!r}")
    residual_placement_run = (ROOT / "scripts" / "run_residual_aware_placement_decisions.py").read_text(encoding="utf-8")
    for marker in ["residual_aware_placement_decisions", "calibrated-residual-governor-bridge.json", "backend-hardware-placement.json", "residual_aware_decision", "accepted_calibrated_source", "source_matching_policy", "fixed_weight_matmul_family_match", "evidence_target"]:
        if marker not in residual_placement_run:
            return fail(f"scripts/run_residual_aware_placement_decisions.py missing marker {marker!r}")
    residual_placement = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "residual-aware-placement-decisions.json").read_text(encoding="utf-8"))
    if residual_placement.get("result_type") != "residual_aware_placement_decisions":
        return fail("residual-aware placement decisions has wrong result_type")
    residual_placement_summary = residual_placement.get("summary") if isinstance(residual_placement.get("summary"), dict) else {}
    if residual_placement_summary.get("residual_aware_analog_allowed", 0) < 1:
        return fail("residual-aware placement decisions has no analog-allowed rows")
    if not residual_placement.get("accepted_calibrated_source"):
        return fail("residual-aware placement decisions missing accepted calibrated source")
    if residual_placement.get("accepted_calibrated_source") != "deep_transformer_mlp_stack":
        return fail("residual-aware placement decisions should select deep_transformer_mlp_stack for dense MatMul backend rows")
    source_policy = residual_placement.get("source_matching_policy") if isinstance(residual_placement.get("source_matching_policy"), dict) else {}
    if source_policy.get("mode") != "fixed_weight_matmul_family_match":
        return fail("residual-aware placement decisions missing fixed-weight MatMul source matching policy")
    if source_policy.get("selected_source") != "deep_transformer_mlp_stack":
        return fail("residual-aware placement source policy did not select deep_transformer_mlp_stack")
    residual_placement_page = (ROOT / "site" / "research" / "residual-aware-placement-decisions.html").read_text(encoding="utf-8")
    for marker in ["Residual-Aware Placement Decisions", "Structural fit is not evidence of correctness", "fixed-weight MatMul family match", "deep transformer-MLP stack", "accepted calibrated simulator evidence", "Refused Claim"]:
        if marker not in residual_placement_page:
            return fail(f"site/research/residual-aware-placement-decisions.html missing marker {marker!r}")

    layout_risk = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "crosssim-layout-risk-adapter.json").read_text(encoding="utf-8"))
    if layout_risk.get("result_type") != "crosssim_layout_risk_adapter":
        return fail("CrossSim layout-risk adapter has wrong result_type")
    if layout_risk.get("accepted_calibrated_tool") != "crosssim":
        return fail("CrossSim layout-risk adapter should be tied to CrossSim evidence")
    if layout_risk.get("source_matching_policy") != "fixed_weight_matmul_family_match":
        return fail("CrossSim layout-risk adapter should preserve the source-matching policy")
    layout_rows = layout_risk.get("rows") if isinstance(layout_risk.get("rows"), list) else []
    if len(layout_rows) != residual_placement_summary.get("residual_aware_analog_allowed"):
        return fail("CrossSim layout-risk adapter row count should match analog-allowed residual-aware rows")
    for item in layout_rows:
        if not isinstance(item, dict):
            return fail("CrossSim layout-risk adapter contains a non-object row")
        for key in ["array", "converter", "wire", "column_current", "model_boundary", "risk", "claim_effect"]:
            if key not in item:
                return fail(f"CrossSim layout-risk adapter row missing {key}")
        converter = item.get("converter") if isinstance(item.get("converter"), dict) else {}
        current = item.get("column_current") if isinstance(item.get("column_current"), dict) else {}
        if not all(key in converter for key in ["adc_bits", "dac_bits", "bit_slices", "adc_range", "dac_precision"]):
            return fail("CrossSim layout-risk adapter converter boundary is incomplete")
        if not all(key in current for key in ["min_ua", "typ_ua", "max_ua"]):
            return fail("CrossSim layout-risk adapter column-current range is incomplete")
    layout_page = (ROOT / "site" / "research" / "crosssim-layout-risk-adapter.html").read_text(encoding="utf-8")
    for marker in ["CrossSim Layout-Risk Adapter", "array size", "row wire", "converter precision", "bit slicing", "column current", "Refused Claim"]:
        if marker not in layout_page:
            return fail(f"site/research/crosssim-layout-risk-adapter.html missing marker {marker!r}")

    onnx_inventory = json.loads((ROOT / "evidence" / "aimc-hardware-lab" / "onnx-fixture-inventory.json").read_text(encoding="utf-8"))
    if onnx_inventory.get("result_type") != "onnx_fixture_inventory":
        return fail("ONNX fixture inventory has wrong result_type")
    inventory_summary = onnx_inventory.get("summary") if isinstance(onnx_inventory.get("summary"), dict) else {}
    if inventory_summary.get("selected_current_best_fixture") != "deep-transformer-mlp-stack.onnx":
        return fail("ONNX fixture inventory should select deep-transformer-mlp-stack.onnx")
    if inventory_summary.get("max_fixed_weight_matmul_count", 0) < 12:
        return fail("ONNX fixture inventory should find at least 12 fixed-weight MatMuls")
    if inventory_summary.get("usable_larger_fixtures", 0) < 3:
        return fail("ONNX fixture inventory should find multiple usable larger fixtures")
    inventory_models = onnx_inventory.get("models") if isinstance(onnx_inventory.get("models"), list) else []
    for name in ["tiny-mlp.onnx", "projection-stack.onnx", "transformer-mlp-block.onnx", "attention-block.onnx", "deep-transformer-mlp-stack.onnx"]:
        if not any(isinstance(item, dict) and item.get("name") == name for item in inventory_models):
            return fail(f"ONNX fixture inventory missing {name}")
    inventory_page = (ROOT / "site" / "research" / "onnx-fixture-inventory.html").read_text(encoding="utf-8")
    for marker in ["ONNX Fixture Inventory", "deep-transformer-mlp-stack.onnx", "fixed-weight MatMul", "current best local fixture", "Refused Claim"]:
        if marker not in inventory_page:
            return fail(f"site/research/onnx-fixture-inventory.html missing marker {marker!r}")

    aihwkit_diagnostic = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-residual-diagnostic.json").read_text(encoding="utf-8"))
    if aihwkit_diagnostic.get("result_type") != "aihwkit_residual_diagnostic":
        return fail("AIHWKIT residual diagnostic has wrong result_type")
    if aihwkit_diagnostic.get("threshold") != 0.15:
        return fail("AIHWKIT residual diagnostic should preserve the 0.15 residual threshold")
    aihwkit_diag_summary = aihwkit_diagnostic.get("summary") if isinstance(aihwkit_diagnostic.get("summary"), dict) else {}
    if aihwkit_diag_summary.get("payloads") != 10:
        return fail("AIHWKIT residual diagnostic should check 10 payloads")
    if aihwkit_diag_summary.get("threshold_fail_payloads", 0) < 5:
        return fail("AIHWKIT residual diagnostic should record the larger threshold-fail payloads")
    if not aihwkit_diag_summary.get("worst_candidate"):
        return fail("AIHWKIT residual diagnostic should record a worst candidate")
    if not isinstance(aihwkit_diag_summary.get("worst_residual_relative"), (int, float)) or aihwkit_diag_summary["worst_residual_relative"] <= 0.15:
        return fail("AIHWKIT residual diagnostic worst residual should exceed the positive boundary")
    aihwkit_diagnostic_page = (ROOT / "site" / "research" / "aihwkit-residual-diagnostic.html").read_text(encoding="utf-8")
    for marker in ["AIHWKIT Residual Diagnostic", "threshold-fail payloads", "Worst Candidate Rows", "current analog mapping damages", "Refused Claim"]:
        if marker not in aihwkit_diagnostic_page:
            return fail(f"site/research/aihwkit-residual-diagnostic.html missing marker {marker!r}")

    aihwkit_mapping = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-ideal-forward-mapping-proof.json").read_text(encoding="utf-8"))
    if aihwkit_mapping.get("result_type") != "aihwkit_ideal_forward_mapping_proof":
        return fail("AIHWKIT ideal-forward mapping proof has wrong result_type")
    mapping_config = aihwkit_mapping.get("configuration") if isinstance(aihwkit_mapping.get("configuration"), dict) else {}
    if mapping_config.get("forward_is_perfect") is not True:
        return fail("AIHWKIT ideal-forward mapping proof should use explicit perfect forward")
    mapping_summary = aihwkit_mapping.get("summary") if isinstance(aihwkit_mapping.get("summary"), dict) else {}
    if mapping_summary.get("rows") != 16:
        return fail("AIHWKIT ideal-forward mapping proof should check 16 MatMul rows")
    if mapping_summary.get("passing_rows") != mapping_summary.get("rows"):
        return fail("AIHWKIT ideal-forward mapping proof should pass every checked row")
    if not isinstance(mapping_summary.get("max_residual_relative"), (int, float)) or mapping_summary["max_residual_relative"] > 1e-5:
        return fail("AIHWKIT ideal-forward mapping proof max residual should stay near floating-point tolerance")
    mapping_page = (ROOT / "site" / "research" / "aihwkit-ideal-forward-mapping-proof.html").read_text(encoding="utf-8")
    for marker in ["AIHWKIT Ideal Forward Mapping Proof", "layer dimensions", "weight orientation", "signed MatMul", "non-perfect forward path", "Refused Claim"]:
        if marker not in mapping_page:
            return fail(f"site/research/aihwkit-ideal-forward-mapping-proof.html missing marker {marker!r}")

    aihwkit_sweep = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-forward-setting-sweep.json").read_text(encoding="utf-8"))
    if aihwkit_sweep.get("result_type") != "aihwkit_forward_setting_sweep":
        return fail("AIHWKIT forward-setting sweep has wrong result_type")
    if aihwkit_sweep.get("positive_threshold") != 0.15:
        return fail("AIHWKIT forward-setting sweep should preserve the 0.15 positive threshold")
    sweep_summary = aihwkit_sweep.get("summary") if isinstance(aihwkit_sweep.get("summary"), dict) else {}
    if sweep_summary.get("settings") != 5:
        return fail("AIHWKIT forward-setting sweep should check 5 settings")
    if sweep_summary.get("rows_per_setting") != 16:
        return fail("AIHWKIT forward-setting sweep should check 16 rows per setting")
    if sweep_summary.get("passing_settings", 0) < 1:
        return fail("AIHWKIT forward-setting sweep should find at least one passing setting")
    settings = aihwkit_sweep.get("settings") if isinstance(aihwkit_sweep.get("settings"), list) else []
    fine_setting = next((item for item in settings if isinstance(item, dict) and item.get("id") == "fine_resolution_no_output_noise"), {})
    if not isinstance(fine_setting.get("summary"), dict) or fine_setting["summary"].get("passes_all_rows") is not True:
        return fail("AIHWKIT forward-setting sweep should show fine_resolution_no_output_noise passes all rows")
    if fine_setting["summary"].get("max_residual_relative", 1.0) > 0.15:
        return fail("AIHWKIT forward-setting sweep fine-resolution setting should stay below the positive threshold")
    sweep_page = (ROOT / "site" / "research" / "aihwkit-forward-setting-sweep.html").read_text(encoding="utf-8")
    for marker in ["AIHWKIT Forward Setting Sweep", "settings checked", "best passing setting", "fine_resolution_no_output_noise", "physically defensible analog tile", "Refused Claim"]:
        if marker not in sweep_page:
            return fail(f"site/research/aihwkit-forward-setting-sweep.html missing marker {marker!r}")

    physical_review = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-physical-setting-review.json").read_text(encoding="utf-8"))
    if physical_review.get("result_type") != "aihwkit_physical_setting_review":
        return fail("AIHWKIT physical-setting review has wrong result_type")
    review = physical_review.get("review") if isinstance(physical_review.get("review"), dict) else {}
    if review.get("status") != "needs_physical_justification":
        return fail("AIHWKIT physical-setting review should require physical justification")
    candidate = physical_review.get("candidate_setting") if isinstance(physical_review.get("candidate_setting"), dict) else {}
    tile = physical_review.get("current_tile_boundary") if isinstance(physical_review.get("current_tile_boundary"), dict) else {}
    if candidate.get("id") != "fine_resolution_no_output_noise":
        return fail("AIHWKIT physical-setting review should focus on fine_resolution_no_output_noise")
    if candidate.get("effective_input_bits") != 10 or candidate.get("effective_output_bits") != 12:
        return fail("AIHWKIT physical-setting review should record the 10/12 effective-bit setting")
    if tile.get("dac_bits") != 4 or tile.get("adc_bits") != 6:
        return fail("AIHWKIT physical-setting review should record the current 4-bit DAC and 6-bit ADC tile")
    physical_page = (ROOT / "site" / "research" / "aihwkit-physical-setting-review.html").read_text(encoding="utf-8")
    for marker in ["AIHWKIT Physical Setting Review", "needs_physical_justification", "candidate effective input bits", "current tile DAC bits", "current tile ADC bits", "Refused Claim"]:
        if marker not in physical_page:
            return fail(f"site/research/aihwkit-physical-setting-review.html missing marker {marker!r}")

    tile_replay = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-current-tile-boundary-replay.json").read_text(encoding="utf-8"))
    if tile_replay.get("result_type") != "aihwkit_current_tile_boundary_replay":
        return fail("AIHWKIT current-tile replay has wrong result_type")
    replay_tile = tile_replay.get("tile_boundary") if isinstance(tile_replay.get("tile_boundary"), dict) else {}
    replay_summary = tile_replay.get("summary") if isinstance(tile_replay.get("summary"), dict) else {}
    if replay_tile.get("dac_bits") != 4 or replay_tile.get("adc_bits") != 6:
        return fail("AIHWKIT current-tile replay should use the 4-bit DAC and 6-bit ADC tile boundary")
    if replay_summary.get("rows") != 16:
        return fail("AIHWKIT current-tile replay should check 16 rows")
    if replay_summary.get("passing_rows") != 0 or replay_summary.get("failing_rows") != 16:
        return fail("AIHWKIT current-tile replay should show the current tile fails all tested rows")
    tile_replay_page = (ROOT / "site" / "research" / "aihwkit-current-tile-boundary-replay.html").read_text(encoding="utf-8")
    for marker in ["AIHWKIT Current Tile Boundary Replay", "tile DAC bits", "tile ADC bits", "passing rows", "failing rows", "4-bit DAC and 6-bit ADC", "Refused Claim"]:
        if marker not in tile_replay_page:
            return fail(f"site/research/aihwkit-current-tile-boundary-replay.html missing marker {marker!r}")

    converter_target = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-converter-upgrade-target.json").read_text(encoding="utf-8"))
    if converter_target.get("result_type") != "aihwkit_converter_upgrade_target":
        return fail("AIHWKIT converter upgrade target has wrong result_type")
    if converter_target.get("status") != "target_defined_not_justified":
        return fail("AIHWKIT converter upgrade target should remain an unjustified target")
    converter_current = converter_target.get("current_boundary") if isinstance(converter_target.get("current_boundary"), dict) else {}
    converter_target_boundary = converter_target.get("minimum_passing_aihwkit_target") if isinstance(converter_target.get("minimum_passing_aihwkit_target"), dict) else {}
    converter_gap = converter_target.get("gap") if isinstance(converter_target.get("gap"), dict) else {}
    if converter_current.get("dac_bits") != 4 or converter_current.get("adc_bits") != 6:
        return fail("AIHWKIT converter target should record the current 4-bit DAC and 6-bit ADC boundary")
    if converter_current.get("current_tile_passing_rows") != 0 or converter_current.get("current_tile_failing_rows") != 16:
        return fail("AIHWKIT converter target should preserve current-tile replay failure counts")
    if converter_target_boundary.get("effective_input_bits") != 10 or converter_target_boundary.get("effective_output_bits") != 12:
        return fail("AIHWKIT converter target should record the 10-bit input and 12-bit output target")
    if converter_target_boundary.get("passing_rows") != 16:
        return fail("AIHWKIT converter target should preserve the passing row count")
    if converter_gap.get("input_bit_gap") != 6 or converter_gap.get("output_bit_gap") != 6:
        return fail("AIHWKIT converter target should record six-bit input and output gaps")
    required_next = converter_target.get("required_next_evidence") if isinstance(converter_target.get("required_next_evidence"), list) else []
    for phrase in ["energy", "latency", "area", "calibration", "noise"]:
        if not any(phrase in str(item) for item in required_next):
            return fail(f"AIHWKIT converter target missing required next evidence for {phrase}")
    converter_page = (ROOT / "site" / "research" / "aihwkit-converter-upgrade-target.html").read_text(encoding="utf-8")
    for marker in ["AIHWKIT Converter Upgrade Target", "target_defined_not_justified", "effective input bits", "effective output bits", "input bit gap", "output bit gap", "68 times finer", "65 times finer", "Refused Claim"]:
        if marker not in converter_page:
            return fail(f"site/research/aihwkit-converter-upgrade-target.html missing marker {marker!r}")

    converter_cost = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-converter-cost-model.json").read_text(encoding="utf-8"))
    if converter_cost.get("result_type") != "aihwkit_converter_cost_model":
        return fail("AIHWKIT converter cost model has wrong result_type")
    cost_decision = converter_cost.get("decision") if isinstance(converter_cost.get("decision"), dict) else {}
    if cost_decision.get("status") != "fallback_preferred_until_cost_is_justified":
        return fail("AIHWKIT converter cost model should prefer fallback until cost is justified")
    current_cost = converter_cost.get("current_cost") if isinstance(converter_cost.get("current_cost"), dict) else {}
    target_cost = converter_cost.get("target_cost") if isinstance(converter_cost.get("target_cost"), dict) else {}
    cost_delta = converter_cost.get("delta") if isinstance(converter_cost.get("delta"), dict) else {}
    if current_cost.get("adc_bits") != 6 or current_cost.get("dac_bits") != 4:
        return fail("AIHWKIT converter cost model should price the current 6-bit ADC and 4-bit DAC tile")
    if target_cost.get("adc_bits") != 12 or target_cost.get("dac_bits") != 10:
        return fail("AIHWKIT converter cost model should price the target 12-bit ADC and 10-bit DAC boundary")
    if not isinstance(cost_delta.get("energy_multiplier_vs_current"), (int, float)) or cost_delta["energy_multiplier_vs_current"] < 40:
        return fail("AIHWKIT converter cost model should expose the large energy multiplier")
    if not isinstance(cost_delta.get("latency_comparison_multiplier_vs_current"), (int, float)) or cost_delta["latency_comparison_multiplier_vs_current"] != 2:
        return fail("AIHWKIT converter cost model should expose the 2x comparison-count multiplier")
    cost_page = (ROOT / "site" / "research" / "aihwkit-converter-cost-model.html").read_text(encoding="utf-8")
    for marker in ["AIHWKIT Converter Cost Model", "fallback_preferred_until_cost_is_justified", "energy multiplier versus current tile", "latency comparison multiplier versus current tile", "digital fallback", "Refused Claim"]:
        if marker not in cost_page:
            return fail(f"site/research/aihwkit-converter-cost-model.html missing marker {marker!r}")

    target_noise = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-target-noise-sensitivity.json").read_text(encoding="utf-8"))
    if target_noise.get("result_type") != "aihwkit_target_noise_sensitivity":
        return fail("AIHWKIT target noise sensitivity has wrong result_type")
    noise_target = target_noise.get("target_boundary") if isinstance(target_noise.get("target_boundary"), dict) else {}
    if noise_target.get("effective_input_bits") != 10 or noise_target.get("effective_output_bits") != 12:
        return fail("AIHWKIT target noise sensitivity should use the 10-bit input and 12-bit output target")
    noise_summary = target_noise.get("summary") if isinstance(target_noise.get("summary"), dict) else {}
    if noise_summary.get("noise_settings") != 4 or noise_summary.get("all_pass_noise_settings") != 3:
        return fail("AIHWKIT target noise sensitivity should record four settings and three all-pass settings")
    if noise_summary.get("highest_all_pass_out_noise") != 0.004:
        return fail("AIHWKIT target noise sensitivity should record 0.004 as highest all-pass output noise")
    if noise_summary.get("passes_any_nonzero_noise") is not True:
        return fail("AIHWKIT target noise sensitivity should pass at least one nonzero output-noise case")
    noise_page = (ROOT / "site" / "research" / "aihwkit-target-noise-sensitivity.html").read_text(encoding="utf-8")
    for marker in ["AIHWKIT Target Noise Sensitivity", "highest all-pass output noise", "0.004", "passes any nonzero noise", "nonzero noise budget", "Refused Claim"]:
        if marker not in noise_page:
            return fail(f"site/research/aihwkit-target-noise-sensitivity.html missing marker {marker!r}")

    break_even = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-converter-break-even.json").read_text(encoding="utf-8"))
    if break_even.get("result_type") != "aihwkit_converter_break_even":
        return fail("AIHWKIT converter break-even has wrong result_type")
    break_even_target = break_even.get("target_boundary") if isinstance(break_even.get("target_boundary"), dict) else {}
    if break_even_target.get("adc_bits") != 12 or break_even_target.get("dac_bits") != 10:
        return fail("AIHWKIT converter break-even should use the 12-bit ADC and 10-bit DAC target")
    if break_even_target.get("highest_all_pass_out_noise") != 0.004:
        return fail("AIHWKIT converter break-even should carry the 0.004 output-noise budget")
    break_even_summary = break_even.get("summary") if isinstance(break_even.get("summary"), dict) else {}
    if break_even_summary.get("scenario_count") != 4:
        return fail("AIHWKIT converter break-even should record four scenarios")
    if break_even_summary.get("default_decision") != "digital_fallback_until_real_converter_and_array_savings_are_measured":
        return fail("AIHWKIT converter break-even should keep digital fallback as default")
    break_even_scenarios = break_even.get("scenarios") if isinstance(break_even.get("scenarios"), list) else []
    if not break_even_scenarios:
        return fail("AIHWKIT converter break-even should include scenario rows")
    for item in break_even_scenarios:
        if not isinstance(item, dict):
            return fail("AIHWKIT converter break-even contains a non-object scenario")
        for key in ["rows", "amortized_outputs_per_conversion", "target_analog_energy_per_output", "digital_energy_per_output", "target_beats_digital"]:
            if key not in item:
                return fail(f"AIHWKIT converter break-even scenario missing {key}")
    break_even_page = (ROOT / "site" / "research" / "aihwkit-converter-break-even.html").read_text(encoding="utf-8")
    for marker in ["AIHWKIT Converter Break-Even Boundary", "target ADC bits", "target DAC bits", "highest all-pass output noise", "Scenario Table", "outputs needed to pay converter", "digital fallback", "Refused Claim"]:
        if marker not in break_even_page:
            return fail(f"site/research/aihwkit-converter-break-even.html missing marker {marker!r}")

    converter_contract_schema = json.loads((ROOT / "sources" / "evidence" / "converter-circuit-evidence-schema.json").read_text(encoding="utf-8"))
    for field in ["target_boundary", "energy", "latency", "noise", "area", "sharing", "provenance", "claim_boundary"]:
        if field not in converter_contract_schema.get("required_top_level_fields", []):
            return fail(f"converter circuit evidence schema missing top-level field {field!r}")
    for level in ["local_estimate", "circuit_simulation", "post_layout_simulation", "measured_silicon"]:
        if level not in converter_contract_schema.get("allowed_measurement_levels", []):
            return fail(f"converter circuit evidence schema missing measurement level {level!r}")
    converter_contract = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-circuit-evidence-contract.json").read_text(encoding="utf-8"))
    if converter_contract.get("result_type") != "converter_circuit_evidence_contract":
        return fail("converter circuit evidence contract has wrong result_type")
    contract_validation = converter_contract.get("validation") if isinstance(converter_contract.get("validation"), dict) else {}
    if contract_validation.get("status") != "contract_defined_placeholder_not_claim_ready":
        return fail("converter circuit evidence contract should be defined but not claim-ready")
    if contract_validation.get("schema_complete") is not True:
        return fail("converter circuit evidence placeholder should satisfy the schema shape")
    if contract_validation.get("claim_ready_to_replace_break_even") is not False:
        return fail("converter circuit evidence placeholder should not replace break-even assumptions")
    placeholder = converter_contract.get("current_placeholder") if isinstance(converter_contract.get("current_placeholder"), dict) else {}
    placeholder_target = placeholder.get("target_boundary") if isinstance(placeholder.get("target_boundary"), dict) else {}
    if placeholder_target.get("adc_bits") != 12 or placeholder_target.get("dac_bits") != 10:
        return fail("converter circuit evidence placeholder should carry the 12-bit ADC and 10-bit DAC target")
    if placeholder_target.get("output_noise_budget") != 0.004:
        return fail("converter circuit evidence placeholder should carry the 0.004 output-noise budget")
    if placeholder.get("measurement_level") != "local_estimate":
        return fail("converter circuit evidence placeholder should remain a local estimate")
    contract_page = (ROOT / "site" / "research" / "converter-circuit-evidence-contract.html").read_text(encoding="utf-8")
    for marker in ["Converter Circuit Evidence Contract", "target ADC bits", "target DAC bits", "output noise budget", "claim-ready to replace break-even", "Energy", "Latency", "Noise", "Area", "Sharing", "Refused Claim"]:
        if marker not in contract_page:
            return fail(f"site/research/converter-circuit-evidence-contract.html missing marker {marker!r}")

    local_converter = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "local-converter-circuit-estimate.json").read_text(encoding="utf-8"))
    if local_converter.get("result_type") != "local_converter_circuit_estimate":
        return fail("local converter circuit estimate has wrong result_type")
    local_validation = local_converter.get("validation") if isinstance(local_converter.get("validation"), dict) else {}
    if local_validation.get("status") != "local_estimate_complete_not_claim_ready":
        return fail("local converter circuit estimate should be complete but not claim-ready")
    if local_validation.get("schema_complete") is not True:
        return fail("local converter circuit estimate should satisfy the converter evidence schema")
    if local_validation.get("claim_ready_to_replace_break_even") is not False:
        return fail("local converter circuit estimate should not replace break-even assumptions")
    estimate = local_converter.get("estimate") if isinstance(local_converter.get("estimate"), dict) else {}
    if estimate.get("measurement_level") != "local_estimate":
        return fail("local converter circuit estimate should remain a local estimate")
    estimate_noise = estimate.get("noise") if isinstance(estimate.get("noise"), dict) else {}
    if estimate_noise.get("output_noise_rms") != 0.004 or estimate_noise.get("meets_output_noise_budget") is not True:
        return fail("local converter circuit estimate should carry the 0.004 planning noise boundary")
    estimate_sharing = estimate.get("sharing") if isinstance(estimate.get("sharing"), dict) else {}
    if estimate_sharing.get("rows_served") != 64 or estimate_sharing.get("outputs_per_conversion_cost") != 16:
        return fail("local converter circuit estimate should record the 64-row, 16-output sharing planning point")
    local_converter_page = (ROOT / "site" / "research" / "local-converter-circuit-estimate.html").read_text(encoding="utf-8")
    for marker in ["Local Converter Circuit Estimate", "local planning numbers", "claim-ready to replace break-even", "ADC bits", "DAC bits", "output noise RMS", "rows served", "outputs sharing converter cost", "Refused Claim"]:
        if marker not in local_converter_page:
            return fail(f"site/research/local-converter-circuit-estimate.html missing marker {marker!r}")

    circuit_sim = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-circuit-simulation-estimate.json").read_text(encoding="utf-8"))
    if circuit_sim.get("result_type") != "converter_circuit_simulation_estimate":
        return fail("converter circuit-simulation estimate has wrong result_type")
    circuit_validation = circuit_sim.get("validation") if isinstance(circuit_sim.get("validation"), dict) else {}
    if circuit_validation.get("status") != "circuit_simulation_complete_not_replacement_ready":
        return fail("converter circuit-simulation estimate should be complete but not replacement-ready")
    if circuit_validation.get("schema_complete") is not True:
        return fail("converter circuit-simulation estimate should satisfy the converter evidence schema")
    if circuit_validation.get("claim_ready_to_replace_break_even") is not False:
        return fail("converter circuit-simulation estimate should not replace break-even assumptions")
    circuit_estimate = circuit_sim.get("estimate") if isinstance(circuit_sim.get("estimate"), dict) else {}
    if circuit_estimate.get("measurement_level") != "circuit_simulation":
        return fail("converter circuit-simulation estimate should use circuit_simulation measurement level")
    circuit_noise = circuit_estimate.get("noise") if isinstance(circuit_estimate.get("noise"), dict) else {}
    if circuit_noise.get("meets_output_noise_budget") is not True:
        return fail("converter circuit-simulation estimate should meet the 0.004 output-noise budget")
    if not isinstance(circuit_noise.get("output_noise_rms"), (int, float)) or circuit_noise["output_noise_rms"] >= 0.004:
        return fail("converter circuit-simulation estimate should keep modeled output noise under 0.004")
    circuit_terms = circuit_sim.get("simulation_terms") if isinstance(circuit_sim.get("simulation_terms"), dict) else {}
    for key in ["adc_quantization_rms", "dac_quantization_rms", "settling_residual_fraction", "settling_error_rms", "comparator_noise_rms", "row_driver_noise_rms"]:
        if key not in circuit_terms:
            return fail(f"converter circuit-simulation estimate missing simulation term {key}")
    circuit_page = (ROOT / "site" / "research" / "converter-circuit-simulation-estimate.html").read_text(encoding="utf-8")
    for marker in ["Converter Circuit-Simulation Estimate", "behavioral circuit model", "modeled output noise RMS", "settling", "quantization", "root-sum-square", "post_layout_simulation", "measured_silicon", "Refused Claim"]:
        if marker not in circuit_page:
            return fail(f"site/research/converter-circuit-simulation-estimate.html missing marker {marker!r}")

    spice_handoff = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-spice-handoff-spec.json").read_text(encoding="utf-8"))
    if spice_handoff.get("result_type") != "converter_spice_handoff_spec":
        return fail("converter SPICE handoff spec has wrong result_type")
    handoff_tests = spice_handoff.get("required_testbenches") if isinstance(spice_handoff.get("required_testbenches"), list) else []
    if len(handoff_tests) != 4:
        return fail("converter SPICE handoff spec should define four required testbenches")
    handoff_names = {item.get("name") for item in handoff_tests if isinstance(item, dict)}
    for name in ["10-bit row DAC settling", "12-bit SAR readout decision", "shared converter loading", "energy accounting"]:
        if name not in handoff_names:
            return fail(f"converter SPICE handoff spec missing testbench {name!r}")
    handoff_acceptance = spice_handoff.get("acceptance_rule") if isinstance(spice_handoff.get("acceptance_rule"), dict) else {}
    if handoff_acceptance.get("can_replace_break_even") is not False:
        return fail("converter SPICE handoff spec should not claim it can replace break-even")
    handoff_fields = spice_handoff.get("required_output_fields") if isinstance(spice_handoff.get("required_output_fields"), list) else []
    for fragment in ["adc_energy_per_conversion", "dac_energy_per_row_drive", "output_noise_rms", "sharing rule", "netlist path"]:
        if not any(fragment in str(field) for field in handoff_fields):
            return fail(f"converter SPICE handoff spec missing output field fragment {fragment!r}")
    handoff_page = (ROOT / "site" / "research" / "converter-spice-handoff-spec.html").read_text(encoding="utf-8")
    for marker in ["Converter SPICE Handoff Spec", "row DAC settling", "SAR readout", "shared converter loading", "supply energy", "post_layout_simulation", "measured_silicon", "Refused claim"]:
        if marker not in handoff_page:
            return fail(f"site/research/converter-spice-handoff-spec.html missing marker {marker!r}")

    row_dac_spice = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "row-dac-settling-spice-evidence.json").read_text(encoding="utf-8"))
    if row_dac_spice.get("result_type") != "row_dac_settling_spice_evidence":
        return fail("row-DAC settling SPICE evidence has wrong result_type")
    row_dac_summary = row_dac_spice.get("summary") if isinstance(row_dac_spice.get("summary"), dict) else {}
    if row_dac_summary.get("status") != "row_dac_settling_spice_passes_simple_load":
        return fail("row-DAC settling SPICE evidence should pass the simple load")
    if row_dac_summary.get("cases") != 3:
        return fail("row-DAC settling SPICE evidence should cover three voltage cases")
    if row_dac_summary.get("all_cases_pass_half_lsb") is not True:
        return fail("row-DAC settling SPICE evidence should pass every half-LSB case")
    if not isinstance(row_dac_summary.get("worst_abs_error_v"), (int, float)) or not isinstance(row_dac_summary.get("half_lsb_v"), (int, float)):
        return fail("row-DAC settling SPICE evidence should record numeric error and half-LSB")
    if row_dac_summary["worst_abs_error_v"] >= row_dac_summary["half_lsb_v"]:
        return fail("row-DAC settling SPICE evidence worst error should be below half-LSB")
    row_dac_handoff = row_dac_spice.get("handoff_connection") if isinstance(row_dac_spice.get("handoff_connection"), dict) else {}
    if row_dac_handoff.get("satisfies_testbench") != "S1. 10-bit row DAC settling":
        return fail("row-DAC settling SPICE evidence should satisfy handoff testbench S1")
    remaining = row_dac_handoff.get("remaining_testbenches") if isinstance(row_dac_handoff.get("remaining_testbenches"), list) else []
    for name in ["12-bit SAR readout decision", "shared converter loading", "energy accounting"]:
        if name not in remaining:
            return fail(f"row-DAC settling SPICE evidence missing remaining testbench {name!r}")
    row_dac_page = (ROOT / "site" / "research" / "row-dac-settling-spice-evidence.html").read_text(encoding="utf-8")
    for marker in ["Row-DAC Settling SPICE Evidence", "all cases pass half-LSB settling", "worst absolute error", "half-LSB limit", "10-bit input target", "Remaining Converter SPICE Work", "12-bit SAR readout decision", "Refused Claim"]:
        if marker not in row_dac_page:
            return fail(f"site/research/row-dac-settling-spice-evidence.html missing marker {marker!r}")

    sar_spice = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "sar-readout-spice-evidence.json").read_text(encoding="utf-8"))
    if sar_spice.get("result_type") != "sar_readout_spice_evidence":
        return fail("SAR readout SPICE evidence has wrong result_type")
    sar_summary = sar_spice.get("summary") if isinstance(sar_spice.get("summary"), dict) else {}
    if sar_summary.get("status") != "sar_readout_spice_passes_simple_sample_load":
        return fail("SAR readout SPICE evidence should pass the simple sample load")
    if sar_summary.get("cases") != 3:
        return fail("SAR readout SPICE evidence should cover three voltage cases")
    if sar_summary.get("comparisons") != 12:
        return fail("SAR readout SPICE evidence should record 12 comparisons")
    if sar_summary.get("all_cases_pass_half_lsb") is not True:
        return fail("SAR readout SPICE evidence should pass every half-LSB case")
    if not isinstance(sar_summary.get("worst_abs_error_v"), (int, float)) or not isinstance(sar_summary.get("half_lsb_v"), (int, float)):
        return fail("SAR readout SPICE evidence should record numeric error and half-LSB")
    if sar_summary["worst_abs_error_v"] > sar_summary["half_lsb_v"]:
        return fail("SAR readout SPICE evidence worst error should be below half-LSB")
    sar_handoff = sar_spice.get("handoff_connection") if isinstance(sar_spice.get("handoff_connection"), dict) else {}
    if sar_handoff.get("satisfies_testbench") != "S2. 12-bit SAR readout decision":
        return fail("SAR readout SPICE evidence should satisfy handoff testbench S2")
    remaining = sar_handoff.get("remaining_testbenches") if isinstance(sar_handoff.get("remaining_testbenches"), list) else []
    for name in ["shared converter loading", "energy accounting"]:
        if name not in remaining:
            return fail(f"SAR readout SPICE evidence missing remaining testbench {name!r}")
    sar_page = (ROOT / "site" / "research" / "sar-readout-spice-evidence.html").read_text(encoding="utf-8")
    for marker in ["SAR Readout SPICE Evidence", "all cases pass half-LSB readout", "worst absolute error", "half-LSB limit", "12-bit ADC claim", "Remaining Converter SPICE Work", "shared converter loading", "Refused Claim"]:
        if marker not in sar_page:
            return fail(f"site/research/sar-readout-spice-evidence.html missing marker {marker!r}")

    shared_loading_spice = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "shared-converter-loading-spice-evidence.json").read_text(encoding="utf-8"))
    if shared_loading_spice.get("result_type") != "shared_converter_loading_spice_evidence":
        return fail("shared converter loading SPICE evidence has wrong result_type")
    shared_summary = shared_loading_spice.get("summary") if isinstance(shared_loading_spice.get("summary"), dict) else {}
    if shared_summary.get("status") != "shared_converter_loading_spice_passes_simple_mux_load":
        return fail("shared converter loading SPICE evidence should pass the simple mux load")
    if shared_summary.get("cases") != 4:
        return fail("shared converter loading SPICE evidence should cover four loading cases")
    if shared_summary.get("max_active_loads") != 32:
        return fail("shared converter loading SPICE evidence should record the 32-load stress case")
    if shared_summary.get("all_cases_pass_half_lsb") is not True:
        return fail("shared converter loading SPICE evidence should pass every half-LSB case")
    if not isinstance(shared_summary.get("worst_abs_error_v"), (int, float)) or not isinstance(shared_summary.get("half_lsb_v"), (int, float)):
        return fail("shared converter loading SPICE evidence should record numeric error and half-LSB")
    if shared_summary["worst_abs_error_v"] > shared_summary["half_lsb_v"]:
        return fail("shared converter loading SPICE evidence worst error should be below half-LSB")
    shared_handoff = shared_loading_spice.get("handoff_connection") if isinstance(shared_loading_spice.get("handoff_connection"), dict) else {}
    if shared_handoff.get("satisfies_testbench") != "S3. shared converter loading":
        return fail("shared converter loading SPICE evidence should satisfy handoff testbench S3")
    remaining = shared_handoff.get("remaining_testbenches") if isinstance(shared_handoff.get("remaining_testbenches"), list) else []
    if "energy accounting" not in remaining:
        return fail("shared converter loading SPICE evidence should leave energy accounting open")
    shared_page = (ROOT / "site" / "research" / "shared-converter-loading-spice-evidence.html").read_text(encoding="utf-8")
    for marker in ["Shared Converter Loading SPICE Evidence", "all cases pass half-LSB shared loading", "worst absolute error", "half-LSB limit", "max active loads", "Remaining Converter SPICE Work", "energy accounting", "Refused Claim"]:
        if marker not in shared_page:
            return fail(f"site/research/shared-converter-loading-spice-evidence.html missing marker {marker!r}")

    supply_energy_spice = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-supply-energy-spice-evidence.json").read_text(encoding="utf-8"))
    if supply_energy_spice.get("result_type") != "converter_supply_energy_spice_evidence":
        return fail("converter supply-energy SPICE evidence has wrong result_type")
    supply_summary = supply_energy_spice.get("summary") if isinstance(supply_energy_spice.get("summary"), dict) else {}
    if supply_summary.get("status") != "converter_supply_energy_spice_complete_simple_load":
        return fail("converter supply-energy SPICE evidence should complete the simple load model")
    if supply_summary.get("cases") != 3:
        return fail("converter supply-energy SPICE evidence should cover three conversion cases")
    if supply_summary.get("all_cases_have_positive_energy") is not True:
        return fail("converter supply-energy SPICE evidence should record positive energy for every case")
    for key in ["worst_total_energy_j", "worst_dac_energy_j", "worst_adc_energy_j", "worst_mux_energy_j"]:
        if not isinstance(supply_summary.get(key), (int, float)) or supply_summary[key] <= 0:
            return fail(f"converter supply-energy SPICE evidence should record positive {key}")
    supply_handoff = supply_energy_spice.get("handoff_connection") if isinstance(supply_energy_spice.get("handoff_connection"), dict) else {}
    if supply_handoff.get("satisfies_testbench") != "S4. energy accounting":
        return fail("converter supply-energy SPICE evidence should satisfy handoff testbench S4")
    remaining = supply_handoff.get("remaining_testbenches") if isinstance(supply_handoff.get("remaining_testbenches"), list) else []
    if remaining:
        return fail("converter supply-energy SPICE evidence should close the local converter handoff test list")
    supply_page = (ROOT / "site" / "research" / "converter-supply-energy-spice-evidence.html").read_text(encoding="utf-8")
    for marker in ["Converter Supply Energy SPICE Evidence", "all cases have positive integrated energy", "worst total energy", "worst DAC energy", "worst ADC energy", "worst mux energy", "Remaining Converter SPICE Work", "all four executable handoff tests", "Refused Claim"]:
        if marker not in supply_page:
            return fail(f"site/research/converter-supply-energy-spice-evidence.html missing marker {marker!r}")

    post_layout = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-readiness.json").read_text(encoding="utf-8"))
    if post_layout.get("result_type") != "converter_post_layout_readiness":
        return fail("converter post-layout readiness has wrong result_type")
    post_validation = post_layout.get("validation") if isinstance(post_layout.get("validation"), dict) else {}
    if post_validation.get("status") != "local_converter_handoff_complete_post_layout_not_ready":
        return fail("converter post-layout readiness should record local handoff complete and post-layout not ready")
    if post_validation.get("local_handoff_complete") is not True:
        return fail("converter post-layout readiness should record local handoff completion")
    if post_validation.get("claim_ready_to_replace_break_even") is not False:
        return fail("converter post-layout readiness should not replace break-even")
    if post_validation.get("missing_replacement_items", 0) < 8:
        return fail("converter post-layout readiness should name concrete replacement items")
    replacement_rule = post_layout.get("replacement_rule") if isinstance(post_layout.get("replacement_rule"), dict) else {}
    if replacement_rule.get("break_even_replacement_levels") != ["measured_silicon", "post_layout_simulation"]:
        return fail("converter post-layout readiness should preserve replacement measurement levels")
    post_page = (ROOT / "site" / "research" / "converter-post-layout-readiness.html").read_text(encoding="utf-8")
    for marker in ["Converter Post-Layout Readiness", "local converter handoff complete", "claim-ready to replace break-even", "current measurement level", "Missing Before Break-Even Replacement", "extracted parasitic netlist", "post-layout energy", "post-layout output noise RMS", "Refused Claim"]:
        if marker not in post_page:
            return fail(f"site/research/converter-post-layout-readiness.html missing marker {marker!r}")

    post_contract = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-evidence-contract.json").read_text(encoding="utf-8"))
    if post_contract.get("result_type") != "converter_post_layout_evidence_contract":
        return fail("converter post-layout evidence contract has wrong result_type")
    post_contract_validation = post_contract.get("validation") if isinstance(post_contract.get("validation"), dict) else {}
    if post_contract_validation.get("status") != "post_layout_contract_defined_placeholder_not_claim_ready":
        return fail("converter post-layout evidence contract should record placeholder as not claim-ready")
    if post_contract_validation.get("schema_complete") is not True:
        return fail("converter post-layout evidence contract placeholder should satisfy schema shape")
    if post_contract_validation.get("claim_ready_to_replace_break_even") is not False:
        return fail("converter post-layout evidence contract placeholder should not replace break-even")
    if post_contract_validation.get("placeholder_refuses_replacement") is not True:
        return fail("converter post-layout evidence contract should explicitly refuse placeholder replacement")
    post_schema = post_contract.get("post_layout_schema") if isinstance(post_contract.get("post_layout_schema"), dict) else {}
    for field in ["extraction", "simulation", "energy", "latency", "noise", "area", "break_even_rerun", "provenance"]:
        if field not in post_schema.get("required_top_level_fields", []):
            return fail(f"converter post-layout schema missing top-level field {field!r}")
    required_schema_sections = {
        "required_simulation_fields": ["run_id"],
        "required_energy_fields": ["adc_energy_per_conversion", "dac_energy_per_row_drive", "run_id"],
        "required_latency_fields": ["conversion_time_ns", "settling_time_ns", "run_id"],
        "required_noise_fields": ["output_noise_rms", "input_referred_noise", "run_id"],
        "required_area_fields": ["adc_area_um2", "dac_area_um2", "run_id"],
        "required_break_even_rerun_fields": ["rerun_artifact", "replacement_decision", "run_id"],
        "required_provenance_fields": ["created_at", "source_schema", "run_id"],
    }
    for schema_key, fields in required_schema_sections.items():
        schema_fields = post_schema.get(schema_key) if isinstance(post_schema.get(schema_key), list) else []
        for field in fields:
            if field not in schema_fields:
                return fail(f"converter post-layout schema missing {schema_key}.{field}")
    if "provenance.run_id" not in str(post_schema.get("same_run_rule", "")):
        return fail("converter post-layout schema should state same-run rule")
    for level in ["post_layout_simulation", "measured_silicon"]:
        if level not in post_schema.get("allowed_measurement_levels", []):
            return fail(f"converter post-layout schema missing measurement level {level!r}")
    post_contract_page = (ROOT / "site" / "research" / "converter-post-layout-evidence-contract.html").read_text(encoding="utf-8")
    for marker in ["Converter Post-Layout Evidence Contract", "claim-ready to replace break-even", "placeholder refuses replacement", "Required Extraction Fields", "extracted_netlist", "Required Energy Fields", "adc_energy_per_conversion", "Required Noise Fields", "output_noise_rms", "Required Area Fields", "adc_area_um2", "Required Break-Even Rerun Fields", "uses_extracted_energy", "replacement_decision", "Required Provenance Fields", "source_schema", "Same-Run Rule", "provenance.run_id", "run_id", "Refused Claim"]:
        if marker not in post_contract_page:
            return fail(f"site/research/converter-post-layout-evidence-contract.html missing marker {marker!r}")

    payload_template = json.loads((ROOT / "sources" / "evidence" / "converter-post-layout-payload.template.json").read_text(encoding="utf-8"))
    if payload_template.get("template_only") is not True:
        return fail("converter post-layout payload template should be marked template_only")
    if payload_template.get("result_type") != "converter_post_layout_evidence":
        return fail("converter post-layout payload template should show the evidence result_type")
    if payload_template.get("simulation", {}).get("voltage_v") != "REPLACE_WITH_NUMERIC_SUPPLY":
        return fail("converter post-layout payload template should keep numeric supply as a replacement field")
    template_report = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-payload-template.json").read_text(encoding="utf-8"))
    if template_report.get("result_type") != "converter_post_layout_payload_template":
        return fail("converter post-layout payload template report has wrong result_type")
    if template_report.get("status") != "template_defined_not_evidence":
        return fail("converter post-layout payload template report should be non-evidence")
    template_page = (ROOT / "site" / "research" / "converter-post-layout-payload-template.html").read_text(encoding="utf-8")
    for marker in ["Converter Post-Layout Payload Template", "template_defined_not_evidence", "How To Fill It", "REPLACE_WITH", "run <code>python3 scripts/validate_converter_post_layout_payload.py FILLED_PAYLOAD.json</code>", "Refused Claim"]:
        if marker not in template_page:
            return fail(f"site/research/converter-post-layout-payload-template.html missing marker {marker!r}")

    placeholder_payload = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "dry-run" / "converter-post-layout-evidence.placeholder.json").read_text(encoding="utf-8"))
    if placeholder_payload.get("result_type") != "converter_post_layout_evidence":
        return fail("converter post-layout placeholder payload has wrong result_type")
    if placeholder_payload.get("break_even_rerun", {}).get("replacement_decision") != "not_ready":
        return fail("converter post-layout placeholder payload should refuse replacement")
    validator_report = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-payload-validator.json").read_text(encoding="utf-8"))
    if validator_report.get("result_type") != "converter_post_layout_payload_validator_report":
        return fail("converter post-layout payload validator report has wrong result_type")
    if validator_report.get("status") != "post_layout_payload_validator_ready_waiting_for_extracted_payload":
        return fail("converter post-layout payload validator should be ready and waiting for extracted payload")
    if validator_report.get("rejected_placeholder") is not True:
        return fail("converter post-layout payload validator should reject the placeholder")
    accepted_boundary = validator_report.get("accepted_payload_boundary") if isinstance(validator_report.get("accepted_payload_boundary"), dict) else {}
    if accepted_boundary.get("max_output_noise_rms") != 0.004:
        return fail("converter post-layout payload validator should preserve 0.004 output-noise boundary")
    if accepted_boundary.get("requires_break_even_rerun_with_extracted_values") is not True:
        return fail("converter post-layout payload validator should require extracted-value break-even rerun")
    validator_page = (ROOT / "site" / "research" / "converter-post-layout-payload-validator.html").read_text(encoding="utf-8")
    for marker in ["Converter Post-Layout Payload Validator", "rejected placeholder", "Accepted Payload Boundary", "post_layout_simulation", "measured_silicon", "0.004", "break-even must be rerun", "Refused Claim"]:
        if marker not in validator_page:
            return fail(f"site/research/converter-post-layout-payload-validator.html missing marker {marker!r}")

    rerun_path = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-break-even-rerun-path.json").read_text(encoding="utf-8"))
    if rerun_path.get("result_type") != "converter_post_layout_break_even_rerun_path":
        return fail("converter post-layout break-even rerun path has wrong result_type")
    if rerun_path.get("status") != "rerun_path_ready_waiting_for_validator_passing_payload":
        return fail("converter post-layout break-even rerun path should wait for validator-passing payload")
    rejection_checks = rerun_path.get("rejection_checks") if isinstance(rerun_path.get("rejection_checks"), list) else []
    if len(rejection_checks) != 2 or not all(isinstance(item, dict) and item.get("passed") is True for item in rejection_checks):
        return fail("converter post-layout break-even rerun path should reject placeholder and template")
    rerun_page = (ROOT / "site" / "research" / "converter-post-layout-break-even-rerun-path.html").read_text(encoding="utf-8")
    for marker in ["Converter Post-Layout Break-Even Rerun Path", "rerun_path_ready_waiting_for_validator_passing_payload", "Validation answers whether the payload is real enough to use", "How To Use With A Real Payload", "rerun_converter_break_even_from_post_layout_payload.py", "Refused Claim"]:
        if marker not in rerun_page:
            return fail(f"site/research/converter-post-layout-break-even-rerun-path.html missing marker {marker!r}")

    strict_intake = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-strict-intake-report.json").read_text(encoding="utf-8"))
    if strict_intake.get("result_type") != "converter_post_layout_strict_intake_report":
        return fail("converter post-layout strict intake report has wrong result_type")
    if strict_intake.get("status") != "strict_file_intake_ready_waiting_for_real_artifacts":
        return fail("converter post-layout strict intake should wait for real artifacts")
    if strict_intake.get("shape_validation_passed") is not True:
        return fail("converter post-layout strict intake should prove shape-only payload passes ordinary validation")
    if strict_intake.get("strict_validation_rejected_missing_files") is not True:
        return fail("converter post-layout strict intake should reject missing files during validation")
    if strict_intake.get("strict_rerun_rejected_missing_files") is not True:
        return fail("converter post-layout strict intake should reject missing files during rerun")
    strict_page = (ROOT / "site" / "research" / "converter-post-layout-strict-intake.html").read_text(encoding="utf-8")
    for marker in ["Converter Post-Layout Strict Intake", "strict_file_intake_ready_waiting_for_real_artifacts", "shape validation passed", "strict validation rejected missing files", "extracted netlist", "model files", "break-even rerun artifact", "Refused Claim"]:
        if marker not in strict_page:
            return fail(f"site/research/converter-post-layout-strict-intake.html missing marker {marker!r}")

    positive_path = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-positive-path-report.json").read_text(encoding="utf-8"))
    if positive_path.get("result_type") != "converter_post_layout_positive_path_report":
        return fail("converter post-layout positive path report has wrong result_type")
    if positive_path.get("status") != "strict_positive_path_proven_with_temporary_synthetic_files":
        return fail("converter post-layout positive path should prove temporary synthetic strict pass")
    if positive_path.get("temporary_fixture_persisted") is not False:
        return fail("converter post-layout positive path should not persist synthetic fixture")
    if positive_path.get("strict_validation_passed") is not True or positive_path.get("strict_rerun_passed") is not True:
        return fail("converter post-layout positive path should pass strict validation and rerun")
    positive_page = (ROOT / "site" / "research" / "converter-post-layout-positive-path.html").read_text(encoding="utf-8")
    for marker in ["Converter Post-Layout Positive Path", "strict_positive_path_proven_with_temporary_synthetic_files", "temporary fixture persisted", "strict validation passed", "strict rerun passed", "not saving synthetic evidence", "Refused Claim"]:
        if marker not in positive_page:
            return fail(f"site/research/converter-post-layout-positive-path.html missing marker {marker!r}")

    submission_path = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-submission-path-report.json").read_text(encoding="utf-8"))
    if submission_path.get("result_type") != "converter_post_layout_submission_path_report":
        return fail("converter post-layout submission path report has wrong result_type")
    if submission_path.get("status") != "submission_path_ready_waiting_for_real_payload":
        return fail("converter post-layout submission path should wait for real payload")
    if submission_path.get("placeholder_rejected") is not True:
        return fail("converter post-layout submission path should reject placeholder")
    if submission_path.get("missing_file_payload_rejected") is not True:
        return fail("converter post-layout submission path should reject missing-file payload")
    if submission_path.get("temporary_positive_payload_accepted") is not True:
        return fail("converter post-layout submission path should accept temporary positive payload")
    submission_page = (ROOT / "site" / "research" / "converter-post-layout-submission-path.html").read_text(encoding="utf-8")
    for marker in ["Converter Post-Layout Submission Path", "submission_path_ready_waiting_for_real_payload", "placeholder rejected", "missing-file payload rejected", "temporary positive payload accepted", "one-command intake path", "submit_converter_post_layout_payload.py", "Refused Claim"]:
        if marker not in submission_page:
            return fail(f"site/research/converter-post-layout-submission-path.html missing marker {marker!r}")

    real_payload_package = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-real-payload-package.json").read_text(encoding="utf-8"))
    if real_payload_package.get("result_type") != "converter_post_layout_real_payload_package":
        return fail("converter post-layout real payload package has wrong result_type")
    if real_payload_package.get("status") != "real_payload_package_contract_ready":
        return fail("converter post-layout real payload package should be ready")
    if real_payload_package.get("submission_command") != "python3 scripts/submit_converter_post_layout_payload.py REAL_PAYLOAD.json":
        return fail("converter post-layout real payload package should name the submission command")
    required_files = real_payload_package.get("required_files") if isinstance(real_payload_package.get("required_files"), list) else []
    if len(required_files) != 4:
        return fail("converter post-layout real payload package should name four required files")
    fixed_boundary = real_payload_package.get("fixed_target_boundary") if isinstance(real_payload_package.get("fixed_target_boundary"), dict) else {}
    if fixed_boundary.get("dac_bits") != 10 or fixed_boundary.get("adc_bits") != 12:
        return fail("converter post-layout real payload package should preserve the 10-bit DAC and 12-bit ADC boundary")
    if fixed_boundary.get("output_noise_budget_max") != 0.004:
        return fail("converter post-layout real payload package should preserve the 0.004 output-noise budget")
    package_page = (ROOT / "site" / "research" / "converter-post-layout-real-payload-package.html").read_text(encoding="utf-8")
    for marker in ["Converter Post-Layout Real Payload Package", "real_payload_package_contract_ready", "extracted netlist", "process or measurement model files", "prior rerun artifact", "A converter claim is a claim about a boundary", "output_noise_budget_max", "Refused Claim"]:
        if marker not in package_page:
            return fail(f"site/research/converter-post-layout-real-payload-package.html missing marker {marker!r}")

    preflight = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-payload-preflight-report.json").read_text(encoding="utf-8"))
    if preflight.get("result_type") != "converter_post_layout_payload_preflight_report":
        return fail("converter post-layout payload preflight report has wrong result_type")
    if preflight.get("status") != "preflight_ready":
        return fail("converter post-layout payload preflight should be ready")
    if preflight.get("missing_file_payload_reported_not_ready") is not True:
        return fail("converter post-layout payload preflight should report missing-file payload as not ready")
    if preflight.get("temporary_complete_payload_reported_ready") is not True:
        return fail("converter post-layout payload preflight should report temporary complete payload as ready")
    if preflight.get("synthetic_accepted_evidence_persisted") is not False:
        return fail("converter post-layout payload preflight should not persist synthetic accepted evidence")
    preflight_page = (ROOT / "site" / "research" / "converter-post-layout-payload-preflight.html").read_text(encoding="utf-8")
    for marker in ["Converter Post-Layout Payload Preflight", "preflight_ready", "missing-file payload reported not ready", "temporary complete payload reported ready", "synthetic accepted evidence persisted", "shape mistake", "file mistake", "Refused Claim"]:
        if marker not in preflight_page:
            return fail(f"site/research/converter-post-layout-payload-preflight.html missing marker {marker!r}")

    candidate_workspace = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-workspace.json").read_text(encoding="utf-8"))
    if candidate_workspace.get("result_type") != "converter_post_layout_candidate_workspace":
        return fail("converter post-layout candidate workspace has wrong result_type")
    if candidate_workspace.get("status") != "candidate_workspace_ready_not_evidence":
        return fail("converter post-layout candidate workspace should be ready but not evidence")
    if candidate_workspace.get("preflight_rejects_default_payload") is not True:
        return fail("converter post-layout candidate workspace should prove preflight rejects default payload")
    if candidate_workspace.get("submission_rejects_default_payload") is not True:
        return fail("converter post-layout candidate workspace should prove submission rejects default payload")
    candidate_payload = ROOT / "evidence" / "aimc-simulator-adapters" / "candidate-post-layout" / "payload.json"
    if not candidate_payload.exists():
        return fail("converter post-layout candidate workspace should write payload.json")
    candidate_payload_json = json.loads(candidate_payload.read_text(encoding="utf-8"))
    if candidate_payload_json.get("template_only") is not True:
        return fail("converter post-layout candidate workspace payload should remain template_only")
    candidate_page = (ROOT / "site" / "research" / "converter-post-layout-candidate-workspace.html").read_text(encoding="utf-8")
    for marker in ["Converter Post-Layout Candidate Workspace", "candidate_workspace_ready_not_evidence", "preflight rejects default payload", "submission rejects default payload", "A real evidence packet is a small filesystem", "not evidence", "Refused Claim"]:
        if marker not in candidate_page:
            return fail(f"site/research/converter-post-layout-candidate-workspace.html missing marker {marker!r}")

    candidate_audit = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-workspace-audit.json").read_text(encoding="utf-8"))
    if candidate_audit.get("result_type") != "converter_post_layout_candidate_workspace_audit":
        return fail("converter post-layout candidate workspace audit has wrong result_type")
    if candidate_audit.get("status") != "candidate_workspace_still_scaffold":
        return fail("converter post-layout candidate workspace audit should report scaffold state")
    if candidate_audit.get("template_only") is not True:
        return fail("converter post-layout candidate workspace audit should preserve template_only boundary")
    if candidate_audit.get("placeholder_count", 0) < 10:
        return fail("converter post-layout candidate workspace audit should find placeholder fields")
    if candidate_audit.get("missing_or_unresolved_file_count", 0) < 3:
        return fail("converter post-layout candidate workspace audit should find missing netlist/model/rerun files")
    audit_page = (ROOT / "site" / "research" / "converter-post-layout-candidate-workspace-audit.html").read_text(encoding="utf-8")
    for marker in ["Converter Post-Layout Candidate Workspace Audit", "candidate_workspace_still_scaffold", "placeholder count", "missing or unresolved file count", "template only", "A candidate workspace becomes useful only when every name points to a real object", "not judge whether the converter is good", "Refused Claim"]:
        if marker not in audit_page:
            return fail(f"site/research/converter-post-layout-candidate-workspace-audit.html missing marker {marker!r}")

    fill_checklist = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-fill-checklist.json").read_text(encoding="utf-8"))
    if fill_checklist.get("result_type") != "converter_post_layout_candidate_fill_checklist":
        return fail("converter post-layout candidate fill checklist has wrong result_type")
    if fill_checklist.get("status") != "fill_checklist_ready":
        return fail("converter post-layout candidate fill checklist should be ready")
    if fill_checklist.get("source_audit") != "evidence/aimc-simulator-adapters/converter-post-layout-candidate-workspace-audit.json":
        return fail("converter post-layout candidate fill checklist should name the audit source")
    if fill_checklist.get("item_count") != 32:
        return fail("converter post-layout candidate fill checklist should include placeholder, file, and run-id items")
    checklist_groups = set(fill_checklist.get("groups") if isinstance(fill_checklist.get("groups"), list) else [])
    for group in ["energy", "noise", "files", "simulation", "break_even"]:
        if group not in checklist_groups:
            return fail(f"converter post-layout candidate fill checklist missing group {group}")
    checklist_page = (ROOT / "site" / "research" / "converter-post-layout-candidate-fill-checklist.html").read_text(encoding="utf-8")
    for marker in ["Converter Post-Layout Candidate Fill Checklist", "fill_checklist_ready", "checklist items", "Filling the payload is not clerical work", "Energy", "Noise", "Files", "Next Commands", "Refused Claim"]:
        if marker not in checklist_page:
            return fail(f"site/research/converter-post-layout-candidate-fill-checklist.html missing marker {marker!r}")

    candidate_progress = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-progress-report.json").read_text(encoding="utf-8"))
    if candidate_progress.get("result_type") != "converter_post_layout_candidate_progress_report":
        return fail("converter post-layout candidate progress report has wrong result_type")
    if candidate_progress.get("status") != "candidate_waiting_for_real_values":
        return fail("converter post-layout candidate progress report should wait for real values")
    if candidate_progress.get("open_checklist_items") != 32:
        return fail("converter post-layout candidate progress report should show open checklist items")
    if candidate_progress.get("ready_for_preflight") is not False:
        return fail("converter post-layout candidate progress report should keep preflight closed for scaffold")
    progress_page = (ROOT / "site" / "research" / "converter-post-layout-candidate-progress-report.html").read_text(encoding="utf-8")
    for marker in ["Converter Post-Layout Candidate Progress Report", "candidate_waiting_for_real_values", "open checklist items", "ready for preflight", "A post-layout converter claim needs two things at once", "numbers and objects", "Refused Claim"]:
        if marker not in progress_page:
            return fail(f"site/research/converter-post-layout-candidate-progress-report.html missing marker {marker!r}")

    progress_gate = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-progress-gate.json").read_text(encoding="utf-8"))
    if progress_gate.get("result_type") != "converter_post_layout_candidate_progress_gate":
        return fail("converter post-layout candidate progress gate has wrong result_type")
    if progress_gate.get("status") != "progress_gate_passed":
        return fail("converter post-layout candidate progress gate should pass")
    if progress_gate.get("current_candidate_not_ready") is not True:
        return fail("converter post-layout candidate progress gate should prove current scaffold is not ready")
    if progress_gate.get("temporary_complete_candidate_ready") is not True:
        return fail("converter post-layout candidate progress gate should prove complete temporary package is ready")
    if progress_gate.get("synthetic_accepted_evidence_persisted") is not False:
        return fail("converter post-layout candidate progress gate should not persist accepted synthetic evidence")
    progress_gate_page = (ROOT / "site" / "research" / "converter-post-layout-candidate-progress-gate.html").read_text(encoding="utf-8")
    for marker in ["Converter Post-Layout Candidate Progress Gate", "progress_gate_passed", "current candidate not ready", "temporary complete candidate ready", "A status page is useful only if it can move", "Refused Claim"]:
        if marker not in progress_gate_page:
            return fail(f"site/research/converter-post-layout-candidate-progress-gate.html missing marker {marker!r}")

    preflight_gate = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-preflight-gate.json").read_text(encoding="utf-8"))
    if preflight_gate.get("result_type") != "converter_post_layout_candidate_preflight_gate":
        return fail("converter post-layout candidate preflight gate has wrong result_type")
    if preflight_gate.get("status") != "preflight_gate_passed":
        return fail("converter post-layout candidate preflight gate should pass")
    if preflight_gate.get("current_scaffold_rejected") is not True:
        return fail("converter post-layout candidate preflight gate should reject current scaffold")
    if preflight_gate.get("temporary_complete_payload_ready") is not True:
        return fail("converter post-layout candidate preflight gate should pass complete temporary package")
    if preflight_gate.get("synthetic_accepted_evidence_persisted") is not False:
        return fail("converter post-layout candidate preflight gate should not persist accepted synthetic evidence")
    preflight_gate_page = (ROOT / "site" / "research" / "converter-post-layout-candidate-preflight-gate.html").read_text(encoding="utf-8")
    for marker in ["Converter Post-Layout Candidate Preflight Gate", "preflight_gate_passed", "current scaffold rejected", "temporary complete payload ready", "Preflight is the door before submission", "packet is complete enough to be judged", "Refused Claim"]:
        if marker not in preflight_gate_page:
            return fail(f"site/research/converter-post-layout-candidate-preflight-gate.html missing marker {marker!r}")

    submission_gate = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-submission-gate.json").read_text(encoding="utf-8"))
    if submission_gate.get("result_type") != "converter_post_layout_candidate_submission_gate":
        return fail("converter post-layout candidate submission gate has wrong result_type")
    if submission_gate.get("status") != "submission_gate_passed":
        return fail("converter post-layout candidate submission gate should pass")
    if submission_gate.get("current_scaffold_rejected") is not True:
        return fail("converter post-layout candidate submission gate should reject current scaffold")
    if submission_gate.get("temporary_complete_payload_submitted_to_temp_output") is not True:
        return fail("converter post-layout candidate submission gate should submit complete temporary package to temp output")
    if submission_gate.get("canonical_accepted_evidence_persisted") is not False:
        return fail("converter post-layout candidate submission gate should not persist canonical accepted evidence")
    if submission_gate.get("temporary_output_file_count") != 2:
        return fail("converter post-layout candidate submission gate should write exactly two temporary output files")
    submission_gate_page = (ROOT / "site" / "research" / "converter-post-layout-candidate-submission-gate.html").read_text(encoding="utf-8")
    for marker in ["Converter Post-Layout Candidate Submission Gate", "submission_gate_passed", "current scaffold rejected", "temporary complete payload submitted to temp output", "canonical accepted evidence persisted", "Submission is where a complete packet starts changing downstream evidence", "Temporary Output Files", "Refused Claim"]:
        if marker not in submission_gate_page:
            return fail(f"site/research/converter-post-layout-candidate-submission-gate.html missing marker {marker!r}")

    readiness_run = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-readiness-run.json").read_text(encoding="utf-8"))
    if readiness_run.get("result_type") != "converter_post_layout_candidate_readiness_run":
        return fail("converter post-layout candidate readiness run has wrong result_type")
    if readiness_run.get("status") != "candidate_not_ready_for_strict_submission":
        return fail("converter post-layout candidate readiness run should keep current scaffold not ready")
    if readiness_run.get("ready_for_strict_submission") is not False:
        return fail("converter post-layout candidate readiness run should not allow current scaffold submission")
    if readiness_run.get("preflight_status") != "not_ready_for_strict_submission":
        return fail("converter post-layout candidate readiness run should record not-ready preflight")
    if readiness_run.get("open_checklist_items") != 32:
        return fail("converter post-layout candidate readiness run should record open checklist items")
    readiness_preflight = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-readiness-preflight.json").read_text(encoding="utf-8"))
    if readiness_preflight.get("status") != "not_ready_for_strict_submission":
        return fail("converter post-layout candidate readiness preflight should reject current scaffold")
    readiness_page = (ROOT / "site" / "research" / "converter-post-layout-candidate-readiness-run.html").read_text(encoding="utf-8")
    for marker in ["Converter Post-Layout Candidate Readiness Run", "candidate_not_ready_for_strict_submission", "ready for strict submission", "audit status", "checklist status", "progress status", "preflight status", "Only when all four answers are clean", "Refused Claim"]:
        if marker not in readiness_page:
            return fail(f"site/research/converter-post-layout-candidate-readiness-run.html missing marker {marker!r}")

    handoff_manifest = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-handoff-manifest.json").read_text(encoding="utf-8"))
    if handoff_manifest.get("result_type") != "converter_post_layout_handoff_manifest":
        return fail("converter post-layout handoff manifest has wrong result_type")
    if handoff_manifest.get("status") != "handoff_manifest_ready":
        return fail("converter post-layout handoff manifest should be ready")
    if handoff_manifest.get("required_file_count") != 3:
        return fail("converter post-layout handoff manifest should name three required missing files")
    if handoff_manifest.get("numeric_value_count", 0) < 10:
        return fail("converter post-layout handoff manifest should name numeric values to supply")
    fixed_manifest_boundary = handoff_manifest.get("fixed_target_boundary") if isinstance(handoff_manifest.get("fixed_target_boundary"), dict) else {}
    if fixed_manifest_boundary.get("dac_bits") != 10 or fixed_manifest_boundary.get("adc_bits") != 12:
        return fail("converter post-layout handoff manifest should preserve DAC/ADC target boundary")
    if fixed_manifest_boundary.get("output_noise_budget_max") != 0.004:
        return fail("converter post-layout handoff manifest should preserve output-noise boundary")
    manifest_commands = handoff_manifest.get("commands") if isinstance(handoff_manifest.get("commands"), dict) else {}
    if manifest_commands.get("readiness") != "python3 scripts/run_converter_post_layout_candidate_readiness.py":
        return fail("converter post-layout handoff manifest should name readiness command")
    manifest_page = (ROOT / "site" / "research" / "converter-post-layout-handoff-manifest.html").read_text(encoding="utf-8")
    for marker in ["Converter Post-Layout Handoff Manifest", "handoff_manifest_ready", "required file count", "numeric value count", "Missing Files", "Numeric Values", "Identity And Provenance", "Fixed Target Boundary", "run_converter_post_layout_candidate_readiness.py", "Refused Claim"]:
        if marker not in manifest_page:
            return fail(f"site/research/converter-post-layout-handoff-manifest.html missing marker {marker!r}")

    blocker_ledger = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-blocker-ledger.json").read_text(encoding="utf-8"))
    if blocker_ledger.get("result_type") != "converter_post_layout_blocker_ledger":
        return fail("converter post-layout blocker ledger has wrong result_type")
    if blocker_ledger.get("status") != "blocked_on_real_post_layout_evidence":
        return fail("converter post-layout blocker ledger should record blocked-on-real-evidence status")
    if blocker_ledger.get("blocker_count", 0) < 25:
        return fail("converter post-layout blocker ledger should expose the current scaffold blockers")
    ledger_categories = blocker_ledger.get("blockers_by_category") if isinstance(blocker_ledger.get("blockers_by_category"), dict) else {}
    for category in ["placeholder", "missing_file", "numeric_boundary"]:
        if category not in ledger_categories:
            return fail(f"converter post-layout blocker ledger missing category {category}")
    if blocker_ledger.get("next_command") != "python3 scripts/run_converter_post_layout_candidate_readiness.py":
        return fail("converter post-layout blocker ledger should name the readiness command")
    ledger_page = (ROOT / "site" / "research" / "converter-post-layout-blocker-ledger.html").read_text(encoding="utf-8")
    for marker in ["Converter Post-Layout Blocker Ledger", "blocked_on_real_post_layout_evidence", "blocker count", "Blockers By Category", "Current Blockers", "evidence action", "Fixed Target Boundary", "Refused Claim"]:
        if marker not in ledger_page:
            return fail(f"site/research/converter-post-layout-blocker-ledger.html missing marker {marker!r}")

    edit_plan = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-edit-plan.json").read_text(encoding="utf-8"))
    if edit_plan.get("result_type") != "converter_post_layout_candidate_edit_plan":
        return fail("converter post-layout candidate edit plan has wrong result_type")
    if edit_plan.get("status") != "candidate_edit_plan_ready":
        return fail("converter post-layout candidate edit plan should be ready")
    if edit_plan.get("edit_count") != 32:
        return fail("converter post-layout candidate edit plan should expose 32 candidate edits")
    if edit_plan.get("blocked_edit_count") != 32:
        return fail("converter post-layout candidate edit plan should mark currently blocked edits")
    edit_fields = {item.get("field") for item in edit_plan.get("edits", []) if isinstance(item, dict)}
    for field in ["extraction.extracted_netlist", "simulation.model_files[0]", "energy.adc_energy_per_conversion", "noise.output_noise_rms", "break_even_rerun.rerun_artifact"]:
        if field not in edit_fields:
            return fail(f"converter post-layout candidate edit plan missing field {field}")
    edit_page = (ROOT / "site" / "research" / "converter-post-layout-candidate-edit-plan.html").read_text(encoding="utf-8")
    for marker in ["Converter Post-Layout Candidate Edit Plan", "candidate_edit_plan_ready", "edit count", "blocked edit count", "Recommended Order", "Field Edits", "evidence source", "accepted value shape", "run_converter_post_layout_candidate_readiness.py", "Refused Claim"]:
        if marker not in edit_page:
            return fail(f"site/research/converter-post-layout-candidate-edit-plan.html missing marker {marker!r}")

    same_run_gate = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-same-run-gate.json").read_text(encoding="utf-8"))
    if same_run_gate.get("result_type") != "converter_post_layout_same_run_gate":
        return fail("converter post-layout same-run gate has wrong result_type")
    if same_run_gate.get("status") != "same_run_gate_passed":
        return fail("converter post-layout same-run gate should pass")
    if same_run_gate.get("current_scaffold_rejected") is not True:
        return fail("converter post-layout same-run gate should reject current scaffold")
    if same_run_gate.get("temporary_same_run_fixture_accepted") is not True:
        return fail("converter post-layout same-run gate should accept temporary same-run fixture")
    run_fields = set(same_run_gate.get("required_run_id_fields") if isinstance(same_run_gate.get("required_run_id_fields"), list) else [])
    for field in ["provenance.run_id", "energy.run_id", "latency.run_id", "noise.run_id", "area.run_id", "break_even_rerun.run_id"]:
        if field not in run_fields:
            return fail(f"converter post-layout same-run gate missing run-id field {field}")
    same_run_page = (ROOT / "site" / "research" / "converter-post-layout-same-run-gate.html").read_text(encoding="utf-8")
    for marker in ["Converter Post-Layout Same-Run Gate", "same_run_gate_passed", "current scaffold rejected", "temporary same-run fixture accepted", "Required Run Id Fields", "provenance.run_id", "energy.run_id", "break_even_rerun.run_id", "Refused Claim"]:
        if marker not in same_run_page:
            return fail(f"site/research/converter-post-layout-same-run-gate.html missing marker {marker!r}")

    identity_initializer = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-identity-initializer.json").read_text(encoding="utf-8"))
    if identity_initializer.get("result_type") != "converter_post_layout_candidate_identity_initializer":
        return fail("converter post-layout candidate identity initializer has wrong result_type")
    if identity_initializer.get("status") != "identity_initializer_ready":
        return fail("converter post-layout candidate identity initializer should be ready")
    if identity_initializer.get("applied_to_source_payload") is not False:
        return fail("converter post-layout candidate identity initializer must not modify the source scaffold in self-test")
    if identity_initializer.get("same_run_identity_validation_passed_after_identity_fill") is not True:
        return fail("converter post-layout candidate identity initializer should pass identity validation")
    if identity_initializer.get("strict_same_run_validation_passed_after_identity_fill") is not False:
        return fail("converter post-layout candidate identity initializer should leave strict validation blocked by template status")
    initialized_fields = set(identity_initializer.get("fields_initialized") if isinstance(identity_initializer.get("fields_initialized"), list) else [])
    if len(initialized_fields) != 14:
        return fail("converter post-layout candidate identity initializer should initialize 14 fields")
    for field in ["converter_id", "provenance.run_id", "simulation.run_id", "break_even_rerun.rerun_artifact"]:
        if field not in initialized_fields:
            return fail(f"converter post-layout candidate identity initializer missing field {field}")
    if "does not write accepted evidence" not in str(identity_initializer.get("claim_boundary", {}).get("not_allowed", "")):
        return fail("converter post-layout candidate identity initializer should refuse accepted evidence writes")
    identity_page = (ROOT / "site" / "research" / "converter-post-layout-candidate-identity-initializer.html").read_text(encoding="utf-8")
    for marker in ["Converter Post-Layout Candidate Identity Initializer", "identity_initializer_ready", "same-run identity validation passed after identity fill", "strict same-run validation passed after identity fill", "applied to source payload: <code>False</code>", "Fields Initialized", "converter_id", "provenance.run_id", "does not invent numeric post-layout values", "Refused Claim"]:
        if marker not in identity_page:
            return fail(f"site/research/converter-post-layout-candidate-identity-initializer.html missing marker {marker!r}")

    builder_page = (ROOT / "site" / "research" / "converter-post-layout-real-candidate-builder.html").read_text(encoding="utf-8")
    builder_artifact = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-real-candidate-builder.json").read_text(encoding="utf-8"))
    if builder_artifact.get("result_type") != "converter_post_layout_real_candidate_builder":
        return fail("converter post-layout real candidate builder has wrong result_type")
    if builder_artifact.get("status") != "candidate_payload_built":
        return fail("converter post-layout real candidate builder self-test should build a temporary payload")
    if builder_artifact.get("self_test") is not True:
        return fail("converter post-layout real candidate builder artifact should come from self-test")
    if builder_artifact.get("strict_validation_passed") is not True or builder_artifact.get("strict_issue_count") != 0:
        return fail("converter post-layout real candidate builder self-test should pass strict validation")
    if builder_artifact.get("temporary_fixture_persisted") is not False:
        return fail("converter post-layout real candidate builder self-test must not persist temporary fixture")
    if builder_artifact.get("preview_status_before_removal") != "ready_to_submit_without_writing":
        return fail("converter post-layout real candidate builder self-test should be preview-ready before removal")
    if builder_artifact.get("preview_would_write_accepted_evidence_before_removal") is not True:
        return fail("converter post-layout real candidate builder self-test preview should be ready to write if submitted")
    if builder_artifact.get("preview_strict_issue_count_before_removal") != 0:
        return fail("converter post-layout real candidate builder self-test preview should have no strict issues")
    for marker in ["Converter Post-Layout Real Candidate Builder", "build_converter_post_layout_candidate_from_real_run.py", "the extracted netlist or measured setup", "one converter id and one run id", "What It Writes", "candidate-post-layout/payload.json", "preview_converter_post_layout_submission.py", "candidate_payload_built", "self-test: <code>True</code>", "temporary fixture persisted: <code>False</code>", "strict validation passed: <code>True</code>", "strict issue count: <code>0</code>", "preview status before removal: <code>ready_to_submit_without_writing</code>", "preview would write accepted evidence before removal: <code>True</code>", "does not write accepted evidence"]:
        if marker not in builder_page:
            return fail(f"site/research/converter-post-layout-real-candidate-builder.html missing marker {marker!r}")

    submission_preview = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-submission-preview.json").read_text(encoding="utf-8"))
    if submission_preview.get("result_type") != "converter_post_layout_submission_preview":
        return fail("converter post-layout submission preview has wrong result_type")
    if submission_preview.get("status") != "blocked_before_submission":
        return fail("converter post-layout submission preview should block the scaffold")
    if submission_preview.get("would_write_accepted_evidence") is not False:
        return fail("converter post-layout submission preview must not write accepted evidence for scaffold")
    if submission_preview.get("strict_issue_count") != 22:
        return fail("converter post-layout submission preview should expose 22 strict issues")
    if "accepted-post-layout" not in str(submission_preview.get("output_dir", "")):
        return fail("converter post-layout submission preview should show accepted output directory")
    if "does not create accepted-post-layout" not in str(submission_preview.get("claim_boundary", {}).get("not_allowed", "")):
        return fail("converter post-layout submission preview should refuse accepted evidence writes")
    preview_page = (ROOT / "site" / "research" / "converter-post-layout-submission-preview.html").read_text(encoding="utf-8")
    for marker in ["Converter Post-Layout Submission Preview", "blocked_before_submission", "would write accepted evidence: <code>False</code>", "strict issue count: <code>22</code>", "Would Write Files", "blocked-until-real-converter-id.break-even-rerun.json", "Strict Issues", "template_boundary", "Refused Claim"]:
        if marker not in preview_page:
            return fail(f"site/research/converter-post-layout-submission-preview.html missing marker {marker!r}")

    leakage_audit = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-evidence-leakage-audit.json").read_text(encoding="utf-8"))
    if leakage_audit.get("result_type") != "converter_post_layout_evidence_leakage_audit":
        return fail("converter post-layout evidence leakage audit has wrong result_type")
    if leakage_audit.get("status") != "no_evidence_leakage_detected":
        return fail("converter post-layout evidence leakage audit should pass")
    if leakage_audit.get("accepted_post_layout_exists") is not False:
        return fail("converter post-layout evidence leakage audit should show no accepted evidence directory")
    if leakage_audit.get("candidate_non_scaffold_file_count") != 0:
        return fail("converter post-layout evidence leakage audit should show no extra candidate files")
    if leakage_audit.get("candidate_temp_marker_hit_count") != 0:
        return fail("converter post-layout evidence leakage audit should show no temp markers in candidate workspace")
    if leakage_audit.get("builder_temp_paths_are_labeled") is not True:
        return fail("converter post-layout evidence leakage audit should show builder temp paths are labeled")
    if leakage_audit.get("builder_preview_ready_before_removal") is not True:
        return fail("converter post-layout evidence leakage audit should show builder preview-ready before removal")
    leakage_page = (ROOT / "site" / "research" / "converter-post-layout-evidence-leakage-audit.html").read_text(encoding="utf-8")
    for marker in ["Converter Post-Layout Evidence Leakage Audit", "no_evidence_leakage_detected", "accepted post-layout exists: <code>False</code>", "candidate non-scaffold file count: <code>0</code>", "candidate temp marker hit count: <code>0</code>", "builder temp paths are labeled: <code>True</code>", "builder preview ready before removal: <code>True</code>", "temporary self-test package removed", "accepted evidence only after strict submission", "Refused Claim"]:
        if marker not in leakage_page:
            return fail(f"site/research/converter-post-layout-evidence-leakage-audit.html missing marker {marker!r}")

    temporary_submission = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-temporary-submission-proof.json").read_text(encoding="utf-8"))
    if temporary_submission.get("result_type") != "converter_post_layout_temporary_submission_proof":
        return fail("converter post-layout temporary submission proof has wrong result_type")
    if temporary_submission.get("status") != "temporary_submission_path_proven":
        return fail("converter post-layout temporary submission proof should pass")
    if temporary_submission.get("temporary_submit_passed") is not True:
        return fail("converter post-layout temporary submission proof should submit to temp dir")
    if temporary_submission.get("temporary_accepted_file_count") != 2:
        return fail("converter post-layout temporary submission proof should write two temp accepted files")
    if temporary_submission.get("temporary_fixture_persisted") is not False:
        return fail("converter post-layout temporary submission proof should remove temp fixture")
    if temporary_submission.get("canonical_accepted_evidence_exists_after_proof") is not False:
        return fail("converter post-layout temporary submission proof should leave canonical accepted evidence absent")
    temp_submission_page = (ROOT / "site" / "research" / "converter-post-layout-temporary-submission-proof.html").read_text(encoding="utf-8")
    for marker in ["Converter Post-Layout Temporary Submission Proof", "temporary_submission_path_proven", "preview would write accepted evidence: <code>True</code>", "temporary submit passed: <code>True</code>", "temporary accepted files written: <code>2</code>", "canonical accepted evidence exists after proof: <code>False</code>", "temporary fixture persisted: <code>False</code>", "The write path works", "Refused Claim"]:
        if marker not in temp_submission_page:
            return fail(f"site/research/converter-post-layout-temporary-submission-proof.html missing marker {marker!r}")

    real_artifact_discovery = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-real-artifact-discovery.json").read_text(encoding="utf-8"))
    if real_artifact_discovery.get("result_type") != "converter_post_layout_real_artifact_discovery":
        return fail("converter post-layout real artifact discovery has wrong result_type")
    if real_artifact_discovery.get("status") != "no_complete_real_artifact_package_found":
        return fail("converter post-layout real artifact discovery should show no complete real package")
    if real_artifact_discovery.get("accepted_post_layout_exists") is not False:
        return fail("converter post-layout real artifact discovery should show no accepted evidence directory")
    candidate_workspace = real_artifact_discovery.get("candidate_workspace") if isinstance(real_artifact_discovery.get("candidate_workspace"), dict) else {}
    if candidate_workspace.get("non_scaffold_file_count") != 2:
        return fail("converter post-layout real artifact discovery should show the two current partial candidate files")
    if real_artifact_discovery.get("current_candidate_would_write_accepted_evidence") is not False:
        return fail("converter post-layout real artifact discovery should show current candidate cannot write accepted evidence")
    if real_artifact_discovery.get("current_candidate_strict_issue_count") != 22:
        return fail("converter post-layout real artifact discovery should record current candidate strict issue count")
    discovery_page = (ROOT / "site" / "research" / "converter-post-layout-real-artifact-discovery.html").read_text(encoding="utf-8")
    for marker in ["Converter Post-Layout Real Artifact Discovery", "no_complete_real_artifact_package_found", "accepted post-layout exists: <code>False</code>", "candidate non-scaffold file count: <code>2</code>", "current candidate would write accepted evidence: <code>False</code>", "current candidate strict issue count: <code>22</code>", "Repo-Local Artifact Counts", "A real post-layout claim needs a chain of named objects", "Refused Claim"]:
        if marker not in discovery_page:
            return fail(f"site/research/converter-post-layout-real-artifact-discovery.html missing marker {marker!r}")

    real_run_recipe_json = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-real-run-recipe.json").read_text(encoding="utf-8"))
    if real_run_recipe_json.get("result_type") != "converter_post_layout_real_run_recipe":
        return fail("converter post-layout real-run recipe has wrong result_type")
    if real_run_recipe_json.get("status") != "real_run_recipe_ready_not_evidence":
        return fail("converter post-layout real-run recipe should be ready but not evidence")
    if real_run_recipe_json.get("source_checklist") != "evidence/aimc-simulator-adapters/converter-post-layout-candidate-fill-checklist.json":
        return fail("converter post-layout real-run recipe should name the checklist source")
    if real_run_recipe_json.get("source_handoff_manifest") != "evidence/aimc-simulator-adapters/converter-post-layout-handoff-manifest.json":
        return fail("converter post-layout real-run recipe should name the handoff source")
    if real_run_recipe_json.get("step_count") != 9:
        return fail("converter post-layout real-run recipe should have nine ordered steps")
    recipe_steps = real_run_recipe_json.get("recipe_steps") if isinstance(real_run_recipe_json.get("recipe_steps"), list) else []
    recipe_step_names = {step.get("name") for step in recipe_steps if isinstance(step, dict)}
    for name in ["choose_converter_layout", "extract_post_layout_circuit", "run_one_named_experiment", "record_physical_values", "rerun_break_even", "strict_submit_only_if_ready"]:
        if name not in recipe_step_names:
            return fail(f"converter post-layout real-run recipe missing step {name}")
    recipe_run_fields = set(real_run_recipe_json.get("required_shared_run_id_fields") if isinstance(real_run_recipe_json.get("required_shared_run_id_fields"), list) else [])
    for field in ["provenance.run_id", "simulation.run_id", "energy.run_id", "latency.run_id", "noise.run_id", "area.run_id", "break_even_rerun.run_id"]:
        if field not in recipe_run_fields:
            return fail(f"converter post-layout real-run recipe missing shared run-id field {field}")
    if "accepted-post-layout" not in str(real_run_recipe_json.get("manual_write_forbidden", "")):
        return fail("converter post-layout real-run recipe should forbid manual accepted-post-layout writes")
    real_run_recipe = (ROOT / "site" / "research" / "converter-post-layout-real-run-recipe.html").read_text(encoding="utf-8")
    for marker in ["Converter Post-Layout Real Run Recipe", "Run Order", "Create or choose one converter layout", "Extract the post-layout circuit", "Run one named post-layout or measured-silicon experiment", "shared <code>run_id</code>", "Check the fixed boundary", "Rerun the break-even calculation", "Do not create <code>accepted-post-layout</code> by hand", "Converter Post-Layout Real Run Recipe Artifact", "real_run_recipe_ready_not_evidence", "Ordered Steps", "choose_converter_layout", "strict_submit_only_if_ready", "Manual Write Boundary", "run_converter_post_layout_candidate_readiness.py", "Refused Claim"]:
        if marker not in real_run_recipe:
            return fail(f"site/research/converter-post-layout-real-run-recipe.html missing marker {marker!r}")

    real_run_coverage = json.loads((ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-real-run-recipe-coverage.json").read_text(encoding="utf-8"))
    if real_run_coverage.get("result_type") != "converter_post_layout_real_run_recipe_coverage":
        return fail("converter post-layout real-run recipe coverage has wrong result_type")
    if real_run_coverage.get("status") != "real_run_recipe_covers_current_checklist":
        return fail("converter post-layout real-run recipe coverage should cover current checklist")
    if real_run_coverage.get("source_recipe") != "evidence/aimc-simulator-adapters/converter-post-layout-real-run-recipe.json":
        return fail("converter post-layout real-run recipe coverage should name recipe source")
    if real_run_coverage.get("checklist_field_count") != 32:
        return fail("converter post-layout real-run recipe coverage should see 32 checklist fields")
    if real_run_coverage.get("covered_checklist_field_count") != 32:
        return fail("converter post-layout real-run recipe coverage should cover all checklist fields")
    if real_run_coverage.get("uncovered_checklist_fields") != []:
        return fail("converter post-layout real-run recipe coverage should have no uncovered checklist fields")
    if real_run_coverage.get("payload_blocker_field_count") != 32:
        return fail("converter post-layout real-run recipe coverage should classify 32 payload blocker fields")
    if real_run_coverage.get("uncovered_blocker_field_count") != 0:
        return fail("converter post-layout real-run recipe coverage should cover all payload blocker fields")
    non_field_blockers = real_run_coverage.get("non_field_boundary_blockers") if isinstance(real_run_coverage.get("non_field_boundary_blockers"), list) else []
    for blocker in ["template payloads cannot be submitted", "template payloads cannot pass same-run consistency"]:
        if blocker not in non_field_blockers:
            return fail(f"converter post-layout real-run recipe coverage missing non-field blocker {blocker!r}")
    coverage_page = (ROOT / "site" / "research" / "converter-post-layout-real-run-recipe-coverage.html").read_text(encoding="utf-8")
    for marker in ["Converter Post-Layout Real Run Recipe Coverage", "real_run_recipe_covers_current_checklist", "covered checklist field count", "payload blocker field count", "non-field boundary blocker count", "Non-Field Boundary Blockers", "template payloads cannot be submitted", "Uncovered Payload Blocker Fields", "none", "Refused Claim"]:
        if marker not in coverage_page:
            return fail(f"site/research/converter-post-layout-real-run-recipe-coverage.html missing marker {marker!r}")

    current_state = json.loads((ROOT / "evidence" / "aimc-hardware-lab" / "current-aimc-system-state.json").read_text(encoding="utf-8"))
    if current_state.get("result_type") != "current_aimc_system_state":
        return fail("current AIMC system state summary has wrong result_type")
    if current_state.get("proof_status") != "PASS":
        return fail("current AIMC system state summary does not record a passing proof")
    if current_state.get("package_id") != "pkg-e931662a01293df2":
        return fail("current AIMC system state summary has the wrong package")
    current_fill_checklist = current_state.get("converter_post_layout_candidate_fill_checklist_state") if isinstance(current_state.get("converter_post_layout_candidate_fill_checklist_state"), dict) else {}
    if current_fill_checklist.get("status") != "fill_checklist_ready":
        return fail("current AIMC system state should include ready converter post-layout candidate fill checklist")
    if current_fill_checklist.get("item_count") != 32:
        return fail("current AIMC system state should include 32 converter fill checklist items")
    current_fill_groups = set(current_fill_checklist.get("groups") if isinstance(current_fill_checklist.get("groups"), list) else [])
    for group in ["energy", "noise", "files", "simulation", "break_even"]:
        if group not in current_fill_groups:
            return fail(f"current AIMC system state fill checklist missing group {group}")
    current_candidate_progress = current_state.get("converter_post_layout_candidate_progress_state") if isinstance(current_state.get("converter_post_layout_candidate_progress_state"), dict) else {}
    if current_candidate_progress.get("status") != "candidate_waiting_for_real_values":
        return fail("current AIMC system state should record candidate progress waiting for real values")
    if current_candidate_progress.get("open_checklist_items") != 32:
        return fail("current AIMC system state should record open candidate checklist items")
    if current_candidate_progress.get("ready_for_preflight") is not False:
        return fail("current AIMC system state should record candidate as not ready for preflight")
    current_candidate_gate_chain = current_state.get("converter_post_layout_candidate_gate_chain_state") if isinstance(current_state.get("converter_post_layout_candidate_gate_chain_state"), dict) else {}
    if current_candidate_gate_chain.get("status") != "candidate_gate_chain_passed":
        return fail("current AIMC system state should record candidate gate chain as passed")
    if current_candidate_gate_chain.get("progress_gate") != "progress_gate_passed":
        return fail("current AIMC system state should record progress gate pass")
    if current_candidate_gate_chain.get("preflight_gate") != "preflight_gate_passed":
        return fail("current AIMC system state should record preflight gate pass")
    if current_candidate_gate_chain.get("submission_gate") != "submission_gate_passed":
        return fail("current AIMC system state should record submission gate pass")
    if current_candidate_gate_chain.get("canonical_accepted_evidence_persisted") is not False:
        return fail("current AIMC system state should record no canonical accepted evidence persisted")
    current_readiness_run = current_state.get("converter_post_layout_candidate_readiness_run_state") if isinstance(current_state.get("converter_post_layout_candidate_readiness_run_state"), dict) else {}
    if current_readiness_run.get("status") != "candidate_not_ready_for_strict_submission":
        return fail("current AIMC system state should record candidate readiness runner as not ready")
    if current_readiness_run.get("ready_for_strict_submission") is not False:
        return fail("current AIMC system state should record readiness runner as not allowing strict submission")
    if current_readiness_run.get("preflight_issue_count") != 22:
        return fail("current AIMC system state should record current candidate preflight issue count")
    current_claims = current_state.get("claim_summary") if isinstance(current_state.get("claim_summary"), dict) else {}
    if current_claims.get("supported_lab_claims") != 3:
        return fail("current AIMC system state summary should record 3 supported lab claims")
    if current_claims.get("needs_review_lab_claims") != 2:
        return fail("current AIMC system state summary should record 2 needs-review lab claims")
    if current_claims.get("production_claim") != "blocked":
        return fail("current AIMC system state summary should keep production blocked")
    current_sim = current_state.get("simulator_state") if isinstance(current_state.get("simulator_state"), dict) else {}
    if current_sim.get("aihwkit", {}).get("status") != "available":
        return fail("current AIMC system state summary should record AIHWKIT as available")
    if current_sim.get("crosssim", {}).get("status") != "available":
        return fail("current AIMC system state summary should record CrossSim as available")
    current_sim_gap = current_state.get("simulator_to_post_layout_gap_state") if isinstance(current_state.get("simulator_to_post_layout_gap_state"), dict) else {}
    if current_sim_gap.get("status") != "simulator_evidence_present_post_layout_converter_evidence_missing":
        return fail("current AIMC system state summary should record simulator-to-post-layout gap")
    if current_sim_gap.get("simulator_payload_count", 0) < 2:
        return fail("current AIMC system state summary should record simulator payloads in gap audit")
    if current_sim_gap.get("post_layout_converter_ready_payload_count") != 0:
        return fail("current AIMC system state summary should record no post-layout converter-ready simulator payloads")
    current_placement = current_state.get("placement_state") if isinstance(current_state.get("placement_state"), dict) else {}
    if current_placement.get("residual_aware_analog_allowed") != 2:
        return fail("current AIMC system state summary should record 2 residual-aware analog allowed rows")
    if current_placement.get("accepted_calibrated_source") != "deep_transformer_mlp_stack":
        return fail("current AIMC system state summary should record deep_transformer_mlp_stack")
    if current_placement.get("source_matching_policy") != "fixed_weight_matmul_family_match":
        return fail("current AIMC system state summary should record fixed-weight MatMul source matching")
    current_onnx = current_state.get("onnx_fixture_state") if isinstance(current_state.get("onnx_fixture_state"), dict) else {}
    if current_onnx.get("status") != "available":
        return fail("current AIMC system state summary should record ONNX fixture inventory as available")
    if current_onnx.get("selected_current_best_fixture") != "deep-transformer-mlp-stack.onnx":
        return fail("current AIMC system state summary should record selected ONNX fixture")
    if current_onnx.get("max_fixed_weight_matmul_count", 0) < 12:
        return fail("current AIMC system state summary should record the larger ONNX fixture MatMul count")
    current_digital_physical = current_state.get("digital_physical_boundary_state") if isinstance(current_state.get("digital_physical_boundary_state"), dict) else {}
    if current_digital_physical.get("status") != "digital_physical_artifacts_present_analog_converter_post_layout_missing":
        return fail("current AIMC system state summary should record digital physical boundary status")
    if current_digital_physical.get("digital_physical_flow_supported_count", 0) < 3:
        return fail("current AIMC system state summary should record supported digital physical runs")
    if current_digital_physical.get("analog_converter_post_layout_supported") is not False:
        return fail("current AIMC system state summary should keep analog converter post-layout unsupported")
    current_analog_layout_work_order = current_state.get("analog_converter_layout_work_order_state") if isinstance(current_state.get("analog_converter_layout_work_order_state"), dict) else {}
    if current_analog_layout_work_order.get("status") != "layout_work_order_ready_waiting_for_converter_layout":
        return fail("current AIMC system state summary should record analog converter layout work order status")
    if current_analog_layout_work_order.get("all_starting_spice_decks_exist") is not True:
        return fail("current AIMC system state summary should record starting SPICE decks")
    if current_analog_layout_work_order.get("deliverable_count") != 5:
        return fail("current AIMC system state summary should record analog converter layout deliverables")
    current_layout = current_state.get("layout_risk_state") if isinstance(current_state.get("layout_risk_state"), dict) else {}
    if current_layout.get("status") != "available":
        return fail("current AIMC system state summary should record layout risk as available")
    if current_layout.get("operators") != 2:
        return fail("current AIMC system state summary should record 2 layout-risk operators")
    if current_layout.get("review") != 2 or current_layout.get("blocked") != 0:
        return fail("current AIMC system state summary should record 2 review layout-risk rows and 0 blocked rows")
    if current_layout.get("source_matching_policy") != "fixed_weight_matmul_family_match":
        return fail("current AIMC system state summary should preserve layout-risk source matching")
    current_aihwkit_diag = current_state.get("aihwkit_diagnostic_state") if isinstance(current_state.get("aihwkit_diagnostic_state"), dict) else {}
    if current_aihwkit_diag.get("status") != "available":
        return fail("current AIMC system state summary should record AIHWKIT diagnostic as available")
    if current_aihwkit_diag.get("threshold_fail_payloads", 0) < 5:
        return fail("current AIMC system state summary should record AIHWKIT threshold-fail payloads")
    if not current_aihwkit_diag.get("worst_candidate"):
        return fail("current AIMC system state summary should record the worst AIHWKIT candidate")
    current_aihwkit_mapping = current_state.get("aihwkit_ideal_mapping_state") if isinstance(current_state.get("aihwkit_ideal_mapping_state"), dict) else {}
    if current_aihwkit_mapping.get("status") != "available":
        return fail("current AIMC system state summary should record AIHWKIT ideal mapping as available")
    if current_aihwkit_mapping.get("rows") != 16 or current_aihwkit_mapping.get("passing_rows") != 16:
        return fail("current AIMC system state summary should record the 16-row AIHWKIT ideal mapping pass")
    current_aihwkit_sweep = current_state.get("aihwkit_forward_sweep_state") if isinstance(current_state.get("aihwkit_forward_sweep_state"), dict) else {}
    if current_aihwkit_sweep.get("status") != "available":
        return fail("current AIMC system state summary should record AIHWKIT forward sweep as available")
    if current_aihwkit_sweep.get("settings") != 5 or current_aihwkit_sweep.get("rows_per_setting") != 16:
        return fail("current AIMC system state summary should record the AIHWKIT forward sweep shape")
    if current_aihwkit_sweep.get("passing_settings", 0) < 1:
        return fail("current AIMC system state summary should record a passing AIHWKIT forward setting")
    current_aihwkit_physical = current_state.get("aihwkit_physical_review_state") if isinstance(current_state.get("aihwkit_physical_review_state"), dict) else {}
    if current_aihwkit_physical.get("status") != "available":
        return fail("current AIMC system state summary should record AIHWKIT physical review as available")
    if current_aihwkit_physical.get("review_status") != "needs_physical_justification":
        return fail("current AIMC system state summary should preserve AIHWKIT physical review status")
    if current_aihwkit_physical.get("candidate_effective_input_bits") != 10 or current_aihwkit_physical.get("candidate_effective_output_bits") != 12:
        return fail("current AIMC system state summary should record candidate effective bit boundary")
    if current_aihwkit_physical.get("tile_dac_bits") != 4 or current_aihwkit_physical.get("tile_adc_bits") != 6:
        return fail("current AIMC system state summary should record current tile bit boundary")
    current_tile_replay = current_state.get("aihwkit_current_tile_replay_state") if isinstance(current_state.get("aihwkit_current_tile_replay_state"), dict) else {}
    if current_tile_replay.get("status") != "available":
        return fail("current AIMC system state summary should record AIHWKIT current-tile replay as available")
    if current_tile_replay.get("dac_bits") != 4 or current_tile_replay.get("adc_bits") != 6:
        return fail("current AIMC system state summary should record replay tile bits")
    if current_tile_replay.get("passing_rows") != 0 or current_tile_replay.get("failing_rows") != 16:
        return fail("current AIMC system state summary should record current-tile replay failures")
    current_converter_target = current_state.get("aihwkit_converter_target_state") if isinstance(current_state.get("aihwkit_converter_target_state"), dict) else {}
    if current_converter_target.get("status") != "target_defined_not_justified":
        return fail("current AIMC system state summary should record converter target status")
    if current_converter_target.get("target_input_bits") != 10 or current_converter_target.get("target_output_bits") != 12:
        return fail("current AIMC system state summary should record converter target bits")
    if current_converter_target.get("input_bit_gap") != 6 or current_converter_target.get("output_bit_gap") != 6:
        return fail("current AIMC system state summary should record converter target bit gaps")
    current_converter_cost = current_state.get("aihwkit_converter_cost_state") if isinstance(current_state.get("aihwkit_converter_cost_state"), dict) else {}
    if current_converter_cost.get("status") != "fallback_preferred_until_cost_is_justified":
        return fail("current AIMC system state summary should record converter cost fallback status")
    if not isinstance(current_converter_cost.get("energy_multiplier_vs_current"), (int, float)) or current_converter_cost["energy_multiplier_vs_current"] < 40:
        return fail("current AIMC system state summary should record converter energy multiplier")
    current_target_noise = current_state.get("aihwkit_target_noise_state") if isinstance(current_state.get("aihwkit_target_noise_state"), dict) else {}
    if current_target_noise.get("status") != "available":
        return fail("current AIMC system state summary should record target noise sensitivity")
    if current_target_noise.get("highest_all_pass_out_noise") != 0.004:
        return fail("current AIMC system state summary should record the 0.004 output-noise budget")
    if current_target_noise.get("passes_any_nonzero_noise") is not True:
        return fail("current AIMC system state summary should record nonzero-noise pass")
    current_break_even = current_state.get("aihwkit_converter_break_even_state") if isinstance(current_state.get("aihwkit_converter_break_even_state"), dict) else {}
    if current_break_even.get("status") != "available":
        return fail("current AIMC system state summary should record converter break-even")
    if current_break_even.get("scenario_count") != 4:
        return fail("current AIMC system state summary should record converter break-even scenario count")
    if current_break_even.get("default_decision") != "digital_fallback_until_real_converter_and_array_savings_are_measured":
        return fail("current AIMC system state summary should preserve converter break-even fallback decision")
    current_converter_contract = current_state.get("converter_circuit_contract_state") if isinstance(current_state.get("converter_circuit_contract_state"), dict) else {}
    if current_converter_contract.get("status") != "contract_defined_placeholder_not_claim_ready":
        return fail("current AIMC system state summary should record converter circuit contract status")
    if current_converter_contract.get("schema_complete") is not True:
        return fail("current AIMC system state summary should record converter circuit contract schema completeness")
    if current_converter_contract.get("claim_ready_to_replace_break_even") is not False:
        return fail("current AIMC system state summary should record converter circuit contract as not claim-ready")
    current_local_converter = current_state.get("local_converter_estimate_state") if isinstance(current_state.get("local_converter_estimate_state"), dict) else {}
    if current_local_converter.get("status") != "local_estimate_complete_not_claim_ready":
        return fail("current AIMC system state summary should record local converter estimate status")
    if current_local_converter.get("schema_complete") is not True:
        return fail("current AIMC system state summary should record local converter estimate schema completeness")
    if current_local_converter.get("claim_ready_to_replace_break_even") is not False:
        return fail("current AIMC system state summary should record local converter estimate as not claim-ready")
    current_circuit_sim = current_state.get("converter_circuit_simulation_estimate_state") if isinstance(current_state.get("converter_circuit_simulation_estimate_state"), dict) else {}
    if current_circuit_sim.get("status") != "circuit_simulation_complete_not_replacement_ready":
        return fail("current AIMC system state summary should record converter circuit-simulation estimate status")
    if current_circuit_sim.get("schema_complete") is not True:
        return fail("current AIMC system state summary should record converter circuit-simulation schema completeness")
    if current_circuit_sim.get("claim_ready_to_replace_break_even") is not False:
        return fail("current AIMC system state summary should record converter circuit-simulation as not claim-ready")
    if current_circuit_sim.get("meets_output_noise_budget") is not True:
        return fail("current AIMC system state summary should record converter circuit-simulation noise pass")
    current_spice_handoff = current_state.get("converter_spice_handoff_spec_state") if isinstance(current_state.get("converter_spice_handoff_spec_state"), dict) else {}
    if current_spice_handoff.get("status") != "available":
        return fail("current AIMC system state summary should record converter SPICE handoff as available")
    if current_spice_handoff.get("testbenches") != 4:
        return fail("current AIMC system state summary should record four converter SPICE handoff testbenches")
    if current_spice_handoff.get("can_replace_break_even") is not False:
        return fail("current AIMC system state summary should record converter SPICE handoff as not replacing break-even")
    current_row_dac = current_state.get("row_dac_settling_spice_state") if isinstance(current_state.get("row_dac_settling_spice_state"), dict) else {}
    if current_row_dac.get("status") != "row_dac_settling_spice_passes_simple_load":
        return fail("current AIMC system state summary should record row-DAC settling SPICE status")
    if current_row_dac.get("cases") != 3:
        return fail("current AIMC system state summary should record three row-DAC settling SPICE cases")
    if current_row_dac.get("all_cases_pass_half_lsb") is not True:
        return fail("current AIMC system state summary should record row-DAC settling SPICE pass")
    current_sar = current_state.get("sar_readout_spice_state") if isinstance(current_state.get("sar_readout_spice_state"), dict) else {}
    if current_sar.get("status") != "sar_readout_spice_passes_simple_sample_load":
        return fail("current AIMC system state summary should record SAR readout SPICE status")
    if current_sar.get("cases") != 3:
        return fail("current AIMC system state summary should record three SAR readout SPICE cases")
    if current_sar.get("comparisons") != 12:
        return fail("current AIMC system state summary should record 12 SAR comparisons")
    if current_sar.get("all_cases_pass_half_lsb") is not True:
        return fail("current AIMC system state summary should record SAR readout SPICE pass")
    current_shared_loading = current_state.get("shared_converter_loading_spice_state") if isinstance(current_state.get("shared_converter_loading_spice_state"), dict) else {}
    if current_shared_loading.get("status") != "shared_converter_loading_spice_passes_simple_mux_load":
        return fail("current AIMC system state summary should record shared converter loading SPICE status")
    if current_shared_loading.get("cases") != 4:
        return fail("current AIMC system state summary should record four shared converter loading SPICE cases")
    if current_shared_loading.get("max_active_loads") != 32:
        return fail("current AIMC system state summary should record shared converter loading stress case")
    if current_shared_loading.get("all_cases_pass_half_lsb") is not True:
        return fail("current AIMC system state summary should record shared converter loading SPICE pass")
    current_supply_energy = current_state.get("converter_supply_energy_spice_state") if isinstance(current_state.get("converter_supply_energy_spice_state"), dict) else {}
    if current_supply_energy.get("status") != "converter_supply_energy_spice_complete_simple_load":
        return fail("current AIMC system state summary should record converter supply-energy SPICE status")
    if current_supply_energy.get("cases") != 3:
        return fail("current AIMC system state summary should record three converter supply-energy SPICE cases")
    if current_supply_energy.get("all_cases_have_positive_energy") is not True:
        return fail("current AIMC system state summary should record converter supply-energy positive-energy pass")
    if not isinstance(current_supply_energy.get("worst_total_energy_j"), (int, float)) or current_supply_energy["worst_total_energy_j"] <= 0:
        return fail("current AIMC system state summary should record positive converter supply-energy")
    current_post_layout = current_state.get("converter_post_layout_readiness_state") if isinstance(current_state.get("converter_post_layout_readiness_state"), dict) else {}
    if current_post_layout.get("status") != "local_converter_handoff_complete_post_layout_not_ready":
        return fail("current AIMC system state summary should record converter post-layout readiness status")
    if current_post_layout.get("local_handoff_complete") is not True:
        return fail("current AIMC system state summary should record local converter handoff complete")
    if current_post_layout.get("claim_ready_to_replace_break_even") is not False:
        return fail("current AIMC system state summary should record post-layout readiness as not claim-ready")
    if current_post_layout.get("missing_replacement_items", 0) < 8:
        return fail("current AIMC system state summary should record missing post-layout replacement items")
    current_post_contract = current_state.get("converter_post_layout_evidence_contract_state") if isinstance(current_state.get("converter_post_layout_evidence_contract_state"), dict) else {}
    if current_post_contract.get("status") != "post_layout_contract_defined_placeholder_not_claim_ready":
        return fail("current AIMC system state summary should record converter post-layout evidence contract status")
    if current_post_contract.get("schema_complete") is not True:
        return fail("current AIMC system state summary should record post-layout evidence contract schema completeness")
    if current_post_contract.get("claim_ready_to_replace_break_even") is not False:
        return fail("current AIMC system state summary should record post-layout evidence contract as not claim-ready")
    if current_post_contract.get("placeholder_refuses_replacement") is not True:
        return fail("current AIMC system state summary should record post-layout evidence contract placeholder refusal")
    current_post_validator = current_state.get("converter_post_layout_payload_validator_state") if isinstance(current_state.get("converter_post_layout_payload_validator_state"), dict) else {}
    if current_post_validator.get("status") != "post_layout_payload_validator_ready_waiting_for_extracted_payload":
        return fail("current AIMC system state summary should record post-layout payload validator status")
    if current_post_validator.get("rejected_placeholder") is not True:
        return fail("current AIMC system state summary should record post-layout payload validator placeholder rejection")
    if current_post_validator.get("requires_break_even_rerun_with_extracted_values") is not True:
        return fail("current AIMC system state summary should record post-layout payload validator break-even rerun requirement")
    current_post_rerun = current_state.get("converter_post_layout_break_even_rerun_path_state") if isinstance(current_state.get("converter_post_layout_break_even_rerun_path_state"), dict) else {}
    if current_post_rerun.get("status") != "rerun_path_ready_waiting_for_validator_passing_payload":
        return fail("current AIMC system state summary should record post-layout break-even rerun path status")
    if current_post_rerun.get("rerun_script") != "scripts/rerun_converter_break_even_from_post_layout_payload.py":
        return fail("current AIMC system state summary should record post-layout break-even rerun script")
    current_post_strict = current_state.get("converter_post_layout_strict_intake_state") if isinstance(current_state.get("converter_post_layout_strict_intake_state"), dict) else {}
    if current_post_strict.get("status") != "strict_file_intake_ready_waiting_for_real_artifacts":
        return fail("current AIMC system state summary should record post-layout strict intake status")
    if current_post_strict.get("shape_validation_passed") is not True:
        return fail("current AIMC system state summary should record shape-only validation pass")
    if current_post_strict.get("strict_validation_rejected_missing_files") is not True:
        return fail("current AIMC system state summary should record strict validation missing-file rejection")
    current_post_positive = current_state.get("converter_post_layout_positive_path_state") if isinstance(current_state.get("converter_post_layout_positive_path_state"), dict) else {}
    if current_post_positive.get("status") != "strict_positive_path_proven_with_temporary_synthetic_files":
        return fail("current AIMC system state summary should record post-layout positive path status")
    if current_post_positive.get("temporary_fixture_persisted") is not False:
        return fail("current AIMC system state summary should record positive fixture as non-persisted")
    if current_post_positive.get("strict_validation_passed") is not True or current_post_positive.get("strict_rerun_passed") is not True:
        return fail("current AIMC system state summary should record positive path pass")
    current_post_submission = current_state.get("converter_post_layout_submission_path_state") if isinstance(current_state.get("converter_post_layout_submission_path_state"), dict) else {}
    if current_post_submission.get("status") != "submission_path_ready_waiting_for_real_payload":
        return fail("current AIMC system state summary should record post-layout submission path status")
    if current_post_submission.get("placeholder_rejected") is not True or current_post_submission.get("missing_file_payload_rejected") is not True:
        return fail("current AIMC system state summary should record submission path rejections")
    if current_post_submission.get("temporary_positive_payload_accepted") is not True:
        return fail("current AIMC system state summary should record submission path positive acceptance")
    current_real_package = current_state.get("converter_post_layout_real_payload_package_state") if isinstance(current_state.get("converter_post_layout_real_payload_package_state"), dict) else {}
    if current_real_package.get("status") != "real_payload_package_contract_ready":
        return fail("current AIMC system state summary should record real payload package status")
    if current_real_package.get("required_files") != 4:
        return fail("current AIMC system state summary should record four real payload package files")
    current_preflight = current_state.get("converter_post_layout_payload_preflight_state") if isinstance(current_state.get("converter_post_layout_payload_preflight_state"), dict) else {}
    if current_preflight.get("status") != "preflight_ready":
        return fail("current AIMC system state summary should record payload preflight status")
    if current_preflight.get("missing_file_payload_reported_not_ready") is not True or current_preflight.get("temporary_complete_payload_reported_ready") is not True:
        return fail("current AIMC system state summary should record payload preflight readiness checks")
    current_candidate = current_state.get("converter_post_layout_candidate_workspace_state") if isinstance(current_state.get("converter_post_layout_candidate_workspace_state"), dict) else {}
    if current_candidate.get("status") != "candidate_workspace_ready_not_evidence":
        return fail("current AIMC system state summary should record candidate workspace status")
    if current_candidate.get("preflight_rejects_default_payload") is not True or current_candidate.get("submission_rejects_default_payload") is not True:
        return fail("current AIMC system state summary should record candidate workspace rejection checks")
    current_candidate_audit = current_state.get("converter_post_layout_candidate_workspace_audit_state") if isinstance(current_state.get("converter_post_layout_candidate_workspace_audit_state"), dict) else {}
    if current_candidate_audit.get("status") != "candidate_workspace_still_scaffold":
        return fail("current AIMC system state summary should record candidate workspace audit scaffold status")
    if current_candidate_audit.get("placeholder_count", 0) < 10 or current_candidate_audit.get("missing_or_unresolved_file_count", 0) < 3:
        return fail("current AIMC system state summary should record candidate workspace audit gaps")
    current_recipe_state = current_state.get("converter_post_layout_real_run_recipe_state") if isinstance(current_state.get("converter_post_layout_real_run_recipe_state"), dict) else {}
    if current_recipe_state.get("status") != "real_run_recipe_ready_not_evidence":
        return fail("current AIMC system state summary should record real-run recipe status")
    if current_recipe_state.get("step_count") != 9:
        return fail("current AIMC system state summary should record real-run recipe step count")
    if "accepted-post-layout" not in str(current_recipe_state.get("manual_write_forbidden", "")):
        return fail("current AIMC system state summary should record manual accepted evidence boundary")
    current_identity_initializer = current_state.get("converter_post_layout_candidate_identity_initializer_state") if isinstance(current_state.get("converter_post_layout_candidate_identity_initializer_state"), dict) else {}
    if current_identity_initializer.get("status") != "identity_initializer_ready":
        return fail("current AIMC system state summary should record candidate identity initializer status")
    if current_identity_initializer.get("applied_to_source_payload") is not False:
        return fail("current AIMC system state summary should record candidate identity initializer as source-safe")
    if current_identity_initializer.get("identity_validation_passed") is not True:
        return fail("current AIMC system state summary should record candidate identity initializer identity validation")
    if current_identity_initializer.get("strict_same_run_validation_passed") is not False:
        return fail("current AIMC system state summary should record strict same-run still blocked")
    if current_identity_initializer.get("initialized_field_count") != 14:
        return fail("current AIMC system state summary should record 14 initialized identity fields")
    current_real_candidate_builder = current_state.get("converter_post_layout_real_candidate_builder_state") if isinstance(current_state.get("converter_post_layout_real_candidate_builder_state"), dict) else {}
    if current_real_candidate_builder.get("status") != "candidate_payload_built":
        return fail("current AIMC system state summary should record real candidate builder status")
    if current_real_candidate_builder.get("self_test") is not True:
        return fail("current AIMC system state summary should record real candidate builder self-test")
    if current_real_candidate_builder.get("strict_validation_passed") is not True or current_real_candidate_builder.get("strict_issue_count") != 0:
        return fail("current AIMC system state summary should record real candidate builder strict pass")
    if current_real_candidate_builder.get("temporary_fixture_persisted") is not False:
        return fail("current AIMC system state summary should record real candidate builder temporary fixture boundary")
    if current_real_candidate_builder.get("preview_status_before_removal") != "ready_to_submit_without_writing":
        return fail("current AIMC system state summary should record real candidate builder preview-ready status")
    if current_real_candidate_builder.get("preview_would_write_accepted_evidence_before_removal") is not True:
        return fail("current AIMC system state summary should record real candidate builder preview would-write state")
    if current_real_candidate_builder.get("preview_strict_issue_count_before_removal") != 0:
        return fail("current AIMC system state summary should record real candidate builder preview issue count")
    current_submission_preview = current_state.get("converter_post_layout_submission_preview_state") if isinstance(current_state.get("converter_post_layout_submission_preview_state"), dict) else {}
    if current_submission_preview.get("status") != "blocked_before_submission":
        return fail("current AIMC system state summary should record submission preview blocked status")
    if current_submission_preview.get("would_write_accepted_evidence") is not False:
        return fail("current AIMC system state summary should record submission preview as non-writing")
    if current_submission_preview.get("strict_issue_count") != 22:
        return fail("current AIMC system state summary should record submission preview issue count")
    current_leakage = current_state.get("converter_post_layout_evidence_leakage_audit_state") if isinstance(current_state.get("converter_post_layout_evidence_leakage_audit_state"), dict) else {}
    if current_leakage.get("status") != "no_evidence_leakage_detected":
        return fail("current AIMC system state summary should record evidence leakage audit pass")
    if current_leakage.get("accepted_post_layout_exists") is not False:
        return fail("current AIMC system state summary should record no accepted-post-layout directory")
    if current_leakage.get("candidate_non_scaffold_file_count") != 0:
        return fail("current AIMC system state summary should record no non-scaffold candidate files")
    if current_leakage.get("candidate_temp_marker_hit_count") != 0:
        return fail("current AIMC system state summary should record no temp marker leakage")
    if current_leakage.get("builder_preview_ready_before_removal") is not True:
        return fail("current AIMC system state summary should record builder preview-ready before removal")
    current_temp_submission = current_state.get("converter_post_layout_temporary_submission_proof_state") if isinstance(current_state.get("converter_post_layout_temporary_submission_proof_state"), dict) else {}
    if current_temp_submission.get("status") != "temporary_submission_path_proven":
        return fail("current AIMC system state summary should record temporary submission proof status")
    if current_temp_submission.get("temporary_submit_passed") is not True:
        return fail("current AIMC system state summary should record temporary submission pass")
    if current_temp_submission.get("temporary_accepted_file_count") != 2:
        return fail("current AIMC system state summary should record two temporary accepted files")
    if current_temp_submission.get("temporary_fixture_persisted") is not False:
        return fail("current AIMC system state summary should record temporary submission fixture cleanup")
    if current_temp_submission.get("canonical_accepted_evidence_exists_after_proof") is not False:
        return fail("current AIMC system state summary should record canonical accepted evidence absence after temp submit")
    current_discovery = current_state.get("converter_post_layout_real_artifact_discovery_state") if isinstance(current_state.get("converter_post_layout_real_artifact_discovery_state"), dict) else {}
    if current_discovery.get("status") != "no_complete_real_artifact_package_found":
        return fail("current AIMC system state summary should record real artifact discovery blocked status")
    if current_discovery.get("accepted_post_layout_exists") is not False:
        return fail("current AIMC system state summary should record no accepted evidence in real artifact discovery")
    if current_discovery.get("candidate_non_scaffold_file_count") != 2:
        return fail("current AIMC system state summary should record the two current partial candidate files in real artifact discovery")
    if current_discovery.get("current_candidate_would_write_accepted_evidence") is not False:
        return fail("current AIMC system state summary should record current candidate cannot write accepted evidence")
    if current_discovery.get("current_candidate_strict_issue_count") != 22:
        return fail("current AIMC system state summary should record discovery strict issue count")
    current_recipe_coverage = current_state.get("converter_post_layout_real_run_recipe_coverage_state") if isinstance(current_state.get("converter_post_layout_real_run_recipe_coverage_state"), dict) else {}
    if current_recipe_coverage.get("status") != "real_run_recipe_covers_current_checklist":
        return fail("current AIMC system state summary should record real-run recipe coverage status")
    if current_recipe_coverage.get("covered_checklist_field_count") != 32 or current_recipe_coverage.get("checklist_field_count") != 32:
        return fail("current AIMC system state summary should record complete checklist coverage")
    if current_recipe_coverage.get("payload_blocker_field_count") != 32 or current_recipe_coverage.get("uncovered_payload_blocker_field_count") != 0:
        return fail("current AIMC system state summary should record complete payload blocker coverage")
    current_state_md = (ROOT / "evidence" / "aimc-hardware-lab" / "current-aimc-system-state.md").read_text(encoding="utf-8")
    for marker in ["Current AIMC System State Summary", "supported lab claims", "ONNX Fixture State", "accepted source", "source policy", "Layout-Risk State", "AIHWKIT Diagnostic State", "AIHWKIT Ideal Mapping State", "AIHWKIT Forward Sweep State", "AIHWKIT Physical Review State", "AIHWKIT Current Tile Replay State", "AIHWKIT Converter Target State", "AIHWKIT Converter Cost State", "AIHWKIT Target Noise State", "AIHWKIT Converter Break-Even State", "Converter Circuit Contract State", "Local Converter Estimate State", "Converter Circuit-Simulation Estimate State", "Converter SPICE Handoff Spec State", "Row-DAC Settling SPICE State", "SAR Readout SPICE State", "Shared Converter Loading SPICE State", "Converter Supply Energy SPICE State", "Converter Post-Layout Readiness State", "Converter Post-Layout Evidence Contract State", "Converter Post-Layout Payload Template State", "Converter Post-Layout Payload Validator State", "Converter Post-Layout Break-Even Rerun Path State", "Converter Post-Layout Strict Intake State", "Converter Post-Layout Positive Path State", "Converter Post-Layout Submission Path State", "Converter Post-Layout Real Payload Package State", "Converter Post-Layout Payload Preflight State", "Converter Post-Layout Candidate Workspace State", "Converter Post-Layout Candidate Workspace Audit State", "Converter Post-Layout Candidate Fill Checklist State", "Converter Post-Layout Candidate Progress State", "Converter Post-Layout Candidate Gate Chain State", "Converter Post-Layout Candidate Readiness Run State", "Converter Post-Layout Real Run Recipe State", "Converter Post-Layout Candidate Identity Initializer State", "Converter Post-Layout Real Candidate Builder State", "Converter Post-Layout Submission Preview State", "Converter Post-Layout Evidence Leakage Audit State", "Converter Post-Layout Temporary Submission Proof State", "Converter Post-Layout Real Run Recipe Coverage State", "Next Handoff"]:
        if marker not in current_state_md:
            return fail(f"current AIMC system state markdown missing marker {marker!r}")
    current_state_page = (ROOT / "site" / "research" / "current-aimc-system-state.html").read_text(encoding="utf-8")
    for marker in ["Current AIMC System State", "current-aimc-system-state.json", "AIHWKIT and CrossSim are installed", "latency and energy need review", "production remains blocked", "Current AIMC System State Summary", "supported lab claims: <code>3</code>", "AIHWKIT: <code>available</code>", "CrossSim: <code>available</code>", "ONNX Fixture State", "selected fixture: <code>deep-transformer-mlp-stack.onnx</code>", "analog allowed rows: <code>dense1.matmul, dense2.matmul</code>", "Layout-Risk State", "review rows: <code>2</code>", "blocked rows: <code>0</code>", "AIHWKIT Diagnostic State", "threshold-fail payloads", "AIHWKIT Ideal Mapping State", "passing rows: <code>16</code>", "AIHWKIT Forward Sweep State", "passing settings", "AIHWKIT Physical Review State", "review status: <code>needs_physical_justification</code>", "AIHWKIT Current Tile Replay State", "failing rows: <code>16</code>", "AIHWKIT Converter Target State", "target input bits: <code>10</code>", "target output bits: <code>12</code>", "AIHWKIT Converter Cost State", "fallback_preferred_until_cost_is_justified", "AIHWKIT Target Noise State", "highest all-pass output noise: <code>0.004</code>", "AIHWKIT Converter Break-Even State", "digital_fallback_until_real_converter_and_array_savings_are_measured", "Converter Circuit Contract State", "contract_defined_placeholder_not_claim_ready", "Local Converter Estimate State", "local_estimate_complete_not_claim_ready", "Converter Circuit-Simulation Estimate State", "circuit_simulation_complete_not_replacement_ready", "Converter SPICE Handoff Spec State", "testbenches: <code>4</code>", "Row-DAC Settling SPICE State", "all cases pass half-LSB settling: <code>True</code>", "SAR Readout SPICE State", "all cases pass half-LSB readout: <code>True</code>", "Shared Converter Loading SPICE State", "all cases pass half-LSB shared loading: <code>True</code>", "Converter Supply Energy SPICE State", "all cases have positive integrated energy: <code>True</code>", "Converter Post-Layout Readiness State", "local handoff complete: <code>True</code>", "Converter Post-Layout Evidence Contract State", "placeholder refuses replacement: <code>True</code>", "Converter Post-Layout Payload Template State", "template_defined_not_evidence", "Converter Post-Layout Payload Validator State", "rejected placeholder: <code>True</code>", "Converter Post-Layout Break-Even Rerun Path State", "rerun_path_ready_waiting_for_validator_passing_payload", "Converter Post-Layout Strict Intake State", "strict validation rejected missing files: <code>True</code>", "Converter Post-Layout Positive Path State", "temporary fixture persisted: <code>False</code>", "Converter Post-Layout Submission Path State", "temporary positive payload accepted: <code>True</code>", "Converter Post-Layout Real Payload Package State", "required files: <code>4</code>", "Converter Post-Layout Payload Preflight State", "preflight_ready", "Converter Post-Layout Candidate Workspace State", "candidate_workspace_ready_not_evidence", "Converter Post-Layout Candidate Workspace Audit State", "placeholder count: <code>29</code>", "missing or unresolved file count: <code>3</code>", "Converter Post-Layout Candidate Fill Checklist State", "item count: <code>32</code>", "groups: <code>area, break_even, energy, extraction, files, identity, latency, noise, provenance, simulation</code>", "Converter Post-Layout Candidate Progress State", "open checklist items: <code>32</code>", "ready for preflight: <code>False</code>", "Converter Post-Layout Candidate Gate Chain State", "status: <code>candidate_gate_chain_passed</code>", "progress gate: <code>progress_gate_passed</code>", "preflight gate: <code>preflight_gate_passed</code>", "submission gate: <code>submission_gate_passed</code>", "canonical accepted evidence persisted: <code>False</code>", "Converter Post-Layout Candidate Readiness Run State", "status: <code>candidate_not_ready_for_strict_submission</code>", "ready for strict submission: <code>False</code>", "preflight issue count: <code>22</code>", "Converter Post-Layout Real Run Recipe State", "step count: <code>9</code>", "manual write forbidden: <code>accepted-post-layout must be written only by scripts/submit_converter_post_layout_payload.py</code>", "Converter Post-Layout Candidate Identity Initializer State", "identity validation passed: <code>True</code>", "strict same-run validation passed: <code>False</code>", "initialized fields: <code>14</code>", "Converter Post-Layout Real Candidate Builder State", "self-test: <code>True</code>", "strict validation passed: <code>True</code>", "temporary fixture persisted: <code>False</code>", "preview status before removal: <code>ready_to_submit_without_writing</code>", "preview would write accepted evidence before removal: <code>True</code>", "Converter Post-Layout Submission Preview State", "would write accepted evidence: <code>False</code>", "strict issue count: <code>22</code>", "Converter Post-Layout Evidence Leakage Audit State", "accepted post-layout exists: <code>False</code>", "candidate non-scaffold files: <code>0</code>", "candidate temp marker hits: <code>0</code>", "builder preview ready before removal: <code>True</code>", "Converter Post-Layout Real Artifact Discovery State", "candidate non-scaffold files: <code>2</code>", "current candidate strict issues: <code>22</code>", "Converter Post-Layout Temporary Submission Proof State", "temporary submit passed: <code>True</code>", "temporary accepted files: <code>2</code>", "canonical accepted evidence exists after proof: <code>False</code>", "Converter Post-Layout Real Run Recipe Coverage State", "covered checklist fields: <code>32</code>", "payload blocker fields: <code>32</code>", "uncovered payload blocker fields: <code>0</code>", "run_converter_post_layout_candidate_readiness.py"]:
        if marker not in current_state_page:
            return fail(f"site/research/current-aimc-system-state.html missing marker {marker!r}")

    next_queue = json.loads((ROOT / "evidence" / "aimc-hardware-lab" / "next-evidence-work-queue.json").read_text(encoding="utf-8"))
    if next_queue.get("result_type") != "next_aimc_evidence_work_queue":
        return fail("next AIMC evidence work queue has wrong result_type")
    if next_queue.get("source_artifact") != "evidence/aimc-hardware-lab/current-aimc-system-state.json":
        return fail("next AIMC evidence work queue should be derived from current system state")
    work_items = next_queue.get("work_items") if isinstance(next_queue.get("work_items"), list) else []
    expected_queue_ids = ["E1", "E2", "E3", "E4", "E5"]
    if [item.get("id") for item in work_items if isinstance(item, dict)] != expected_queue_ids:
        return fail("next AIMC evidence work queue should contain E1 through E5 in order")
    for item in work_items:
        if not isinstance(item, dict):
            return fail("next AIMC evidence work queue contains a non-object item")
        for key in ["claim_target", "why_next", "object", "method", "acceptance_evidence", "blocked_until", "refused_claim"]:
            if key not in item:
                return fail(f"next AIMC evidence work queue item {item.get('id')} missing {key}")
        if not isinstance(item.get("acceptance_evidence"), list) or len(item["acceptance_evidence"]) < 3:
            return fail(f"next AIMC evidence work queue item {item.get('id')} has weak acceptance evidence")
    e3 = next((item for item in work_items if isinstance(item, dict) and item.get("id") == "E3"), {})
    e1 = next((item for item in work_items if isinstance(item, dict) and item.get("id") == "E1"), {})
    e2 = next((item for item in work_items if isinstance(item, dict) and item.get("id") == "E2"), {})
    if e1.get("status") != "local_fixture_selected":
        return fail("next AIMC evidence work queue should mark E1 as local_fixture_selected")
    if "not blocked locally" not in str(e1.get("blocked_until")):
        return fail("next AIMC evidence work queue should not mark E1 as locally blocked")
    if e2.get("status") != "post_layout_candidate_gate_chain_passed_waiting_for_real_values":
        return fail("next AIMC evidence work queue should mark E2 as post_layout_candidate_gate_chain_passed_waiting_for_real_values")
    if "candidate transition chain" not in str(e2.get("why_next")) or "one-command readiness runner" not in str(e2.get("why_next")) or "run_converter_post_layout_candidate_readiness.py" not in str(e2.get("why_next")) or "32 exact edit items" not in str(e2.get("why_next")) or "placeholder fields" not in str(e2.get("why_next")) or "missing or unresolved files" not in str(e2.get("why_next")) or "candidate identity initializer is identity_initializer_ready" not in str(e2.get("why_next")) or "stamp one shared run id" not in str(e2.get("why_next")) or "leaves strict validation blocked" not in str(e2.get("why_next")) or "real-candidate builder command" not in str(e2.get("why_next")) or "direct path from existing extracted files" not in str(e2.get("why_next")) or "submission preview is blocked_before_submission" not in str(e2.get("why_next")) or "would_write_accepted_evidence=False" not in str(e2.get("why_next")) or "accepted evidence is still protected" not in str(e2.get("why_next")) or "generated real-run recipe has 9 ordered steps" not in str(e2.get("why_next")) or "32/32 checklist fields covered" not in str(e2.get("why_next")) or "0 uncovered payload blocker fields" not in str(e2.get("why_next")):
        return fail("next AIMC evidence work queue should record candidate gate chain state")
    if e3.get("status") != "supported":
        return fail("next AIMC evidence work queue should mark CrossSim layout-risk adapter as supported")
    if "not blocked locally" not in str(e3.get("blocked_until")):
        return fail("next AIMC evidence work queue should not mark layout-risk adapter as locally blocked")
    next_queue_page = (ROOT / "site" / "research" / "next-aimc-evidence-work-queue.html").read_text(encoding="utf-8")
    for marker in ["Next AIMC Evidence Work Queue", "Larger real-model ONNX simulator slice", "AIHWKIT positive residual mapping", "status: post_layout_candidate_gate_chain_passed_waiting_for_real_values", "candidate transition chain", "one-command readiness runner", "run_converter_post_layout_candidate_readiness.py", "canonical accepted evidence", "candidate workspace", "fill checklist", "32 exact edit items", "placeholder fields", "missing or unresolved files", "candidate identity initializer is identity_initializer_ready", "stamp one shared run id", "leaves strict validation blocked", "real-candidate builder command", "direct path from existing extracted files", "submission preview is blocked_before_submission", "would_write_accepted_evidence=False", "accepted evidence is still protected", "generated real-run recipe has 9 ordered steps", "32/32 checklist fields covered", "0 uncovered payload blocker fields", "post-layout simulation", "measured silicon", "CrossSim layout-risk adapter", "status: supported", "not blocked locally", "Measured board runtime trace", "Synchronized measured power trace", "Refused claim"]:
        if marker not in next_queue_page:
            return fail(f"site/research/next-aimc-evidence-work-queue.html missing marker {marker!r}")

    site_synthesis = (ROOT / "site" / "synthesis.html").read_text(encoding="utf-8")
    for marker in ["From Charge To Manufactured Logic", "false preservation", "verified manufactured chip"]:
        if marker not in site_synthesis:
            return fail(f"site/synthesis.html missing marker {marker!r}")

    site_paper_synthesis = (ROOT / "site" / "paper-synthesis.html").read_text(encoding="utf-8")
    for marker in ["What The 20 Chip And EDA Papers Are Really About", "preservation under translation", "Open Flows Make The Translation Visible", "Signoff Turns Hidden Physics Into Explicit Risk"]:
        if marker not in site_paper_synthesis:
            return fail(f"site/paper-synthesis.html missing marker {marker!r}")

    site_aimc_synthesis = (ROOT / "site" / "analog-in-memory-foundation-model-synthesis.html").read_text(encoding="utf-8")
    for marker in ["Analog In-Memory Compute For Foundation Models", "Why Foundation Models Are A Hard Target", "The Architecture Argument", "The Cost Boundary"]:
        if marker not in site_aimc_synthesis:
            return fail(f"site/analog-in-memory-foundation-model-synthesis.html missing marker {marker!r}")

    site_coverage = (ROOT / "site" / "coverage-audit.html").read_text(encoding="utf-8")
    for marker in ["Coverage Audit And Next Expansion", "Current Proven Coverage", "Track Balance", "Next 25-Paper Target"]:
        if marker not in site_coverage:
            return fail(f"site/coverage-audit.html missing marker {marker!r}")

    schema = json.loads((ROOT / "sources" / "papers" / "paper-entry-schema.json").read_text(encoding="utf-8"))
    papers = json.loads((ROOT / "sources" / "papers" / "seed-paper-index.json").read_text(encoding="utf-8"))
    required_paper_fields = schema["required_fields"]
    allowed_tracks = set(schema["tracks"])
    concept_slugs = {path.stem for path in concept_dir.glob("*.md")}
    if len(papers) < 5:
        return fail("expected at least 5 seed paper entries")
    for paper in papers:
        for field in required_paper_fields:
            if field not in paper:
                return fail(f"paper entry {paper.get('slug', '<missing>')} missing field {field!r}")
            value = paper[field]
            if isinstance(value, str) and len(value) < 8:
                return fail(f"paper entry {paper.get('slug', '<missing>')} field {field!r} too short")
            if isinstance(value, list) and not value:
                return fail(f"paper entry {paper.get('slug', '<missing>')} field {field!r} must not be empty")
        if paper["track"] not in allowed_tracks:
            return fail(f"paper entry {paper['slug']} has unknown track {paper['track']!r}")
        if paper["source"] == "seed-needed":
            return fail(f"paper entry {paper['slug']} still needs a verified source")
        for concept in paper["related_concepts"]:
            if concept not in concept_slugs:
                return fail(f"paper entry {paper['slug']} references missing concept {concept!r}")

    site_papers = (ROOT / "site" / "papers.html").read_text(encoding="utf-8")
    for marker in ["Paper Index", "Seed Paper Index", "Object:", "Constraint:", "Concrete method:", "Failure boundary:"]:
        if marker not in site_papers:
            return fail(f"site/papers.html missing marker {marker!r}")
    if site_papers.count("<article class=\"card\">") < len(papers):
        return fail("site/papers.html does not render all seed papers")
    paper_note_slugs = {path.stem for path in (ROOT / "docs" / "papers").glob("*.md") if path.name != "paper-note-template.md"}
    paper_slugs = {paper["slug"] for paper in papers}
    if paper_note_slugs != paper_slugs:
        return fail("full paper note slugs do not match seed paper slugs")
    paper_note_count = len(paper_note_slugs)
    paper_note_page_count = len(list((ROOT / "site" / "papers").glob("*.html")))
    if paper_note_count != len(papers):
        return fail("expected one full paper note per seed paper")
    if paper_note_page_count != paper_note_count:
        return fail("site paper note count does not match paper notes")
    if site_papers.count("Read full paper note") < paper_note_count:
        return fail("site/papers.html does not link every full paper note")

    print("PASS")
    print(f"concept_articles {concept_count}")
    print(f"concept_pages {concept_page_count}")
    print(f"analog_labs {analog_lab_count}")
    print(f"digital_labs {digital_lab_count}")
    print(f"eda_labs {eda_lab_count}")
    print(f"total_labs {total_lab_count}")
    print(f"lab_pages {lab_page_count}")
    print(f"research_pages {research_page_count}")
    print(f"paper_entries {len(papers)}")
    print(f"paper_notes {paper_note_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
