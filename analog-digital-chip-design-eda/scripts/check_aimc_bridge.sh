#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SIM_PYTHON="${AIMC_SIM_PYTHON:-$HOME/eda-tools/aimc-simulators-venv/bin/python}"
if [ ! -x "$SIM_PYTHON" ]; then
  SIM_PYTHON="python3"
fi

import_aihwkit_tensor_shape_payload() {
  local payload="evidence/aimc-simulator-adapters/aihwkit-tensor-shape-analog-error-simulation.json"
  local pass_flag
  pass_flag="$(python3 -c 'import json,sys; payload=json.load(open(sys.argv[1], encoding="utf-8")); print("true" if payload.get("accuracy_impact", {}).get("pass") is True else "false")' "$payload")"
  if [ "$pass_flag" = "true" ]; then
    python3 scripts/import_analog_simulator_payload.py "$payload"
  else
    python3 scripts/import_analog_simulator_payload.py --expect-reject "$payload"
  fi
}

echo "AIMC bridge check"
echo "================="

echo
echo "[1/164] Backend hardware placement import"
(
  cd "$ROOT"
  python3 scripts/import_backend_hardware_placement.py
)

echo
echo "[2/164] SPICE crossbar comparison"
(
  cd "$ROOT/labs/analog/analog-in-memory-foundation-model-hardware"
  python3 python/spice_crossbar_comparison.py
)

echo
echo "[3/164] SPICE signed-weight comparison"
(
  cd "$ROOT/labs/analog/analog-in-memory-foundation-model-hardware"
  python3 python/spice_signed_crossbar_comparison.py
)

echo
echo "[4/164] SPICE row-wire-drop comparison"
(
  cd "$ROOT/labs/analog/analog-in-memory-foundation-model-hardware"
  python3 python/spice_row_drop_comparison.py
)

echo
echo "[5/164] Analog tile error evidence"
(
  cd "$ROOT/labs/analog/analog-in-memory-foundation-model-hardware"
  python3 python/analog_tile_error_evidence.py
)

echo
echo "[6/164] Analog tile state trace"
(
  cd "$ROOT/labs/analog/analog-in-memory-foundation-model-hardware"
  python3 python/analog_tile_state_trace.py
)

echo
echo "[7/164] Converter boundary sweep"
(
  cd "$ROOT/labs/analog/analog-in-memory-foundation-model-hardware"
  python3 python/converter_boundary_sweep.py
)

echo
echo "[8/164] Tile operating point"
(
  cd "$ROOT/labs/analog/analog-in-memory-foundation-model-hardware"
  python3 python/tile_operating_point.py
)

echo
echo "[9/164] Analog nonideality stack"
(
  cd "$ROOT/labs/analog/analog-in-memory-foundation-model-hardware"
  python3 python/analog_nonideality_stack.py
)

echo
echo "[10/164] Measured tile transformer impact"
(
  cd "$ROOT/labs/analog/analog-in-memory-foundation-model-hardware"
  python3 python/measured_tile_transformer_impact.py
)

echo
echo "[11/164] Model impact governor requests"
(
  cd "$ROOT/labs/analog/analog-in-memory-foundation-model-hardware"
  python3 python/model_impact_governor_requests.py
)

echo
echo "[12/164] Generated model-impact governor-to-RTL trace"
(
  cd "$ROOT/labs/digital/aimc-control-plane-rtl"
  python3 check_generated_model_impact_governor_trace.py
)

echo
echo "[13/164] Generated analog-to-RTL trace"
(
  cd "$ROOT/labs/digital/aimc-control-plane-rtl"
  python3 check_generated_micro_tile_trace.py
)

echo
echo "[14/164] Generated scheduler runtime-to-RTL trace"
(
  cd "$ROOT/labs/digital/aimc-control-plane-rtl"
  python3 check_generated_scheduler_trace.py
)

echo
echo "[15/164] Generated error-budget governor trace"
(
  cd "$ROOT/labs/digital/aimc-control-plane-rtl"
  python3 check_generated_error_budget_governor_trace.py
)

echo
echo "[16/164] Generated integrated scheduler/governor trace"
(
  cd "$ROOT/labs/digital/aimc-control-plane-rtl"
  python3 check_generated_integrated_scheduler_governor_trace.py
)

echo
echo "[17/164] Generated pipelined scheduler/governor trace"
(
  cd "$ROOT/labs/digital/aimc-control-plane-rtl"
  python3 check_generated_pipelined_scheduler_governor_trace.py
)

echo
echo "[18/164] Yosys micro-tile controller synthesis"
(
  cd "$ROOT/labs/digital/aimc-control-plane-synthesis"
  yosys synth_aimc_micro_tile_controller.ys >/tmp/aimc_micro_tile_controller_yosys.log
  rg -n 'Number of cells:|\$_DFF_PN0_|End of script' reports/aimc_micro_tile_controller_synth.log
)

