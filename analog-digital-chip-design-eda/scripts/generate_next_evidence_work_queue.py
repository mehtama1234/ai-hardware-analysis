#!/usr/bin/env python3
"""Generate next evidence work queue from the current AIMC state summary."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CURRENT_STATE = ROOT / "evidence" / "aimc-hardware-lab" / "current-aimc-system-state.json"
OUT_JSON = ROOT / "evidence" / "aimc-hardware-lab" / "next-evidence-work-queue.json"
OUT_MD = ROOT / "evidence" / "aimc-hardware-lab" / "next-evidence-work-queue.md"


def load_state() -> dict:
    if not CURRENT_STATE.exists():
        raise SystemExit(f"missing current state summary: {CURRENT_STATE}")
    return json.loads(CURRENT_STATE.read_text(encoding="utf-8"))


def make_queue(state: dict) -> list[dict[str, object]]:
    package_id = state.get("package_id", "unknown")
    onnx = state.get("onnx_fixture_state") if isinstance(state.get("onnx_fixture_state"), dict) else {}
    placement = state.get("placement_state") if isinstance(state.get("placement_state"), dict) else {}
    layout = state.get("layout_risk_state") if isinstance(state.get("layout_risk_state"), dict) else {}
    aihwkit_diag = state.get("aihwkit_diagnostic_state") if isinstance(state.get("aihwkit_diagnostic_state"), dict) else {}
    aihwkit_mapping = state.get("aihwkit_ideal_mapping_state") if isinstance(state.get("aihwkit_ideal_mapping_state"), dict) else {}
    aihwkit_sweep = state.get("aihwkit_forward_sweep_state") if isinstance(state.get("aihwkit_forward_sweep_state"), dict) else {}
    aihwkit_physical = state.get("aihwkit_physical_review_state") if isinstance(state.get("aihwkit_physical_review_state"), dict) else {}
    aihwkit_tile_replay = state.get("aihwkit_current_tile_replay_state") if isinstance(state.get("aihwkit_current_tile_replay_state"), dict) else {}
    aihwkit_converter_target = state.get("aihwkit_converter_target_state") if isinstance(state.get("aihwkit_converter_target_state"), dict) else {}
    aihwkit_converter_cost = state.get("aihwkit_converter_cost_state") if isinstance(state.get("aihwkit_converter_cost_state"), dict) else {}
    aihwkit_target_noise = state.get("aihwkit_target_noise_state") if isinstance(state.get("aihwkit_target_noise_state"), dict) else {}
    aihwkit_converter_break_even = state.get("aihwkit_converter_break_even_state") if isinstance(state.get("aihwkit_converter_break_even_state"), dict) else {}
    converter_contract = state.get("converter_circuit_contract_state") if isinstance(state.get("converter_circuit_contract_state"), dict) else {}
    local_converter = state.get("local_converter_estimate_state") if isinstance(state.get("local_converter_estimate_state"), dict) else {}
    circuit_sim_converter = state.get("converter_circuit_simulation_estimate_state") if isinstance(state.get("converter_circuit_simulation_estimate_state"), dict) else {}
    spice_handoff = state.get("converter_spice_handoff_spec_state") if isinstance(state.get("converter_spice_handoff_spec_state"), dict) else {}
    row_dac_spice = state.get("row_dac_settling_spice_state") if isinstance(state.get("row_dac_settling_spice_state"), dict) else {}
    sar_readout_spice = state.get("sar_readout_spice_state") if isinstance(state.get("sar_readout_spice_state"), dict) else {}
    shared_loading_spice = state.get("shared_converter_loading_spice_state") if isinstance(state.get("shared_converter_loading_spice_state"), dict) else {}
    supply_energy_spice = state.get("converter_supply_energy_spice_state") if isinstance(state.get("converter_supply_energy_spice_state"), dict) else {}
    post_layout_readiness = state.get("converter_post_layout_readiness_state") if isinstance(state.get("converter_post_layout_readiness_state"), dict) else {}
    post_layout_contract = state.get("converter_post_layout_evidence_contract_state") if isinstance(state.get("converter_post_layout_evidence_contract_state"), dict) else {}
    post_layout_validator = state.get("converter_post_layout_payload_validator_state") if isinstance(state.get("converter_post_layout_payload_validator_state"), dict) else {}
    post_layout_rerun = state.get("converter_post_layout_break_even_rerun_path_state") if isinstance(state.get("converter_post_layout_break_even_rerun_path_state"), dict) else {}
    post_layout_strict_intake = state.get("converter_post_layout_strict_intake_state") if isinstance(state.get("converter_post_layout_strict_intake_state"), dict) else {}
    post_layout_positive_path = state.get("converter_post_layout_positive_path_state") if isinstance(state.get("converter_post_layout_positive_path_state"), dict) else {}
    post_layout_submission_path = state.get("converter_post_layout_submission_path_state") if isinstance(state.get("converter_post_layout_submission_path_state"), dict) else {}
    post_layout_payload_preflight = state.get("converter_post_layout_payload_preflight_state") if isinstance(state.get("converter_post_layout_payload_preflight_state"), dict) else {}
    post_layout_candidate_workspace = state.get("converter_post_layout_candidate_workspace_state") if isinstance(state.get("converter_post_layout_candidate_workspace_state"), dict) else {}
    post_layout_candidate_audit = state.get("converter_post_layout_candidate_workspace_audit_state") if isinstance(state.get("converter_post_layout_candidate_workspace_audit_state"), dict) else {}
    post_layout_candidate_fill_checklist = state.get("converter_post_layout_candidate_fill_checklist_state") if isinstance(state.get("converter_post_layout_candidate_fill_checklist_state"), dict) else {}
    post_layout_candidate_gate_chain = state.get("converter_post_layout_candidate_gate_chain_state") if isinstance(state.get("converter_post_layout_candidate_gate_chain_state"), dict) else {}
    post_layout_candidate_readiness_run = state.get("converter_post_layout_candidate_readiness_run_state") if isinstance(state.get("converter_post_layout_candidate_readiness_run_state"), dict) else {}
    post_layout_candidate_identity_initializer = state.get("converter_post_layout_candidate_identity_initializer_state") if isinstance(state.get("converter_post_layout_candidate_identity_initializer_state"), dict) else {}
    post_layout_submission_preview = state.get("converter_post_layout_submission_preview_state") if isinstance(state.get("converter_post_layout_submission_preview_state"), dict) else {}
    post_layout_real_run_recipe = state.get("converter_post_layout_real_run_recipe_state") if isinstance(state.get("converter_post_layout_real_run_recipe_state"), dict) else {}
    post_layout_real_run_recipe_coverage = state.get("converter_post_layout_real_run_recipe_coverage_state") if isinstance(state.get("converter_post_layout_real_run_recipe_coverage_state"), dict) else {}
    accepted_source = placement.get("accepted_calibrated_source", "unknown")
    source_policy = placement.get("source_matching_policy", "unknown")
    analog_rows = placement.get("analog_allowed_rows") if isinstance(placement.get("analog_allowed_rows"), list) else []
    onnx_available = onnx.get("status") == "available"
    layout_available = layout.get("status") == "available"
    aihwkit_diag_available = aihwkit_diag.get("status") == "available"
    aihwkit_mapping_available = aihwkit_mapping.get("status") == "available"
    aihwkit_sweep_available = aihwkit_sweep.get("status") == "available"
    aihwkit_physical_available = aihwkit_physical.get("status") == "available"
    aihwkit_tile_replay_available = aihwkit_tile_replay.get("status") == "available"
    aihwkit_converter_target_available = aihwkit_converter_target.get("status") == "target_defined_not_justified"
    aihwkit_converter_cost_available = aihwkit_converter_cost.get("status") == "fallback_preferred_until_cost_is_justified"
    aihwkit_target_noise_available = aihwkit_target_noise.get("status") == "available"
    aihwkit_converter_break_even_available = aihwkit_converter_break_even.get("status") == "available"
    converter_contract_available = converter_contract.get("status") == "contract_defined_placeholder_not_claim_ready"
    local_converter_available = local_converter.get("status") == "local_estimate_complete_not_claim_ready"
    circuit_sim_converter_available = circuit_sim_converter.get("status") == "circuit_simulation_complete_not_replacement_ready"
    spice_handoff_available = spice_handoff.get("status") == "available"
    row_dac_spice_available = row_dac_spice.get("status") == "row_dac_settling_spice_passes_simple_load"
    sar_readout_spice_available = sar_readout_spice.get("status") == "sar_readout_spice_passes_simple_sample_load"
    shared_loading_spice_available = shared_loading_spice.get("status") == "shared_converter_loading_spice_passes_simple_mux_load"
    supply_energy_spice_available = supply_energy_spice.get("status") == "converter_supply_energy_spice_complete_simple_load"
    post_layout_readiness_available = post_layout_readiness.get("status") == "local_converter_handoff_complete_post_layout_not_ready"
    post_layout_contract_available = post_layout_contract.get("status") == "post_layout_contract_defined_placeholder_not_claim_ready"
    post_layout_validator_available = post_layout_validator.get("status") == "post_layout_payload_validator_ready_waiting_for_extracted_payload"
    post_layout_rerun_available = post_layout_rerun.get("status") == "rerun_path_ready_waiting_for_validator_passing_payload"
    post_layout_strict_intake_available = post_layout_strict_intake.get("status") == "strict_file_intake_ready_waiting_for_real_artifacts"
    post_layout_positive_path_available = post_layout_positive_path.get("status") == "strict_positive_path_proven_with_temporary_synthetic_files"
    post_layout_submission_path_available = post_layout_submission_path.get("status") == "submission_path_ready_waiting_for_real_payload"
    post_layout_payload_preflight_available = post_layout_payload_preflight.get("status") == "preflight_ready"
    post_layout_candidate_workspace_available = post_layout_candidate_workspace.get("status") == "candidate_workspace_ready_not_evidence"
    post_layout_candidate_audit_available = post_layout_candidate_audit.get("status") == "candidate_workspace_still_scaffold"
    post_layout_candidate_fill_checklist_available = post_layout_candidate_fill_checklist.get("status") == "fill_checklist_ready"
    post_layout_candidate_gate_chain_available = post_layout_candidate_gate_chain.get("status") == "candidate_gate_chain_passed"
    post_layout_candidate_readiness_run_available = post_layout_candidate_readiness_run.get("status") == "candidate_not_ready_for_strict_submission"
    post_layout_candidate_identity_initializer_available = post_layout_candidate_identity_initializer.get("status") == "identity_initializer_ready"
    post_layout_submission_preview_available = post_layout_submission_preview.get("status") in {"blocked_before_submission", "ready_to_submit_without_writing"}
    post_layout_real_run_recipe_available = post_layout_real_run_recipe.get("status") == "real_run_recipe_ready_not_evidence"
    post_layout_real_run_recipe_coverage_available = post_layout_real_run_recipe_coverage.get("status") == "real_run_recipe_covers_current_checklist"
    worst_residual = aihwkit_diag.get("worst_residual_relative")
    worst_residual_text = f"{float(worst_residual):.6f}" if isinstance(worst_residual, (int, float)) else "unknown"
    if post_layout_candidate_readiness_run_available and post_layout_candidate_gate_chain_available and post_layout_candidate_fill_checklist_available and post_layout_candidate_audit_available and post_layout_candidate_workspace_available and post_layout_payload_preflight_available and post_layout_submission_path_available:
        e2_status = "post_layout_candidate_gate_chain_passed_waiting_for_real_values"
        e2_why_next = (
            "The local converter handoff is complete, the one-command submission path exists, preflight can separate shape mistakes from missing files, and a concrete candidate workspace now exists. "
            "The candidate transition chain is now proven: the progress gate distinguishes scaffold from complete package, the preflight gate rejects the scaffold and accepts a complete temporary package, and the submission gate rejects the scaffold while writing complete temporary output only outside canonical accepted evidence. "
            f"The one-command readiness runner currently reports {post_layout_candidate_readiness_run.get('status')} with {post_layout_candidate_readiness_run.get('preflight_issue_count')} preflight issues, so it is the command to rerun after real files and values are filled. "
            f"The workspace audit still reports {post_layout_candidate_audit.get('placeholder_count')} placeholder fields and {post_layout_candidate_audit.get('missing_or_unresolved_file_count')} missing or unresolved files. "
            f"The fill checklist turns those gaps into {post_layout_candidate_fill_checklist.get('item_count')} exact edit items across {', '.join(post_layout_candidate_fill_checklist.get('groups') or [])}. "
            f"The candidate identity initializer is {post_layout_candidate_identity_initializer.get('status') if post_layout_candidate_identity_initializer_available else 'missing'}: it can stamp one shared run id and file names, passes identity validation, does not touch the source scaffold, and leaves strict validation blocked until template status and real values are replaced. "
            "The real-candidate builder command now gives the handoff a direct path from existing extracted files plus numeric converter terms into the candidate payload before preview or submission. "
            f"The submission preview is {post_layout_submission_preview.get('status') if post_layout_submission_preview_available else 'missing'} with {post_layout_submission_preview.get('strict_issue_count') if post_layout_submission_preview_available else 'missing'} strict issues and would_write_accepted_evidence={post_layout_submission_preview.get('would_write_accepted_evidence') if post_layout_submission_preview_available else 'missing'}, so accepted evidence is still protected before the real package is filled. "
            f"The generated real-run recipe has {post_layout_real_run_recipe.get('step_count') if post_layout_real_run_recipe_available else 'missing'} ordered steps, and the coverage audit reports {post_layout_real_run_recipe_coverage.get('covered_checklist_field_count') if post_layout_real_run_recipe_coverage_available else 'missing'}/{post_layout_real_run_recipe_coverage.get('checklist_field_count') if post_layout_real_run_recipe_coverage_available else 'missing'} checklist fields covered with {post_layout_real_run_recipe_coverage.get('uncovered_payload_blocker_field_count') if post_layout_real_run_recipe_coverage_available else 'missing'} uncovered payload blocker fields. "
            "The next proof is to work through that checklist: replace the scaffold with a real extracted netlist, real model files, a source break-even rerun artifact, and numeric post-layout simulation or measured silicon values. "
            "Only after that should `python3 scripts/run_converter_post_layout_candidate_readiness.py` run cleanly and allow the strict submission command to write accepted evidence."
        )
    elif post_layout_submission_path_available:
        e2_status = "post_layout_submission_path_ready_waiting_for_real_payload"
        e2_why_next = (
            "The local converter handoff is complete, and the post-layout intake now has a one-command submission path. "
            "That command rejects the placeholder, rejects a shape-correct payload with missing files, accepts a temporary complete fixture, runs strict validation, reruns break-even, and writes a submission report only after success. "
            "The next proof must run that command on a real extracted post-layout simulation payload or measured silicon payload."
        )
    elif post_layout_positive_path_available:
        e2_status = "post_layout_intake_positive_and_negative_paths_ready"
        e2_why_next = (
            "The local converter handoff is complete, the post-layout contract exists, the validator rejects the placeholder, the break-even rerun path rejects non-evidence inputs, strict intake rejects a shape-correct payload when referenced files are missing, and the temporary positive-path fixture proves strict validation plus rerun can pass when files exist. "
            "The next proof must submit a real extracted post-layout simulation payload or measured silicon payload whose extracted netlist, model files, and rerun artifact exist, then use the generated replace-or-fallback decision as the converter boundary."
        )
    elif post_layout_strict_intake_available:
        e2_status = "post_layout_strict_intake_ready_waiting_for_real_artifacts"
        e2_why_next = (
            "The local converter handoff is complete, the post-layout contract exists, the validator rejects the placeholder, the break-even rerun path rejects non-evidence inputs, and strict intake rejects a shape-correct payload when its referenced files are missing. "
            "The next proof must submit a real extracted post-layout simulation payload or measured silicon payload whose extracted netlist, model files, and rerun artifact exist, then pass validation and produce a replace-or-fallback decision."
        )
    elif post_layout_rerun_available:
        e2_status = "post_layout_rerun_path_ready_waiting_for_extracted_payload"
        e2_why_next = (
            "The local converter handoff is complete, the post-layout contract exists, the validator rejects the placeholder, and the break-even rerun path rejects non-evidence inputs. "
            "The next proof must submit a real extracted post-layout simulation payload or measured silicon payload that passes the validator, then run the rerun script to produce a replace-or-fallback decision from extracted energy, latency, noise, area, and the same sharing rule."
        )
    elif post_layout_validator_available:
        e2_status = "post_layout_payload_validator_ready_waiting_for_extracted_payload"
        e2_why_next = (
            "The local converter handoff is complete, the post-layout contract exists, and the executable validator rejects the placeholder. "
            "The next proof must submit a real extracted post-layout simulation payload or measured silicon payload that passes the validator and reruns break-even with extracted energy, latency, noise, area, and the same sharing rule."
        )
    elif post_layout_contract_available:
        e2_status = "post_layout_contract_defined_placeholder_not_claim_ready"
        e2_why_next = (
            "The local converter handoff is complete and a strict post-layout evidence contract now exists. "
            "The placeholder satisfies the contract shape but refuses break-even replacement because it has no extracted netlist, no post-layout simulation command, no extracted energy, no extracted noise, no extracted area, and no break-even rerun that uses extracted values. "
            "The next proof must submit a real post-layout payload against that contract."
        )
    elif post_layout_readiness_available:
        e2_status = "post_layout_replacement_evidence_defined_not_ready"
        e2_why_next = (
            f"All four local converter SPICE handoff tests now have evidence, and the post-layout readiness gate names {post_layout_readiness.get('missing_replacement_items')} missing replacement items. "
            "The local converter story is internally checked for clean load models, but the break-even table still cannot be replaced. "
            "The next proof must attach an extracted parasitic netlist and post-layout simulation evidence for energy, latency, noise, area, and sharing for the same 10-bit input and 12-bit output target."
        )
    elif supply_energy_spice_available:
        e2_status = "converter_spice_handoff_complete_post_layout_or_silicon_open"
        e2_why_next = (
            f"All four local converter SPICE handoff tests now have evidence. Row-DAC settling passes, 12-bit SAR readout passes, shared converter loading passes up to {shared_loading_spice.get('max_active_loads')} active loads, and supply-energy accounting records {supply_energy_spice.get('cases')} positive-energy cases with worst total energy {supply_energy_spice.get('worst_total_energy_j')} J. "
            "That makes the local converter story internally checked for the simple load models. "
            "The next proof is no longer another local handoff test; it is post-layout simulation or measured silicon so the break-even assumptions can be replaced rather than only narrowed."
        )
    elif shared_loading_spice_available:
        e2_status = "row_dac_sar_and_shared_loading_spice_pass_remaining_energy_open"
        e2_why_next = (
            f"The first three converter SPICE handoff tests now pass. Row-DAC settling passes with worst error {row_dac_spice.get('worst_abs_error_v')} V, 12-bit SAR readout passes {sar_readout_spice.get('cases')} sampled cases with worst error {sar_readout_spice.get('worst_abs_error_v')} V, and shared converter loading passes {shared_loading_spice.get('cases')} cases up to {shared_loading_spice.get('max_active_loads')} active loads with worst error {shared_loading_spice.get('worst_abs_error_v')} V under its half-LSB limit {shared_loading_spice.get('half_lsb_v')} V. "
            "That supports the simple row-drive, sampled-readout, and shared-loading timing assumptions. "
            "The next proof must execute supply-energy accounting; after that, post-layout simulation or measured silicon is still required before replacing break-even."
        )
    elif sar_readout_spice_available:
        e2_status = "row_dac_and_sar_spice_pass_remaining_shared_loading_energy_open"
        e2_why_next = (
            f"The first two converter SPICE handoff tests now pass. Row-DAC settling passes with worst error {row_dac_spice.get('worst_abs_error_v')} V under its half-LSB limit, and 12-bit SAR readout passes {sar_readout_spice.get('cases')} sampled cases with worst error {sar_readout_spice.get('worst_abs_error_v')} V under its half-LSB limit {sar_readout_spice.get('half_lsb_v')} V. "
            "That supports the simple row-drive and sampled-readout timing assumptions. "
            "The next proof must execute shared-converter loading and supply-energy accounting; after that, post-layout simulation or measured silicon is still required before replacing break-even."
        )
    elif row_dac_spice_available:
        e2_status = "row_dac_settling_spice_passes_remaining_converter_spice_open"
        e2_why_next = (
            f"The first converter SPICE handoff test now passes: the 10-bit row-DAC simple load settles in {row_dac_spice.get('cases')} cases, with worst error {row_dac_spice.get('worst_abs_error_v')} V under the half-LSB limit {row_dac_spice.get('half_lsb_v')} V. "
            "That supports the row-drive settling part of the behavioral converter model. "
            "The next proof must execute the remaining converter SPICE tests: 12-bit SAR readout decision error, shared-converter loading, and supply-energy accounting; after that, post-layout simulation or measured silicon is still required before replacing break-even."
        )
    elif spice_handoff_available:
        e2_status = "spice_handoff_defined_not_executed"
        e2_why_next = (
            f"The converter SPICE handoff now defines {spice_handoff.get('testbenches')} transistor-level testbenches for the same 10-bit input and 12-bit output target. "
            "Those testbenches must turn the behavioral terms into circuit evidence: row-DAC settling, SAR readout decision error, shared-converter loading, and supply-energy accounting. "
            "The next proof is to execute those SPICE testbenches and emit a converter evidence record; after that, post-layout simulation or measured silicon is still required before replacing break-even. "
            "Until then the behavioral estimate narrows the target but does not replace break-even."
        )
    elif circuit_sim_converter_available:
        e2_status = "circuit_simulation_estimate_complete_not_replacement_ready"
        e2_why_next = (
            "The converter circuit-simulation estimate now tests the 10-bit input and 12-bit output target with explicit settling, quantization, comparator-noise, row-driver-noise, latency, energy, area-proxy, and sharing terms. "
            f"It records output noise {circuit_sim_converter.get('output_noise_rms')} against the 0.004 budget and keeps the break-even replacement claim closed. "
            "The next proof must replace the behavioral model with transistor-level circuit simulation, post-layout simulation, or measured silicon before the converter assumptions can be trusted."
        )
    elif local_converter_available:
        e2_status = "local_converter_estimate_complete_not_claim_ready"
        e2_why_next = (
            "The local converter estimate now fills the contract fields, but it is still a planning estimate. "
            "It gives explicit ADC energy, DAC row-drive energy, settling time, conversion time, area, and sharing assumptions for the 10-bit input and 12-bit output target. "
            "The next proof must replace those planning numbers with circuit simulation, post-layout simulation, or measured silicon before the break-even assumptions can be trusted."
        )
    elif converter_contract_available:
        e2_status = "converter_contract_defined_not_claim_ready"
        e2_why_next = (
            "The converter evidence contract is now defined, but the current placeholder is not claim-ready. "
            "The next proof must fill that contract with circuit, post-layout, or measured data: 12-bit ADC energy, 10-bit DAC row-driver energy, conversion and settling time, area, sharing rule, and output noise at or below 0.004. "
            "Until that exists, the break-even table remains assumption-based and digital fallback remains the default."
        )
    elif aihwkit_converter_break_even_available:
        e2_status = "break_even_boundary_available"
        e2_why_next = (
            f"The break-even boundary now tests {aihwkit_converter_break_even.get('scenario_count')} local scenarios and finds "
            f"{aihwkit_converter_break_even.get('passing_scenarios')} where the target beats digital under the stated assumptions. "
            f"The first passing scenario is {aihwkit_converter_break_even.get('first_passing_scenario')}. This is still not permission "
            "to place analog work; it names the exact assumptions that must be replaced by real converter energy, real array energy, "
            "sharing policy, timing, area, and a noise source that stays within the 0.004 output-noise budget."
        )
    elif aihwkit_target_noise_available:
        e2_status = "noise_budget_available_cost_unjustified"
        e2_why_next = (
            f"The target noise replay shows the 10-bit input and 12-bit output setting passes at least one nonzero output-noise case, "
            f"with highest all-pass output noise {aihwkit_target_noise.get('highest_all_pass_out_noise')}. But the local cost model "
            f"still prices that target at {float(aihwkit_converter_cost.get('energy_multiplier_vs_current')):.3f} times the current "
            "converter energy. The next proof must show a circuit or measured converter design that meets that noise budget and pays "
            "less than the analog array saves; otherwise digital fallback remains the honest default."
        )
    elif aihwkit_converter_cost_available:
        e2_status = "local_cost_model_prefers_fallback"
        e2_why_next = (
            f"The local cost model prices the 10-bit input and 12-bit output target at {float(aihwkit_converter_cost.get('energy_multiplier_vs_current')):.3f} "
            f"times the current converter energy and {float(aihwkit_converter_cost.get('latency_multiplier_vs_current')):.3f} times the current SAR comparison count. "
            "That makes digital fallback the honest default until measured or circuit-level evidence shows the high-precision analog path wins for the same workload."
        )
    elif aihwkit_converter_target_available:
        e2_status = "converter_target_defined"
        e2_why_next = (
            f"The converter target is now explicit: the current boundary is {aihwkit_converter_target.get('current_dac_bits')}-bit DAC and "
            f"{aihwkit_converter_target.get('current_adc_bits')}-bit ADC, while the minimum passing AIHWKIT target is about "
            f"{aihwkit_converter_target.get('target_input_bits')} effective input bits and {aihwkit_converter_target.get('target_output_bits')} effective output bits. "
            f"That is a {aihwkit_converter_target.get('input_bit_gap')}-bit input gap and a {aihwkit_converter_target.get('output_bit_gap')}-bit output gap. "
            "The next proof must cost that stronger converter/noise boundary, rerun held-out rows, and only then decide whether analog placement is honest; otherwise the rows stay digital fallback."
        )
    elif aihwkit_tile_replay_available:
        e2_status = "current_tile_replay_available"
        e2_why_next = (
            f"The current-tile replay uses the existing {aihwkit_tile_replay.get('dac_bits')}-bit DAC and {aihwkit_tile_replay.get('adc_bits')}-bit ADC boundary. "
            f"It passes {aihwkit_tile_replay.get('passing_rows')} of {aihwkit_tile_replay.get('rows')} rows and reaches max residual {aihwkit_tile_replay.get('max_residual_relative')}. "
            "So the current tile is too coarse for these AIHWKIT rows; the next proof must design and cost a stronger converter/noise boundary or keep digital fallback."
        )
    elif aihwkit_physical_available:
        e2_status = "physical_review_available"
        e2_why_next = (
            f"The physical-setting review says {aihwkit_physical.get('candidate_setting')} needs about {aihwkit_physical.get('candidate_effective_input_bits')} input bits and "
            f"{aihwkit_physical.get('candidate_effective_output_bits')} output bits, while the current tile boundary is {aihwkit_physical.get('tile_dac_bits')}-bit DAC and "
            f"{aihwkit_physical.get('tile_adc_bits')}-bit ADC. Its status is {aihwkit_physical.get('review_status')}. "
            "The next step is to either cost that stronger converter/noise boundary or rerun AIHWKIT under the current tile boundary."
        )
    elif aihwkit_sweep_available:
        e2_status = "forward_sweep_available"
        e2_why_next = (
            f"The forward-setting sweep checks {aihwkit_sweep.get('settings')} settings over {aihwkit_sweep.get('rows_per_setting')} rows and finds "
            f"{aihwkit_sweep.get('passing_settings')} settings that pass every row. The best passing setting is {aihwkit_sweep.get('best_passing_setting')} "
            f"with max residual {aihwkit_sweep.get('best_max_residual_relative')}. The next step is not to weaken the importer; it is to decide which passing setting has a physically defensible device, converter, and calibration meaning."
        )
    elif aihwkit_mapping_available:
        e2_status = "ideal_mapping_proven"
        e2_why_next = (
            f"The diagnostic checks {aihwkit_diag.get('payloads')} AIHWKIT payloads and finds {aihwkit_diag.get('threshold_fail_payloads')} threshold-fail payloads. "
            f"The worst row is {aihwkit_diag.get('worst_fixture')}/{aihwkit_diag.get('worst_candidate')} at residual {worst_residual_text}. "
            f"The ideal-forward mapping proof passes {aihwkit_mapping.get('passing_rows')} rows with max residual {aihwkit_mapping.get('max_residual_relative')}. "
            "So the shape and transpose path are not the repair target; the next work is non-perfect forward tuning."
        )
    elif aihwkit_diag_available:
        e2_status = "diagnostic_available"
        e2_why_next = (
            f"The diagnostic checks {aihwkit_diag.get('payloads')} AIHWKIT payloads and finds {aihwkit_diag.get('threshold_fail_payloads')} threshold-fail payloads. "
            f"The worst row is {aihwkit_diag.get('worst_fixture')}/{aihwkit_diag.get('worst_candidate')} at residual {worst_residual_text}. "
            "That is useful negative evidence, not placement permission."
        )
    else:
        e2_status = "open"
        e2_why_next = "AIHWKIT is installed and runs, but larger payloads currently exceed the positive-claim residual threshold. That is useful negative evidence, not placement permission."
    if post_layout_candidate_readiness_run_available and post_layout_candidate_gate_chain_available and post_layout_candidate_fill_checklist_available and post_layout_candidate_audit_available and post_layout_candidate_workspace_available and post_layout_payload_preflight_available and post_layout_submission_path_available:
        e2_blocked_until = "not blocked locally; run_converter_post_layout_candidate_readiness.py is ready and now needs real netlist/model/rerun files and numeric post-layout simulation or measured silicon values"
    elif post_layout_submission_path_available:
        e2_blocked_until = "not blocked locally; replacement proof needs a real payload submitted through scripts/submit_converter_post_layout_payload.py"
    elif post_layout_positive_path_available:
        e2_blocked_until = "not blocked locally; replacement proof needs real extracted post-layout or measured-silicon artifacts rather than temporary synthetic files"
    elif post_layout_strict_intake_available:
        e2_blocked_until = "not blocked locally; replacement proof needs a real extracted post-layout simulation payload or measured silicon payload with referenced files present"
    elif post_layout_rerun_available:
        e2_blocked_until = "not blocked locally; replacement proof needs a real extracted post-layout simulation payload or measured silicon payload that passes the validator and rerun script"
    elif post_layout_validator_available:
        e2_blocked_until = "not blocked locally; replacement proof needs a real extracted post-layout simulation payload or measured silicon payload that passes the validator"
    elif post_layout_contract_available:
        e2_blocked_until = "not blocked locally for contract work; replacement proof needs a real extracted post-layout payload or measured silicon payload"
    elif post_layout_readiness_available:
        e2_blocked_until = "not blocked locally for documentation or modeling; replacement proof needs extracted post-layout artifacts or measured silicon"
    elif supply_energy_spice_available:
        e2_blocked_until = "not blocked locally for documentation or modeling; stronger replacement proof needs post-layout simulation or measured silicon"
    elif shared_loading_spice_available:
        e2_blocked_until = "not blocked locally; next proof needs supply-energy SPICE evidence"
    elif sar_readout_spice_available:
        e2_blocked_until = "not blocked locally; next proof needs shared-converter loading and supply-energy SPICE evidence"
    elif row_dac_spice_available:
        e2_blocked_until = "not blocked locally; next proof needs SAR readout, shared-converter loading, and supply-energy SPICE evidence"
    elif spice_handoff_available:
        e2_blocked_until = "not blocked locally; next proof needs executable SPICE testbenches that fill the converter evidence contract"
    elif circuit_sim_converter_available:
        e2_blocked_until = "not blocked locally; next proof needs transistor-level circuit simulation, post-layout simulation, or measured silicon to replace the behavioral converter estimate"
    elif local_converter_available:
        e2_blocked_until = "not blocked locally; next proof needs circuit simulation, post-layout simulation, or measured silicon to replace the local converter estimate"
    elif converter_contract_available:
        e2_blocked_until = "not blocked locally; next proof needs a filled converter evidence record with post-layout or measured energy, latency, area, sharing, and noise below 0.004"
    elif aihwkit_converter_break_even_available:
        e2_blocked_until = "not blocked locally; next proof needs real converter energy, real array energy, sharing policy, latency, area, and a noise source inside 0.004 to replace the local break-even assumptions"
    elif aihwkit_target_noise_available:
        e2_blocked_until = "not blocked locally; next proof needs circuit-level or measured converter evidence that meets the 0.004 output-noise budget and beats digital fallback on energy/latency"
    elif aihwkit_converter_cost_available:
        e2_blocked_until = "not blocked locally; next proof needs measured or circuit-level converter energy, latency, area, calibration, and nonzero-noise replay to overturn the fallback default"
    elif aihwkit_converter_target_available:
        e2_blocked_until = "not blocked locally; next proof needs energy, latency, area, calibration, and noise evidence for the 10-bit input and 12-bit output target, or an explicit digital fallback policy"
    elif aihwkit_tile_replay_available:
        e2_blocked_until = "not blocked locally; next proof needs a stronger converter/noise design cost or explicit digital fallback policy for the failing AIHWKIT rows"
    elif aihwkit_physical_available:
        e2_blocked_until = "not blocked locally; next proof needs converter/noise cost for the stronger AIHWKIT setting or a rerun under the current 4-bit DAC and 6-bit ADC tile boundary"
    elif aihwkit_sweep_available:
        e2_blocked_until = "not blocked locally; next proof needs a physically defensible AIHWKIT forward setting, then a guarded payload using that setting"
    elif aihwkit_mapping_available:
        e2_blocked_until = "not blocked locally; next proof needs non-perfect forward tuning that moves worst rows under threshold without weakening the importer"
    elif aihwkit_diag_available:
        e2_blocked_until = "not blocked locally; next proof needs a mapping change that moves worst rows under threshold without weakening the importer"
    else:
        e2_blocked_until = "a mapping change improves held-out residual without weakening the claim rule"

    return [
        {
            "id": "E1",
            "title": "Larger real-model ONNX simulator slice",
            "claim_target": "strengthen C4 and residual-aware placement",
            "status": "local_fixture_selected" if onnx_available else "open",
            "why_next": (
                f"The current best local fixture is {onnx.get('selected_current_best_fixture')} with {onnx.get('max_fixed_weight_matmul_count')} fixed-weight MatMul rows. "
                "The next stronger step is replacing that fixture with a real uploaded or imported model slice."
                if onnx_available
                else "The current accepted source is a fixture. A larger real-model slice would test whether the same fixed-weight MatMul rule survives a less toy-shaped model object."
            ),
            "object": "one uploaded ONNX slice with fixed-weight MatMul rows, digital support ops, real initializer weights, and a digital reference output",
            "method": (
                "use the selected local ONNX fixture as the current rehearsal path, then rerun the same extractor, simulator exporters, and guarded importer on a real uploaded model slice"
                if onnx_available
                else "extract MatMul weights, keep non-MatMul support operations digital, run AIHWKIT and CrossSim payload exporters, and pass the guarded importer"
            ),
            "acceptance_evidence": [
                "ONNX fixture inventory names the selected current local fixture and fixed-weight MatMul count",
                "strict AIHWKIT or CrossSim payload exists for the larger ONNX slice",
                "payload names target object, device assumptions, array assumptions, ADC bits, DAC bits, temperature boundary, and voltage boundary",
                "guarded importer accepts the payload or records a threshold-fail rejection",
                f"residual-aware placement records source policy {source_policy} against package {package_id}",
            ],
            "blocked_until": "not blocked locally; stronger proof waits for a real uploaded or imported model slice" if onnx_available else "a larger ONNX fixture or uploaded model slice is selected",
            "refused_claim": "does not prove full foundation-model accuracy, measured board latency, measured energy, calibrated silicon, or production readiness",
        },
        {
            "id": "E2",
            "title": "AIHWKIT positive residual mapping",
            "claim_target": "turn AIHWKIT from run evidence into positive simulator evidence where justified",
            "status": e2_status,
            "why_next": e2_why_next,
            "object": "the same fixed-weight MatMul family currently represented by the analog-allowed rows",
            "method": "adjust mapping, scaling, calibration, converter circuit assumptions, sharing policy, or device assumptions outside the guarded claim path, then rerun held-out payloads without relaxing the importer threshold",
            "acceptance_evidence": [
                "AIHWKIT residual diagnostic ranks worst rows before any threshold or mapping change",
                "AIHWKIT ideal-forward mapping proof shows shape and transpose correctness before noisy forward tuning",
                "AIHWKIT forward-setting sweep names the passing settings and their max residuals",
                "AIHWKIT physical-setting review compares the passing setting to the current tile ADC/DAC boundary",
                "AIHWKIT current-tile replay measures the same rows under the existing 4-bit DAC and 6-bit ADC boundary",
                "AIHWKIT converter upgrade target records the 10-bit input, 12-bit output, six-bit input gap, and six-bit output gap",
                "AIHWKIT converter cost model estimates energy and comparison cost for the stronger converter boundary",
                "AIHWKIT target noise sensitivity records the highest all-pass nonzero output-noise setting",
                "AIHWKIT converter break-even records the rows, sharing, array-saving, and digital-fallback assumptions needed before the target can beat digital",
                "converter circuit evidence contract records the ADC/DAC energy, latency, noise, area, and sharing fields needed to replace the break-even assumptions",
                "local converter circuit estimate fills that contract with planning numbers while staying not claim-ready",
                "converter circuit-simulation estimate narrows the target with explicit settling, quantization, noise, latency, energy, area-proxy, and sharing terms while staying not replacement-ready",
                "converter SPICE handoff spec defines row-DAC settling, SAR readout, shared-converter loading, and energy-accounting testbenches",
                "row-DAC settling SPICE evidence passes the simple 10-bit row-driver load against the half-LSB settling rule",
                "SAR readout SPICE evidence passes the simple 12-bit sampled-readout load against the half-LSB decision rule",
                "shared converter loading SPICE evidence passes the simple muxed readout load against the half-LSB decision rule",
                "converter supply-energy SPICE evidence records positive integrated row-drive, ADC-reference, and mux energy on a named rail",
                "converter post-layout readiness names the extracted parasitic, energy, latency, noise, area, sharing, and break-even rerun fields required before replacement",
                "converter post-layout evidence contract defines the importable payload shape and keeps the placeholder not claim-ready",
                "converter post-layout payload validator rejects the placeholder and waits for a real extracted payload",
                "converter post-layout break-even rerun path rejects non-evidence inputs and waits for a validator-passing payload",
                "converter post-layout strict intake rejects shape-correct payloads whose referenced files are missing",
                "converter post-layout positive path proves strict validation and rerun can pass with temporary synthetic files",
                "converter post-layout submission path provides one command for strict validation, break-even rerun, and submission report writing",
                "converter real payload package names the required payload, netlist, model files, and rerun artifact",
                "converter payload preflight reports missing-file payloads as not ready and complete temporary payloads as ready without accepted evidence",
                "converter candidate workspace provides payload, netlist, models, and rerun staging folders while rejecting the default scaffold",
                "converter candidate workspace audit reports the scaffold placeholder count and missing file count before preflight",
                "converter candidate fill checklist turns the audit into exact field and file edits before preflight",
                "converter candidate gate chain proves progress, preflight, and strict submission transitions without persisting canonical accepted evidence",
                "converter candidate readiness runner gives one command for audit, checklist, progress, and preflight before strict submission",
                "AIHWKIT larger or calibrated payload reports accuracy_impact.pass true",
                "guarded importer accepts the AIHWKIT payload without --expect-reject",
                "current-state summary records at least one larger AIHWKIT outcome as wrote_payload without threshold_fail",
                f"allowed rows remain explicit: {', '.join(str(row) for row in analog_rows) or 'none'}",
            ],
            "blocked_until": e2_blocked_until,
            "refused_claim": "does not allow threshold-fail AIHWKIT output to support positive analog placement",
        },
        {
            "id": "E3",
            "title": "CrossSim layout-risk adapter",
            "claim_target": "separate array-layout risk from model-level simulator residual",
            "status": "supported" if layout_available else "open",
            "why_next": (
                f"The first local layout-risk adapter exists and covers {layout.get('operators')} CrossSim-backed analog rows. "
                "The next upgrade is stronger physical evidence: extracted parasitics or a fuller crossbar simulation flow."
                if layout_available
                else "CrossSim currently supports calibrated MatMul residual evidence. A layout-risk adapter should expose why a row passes or fails physically: array size, wire drop, bit slicing, converter range, and column current."
            ),
            "object": "one analog tile candidate with row count, column count, conductance range, bit slicing, DAC precision, ADC range, wire assumptions, and column-current range",
            "method": (
                "keep the current generated layout-risk record as the local review boundary, then replace local estimates with extracted macro parasitics or a stronger crossbar flow"
                if layout_available
                else "derive tile assumptions from the selected MatMul rows, run CrossSim or a CrossSim-backed wrapper, and emit a backend-importable physical-layout risk record"
            ),
            "acceptance_evidence": [
                "layout-risk JSON names array size, wire assumptions, ADC range, DAC precision, bit slicing, and column-current range",
                "record links back to residual-aware placement source",
                f"record preserves accepted source {accepted_source}",
                "frontend and current-state summary refuse to treat it as analog macro signoff",
            ],
            "blocked_until": "not blocked locally; stronger proof waits for extracted macro parasitics or fuller crossbar simulation" if layout_available else "a layout-risk schema and backend source ID are defined",
            "refused_claim": "does not prove full analog macro layout, extraction, DRC/LVS signoff, or silicon behavior",
        },
        {
            "id": "E4",
            "title": "Measured board runtime trace",
            "claim_target": "upgrade C2 from needs review to supported",
            "why_next": "The current runtime evidence is local RTL/runtime behavior. Measured latency needs a real board or instrumented runtime trace.",
            "object": "one board or instrumented runtime execution of the same package and workload",
            "method": "record package ID, workload ID, board ID, board revision, runtime version, runtime trace ID, start/end timestamps, fallback events, repeated runs, p50, p95, and host-overhead boundary",
            "acceptance_evidence": [
                "measured board runtime payload passes /evidence/validate-measured",
                "local board ID and local/not-measured provenance are absent",
                "claim readiness moves C2 to supported for the exact setup",
                "C3 remains needs review unless matching measured power is attached",
            ],
            "blocked_until": "real board or stronger instrumented runtime source is available",
            "refused_claim": "does not prove measured energy, measured power, calibrated silicon, production readiness, or another board",
        },
        {
            "id": "E5",
            "title": "Synchronized measured power trace",
            "claim_target": "upgrade C3 from needs review to supported",
            "why_next": "Energy is voltage times current over the same runtime window. A measured power artifact is not enough if it describes a different run.",
            "object": "meter-backed voltage/current samples for the same package, workload, board, runtime trace ID, and run window as the runtime trace",
            "method": "record meter, measured rail, sampling rate, voltage/current samples, integration timestamps, energy, average power, peak power, thermal samples, repeated-run count, and host-overhead boundary",
            "acceptance_evidence": [
                "measured power payload passes /evidence/validate-measured",
                "runtime and power records share runtime trace ID, package ID, workload ID, board ID, start time, and end time",
                "claim readiness moves C3 to supported",
                "mismatched runtime_trace_id still keeps C3 needs review in regression tests",
            ],
            "blocked_until": "meter or instrumented power source is available for the same runtime trace",
            "refused_claim": "does not prove production power, another workload, another temperature, or signoff energy",
        },
    ]


def write_markdown(state: dict, queue: list[dict[str, object]]) -> None:
    lines = [
        "# Next AIMC Evidence Work Queue",
        "",
        "This file is generated from the current AIMC system state.",
        "",
        f"- package: `{state.get('package_id')}`",
        f"- proof status: `{state.get('proof_status')}`",
        f"- supported lab claims: `{state.get('claim_summary', {}).get('supported_lab_claims')}`",
        f"- needs-review lab claims: `{state.get('claim_summary', {}).get('needs_review_lab_claims')}`",
        f"- production claim: `{state.get('claim_summary', {}).get('production_claim')}`",
        "",
    ]
    for item in queue:
        lines.extend(
            [
                f"## {item['id']}. {item['title']}",
                "",
                f"- claim target: {item['claim_target']}",
                f"- status: {item.get('status', 'open')}",
                f"- why next: {item['why_next']}",
                f"- object: {item['object']}",
                f"- method: {item['method']}",
                "",
                "Acceptance evidence:",
                "",
            ]
        )
        lines.extend(f"- {evidence}" for evidence in item["acceptance_evidence"])
        lines.extend(
            [
                "",
                f"Blocked until: {item['blocked_until']}",
                "",
                f"Refused claim: {item['refused_claim']}",
                "",
            ]
        )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    state = load_state()
    queue = make_queue(state)
    body = {
        "result_type": "next_aimc_evidence_work_queue",
        "source_artifact": str(CURRENT_STATE.relative_to(ROOT)),
        "package_id": state.get("package_id"),
        "proof_status": state.get("proof_status"),
        "work_items": queue,
    }
    OUT_JSON.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(state, queue)
    print("next_aimc_evidence_work_queue")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    print(f"items,{len(queue)}")


if __name__ == "__main__":
    main()