echo
echo "[19/164] Yosys tile-service scheduler synthesis"
(
  cd "$ROOT/labs/digital/aimc-control-plane-synthesis"
  yosys synth_aimc_tile_service_scheduler.ys >/tmp/aimc_tile_service_scheduler_yosys.log
  rg -n 'Number of cells:|End of script' reports/aimc_tile_service_scheduler_synth.log
)

echo
echo "[20/164] Yosys error-budget governor synthesis"
(
  cd "$ROOT/labs/digital/aimc-control-plane-synthesis"
  yosys synth_aimc_error_budget_governor.ys >/tmp/aimc_error_budget_governor_yosys.log
  rg -n 'Number of cells:|End of script' reports/aimc_error_budget_governor_synth.log
)

echo "[21/164] Yosys integrated scheduler/governor synthesis"
(
  cd "$ROOT/labs/digital/aimc-control-plane-synthesis"
  yosys synth_aimc_scheduler_governor.ys >/tmp/aimc_scheduler_governor_yosys.log
  rg -n 'Number of cells:|End of script' reports/aimc_scheduler_governor_synth.log
)

echo
echo
echo "[22/164] Yosys pipelined scheduler/governor synthesis"
(
  cd "$ROOT/labs/digital/aimc-control-plane-synthesis"
  yosys synth_aimc_scheduler_governor_pipelined.ys >/tmp/aimc_scheduler_governor_pipelined_yosys.log
  rg -n 'Number of cells:|\$_DFF_PN0_|End of script' reports/aimc_scheduler_governor_pipelined_synth.log
)

echo
echo "[23/164] Micro-tile controller OpenLane package readiness"
(
  cd "$ROOT"
  AIMC_OPENLANE_PREP=aimc-micro-tile-controller-openlane-prep \
  AIMC_OPENLANE_DESIGN=aimc_micro_tile_controller \
  ./scripts/check_aimc_openlane_readiness.sh
)

echo
echo "[24/164] Tile-service scheduler OpenLane package readiness"
(
  cd "$ROOT"
  AIMC_OPENLANE_PREP=aimc-tile-service-scheduler-openlane-prep \
  AIMC_OPENLANE_DESIGN=aimc_tile_service_scheduler_physical \
  AIMC_OPENLANE_RTL=aimc_tile_service_scheduler.v \
  ./scripts/check_aimc_openlane_readiness.sh
)

echo
echo "[25/164] Error-budget governor OpenLane package readiness"
(
  cd "$ROOT"
  AIMC_OPENLANE_PREP=aimc-error-budget-governor-openlane-prep \
  AIMC_OPENLANE_DESIGN=aimc_error_budget_governor_physical \
  AIMC_OPENLANE_RTL=aimc_error_budget_governor.v \
  ./scripts/check_aimc_openlane_readiness.sh
)

echo
echo "[26/164] Integrated scheduler/governor OpenLane package readiness"
(
  cd "$ROOT"
  AIMC_OPENLANE_PREP=aimc-scheduler-governor-openlane-prep \
  AIMC_OPENLANE_DESIGN=aimc_scheduler_governor_physical \
  AIMC_OPENLANE_RTL=aimc_scheduler_governor.v \
  ./scripts/check_aimc_openlane_readiness.sh
)

echo
echo "[27/164] Pipelined scheduler/governor OpenLane package readiness"
(
  cd "$ROOT"
  AIMC_OPENLANE_PREP=aimc-scheduler-governor-pipelined-openlane-prep \
  AIMC_OPENLANE_DESIGN=aimc_scheduler_governor_pipelined \
  AIMC_OPENLANE_RTL=aimc_scheduler_governor_pipelined.v \
  ./scripts/check_aimc_openlane_readiness.sh
)

echo
echo "[28/164] Digital physical artifact boundary"
(
  cd "$ROOT"
  python3 scripts/audit_digital_physical_artifact_boundary.py
)

echo
echo "[29/164] AIHWKIT/CrossSim simulator adapter status"
(
  cd "$ROOT"
  "$SIM_PYTHON" scripts/check_aimc_simulator_adapters.py
)

echo
echo
echo "[30/164] Optional AIHWKIT/CrossSim simulator payload run path"
(
  cd "$ROOT"
  "$SIM_PYTHON" scripts/run_optional_aimc_simulator_payloads.py
)

echo
echo "[31/164] Workload-shaped AIHWKIT/CrossSim simulator payload run path"
(
  cd "$ROOT"
  "$SIM_PYTHON" scripts/run_workload_aimc_simulator_payloads.py
)

echo
echo "[32/164] Tensor-shaped AIHWKIT/CrossSim simulator payload run path"
(
  cd "$ROOT"
  "$SIM_PYTHON" scripts/run_tensor_shape_aimc_simulator_payloads.py
)

echo
echo "[33/164] Trained-weight AIHWKIT/CrossSim simulator payload run path"
(
  cd "$ROOT"
  "$SIM_PYTHON" scripts/run_trained_weight_aimc_simulator_payloads.py
)

echo
echo "[34/164] Projection-stack AIHWKIT/CrossSim simulator payload run path"
(
  cd "$ROOT"
  "$SIM_PYTHON" scripts/run_projection_stack_aimc_simulator_payloads.py
)

echo
echo "[35/164] Transformer MLP-block AIHWKIT/CrossSim simulator payload run path"
(
  cd "$ROOT"
  "$SIM_PYTHON" scripts/run_transformer_mlp_block_aimc_simulator_payloads.py
)

echo
echo "[36/164] Calibrated transformer MLP-block AIHWKIT/CrossSim simulator payload run path"
(
  cd "$ROOT"
  "$SIM_PYTHON" scripts/run_calibrated_transformer_mlp_block_aimc_simulator_payloads.py
)

echo
echo "[37/164] Calibrated deep transformer MLP-stack AIHWKIT/CrossSim simulator payload run path"
(
  cd "$ROOT"
  "$SIM_PYTHON" scripts/run_calibrated_deep_transformer_mlp_stack_aimc_simulator_payloads.py
)

echo
echo "[38/164] Attention-block AIHWKIT/CrossSim simulator payload run path"
(
  cd "$ROOT"
  "$SIM_PYTHON" scripts/run_attention_block_aimc_simulator_payloads.py
)

echo
echo "[39/164] Calibrated attention-block AIHWKIT/CrossSim simulator payload run path"
(
  cd "$ROOT"
  "$SIM_PYTHON" scripts/run_calibrated_attention_block_aimc_simulator_payloads.py
)

echo
echo "[40/164] AIHWKIT residual diagnostic"
(
  cd "$ROOT"
  python3 scripts/generate_aihwkit_residual_diagnostic.py
)

echo
echo "[41/164] AIHWKIT ideal-forward mapping proof"
(
  cd "$ROOT"
  "$SIM_PYTHON" scripts/generate_aihwkit_ideal_forward_mapping_proof.py
)

echo
echo "[42/164] AIHWKIT forward-setting sweep"
(
  cd "$ROOT"
  "$SIM_PYTHON" scripts/generate_aihwkit_forward_setting_sweep.py
)

echo
echo "[43/164] AIHWKIT physical-setting review"
(
  cd "$ROOT"
  python3 scripts/generate_aihwkit_physical_setting_review.py
)

echo
echo "[44/164] AIHWKIT current-tile boundary replay"
(
  cd "$ROOT"
  "$SIM_PYTHON" scripts/generate_aihwkit_current_tile_boundary_replay.py
)

echo
echo "[45/164] AIHWKIT converter upgrade target"
(
  cd "$ROOT"
  python3 scripts/generate_aihwkit_converter_upgrade_target.py
)

echo
echo "[46/164] AIHWKIT converter cost model"
(
  cd "$ROOT"
  python3 scripts/generate_aihwkit_converter_cost_model.py
)

echo
echo "[47/164] AIHWKIT target noise sensitivity"
(
  cd "$ROOT"
  "$SIM_PYTHON" scripts/generate_aihwkit_target_noise_sensitivity.py
)

echo
echo "[48/164] AIHWKIT converter break-even"
(
  cd "$ROOT"
  python3 scripts/generate_aihwkit_converter_break_even.py
)

echo
echo "[49/164] Converter circuit evidence contract"
(
  cd "$ROOT"
  python3 scripts/generate_converter_circuit_evidence_contract.py
)

echo
echo "[50/164] Local converter circuit estimate"
(
  cd "$ROOT"
  python3 scripts/generate_local_converter_circuit_estimate.py
)

echo
echo "[51/164] Converter circuit-simulation estimate"
(
  cd "$ROOT"
  python3 scripts/generate_converter_circuit_simulation_estimate.py
)

echo
echo "[52/164] Converter SPICE handoff spec"
(
  cd "$ROOT"
  python3 scripts/generate_converter_spice_handoff_spec.py
)

echo
echo "[53/164] Row-DAC settling SPICE evidence"
(
  cd "$ROOT/labs/analog/analog-in-memory-foundation-model-hardware"
  python3 python/row_dac_settling_spice.py
  cd "$ROOT"
  python3 scripts/generate_row_dac_settling_spice_evidence.py
)

echo
echo "[54/164] SAR readout SPICE evidence"
(
  cd "$ROOT/labs/analog/analog-in-memory-foundation-model-hardware"
  python3 python/sar_readout_12bit_spice.py
  cd "$ROOT"
  python3 scripts/generate_sar_readout_spice_evidence.py
)

echo
echo "[55/164] Shared converter loading SPICE evidence"
(
  cd "$ROOT/labs/analog/analog-in-memory-foundation-model-hardware"
  python3 python/shared_converter_loading_spice.py
  cd "$ROOT"
  python3 scripts/generate_shared_converter_loading_spice_evidence.py
)

echo
echo "[56/164] Converter supply-energy SPICE evidence"
(
  cd "$ROOT/labs/analog/analog-in-memory-foundation-model-hardware"
  python3 python/converter_supply_energy_spice.py
  cd "$ROOT"
  python3 scripts/generate_converter_supply_energy_spice_evidence.py
)

echo
echo "[57/164] Simulator to post-layout gap audit"
(
  cd "$ROOT"
  python3 scripts/audit_simulator_to_post_layout_gap.py
)

echo
echo "[58/164] Analog converter layout work order"
(
  cd "$ROOT"
  python3 scripts/generate_analog_converter_layout_work_order.py
)

echo
echo "[59/164] Analog converter layout starter package"
(
  cd "$ROOT"
  python3 scripts/generate_analog_converter_layout_starter_package.py
)

echo
echo "[60/164] Analog converter layout tool readiness"
(
  cd "$ROOT"
  python3 scripts/audit_analog_converter_layout_tool_readiness.py
)

echo
echo "[61/164] Analog converter PDK readiness"
(
  cd "$ROOT"
  python3 scripts/audit_analog_converter_pdk_readiness.py
)

echo
echo "[62/164] Magic Sky130 extraction smoke"
(
  cd "$ROOT"
  python3 scripts/run_magic_sky130_extraction_smoke.py
)

echo
echo "[63/164] Magic Sky130 compatibility audit"
(
  cd "$ROOT"
  python3 scripts/audit_magic_sky130_compatibility.py
)

echo
echo "[64/164] Row-DAC 10b layout smoke"
(
  cd "$ROOT"
  python3 scripts/run_row_dac_10b_layout_smoke.py
)

echo
echo "[65/164] Converter starter layout smoke"
(
  cd "$ROOT"
  python3 scripts/run_converter_starter_layout_smoke.py
)

echo
echo "[66/164] Converter starter post-layout candidate"
(
  cd "$ROOT"
  python3 scripts/build_converter_starter_post_layout_candidate.py
)

echo
echo "[67/164] Converter starter physical artifacts"
(
  cd "$ROOT"
  python3 scripts/audit_converter_starter_physical_artifacts.py
)

echo
echo "[68/164] Converter starter parasitic load estimate"
(
  cd "$ROOT"
  python3 scripts/measure_converter_starter_parasitic_load.py
)

echo
echo "[69/164] Converter starter parasitic break-even rerun"
(
  cd "$ROOT"
  python3 scripts/rerun_converter_break_even_with_starter_parasitics.py
)

echo
echo "[70/164] Converter starter extracted RC ngspice"
(
  cd "$ROOT"
  python3 scripts/run_converter_starter_extracted_rc_ngspice.py
)

echo
echo "[71/164] Sky130 transistor sample switch ngspice"
(
  cd "$ROOT"
  python3 scripts/run_sky130_transistor_sample_switch_ngspice.py
)

echo
echo "[72/164] Sky130 sample switch hold-mode ngspice"
(
  cd "$ROOT"
  python3 scripts/run_sky130_sample_switch_hold_mode_ngspice.py
)

echo
echo "[73/164] Sky130 sample switch hold mitigation sweep"
(
  cd "$ROOT"
  python3 scripts/run_sky130_sample_switch_hold_mitigation_sweep.py
)

echo
echo "[74/164] Sky130 sample switch dummy cancellation ngspice"
(
  cd "$ROOT"
  python3 scripts/run_sky130_sample_switch_dummy_cancellation_ngspice.py
)

echo
echo "[75/164] Sky130 bottom-plate sampling ngspice"
(
  cd "$ROOT"
  python3 scripts/run_sky130_bottom_plate_sampling_ngspice.py
)

echo
echo "[76/164] Sky130 sample-hold topology decision gate"
(
  cd "$ROOT"
  python3 scripts/generate_sky130_sample_hold_topology_decision_gate.py
)

echo
echo "[77/164] Sky130 buffered sample-hold ngspice"
(
  cd "$ROOT"
  python3 scripts/run_sky130_buffered_sample_hold_ngspice.py
)

echo
echo "[78/164] Sky130 bootstrapped switch ngspice"
(
  cd "$ROOT"
  python3 scripts/run_sky130_bootstrapped_switch_ngspice.py
)

echo
echo "[79/164] Sky130 fully differential sampling ngspice"
(
  cd "$ROOT"
  python3 scripts/run_sky130_fully_differential_sampling_ngspice.py
)

echo
echo "[80/164] Sky130 differential dummy cancellation ngspice"
(
  cd "$ROOT"
  python3 scripts/run_sky130_differential_dummy_cancellation_ngspice.py
)

echo
echo "[81/164] Sky130 differential dummy candidate input sweep"
(
  cd "$ROOT"
  python3 scripts/run_sky130_differential_dummy_candidate_input_sweep.py
)

echo
echo "[82/164] Sky130 differential dummy candidate mismatch sweep"
(
  cd "$ROOT"
  python3 scripts/run_sky130_differential_dummy_candidate_mismatch_sweep.py
)

echo
echo "[83/164] Sky130 differential dummy candidate decision margin"
(
  cd "$ROOT"
  python3 scripts/generate_sky130_differential_dummy_candidate_decision_margin.py
)

echo
echo "[84/164] Sky130 differential dummy candidate offset/noise stress"
(
  cd "$ROOT"
  python3 scripts/generate_sky130_differential_dummy_candidate_offset_noise_stress.py
)

echo
echo "[85/164] Differential sampling control proof ngspice"
(
  cd "$ROOT"
  python3 scripts/run_differential_sampling_control_proof_ngspice.py
)

echo
echo "[86/164] Sky130 single-device charge injection ngspice"
(
  cd "$ROOT"
  python3 scripts/run_sky130_single_device_charge_injection_ngspice.py
)

echo
echo "[87/164] Sky130 sample switch clock edge sweep"
(
  cd "$ROOT"
  python3 scripts/run_sky130_sample_switch_clock_edge_sweep.py
)

echo
echo "[88/164] Sky130 sample-hold design target"
(
  cd "$ROOT"
  python3 scripts/generate_sky130_sample_hold_design_target.py
)

echo
echo "[89/164] Sky130 differential matching requirement"
(
  cd "$ROOT"
  python3 scripts/generate_sky130_differential_matching_requirement.py
)

echo
echo "[90/164] Sky130 next transistor fixture work order"
(
  cd "$ROOT"
  python3 scripts/generate_sky130_next_transistor_fixture_work_order.py
)

echo
echo "[91/164] Sky130 comparator acceptance fixture spec"
(
  cd "$ROOT"
  python3 scripts/generate_sky130_comparator_acceptance_fixture_spec.py
)

echo
echo "[92/164] Sky130 comparator input-stage ngspice"
(
  cd "$ROOT"
  python3 scripts/run_sky130_comparator_input_stage_ngspice.py
)

echo
echo "[93/164] Sky130 clocked comparator latch ngspice"
(
  cd "$ROOT"
  python3 scripts/run_sky130_clocked_comparator_latch_ngspice.py
)

echo
echo "[94/164] Sky130 sample-hold latch kickback ngspice"
(
  cd "$ROOT"
  python3 scripts/run_sky130_sample_hold_latch_kickback_ngspice.py
)

echo
echo "[95/164] Sky130 latch input-size kickback sweep"
(
  cd "$ROOT"
  python3 scripts/run_sky130_latch_input_size_kickback_sweep.py
)

echo
echo "[96/164] Sky130 comparator isolation target"
(
  cd "$ROOT"
  python3 scripts/generate_sky130_comparator_isolation_target.py
)

echo
echo "[97/164] Sky130 capacitive latch input isolation sweep"
(
  cd "$ROOT"
  python3 scripts/run_sky130_capacitive_latch_input_isolation_sweep.py
)

echo
echo "[98/164] Sky130 capacitive isolation both-polarity confirm"
(
  cd "$ROOT"
  python3 scripts/run_sky130_capacitive_isolation_both_polarity_confirm.py
)

echo
echo "[99/164] Sky130 capacitive isolation post-layout handoff"
(
  cd "$ROOT"
  python3 scripts/generate_sky130_capacitive_isolation_post_layout_handoff.py
)

echo
echo "[100/164] Sky130 capacitive isolation physical cell gap"
(
  cd "$ROOT"
  python3 scripts/audit_sky130_capacitive_isolation_physical_cell_gap.py
)

echo
echo "[101/164] Sky130 capacitive isolation post-layout both-polarity rerun"
(
  cd "$ROOT"
  python3 scripts/run_sky130_capacitive_isolation_post_layout_both_polarity.py
)

echo
echo "[102/164] Sky130 capacitive isolation extracted port-mapping diagnostic"
(
  cd "$ROOT"
  python3 scripts/run_sky130_capacitive_isolation_extracted_port_mapping_diagnostic.py
)

echo
echo "[103/164] Sky130 capacitive isolation extracted coupling-strength sweep"
(
  cd "$ROOT"
  python3 scripts/run_sky130_capacitive_isolation_extracted_coupling_strength_sweep.py
)

echo
echo "[104/164] Sky130 extracted frontend redesign target"
(
  cd "$ROOT"
  python3 scripts/generate_sky130_extracted_frontend_redesign_target.py
)

echo
echo "[105/164] Sky130 balanced frontend work order"
(
  cd "$ROOT"
  python3 scripts/generate_sky130_balanced_frontend_work_order.py
)

echo
echo "[106/164] Sky130 balanced frontend starter extraction audit"
(
  cd "$ROOT"
  python3 scripts/audit_sky130_balanced_frontend_starter_extraction.py
)

echo
echo "[107/164] Sky130 balanced frontend sign preservation"
(
  cd "$ROOT"
  python3 scripts/run_sky130_balanced_frontend_sign_preservation.py
)

echo
echo "[108/164] Sky130 balanced frontend latch-decision margin"
(
  cd "$ROOT"
  python3 scripts/run_sky130_balanced_frontend_latch_decision.py
)

echo
echo "[109/164] Sky130 balanced frontend sense-gain target"
(
  cd "$ROOT"
  python3 scripts/generate_sky130_balanced_frontend_sense_gain_target.py
)

echo
echo "[110/164] Sky130 strong sense frontend candidate"
(
  cd "$ROOT"
  python3 scripts/run_sky130_strong_sense_frontend_candidate.py
)

echo
echo "[111/164] Sky130 ultra sense frontend candidate"
(
  cd "$ROOT"
  python3 scripts/run_sky130_ultra_sense_frontend_candidate.py
)

echo
echo "[112/164] Sky130 frontend sense efficiency audit"
(
  cd "$ROOT"
  python3 scripts/generate_sky130_frontend_sense_efficiency_audit.py
)

echo
echo "[113/164] Analog converter Sky130 workbench environment"
(
  cd "$ROOT"
  python3 scripts/generate_analog_converter_sky130_workbench_env.py
)

echo
echo "[114/164] Analog converter physical cell gate"
(
  cd "$ROOT"
  python3 scripts/audit_analog_converter_physical_cell_gate.py
)

echo
echo "[115/164] Analog converter physical flow run"
(
  cd "$ROOT"
  python3 scripts/run_analog_converter_physical_flow.py
)

echo
echo "[116/164] Converter post-layout readiness"
(
  cd "$ROOT"
  python3 scripts/generate_converter_post_layout_readiness.py
)

echo
echo "[117/164] Converter post-layout evidence contract"
(
  cd "$ROOT"
  python3 scripts/generate_converter_post_layout_evidence_contract.py
)

echo
echo "[118/164] Converter post-layout payload template"
(
  cd "$ROOT"
  python3 scripts/generate_converter_post_layout_payload_template.py
)

echo
echo "[119/164] Converter post-layout payload validator"
(
  cd "$ROOT"
  python3 scripts/generate_converter_post_layout_payload_validator_report.py
)

echo
echo "[120/164] Converter post-layout break-even rerun path"
(
  cd "$ROOT"
  python3 scripts/generate_converter_post_layout_break_even_rerun_path.py
)

echo
echo "[121/164] Converter post-layout strict intake"
(
  cd "$ROOT"
  python3 scripts/generate_converter_post_layout_strict_intake_report.py
)

echo
echo "[122/164] Converter post-layout positive path"
(
  cd "$ROOT"
  python3 scripts/generate_converter_post_layout_positive_path_report.py
)

echo
echo "[123/164] Converter post-layout submission path"
(
  cd "$ROOT"
  python3 scripts/generate_converter_post_layout_submission_path_report.py
)

echo
echo "[124/164] Converter post-layout real payload package"
(
  cd "$ROOT"
  python3 scripts/generate_converter_post_layout_real_payload_package.py
)

echo
echo "[125/164] Converter post-layout payload preflight"
(
  cd "$ROOT"
  python3 scripts/generate_converter_post_layout_payload_preflight_report.py
)

echo
echo "[126/164] Converter post-layout candidate workspace"
(
  cd "$ROOT"
  python3 scripts/generate_converter_post_layout_candidate_workspace.py
)

echo
echo "[127/164] Converter post-layout candidate workspace audit"
(
  cd "$ROOT"
  python3 scripts/audit_converter_post_layout_candidate_workspace.py
)

echo
echo "[128/164] Converter post-layout candidate fill checklist"
(
  cd "$ROOT"
  python3 scripts/generate_converter_post_layout_candidate_fill_checklist.py
)

echo
echo "[129/164] Converter post-layout candidate progress report"
(
  cd "$ROOT"
  python3 scripts/generate_converter_post_layout_candidate_progress_report.py
)

echo
echo "[130/164] Converter post-layout candidate progress gate"
(
  cd "$ROOT"
  python3 scripts/generate_converter_post_layout_candidate_progress_gate.py
)

echo
echo "[131/164] Converter post-layout candidate preflight gate"
(
  cd "$ROOT"
  python3 scripts/generate_converter_post_layout_candidate_preflight_gate.py
)

echo
echo "[132/164] Converter post-layout candidate submission gate"
(
  cd "$ROOT"
  python3 scripts/generate_converter_post_layout_candidate_submission_gate.py
)

echo
echo "[133/164] Converter post-layout candidate readiness run"
(
  cd "$ROOT"
  python3 scripts/run_converter_post_layout_candidate_readiness.py
)

echo
echo "[134/164] Converter post-layout handoff manifest"
(
  cd "$ROOT"
  python3 scripts/generate_converter_post_layout_handoff_manifest.py
)

echo
echo "[135/164] Converter post-layout blocker ledger"
(
  cd "$ROOT"
  python3 scripts/generate_converter_post_layout_blocker_ledger.py
)

echo
echo "[136/164] Converter post-layout candidate edit plan"
(
  cd "$ROOT"
  python3 scripts/generate_converter_post_layout_candidate_edit_plan.py
)

echo
echo "[137/164] Converter post-layout same-run gate"
(
  cd "$ROOT"
  python3 scripts/generate_converter_post_layout_same_run_gate.py
)

echo
echo "[138/164] Converter post-layout candidate identity initializer"
(
  cd "$ROOT"
  python3 scripts/initialize_converter_post_layout_candidate_identity.py --self-test
)

echo
echo "[139/164] Converter post-layout real candidate builder command"
(
  cd "$ROOT"
  python3 scripts/build_converter_post_layout_candidate_from_real_run.py --self-test
)

echo
echo "[140/164] Converter post-layout submission preview"
(
  cd "$ROOT"
  python3 scripts/preview_converter_post_layout_submission.py --expect-blocked
)

echo
echo "[141/164] Converter post-layout evidence leakage audit"
(
  cd "$ROOT"
  python3 scripts/audit_converter_post_layout_evidence_leakage.py
)

echo
echo "[142/164] Converter post-layout temporary submission proof"
(
  cd "$ROOT"
  python3 scripts/prove_converter_post_layout_temporary_submission.py
)

echo
echo "[143/164] Converter post-layout real artifact discovery"
(
  cd "$ROOT"
  python3 scripts/audit_converter_post_layout_real_artifact_discovery.py
)

echo
echo "[144/164] Converter post-layout real-run recipe"
(
  cd "$ROOT"
  python3 scripts/generate_converter_post_layout_real_run_recipe.py
)

echo
echo "[145/164] Converter post-layout real-run recipe coverage"
(
  cd "$ROOT"
  python3 scripts/generate_converter_post_layout_real_run_recipe_coverage.py
)

echo
echo "[146/164] Calibrated residual governor bridge"
(
  cd "$ROOT"
  python3 scripts/run_calibrated_residual_governor_bridge.py
)

echo
echo "[147/164] Residual-aware placement decisions"
(
  cd "$ROOT"
  python3 scripts/run_residual_aware_placement_decisions.py
)

echo
echo "[148/164] CrossSim layout-risk adapter"
(
  cd "$ROOT"
  python3 scripts/generate_crosssim_layout_risk_adapter.py
)

echo
echo "[149/164] ONNX fixture inventory"
(
  cd "$ROOT"
  python3 scripts/generate_onnx_fixture_inventory.py
)

echo
echo "[150/164] Hardware-lab evidence export"
(
  cd "$ROOT"
  python3 scripts/export_aimc_hardware_lab_evidence.py
)

echo
echo "[151/164] Strict analog tool evidence export"
(
  cd "$ROOT"
  python3 scripts/export_strict_analog_tool_evidence.py
)

echo
echo "[152/164] Static site build"
(
  cd "$ROOT"
  python3 scripts/build_site.py
)

echo
echo "[153/164] Analog simulator adapter dry-run payloads"
(
  cd "$ROOT"
  python3 scripts/generate_analog_simulator_adapter_dry_run.py
)

echo
echo "[154/164] Project validator"
(
  cd "$ROOT"
  python3 scripts/validate_project.py
)

echo
echo "[155/164] Analog simulator adapter contract"
(
  cd "$ROOT"
  python3 scripts/validate_analog_simulator_adapter_contract.py
)

echo
echo "[156/164] Guarded simulator payload import path"
(
  cd "$ROOT"
  python3 scripts/import_analog_simulator_payload.py evidence/aimc-hardware-lab/analog_error_simulation_strict_tool.json
  python3 scripts/import_analog_simulator_payload.py evidence/aimc-simulator-adapters/aihwkit-analog-error-simulation.json
  python3 scripts/import_analog_simulator_payload.py evidence/aimc-simulator-adapters/crosssim-analog-error-simulation.json
  python3 scripts/import_analog_simulator_payload.py evidence/aimc-simulator-adapters/aihwkit-workload-analog-error-simulation.json
  python3 scripts/import_analog_simulator_payload.py evidence/aimc-simulator-adapters/crosssim-workload-analog-error-simulation.json
  import_aihwkit_tensor_shape_payload
  python3 scripts/import_analog_simulator_payload.py evidence/aimc-simulator-adapters/crosssim-tensor-shape-analog-error-simulation.json
  python3 scripts/import_analog_simulator_payload.py --expect-reject evidence/aimc-simulator-adapters/aihwkit-trained-weight-analog-error-simulation.json
  python3 scripts/import_analog_simulator_payload.py evidence/aimc-simulator-adapters/crosssim-trained-weight-analog-error-simulation.json
  python3 scripts/import_analog_simulator_payload.py --expect-reject evidence/aimc-simulator-adapters/aihwkit-projection-stack-analog-error-simulation.json
  python3 scripts/import_analog_simulator_payload.py evidence/aimc-simulator-adapters/crosssim-projection-stack-analog-error-simulation.json
  python3 scripts/import_analog_simulator_payload.py --expect-reject evidence/aimc-simulator-adapters/aihwkit-transformer-mlp-block-analog-error-simulation.json
  python3 scripts/import_analog_simulator_payload.py evidence/aimc-simulator-adapters/crosssim-transformer-mlp-block-analog-error-simulation.json
  python3 scripts/import_analog_simulator_payload.py --expect-reject evidence/aimc-simulator-adapters/aihwkit-calibrated-transformer-mlp-block-analog-error-simulation.json
  python3 scripts/import_analog_simulator_payload.py evidence/aimc-simulator-adapters/crosssim-calibrated-transformer-mlp-block-analog-error-simulation.json
  python3 scripts/import_analog_simulator_payload.py --expect-reject evidence/aimc-simulator-adapters/aihwkit-calibrated-deep-transformer-mlp-stack-analog-error-simulation.json
  python3 scripts/import_analog_simulator_payload.py evidence/aimc-simulator-adapters/crosssim-calibrated-deep-transformer-mlp-stack-analog-error-simulation.json
  python3 scripts/import_analog_simulator_payload.py --expect-reject evidence/aimc-simulator-adapters/aihwkit-attention-block-analog-error-simulation.json
  python3 scripts/import_analog_simulator_payload.py evidence/aimc-simulator-adapters/crosssim-attention-block-analog-error-simulation.json
  python3 scripts/import_analog_simulator_payload.py --expect-reject evidence/aimc-simulator-adapters/aihwkit-calibrated-attention-block-analog-error-simulation.json
  python3 scripts/import_analog_simulator_payload.py evidence/aimc-simulator-adapters/crosssim-calibrated-attention-block-analog-error-simulation.json
  python3 scripts/import_analog_simulator_payload.py --expect-reject evidence/aimc-simulator-adapters/dry-run/aihwkit-analog-error-simulation.dry-run.json
)

echo
echo "[157/164] Cross-repo AIMC loop proof"
(
  cd "$ROOT"
  python3 scripts/prove_cross_repo_aimc_loop.py
)

echo
echo "[158/164] Current AIMC system state summary"
(
  cd "$ROOT"
  python3 scripts/generate_current_aimc_system_state.py
)

echo
echo "[159/164] Next evidence work queue"
(
  cd "$ROOT"
  python3 scripts/generate_next_evidence_work_queue.py
)

echo
echo "[160/164] Static site rebuild after current-state summary"
(
  cd "$ROOT"
  python3 scripts/build_site.py
)

echo
echo "[161/164] Project validator after current-state summary"
(
  cd "$ROOT"
  python3 scripts/validate_project.py
)

echo
echo "[162/164] Backend residual-aware placement API"
(
  cd "$ROOT/../ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture"
  backend/.venv/bin/python backend/scripts/check_residual_aware_placement_api.py
)

echo
echo "[163/164] Backend residual-aware placement archive"
(
  cd "$ROOT/../ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture"
  backend/.venv/bin/python backend/scripts/check_residual_aware_placement_archive.py
)

echo
echo "[164/164] Backend measured evidence boundary"
(
  cd "$ROOT/../ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture"
  backend/.venv/bin/python backend/scripts/check_measured_evidence_readiness.py
)

echo
echo "PASS aimc_bridge_check"
