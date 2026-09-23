#!/usr/bin/env python3
"""Compile current evidence into the next bounded recursive action queue."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/converter-to-inference-v1/results/current-mode-policy-bridge.json"
COST = Path(__file__).resolve().parent / "cost-model-break-even.json"
MEASUREMENT = Path(__file__).resolve().parent / "physical-cost-calibration-contract.json"
REGULATED = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/regulated-cascode-current-mode-search.json"
REGULATED_LOAD_MUTATION = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/regulated-cascode-load-mutation-search.json"
REGULATED_MISMATCH = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/regulated-cascode-mismatch-population.json"
SUPPORTED_MISMATCH = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/regulated-cascode-supported-mismatch-summary.json"
BOUNDARY_REUSE = Path(__file__).resolve().parent / "boundary-reuse-cost-experiment.json"
READINESS = Path(__file__).resolve().parent / "end-to-end-readiness-audit.json"
DIFFERENTIAL_POLICY = Path(__file__).resolve().parent / "differential-correction-policy-handoff.json"
DIFFERENTIAL_TRANSFER = Path(__file__).resolve().parent / "differential-correction-workload-transfer.json"
THERMOMETER = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-thermometer-search.json"
SOURCE_DEGENERATED = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-source-degenerated-search.json"
ACTIVE_FEEDBACK = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-search.json"
ACTIVE_FEEDBACK_PROVENANCE = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-provenance.json"
ACTIVE_FEEDBACK_GROUPED_REFERENCE = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-grouped-reference-search.json"
ACTIVE_FEEDBACK_GROUPED_REFERENCE_PROVENANCE = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-grouped-reference-search-provenance.json"
ACTIVE_FEEDBACK_GROUPED_SENSITIVITY = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-grouped-reference-sensitivity-search.json"
ACTIVE_FEEDBACK_GROUPED_SENSITIVITY_PROVENANCE = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-grouped-reference-sensitivity-search-provenance.json"
ACTIVE_FEEDBACK_GROUP0_NMOS_REFINEMENT = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-group0-nmos-refinement.json"
ACTIVE_FEEDBACK_GROUP0_NMOS_REFINEMENT_PROVENANCE = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-group0-nmos-refinement-provenance.json"
ACTIVE_FEEDBACK_GROUP0_NMOS_LOWER_RANGE = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-group0-nmos-lower-range-search.json"
ACTIVE_FEEDBACK_GROUP0_NMOS_LOWER_RANGE_PROVENANCE = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-group0-nmos-lower-range-search-provenance.json"
ACTIVE_FEEDBACK_GROUP0_NMOS_MIN_GEOMETRY = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-group0-nmos-min-geometry-search.json"
ACTIVE_FEEDBACK_GROUP0_NMOS_MIN_GEOMETRY_PROVENANCE = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-group0-nmos-min-geometry-search-provenance.json"
ACTIVE_FEEDBACK_GROUP1_NMOS = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-group1-nmos-search.json"
ACTIVE_FEEDBACK_GROUP1_NMOS_PROVENANCE = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-group1-nmos-search-provenance.json"
ACTIVE_FEEDBACK_GROUP2_NMOS = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-group2-nmos-search.json"
ACTIVE_FEEDBACK_GROUP2_NMOS_PROVENANCE = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-group2-nmos-search-provenance.json"
ACTIVE_FEEDBACK_GROUP2_SENSITIVITY = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-group2-sensitivity-analysis.json"
ACTIVE_FEEDBACK_GROUP2_SENSITIVITY_PROVENANCE = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-group2-sensitivity-analysis-provenance.json"
ACTIVE_FEEDBACK_REFINEMENT = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-refinement-search.json"
ACTIVE_FEEDBACK_REFINEMENT_PROVENANCE = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-refinement-provenance.json"
ACTIVE_FEEDBACK_WIDTH_REFINEMENT = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-feedback-correction-width-refinement-search.json"
ACTIVE_FEEDBACK_FINGER_REFINEMENT = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-feedback-finger-refinement-search.json"
ACTIVE_FEEDBACK_SHARED_BIAS = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-shared-bias-search.json"
ACTIVE_FEEDBACK_SHARED_BIAS_PROVENANCE = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-shared-bias-provenance.json"
ACTIVE_FEEDBACK_MOS_REFERENCE = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-mos-reference-search.json"
ACTIVE_FEEDBACK_MOS_REFERENCE_PROVENANCE = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-mos-reference-provenance.json"
ACTIVE_FEEDBACK_MOS_REFERENCE_RESULTS = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results"
ACTIVE_FEEDBACK_MOS_GEOMETRY_STRESS = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-mos-reference-geometry-stress.json"
ACTIVE_FEEDBACK_MOS_GEOMETRY_STRESS_PROVENANCE = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-active-feedback-mos-reference-geometry-stress-provenance.json"
PHYSICAL_POLICY = Path(__file__).resolve().parent / "physical-rsi-policy-learning.json"
PHYSICAL_PROMOTION = Path(__file__).resolve().parent / "physical-rsi-promotion-evaluation.json"
COST_CONSISTENCY = Path(__file__).resolve().parent / "runtime-cost-model-consistency.json"
PREPARED_PACKAGE = Path(__file__).resolve().parent / "prepared-board-package.json"
MUTATION_MEMORY = Path(__file__).resolve().parent / "converter-mutation-failure-memory.json"
SEGMENTED_MISMATCH = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/segmented-residue-mismatch-stress.json"
SEGMENTED_TRANSFER = Path(__file__).resolve().parent / "segmented-residue-workload-transfer.json"
SEGMENTED_COST_ROLLBACK = Path(__file__).resolve().parent / "segmented-residue-cost-rollback-validation.json"
SEGMENTED_POLICY = Path(__file__).resolve().parent / "segmented-residue-policy-handoff.json"
OUT = Path(__file__).resolve().parent / "next-recursive-action-queue.json"
MUTATION_MEMORY_SCHEMA = "recursive_converter_mutation_failure_memory.v3"
ACTIVE_FEEDBACK_SHARED_BIAS_FAMILY = "analog_converter_differential_active_feedback_shared_bias_search.v1"
ACTIVE_FEEDBACK_MOS_REFERENCE_FAMILY = "analog_converter_differential_active_feedback_mos_reference_search.v1"
ACTIVE_FEEDBACK_CORRECTION_WIDTH_FAMILY = "analog_converter_differential_active_feedback_correction_width_search.v1"
ACTIVE_FEEDBACK_GATE_DRIVE_FAMILY = "analog_converter_differential_active_feedback_gate_drive_search.v1"
ACTIVE_FEEDBACK_INPUT_PAIR_WIDTH_FAMILY = "analog_converter_differential_active_feedback_input_pair_width_search.v1"
ACTIVE_FEEDBACK_TAIL_WIDTH_FAMILY = "analog_converter_differential_active_feedback_tail_width_search.v1"
ACTIVE_FEEDBACK_GROUPED_REFERENCE_FAMILY = "analog_converter_differential_active_feedback_grouped_reference_search.v1"
ACTIVE_FEEDBACK_GROUPED_REFERENCE_SENSITIVITY_FAMILY = "analog_converter_differential_active_feedback_grouped_reference_sensitivity_search.v1"
ACTIVE_FEEDBACK_GROUP0_NMOS_REFINEMENT_FAMILY = "analog_converter_differential_active_feedback_group0_nmos_refinement.v1"
ACTIVE_FEEDBACK_GROUP0_NMOS_LOWER_RANGE_FAMILY = "analog_converter_differential_active_feedback_group0_nmos_lower_range_search.v1"
ACTIVE_FEEDBACK_GROUP0_NMOS_MIN_GEOMETRY_FAMILY = "analog_converter_differential_active_feedback_group0_nmos_min_geometry_search.v1"
ACTIVE_FEEDBACK_GROUP1_NMOS_FAMILY = "analog_converter_differential_active_feedback_group1_nmos_search.v1"
ACTIVE_FEEDBACK_GROUP2_NMOS_FAMILY = "analog_converter_differential_active_feedback_group2_nmos_search.v1"
CODE_DEPENDENT_TRANSFER_SHAPING_FAMILY = "analog_converter_code_dependent_transfer_shaping_search.v1"
RESIDUE_INJECTION_FAMILY = "analog_converter_residue_injection_topology_search.v1"
CODE_DEPENDENT_RESIDUE_REFINEMENT_FAMILY = "analog_converter_code_dependent_residue_refinement.v1"
SEGMENTED_RESIDUE_FAMILY = "analog_converter_segmented_residue_topology_search.v1"
SEGMENTED_BRANCH_REFINEMENT_FAMILY = "analog_converter_segmented_residue_branch_refinement.v1"
SOURCE_DEGENERATED_FEEDBACK_FAMILY = "analog_converter_source_degenerated_feedback_search.v1"
CHARGE_REDISTRIBUTION_FAMILY = "analog_converter_charge_redistribution_search.v1"
MOS_REFERENCE_PMOS_WIDTHS = ("0.5u", "1u", "2u", "4u")
MOS_REFERENCE_NMOS_WIDTHS = ("2.5u", "5u", "10u", "20u", "40u")


def choose_untried_reference_width_pair(entries: list[dict]) -> tuple[str, str] | None:
    """Explore the nearest untested MOS width ratio to the best observed candidate."""
    mos_entries = []
    known = set()
    for entry in entries:
        if not isinstance(entry, dict) or entry.get("family") != ACTIVE_FEEDBACK_MOS_REFERENCE_FAMILY:
            continue
        action = entry.get("action")
        if not isinstance(action, dict) or action.get("feedback_reference_topology") != "mos_diode_ratio":
            continue
        pmos = action.get("feedback_reference_pmos_width")
        nmos = action.get("feedback_reference_nmos_width")
        if pmos in MOS_REFERENCE_PMOS_WIDTHS and nmos in MOS_REFERENCE_NMOS_WIDTHS:
            pair = (pmos, nmos)
            known.add(pair)
            value = entry.get("max_inl_lsb")
            if (isinstance(value, (int, float)) and not isinstance(value, bool)
                    and math.isfinite(float(value))):
                mos_entries.append((float(value), pair, entry))
    if not mos_entries:
        return None
    _, (best_pmos, best_nmos), _ = min(mos_entries, key=lambda item: item[0])
    best_ratio = float(best_pmos[:-1]) / float(best_nmos[:-1])
    candidates = []
    for pmos in MOS_REFERENCE_PMOS_WIDTHS:
        for nmos in MOS_REFERENCE_NMOS_WIDTHS:
            if (pmos, nmos) in known:
                continue
            ratio = float(pmos[:-1]) / float(nmos[:-1])
            candidates.append((abs(math.log(ratio / best_ratio)),
                               float(pmos[:-1]) + float(nmos[:-1]), pmos, nmos))
    if not candidates:
        return None
    _, _, pmos, nmos = min(candidates)
    return pmos, nmos


def derive_mutation_memory_guidance(memory: dict, memory_sha256: str | None = None,
                                    group2_sensitivity_analysis: dict | None = None) -> dict:
    """Turn typed mutation outcomes into a bounded next-experiment hint."""
    if memory.get("schema_version") != MUTATION_MEMORY_SCHEMA:
        return {"status": "unavailable", "reason": "unsupported_or_missing_memory_schema",
                "recommendation_id": None, "runtime_authorized": False}
    entries = memory.get("entries")
    if not isinstance(entries, list) or not entries:
        return {"status": "unavailable", "reason": "mutation_outcomes_missing",
                "recommendation_id": None, "runtime_authorized": False}

    reason_counts: dict[str, int] = {}
    target_family = []
    correction_width_entries = []
    gate_drive_entries = []
    input_pair_width_entries = []
    tail_width_entries = []
    grouped_reference_entries = []
    grouped_sensitivity_entries = []
    group0_nmos_refinement_entries = []
    group0_nmos_lower_range_entries = []
    group0_nmos_min_geometry_entries = []
    group1_nmos_entries = []
    group2_nmos_entries = []
    code_dependent_transfer_entries = []
    residue_injection_entries = []
    code_dependent_residue_entries = []
    segmented_residue_entries = []
    segmented_branch_refinement_entries = []
    source_degenerated_feedback_entries = []
    charge_redistribution_entries = []
    known_reference_topologies = set()
    known_reference_width_pairs = set()
    best_mos_reference_entry = None
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        reasons = entry.get("rejection_reasons", [])
        if isinstance(reasons, list):
            for reason in reasons:
                if isinstance(reason, str):
                    reason_counts[reason] = reason_counts.get(reason, 0) + 1
        if entry.get("family") in {ACTIVE_FEEDBACK_SHARED_BIAS_FAMILY,
                                    ACTIVE_FEEDBACK_MOS_REFERENCE_FAMILY,
                                    ACTIVE_FEEDBACK_GROUPED_REFERENCE_FAMILY,
                                    ACTIVE_FEEDBACK_GROUPED_REFERENCE_SENSITIVITY_FAMILY,
                                    ACTIVE_FEEDBACK_GROUP0_NMOS_REFINEMENT_FAMILY,
                                    ACTIVE_FEEDBACK_GROUP0_NMOS_LOWER_RANGE_FAMILY,
                                    ACTIVE_FEEDBACK_GROUP0_NMOS_MIN_GEOMETRY_FAMILY,
                                    ACTIVE_FEEDBACK_GROUP1_NMOS_FAMILY,
                                    ACTIVE_FEEDBACK_GROUP2_NMOS_FAMILY}:
            target_family.append(entry)
        if entry.get("family") == ACTIVE_FEEDBACK_CORRECTION_WIDTH_FAMILY:
            correction_width_entries.append(entry)
        if entry.get("family") == ACTIVE_FEEDBACK_GATE_DRIVE_FAMILY:
            gate_drive_entries.append(entry)
        if entry.get("family") == ACTIVE_FEEDBACK_INPUT_PAIR_WIDTH_FAMILY:
            input_pair_width_entries.append(entry)
        if entry.get("family") == ACTIVE_FEEDBACK_TAIL_WIDTH_FAMILY:
            tail_width_entries.append(entry)
        if entry.get("family") == ACTIVE_FEEDBACK_GROUPED_REFERENCE_FAMILY:
            grouped_reference_entries.append(entry)
        if entry.get("family") == ACTIVE_FEEDBACK_GROUPED_REFERENCE_SENSITIVITY_FAMILY:
            grouped_reference_entries.append(entry)
            grouped_sensitivity_entries.append(entry)
        if entry.get("family") == ACTIVE_FEEDBACK_GROUP0_NMOS_REFINEMENT_FAMILY:
            grouped_reference_entries.append(entry)
            group0_nmos_refinement_entries.append(entry)
        if entry.get("family") == ACTIVE_FEEDBACK_GROUP0_NMOS_LOWER_RANGE_FAMILY:
            grouped_reference_entries.append(entry)
            group0_nmos_lower_range_entries.append(entry)
        if entry.get("family") == ACTIVE_FEEDBACK_GROUP0_NMOS_MIN_GEOMETRY_FAMILY:
            grouped_reference_entries.append(entry)
            group0_nmos_min_geometry_entries.append(entry)
        if entry.get("family") == ACTIVE_FEEDBACK_GROUP1_NMOS_FAMILY:
            grouped_reference_entries.append(entry)
            group1_nmos_entries.append(entry)
        if entry.get("family") == ACTIVE_FEEDBACK_GROUP2_NMOS_FAMILY:
            grouped_reference_entries.append(entry)
            group2_nmos_entries.append(entry)
        if entry.get("family") == CODE_DEPENDENT_TRANSFER_SHAPING_FAMILY:
            target_family.append(entry)
            code_dependent_transfer_entries.append(entry)
        if entry.get("family") == RESIDUE_INJECTION_FAMILY:
            target_family.append(entry)
            residue_injection_entries.append(entry)
        if entry.get("family") == CODE_DEPENDENT_RESIDUE_REFINEMENT_FAMILY:
            target_family.append(entry)
            code_dependent_residue_entries.append(entry)
        if entry.get("family") == SEGMENTED_RESIDUE_FAMILY:
            target_family.append(entry)
            segmented_residue_entries.append(entry)
        if entry.get("family") == SEGMENTED_BRANCH_REFINEMENT_FAMILY:
            target_family.append(entry)
            segmented_branch_refinement_entries.append(entry)
        if entry.get("family") == SOURCE_DEGENERATED_FEEDBACK_FAMILY:
            target_family.append(entry)
            source_degenerated_feedback_entries.append(entry)
        if entry.get("family") == CHARGE_REDISTRIBUTION_FAMILY:
            target_family.append(entry)
            charge_redistribution_entries.append(entry)
        action = entry.get("action", {})
        if isinstance(action, dict):
            topology = action.get("feedback_reference_topology")
            if isinstance(topology, str) and topology:
                known_reference_topologies.add(topology)
            pmos_width = action.get("feedback_reference_pmos_width")
            nmos_width = action.get("feedback_reference_nmos_width")
            if isinstance(pmos_width, str) and isinstance(nmos_width, str):
                known_reference_width_pairs.add((pmos_width, nmos_width))
            value = entry.get("max_inl_lsb")
            if (entry.get("family") == ACTIVE_FEEDBACK_MOS_REFERENCE_FAMILY
                    and topology == "mos_diode_ratio"
                    and isinstance(value, (int, float)) and not isinstance(value, bool)
                    and math.isfinite(float(value))
                    and (best_mos_reference_entry is None
                         or float(value) < best_mos_reference_entry["max_inl_lsb"])):
                best_mos_reference_entry = {**entry, "max_inl_lsb": float(value)}
        action = entry.get("action", {})
        if (entry.get("family") == ACTIVE_FEEDBACK_SHARED_BIAS_FAMILY
                and isinstance(action, dict)
                and not action.get("feedback_reference_topology")):
            known_reference_topologies.add("passive_resistor_divider")

    if not reason_counts:
        return {"status": "unavailable", "reason": "failure_reasons_missing",
                "recommendation_id": None, "runtime_authorized": False}
    dominant_reason = min(reason_counts, key=lambda reason: (-reason_counts[reason], reason))
    if dominant_reason == "inl_gate" and target_family:
        if charge_redistribution_entries:
            recommendation_id = "active_feedback_charge_redistribution_plateau_escalate_to_mismatch_heldout"
            next_action = (
                "the switched charge-redistribution cohort completed all eight settings over "
                "all codes at TT/SS/FF, but every setting reproduced the 0.7828549 LSB "
                "active-feedback control and none beat the 0.7778267 LSB segmented control; "
                "close static topology search and run mismatch plus held-out-code/workload "
                "validation on the best segmented control before any runtime policy change"
            )
            direction = "charge_redistribution_closed_begin_mismatch_and_heldout_validation"
        elif source_degenerated_feedback_entries:
            recommendation_id = "active_feedback_source_degenerated_plateau_escalate_charge_redistribution"
            next_action = (
                "the source-degenerated local-feedback cohort completed all eight settings over "
                "all codes at TT/SS/FF, but its best 0.9246574 LSB result regressed the "
                "0.7778267 LSB segmented control; close this linearization family, retain the "
                "segmented control, and design a distinct charge-redistribution mechanism "
                "before any mismatch, runtime, or policy promotion"
            )
            direction = "source_degenerated_feedback_rejected_escalate_to_charge_redistribution"
        elif segmented_branch_refinement_entries:
            recommendation_id = "active_feedback_segmented_residue_plateau_escalate_linearization"
            next_action = (
                "the per-decoded-branch segmented refinement reproduced the 0.7778267 LSB "
                "control; close this segmented width/gate family, retain the best control, "
                "and design a distinct feedback-linearization or charge-redistribution "
                "mechanism before further policy or workload promotion"
            )
            direction = "segmented_residue_plateau_escalate_to_distinct_linearization"
        elif segmented_residue_entries:
            recommendation_id = "active_feedback_segmented_residue_code_dependent_refinement"
            next_action = (
                "the two-level segmented residue topology improved the prior control to "
                "0.7778267 LSB; retain its best coarse/fine settings and run a bounded "
                "per-decoded-branch segmented refinement, then require mismatch, held-out "
                "codes/workloads, and the 0.5 LSB gate before any policy promotion"
            )
            direction = "segmented_residue_strict_gain_refine_per_decoded_branch"
        elif code_dependent_residue_entries:
            recommendation_id = "active_feedback_segmented_residue_topology_search"
            next_action = (
                "the 9-setting code-dependent residue refinement reproduced the 0.780264 LSB "
                "control with no local gain; close this width/gate neighborhood and design a "
                "distinct segmented-residue or multi-level injection mechanism, preserving the "
                "best residue control and all-code TT/SS/FF, mismatch, and held-out-code gates"
            )
            direction = "code_dependent_residue_plateau_escalate_to_segmented_residue_topology"
        elif residue_injection_entries:
            recommendation_id = "active_feedback_residue_injection_code_dependent_refinement"
            next_action = (
                "the direct residue-injection topology improved the matched control from "
                "0.78285 to 0.78026 LSB but remains far above 0.5 LSB; retain the best "
                "residue branch as control and run a preregistered code-dependent residue "
                "width/gate refinement around it, with all-code TT/SS/FF, mismatch and "
                "held-out-code evidence before any promotion"
            )
            direction = "residue_injection_strict_gain_refine_code_dependent_residue"
        elif code_dependent_transfer_entries:
            recommendation_id = "active_feedback_distinct_residue_injection_topology_search"
            next_action = (
                "the independently decoded six-branch transfer-shaping cohort completed with "
                "no improvement over the 0.78285 LSB control; do not repeat amplitude or width "
                "shaping unchanged. Design a distinct residue-injection or segmented-correction "
                "topology, preserve the matched active-feedback control, and validate all-code "
                "TT/SS/FF monotonicity, 10mV settling, model coverage, and the 0.5 LSB gate"
            )
            direction = "code_dependent_transfer_shaping_rejected_escalate_to_distinct_residue_topology"
        elif group2_nmos_entries:
            if (group2_sensitivity_analysis
                    and group2_sensitivity_analysis.get("status") == "completed"
                    and group2_sensitivity_analysis.get("width_only_plateau_detected") is True):
                recommendation_id = "active_feedback_code_dependent_transfer_shaping_search"
                next_action = (
                    "width finite differences and the worst-code residuals are now measured at "
                    "TT/SS/FF, with less than 0.001 LSB width-only gain; stop width-only tuning, "
                    "design a distinct code-dependent transfer-shaping correction topology, and "
                    "validate it on held-out codes and PVT corners before any promotion"
                )
                direction = "width_plateau_confirmed_escalate_to_code_dependent_transfer_shaping"
            else:
                recommendation_id = "active_feedback_grouped_reference_saturation_review"
                next_action = (
                    "compare measured per-group finite differences against the worst-code residual "
                    "profile; keep runtime promotion closed while INL exceeds 0.5 LSB, and if the "
                    "best width-only change is below 0.001 LSB, stop width-only search and propose "
                    "a new code-dependent transfer-shaping topology with explicit held-out tests"
                )
                direction = "detect_reference_width_plateau_and_escalate_topology_hypothesis"
        elif group1_nmos_entries:
            recommendation_id = "active_feedback_group2_nmos_search"
            next_action = (
                "using the measured best group-0 and group-1 NMOS references, test group-2 "
                "NMOS widths 1u, 2u, and 2.5u one at a time; retain group-2 PMOS at 4u, "
                "preflight each device at TT/SS/FF, and record every code's output and "
                "reference voltage with exact provenance"
            )
            direction = "transfer_finite_difference_search_to_final_code_group"
        elif group0_nmos_min_geometry_entries:
            recommendation_id = "active_feedback_group1_nmos_search"
            next_action = (
                "using the selected group-0 NMOS reference from the completed local sweep, "
                "test group-1 NMOS widths 1u, 2u, and 2.5u one at a time while retaining "
                "group-0 PMOS at 8u and group-2 reference at its measured control; preflight "
                "each geometry and retain all-code TT/SS/FF output/reference evidence"
            )
            direction = "transfer_finite_difference_search_to_next_code_group"
        elif group0_nmos_lower_range_entries:
            recommendation_id = "active_feedback_group0_nmos_min_geometry_search"
            next_action = (
                "the group-0 NMOS response continues improving through 0.5u; compare the "
                "lowest model-supported 0.4u against the 0.5u replay control and 0.75u "
                "reference, after verifying every geometry at TT/SS/FF; preserve per-code "
                "reference/output evidence and stop below the supported model boundary"
            )
            direction = "approach_supported_group0_nmos_geometry_boundary_with_preflight"
        elif group0_nmos_refinement_entries:
            recommendation_id = "active_feedback_group0_nmos_lower_range_search"
            next_action = (
                "the measured group-0 NMOS response improved from 2.5u through 2u to 1u; "
                "continue that local finite-difference trend with model-preflighted 0.5u and "
                "0.75u candidates against the 1u control, holding group-0 PMOS at 8u and all "
                "other groups fixed; retain complete TT/SS/FF per-code output/reference evidence"
            )
            direction = "follow_measured_group0_nmos_gradient_with_geometry_preflight"
        elif grouped_sensitivity_entries:
            recommendation_id = "active_feedback_grouped_reference_nmos_refinement_search"
            next_action = (
                "refine group-0 NMOS reference width around the measured 2u best: compare "
                "model-preflighted 1u, 2u control, and 2.5u while keeping group-0 PMOS at 8u "
                "and groups 1/2 fixed at their measured settings; preserve all-code TT/SS/FF "
                "reference/output measurements and provenance, and keep promotion closed above 0.5 LSB"
            )
            direction = "refine_group0_nmos_around_measured_best_with_finite_differences"
        elif grouped_reference_entries:
            recommendation_id = "active_feedback_grouped_reference_sensitivity_search"
            next_action = (
                "use the measured group-0 PMOS response (2u worsened INL; 8u improved it) "
                "to run a bounded one-device-at-a-time finite-difference sweep around the "
                "8u setting; first vary group-0 NMOS while holding PMOS fixed, then test "
                "the other code groups with model-preflighted 2u/4u/8u devices; retain every "
                "all-code TT/SS/FF result, measured group reference voltage, and provenance"
            )
            direction = "follow_measured_group_reference_gradient_without_runtime_promotion"
        elif tail_width_entries:
            recommendation_id = "active_feedback_grouped_reference_search"
            next_action = (
                "retain the measured output-response data and 15u OTA input-pair setting; "
                "compare the shared MOS reference against a matched per-code-group diode "
                "reference, then perturb the group-0 PMOS/NMOS reference ratio one device "
                "at a time while holding correction geometry fixed; record per-code reference "
                "and output values at TT/SS/FF and reject any gate or provenance failure"
            )
            direction = "add_code_group_reference_trim_after_shared_reference_plateau"
        elif input_pair_width_entries:
            recommendation_id = "active_feedback_tail_width_search"
            next_action = (
                "hold the measured 15u OTA differential-input pair, best MOS reference, "
                "correction widths, and unit correction gate fractions fixed; compare the "
                "model-supported 80u feedback-tail device against a matched 100u control, "
                "with all-code TT/SS/FF settling, monotonicity, per-corner INL, and exact provenance"
            )
            direction = "probe_shared_feedback_tail_current_after_input_pair_plateau"
        elif gate_drive_entries:
            recommendation_id = "active_feedback_input_pair_width_search"
            next_action = (
                "hold the best measured MOS reference and correction geometry fixed; "
                "run a model-preflighted sweep of active-feedback OTA differential-input "
                "pair widths [10u, 15u, 20u control, 30u, 40u], retaining all-code TT/SS/FF "
                "settling, monotonicity, per-corner INL, and exact model/tool provenance"
            )
            direction = "probe_active_feedback_input_transconductance_after_gate_drive_plateau"
        elif correction_width_entries:
            recommendation_id = "active_feedback_group_gate_drive_search"
            next_action = (
                "hold the best measured MOS reference and matched correction widths fixed; "
                "run a bounded one-group-at-a-time correction_gate_fraction sweep around "
                "[1.0, 1.0, 1.0], measuring every code at TT/SS/FF with exact model/tool "
                "provenance; reject any candidate above 0.5 LSB"
            )
            direction = "probe_active_feedback_group_gate_drive_after_width_plateau"
        elif "mos_diode_ratio" not in known_reference_topologies:
            recommendation_id = "transistor_reference_topology_followup"
            next_action = (
                "replace the passive OTA reference divider with a transistor-level reference, "
                "then rerun all-code TT/SS/FF and mismatch evaluation"
            )
            direction = "change_reference_topology_after_repeated_inl_gate_failures"
        else:
            recommendation_id = "refine_untried_mos_reference_ratio"
            proposed_pair = choose_untried_reference_width_pair(entries)
            if proposed_pair:
                next_action = (
                    f"test PMOS/NMOS reference widths {proposed_pair[0]}/{proposed_pair[1]} "
                    "as the nearest untried ratio to the best observed candidate; retain measured "
                    "per-corner reference voltages, then rerun all-code TT/SS/FF and mismatch evaluation"
                )
            else:
                next_action = "expand the MOS reference width grid only after preserving prior PVT measurements and mismatch checks"
            direction = "refine_device_ratio_from_measured_reference_and_inl"
    elif dominant_reason == "simulator_or_model_blocked":
        recommendation_id = "repair_model_coverage_before_mutating"
        next_action = "repair unsupported simulator/model cases before drawing electrical conclusions"
        direction = "repair_model_coverage"
    elif dominant_reason == "settling_gate":
        recommendation_id = "compensation_bandwidth_followup"
        next_action = "change compensation or bandwidth, then rerun the same all-code PVT settling checks"
        direction = "target_settling_failures"
    elif dominant_reason == "non_monotonic":
        recommendation_id = "ordering_preserving_topology_followup"
        next_action = "preserve branch ordering while changing the correction topology, then rerun all-code PVT checks"
        direction = "target_code_ordering_failures"
    else:
        recommendation_id = "repair_measurement_contract_before_search"
        next_action = "repair missing or invalid candidate measurements before using them to guide mutations"
        direction = "repair_evidence_quality"

    family_values = []
    for entry in target_family:
        value = entry.get("max_inl_lsb")
        if (isinstance(value, (int, float)) and not isinstance(value, bool)
                and math.isfinite(float(value))):
            family_values.append(float(value))
    return {
        "status": "derived",
        "evidence_schema": MUTATION_MEMORY_SCHEMA,
        "evidence_sha256": memory_sha256,
        "entry_count": len(entries),
        "dominant_failure_reason": dominant_reason,
        "failure_reason_counts": reason_counts,
        "direction": direction,
        "recommendation_id": recommendation_id,
        "next_action": next_action,
        "target_family": (ACTIVE_FEEDBACK_GATE_DRIVE_FAMILY
                          if recommendation_id == "active_feedback_input_pair_width_search"
                          else ACTIVE_FEEDBACK_CORRECTION_WIDTH_FAMILY
                          if recommendation_id == "active_feedback_group_gate_drive_search"
                          else ACTIVE_FEEDBACK_INPUT_PAIR_WIDTH_FAMILY
                          if recommendation_id == "active_feedback_tail_width_search"
                          else ACTIVE_FEEDBACK_TAIL_WIDTH_FAMILY
                          if recommendation_id == "active_feedback_grouped_reference_search"
                          else ACTIVE_FEEDBACK_GROUPED_REFERENCE_FAMILY
                          if recommendation_id == "active_feedback_grouped_reference_sensitivity_search"
                          else ACTIVE_FEEDBACK_GROUPED_REFERENCE_SENSITIVITY_FAMILY
                          if recommendation_id == "active_feedback_grouped_reference_nmos_refinement_search"
                          else ACTIVE_FEEDBACK_GROUP0_NMOS_REFINEMENT_FAMILY
                          if recommendation_id == "active_feedback_group0_nmos_lower_range_search"
                          else ACTIVE_FEEDBACK_GROUP0_NMOS_LOWER_RANGE_FAMILY
                          if recommendation_id == "active_feedback_group0_nmos_min_geometry_search"
                          else ACTIVE_FEEDBACK_GROUP0_NMOS_MIN_GEOMETRY_FAMILY
                          if recommendation_id == "active_feedback_group1_nmos_search"
                          else ACTIVE_FEEDBACK_GROUP1_NMOS_FAMILY
                          if recommendation_id == "active_feedback_group2_nmos_search"
                          else ACTIVE_FEEDBACK_GROUP2_NMOS_FAMILY
                          if recommendation_id in {"active_feedback_grouped_reference_saturation_review",
                                                   "active_feedback_code_dependent_transfer_shaping_search"}
                          else ACTIVE_FEEDBACK_MOS_REFERENCE_FAMILY
                          if "mos_diode_ratio" in known_reference_topologies
                          else ACTIVE_FEEDBACK_SHARED_BIAS_FAMILY),
        "target_family_attempts": len(target_family),
        "target_family_best_max_inl_lsb": min(family_values) if family_values else None,
        "proposed_reference_topology": (
            "mos_diode_ratio"
            if recommendation_id == "transistor_reference_topology_followup" else None),
        "known_reference_width_pairs": [list(pair) for pair in sorted(known_reference_width_pairs)],
        "proposed_reference_width_pair": (
            list(choose_untried_reference_width_pair(entries))
            if recommendation_id == "refine_untried_mos_reference_ratio"
            and choose_untried_reference_width_pair(entries) else None),
        "best_mos_reference_width_pair": (
            [best_mos_reference_entry.get("action", {}).get("feedback_reference_pmos_width"),
             best_mos_reference_entry.get("action", {}).get("feedback_reference_nmos_width")]
            if best_mos_reference_entry else None),
        "best_mos_reference_voltage_summary_by_corner": (
            best_mos_reference_entry.get("reference_voltage_summary_by_corner", {})
            if best_mos_reference_entry else {}),
        "known_reference_topologies": sorted(known_reference_topologies),
        "correction_width_search_attempts": len(correction_width_entries),
        "correction_width_search_best_max_inl_lsb": min(
            (float(entry["max_inl_lsb"]) for entry in correction_width_entries
             if isinstance(entry.get("max_inl_lsb"), (int, float))
             and not isinstance(entry.get("max_inl_lsb"), bool)
             and math.isfinite(float(entry["max_inl_lsb"]))),
            default=None),
        "gate_drive_search_attempts": len(gate_drive_entries),
        "gate_drive_search_best_max_inl_lsb": min(
            (float(entry["max_inl_lsb"]) for entry in gate_drive_entries
             if isinstance(entry.get("max_inl_lsb"), (int, float))
             and not isinstance(entry.get("max_inl_lsb"), bool)
             and math.isfinite(float(entry["max_inl_lsb"]))),
            default=None),
        "input_pair_width_search_attempts": len(input_pair_width_entries),
        "input_pair_width_search_best_max_inl_lsb": min(
            (float(entry["max_inl_lsb"]) for entry in input_pair_width_entries
             if isinstance(entry.get("max_inl_lsb"), (int, float))
             and not isinstance(entry.get("max_inl_lsb"), bool)
             and math.isfinite(float(entry["max_inl_lsb"]))),
            default=None),
        "proposed_feedback_input_widths": (
            ["10u", "15u", "20u", "30u", "40u"]
            if recommendation_id == "active_feedback_input_pair_width_search" else None),
        "proposed_feedback_tail_widths": (
            ["80u", "100u"]
            if recommendation_id == "active_feedback_tail_width_search" else None),
        "tail_width_search_attempts": len(tail_width_entries),
        "tail_width_search_best_max_inl_lsb": min(
            (float(entry["max_inl_lsb"]) for entry in tail_width_entries
             if isinstance(entry.get("max_inl_lsb"), (int, float))
             and not isinstance(entry.get("max_inl_lsb"), bool)
             and math.isfinite(float(entry["max_inl_lsb"]))),
            default=None),
        "grouped_reference_search_attempts": len(grouped_reference_entries),
        "grouped_reference_search_best_max_inl_lsb": min(
            (float(entry["max_inl_lsb"]) for entry in grouped_reference_entries
             if isinstance(entry.get("max_inl_lsb"), (int, float))
             and not isinstance(entry.get("max_inl_lsb"), bool)
             and math.isfinite(float(entry["max_inl_lsb"]))),
            default=None),
        "proposed_reference_topology_is_unseen": (
            "mos_diode_ratio" not in known_reference_topologies
        ),
        "runtime_authorized": False,
        "promotion_eligible": False,
        "group2_sensitivity_analysis": {
            "status": group2_sensitivity_analysis.get("status", "missing")
            if group2_sensitivity_analysis else "missing",
            "report_sha256": group2_sensitivity_analysis.get("_verified_report_sha256")
            if group2_sensitivity_analysis else None,
            "source_result_sha256": group2_sensitivity_analysis.get("inputs", {}).get("result_sha256")
            if group2_sensitivity_analysis else None,
            "best_width_only_gain_lsb": group2_sensitivity_analysis.get("best_width_only_gain_lsb")
            if group2_sensitivity_analysis else None,
            "width_only_plateau_detected": group2_sensitivity_analysis.get("width_only_plateau_detected", False)
            if group2_sensitivity_analysis else False,
        },
    }


def main() -> int:
    bridge = json.loads(BRIDGE.read_text())
    cost = json.loads(COST.read_text())
    measurement = json.loads(MEASUREMENT.read_text())
    regulated = json.loads(REGULATED.read_text()) if REGULATED.is_file() else {}
    regulated_load_mutation = json.loads(REGULATED_LOAD_MUTATION.read_text()) if REGULATED_LOAD_MUTATION.is_file() else {}
    regulated_mismatch = json.loads(REGULATED_MISMATCH.read_text()) if REGULATED_MISMATCH.is_file() else {}
    supported_mismatch = json.loads(SUPPORTED_MISMATCH.read_text()) if SUPPORTED_MISMATCH.is_file() else {}
    boundary_reuse = json.loads(BOUNDARY_REUSE.read_text()) if BOUNDARY_REUSE.is_file() else {}
    readiness = json.loads(READINESS.read_text()) if READINESS.is_file() else {}
    differential_policy = json.loads(DIFFERENTIAL_POLICY.read_text()) if DIFFERENTIAL_POLICY.is_file() else {}
    differential_transfer = json.loads(DIFFERENTIAL_TRANSFER.read_text()) if DIFFERENTIAL_TRANSFER.is_file() else {}
    thermometer = json.loads(THERMOMETER.read_text()) if THERMOMETER.is_file() else {}
    source_degenerated = json.loads(SOURCE_DEGENERATED.read_text()) if SOURCE_DEGENERATED.is_file() else {}
    active_feedback = json.loads(ACTIVE_FEEDBACK.read_text()) if ACTIVE_FEEDBACK.is_file() else {}
    active_feedback_provenance = json.loads(ACTIVE_FEEDBACK_PROVENANCE.read_text()) if ACTIVE_FEEDBACK_PROVENANCE.is_file() else {}
    active_feedback_grouped_reference = json.loads(ACTIVE_FEEDBACK_GROUPED_REFERENCE.read_text()) if ACTIVE_FEEDBACK_GROUPED_REFERENCE.is_file() else {}
    active_feedback_grouped_reference_provenance = json.loads(ACTIVE_FEEDBACK_GROUPED_REFERENCE_PROVENANCE.read_text()) if ACTIVE_FEEDBACK_GROUPED_REFERENCE_PROVENANCE.is_file() else {}
    active_feedback_grouped_sensitivity = json.loads(ACTIVE_FEEDBACK_GROUPED_SENSITIVITY.read_text()) if ACTIVE_FEEDBACK_GROUPED_SENSITIVITY.is_file() else {}
    active_feedback_grouped_sensitivity_provenance = json.loads(ACTIVE_FEEDBACK_GROUPED_SENSITIVITY_PROVENANCE.read_text()) if ACTIVE_FEEDBACK_GROUPED_SENSITIVITY_PROVENANCE.is_file() else {}
    active_feedback_group0_nmos_refinement = json.loads(ACTIVE_FEEDBACK_GROUP0_NMOS_REFINEMENT.read_text()) if ACTIVE_FEEDBACK_GROUP0_NMOS_REFINEMENT.is_file() else {}
    active_feedback_group0_nmos_refinement_provenance = json.loads(ACTIVE_FEEDBACK_GROUP0_NMOS_REFINEMENT_PROVENANCE.read_text()) if ACTIVE_FEEDBACK_GROUP0_NMOS_REFINEMENT_PROVENANCE.is_file() else {}
    active_feedback_group0_nmos_lower_range = json.loads(ACTIVE_FEEDBACK_GROUP0_NMOS_LOWER_RANGE.read_text()) if ACTIVE_FEEDBACK_GROUP0_NMOS_LOWER_RANGE.is_file() else {}
    active_feedback_group0_nmos_lower_range_provenance = json.loads(ACTIVE_FEEDBACK_GROUP0_NMOS_LOWER_RANGE_PROVENANCE.read_text()) if ACTIVE_FEEDBACK_GROUP0_NMOS_LOWER_RANGE_PROVENANCE.is_file() else {}
    active_feedback_group0_nmos_min_geometry = json.loads(ACTIVE_FEEDBACK_GROUP0_NMOS_MIN_GEOMETRY.read_text()) if ACTIVE_FEEDBACK_GROUP0_NMOS_MIN_GEOMETRY.is_file() else {}
    active_feedback_group0_nmos_min_geometry_provenance = json.loads(ACTIVE_FEEDBACK_GROUP0_NMOS_MIN_GEOMETRY_PROVENANCE.read_text()) if ACTIVE_FEEDBACK_GROUP0_NMOS_MIN_GEOMETRY_PROVENANCE.is_file() else {}
    active_feedback_group1_nmos = json.loads(ACTIVE_FEEDBACK_GROUP1_NMOS.read_text()) if ACTIVE_FEEDBACK_GROUP1_NMOS.is_file() else {}
    active_feedback_group1_nmos_provenance = json.loads(ACTIVE_FEEDBACK_GROUP1_NMOS_PROVENANCE.read_text()) if ACTIVE_FEEDBACK_GROUP1_NMOS_PROVENANCE.is_file() else {}
    active_feedback_group2_nmos = json.loads(ACTIVE_FEEDBACK_GROUP2_NMOS.read_text()) if ACTIVE_FEEDBACK_GROUP2_NMOS.is_file() else {}
    active_feedback_group2_nmos_provenance = json.loads(ACTIVE_FEEDBACK_GROUP2_NMOS_PROVENANCE.read_text()) if ACTIVE_FEEDBACK_GROUP2_NMOS_PROVENANCE.is_file() else {}
    active_feedback_refinement = json.loads(ACTIVE_FEEDBACK_REFINEMENT.read_text()) if ACTIVE_FEEDBACK_REFINEMENT.is_file() else {}
    active_feedback_refinement_provenance = json.loads(ACTIVE_FEEDBACK_REFINEMENT_PROVENANCE.read_text()) if ACTIVE_FEEDBACK_REFINEMENT_PROVENANCE.is_file() else {}
    active_feedback_width_refinement = json.loads(ACTIVE_FEEDBACK_WIDTH_REFINEMENT.read_text()) if ACTIVE_FEEDBACK_WIDTH_REFINEMENT.is_file() else {}
    active_feedback_finger_refinement = json.loads(ACTIVE_FEEDBACK_FINGER_REFINEMENT.read_text()) if ACTIVE_FEEDBACK_FINGER_REFINEMENT.is_file() else {}
    active_feedback_shared_bias = json.loads(ACTIVE_FEEDBACK_SHARED_BIAS.read_text()) if ACTIVE_FEEDBACK_SHARED_BIAS.is_file() else {}
    active_feedback_shared_bias_provenance = json.loads(ACTIVE_FEEDBACK_SHARED_BIAS_PROVENANCE.read_text()) if ACTIVE_FEEDBACK_SHARED_BIAS_PROVENANCE.is_file() else {}
    active_feedback_mos_reference = json.loads(ACTIVE_FEEDBACK_MOS_REFERENCE.read_text()) if ACTIVE_FEEDBACK_MOS_REFERENCE.is_file() else {}
    active_feedback_mos_reference_provenance = json.loads(ACTIVE_FEEDBACK_MOS_REFERENCE_PROVENANCE.read_text()) if ACTIVE_FEEDBACK_MOS_REFERENCE_PROVENANCE.is_file() else {}
    active_feedback_mos_reference_refinements = []
    for result_path in sorted(ACTIVE_FEEDBACK_MOS_REFERENCE_RESULTS.glob(
            "differential-active-feedback-mos-reference-refinement-*.json")):
        if result_path.name.endswith("-provenance.json"):
            continue
        provenance_path = result_path.with_name(result_path.stem + "-provenance.json")
        result_doc = json.loads(result_path.read_text())
        provenance_doc = json.loads(provenance_path.read_text()) if provenance_path.is_file() else {}
        active_feedback_mos_reference_refinements.append({
            "path": str(result_path.relative_to(ROOT)),
            "status": result_doc.get("status", "missing"),
            "best_max_inl_lsb": result_doc.get("summary", {}).get("best_mos_max_inl_lsb"),
            "provenance_bound": bool(
                provenance_doc.get("result_sha256")
                and provenance_doc["result_sha256"] == hashlib.sha256(result_path.read_bytes()).hexdigest()
            ),
        })
    active_feedback_mos_geometry_stress = json.loads(ACTIVE_FEEDBACK_MOS_GEOMETRY_STRESS.read_text()) if ACTIVE_FEEDBACK_MOS_GEOMETRY_STRESS.is_file() else {}
    active_feedback_mos_geometry_stress_provenance = json.loads(ACTIVE_FEEDBACK_MOS_GEOMETRY_STRESS_PROVENANCE.read_text()) if ACTIVE_FEEDBACK_MOS_GEOMETRY_STRESS_PROVENANCE.is_file() else {}
    physical_policy = json.loads(PHYSICAL_POLICY.read_text()) if PHYSICAL_POLICY.is_file() else {}
    physical_promotion = json.loads(PHYSICAL_PROMOTION.read_text()) if PHYSICAL_PROMOTION.is_file() else {}
    cost_consistency = json.loads(COST_CONSISTENCY.read_text()) if COST_CONSISTENCY.is_file() else {}
    prepared_package = json.loads(PREPARED_PACKAGE.read_text()) if PREPARED_PACKAGE.is_file() else {}
    mutation_memory = json.loads(MUTATION_MEMORY.read_text()) if MUTATION_MEMORY.is_file() else {}
    segmented_mismatch = json.loads(SEGMENTED_MISMATCH.read_text()) if SEGMENTED_MISMATCH.is_file() else {}
    segmented_transfer = json.loads(SEGMENTED_TRANSFER.read_text()) if SEGMENTED_TRANSFER.is_file() else {}
    segmented_cost_rollback = json.loads(SEGMENTED_COST_ROLLBACK.read_text()) if SEGMENTED_COST_ROLLBACK.is_file() else {}
    segmented_policy = json.loads(SEGMENTED_POLICY.read_text()) if SEGMENTED_POLICY.is_file() else {}
    mutation_memory_sha256 = (
        hashlib.sha256(MUTATION_MEMORY.read_bytes()).hexdigest()
        if MUTATION_MEMORY.is_file() else None
    )
    group2_sensitivity_analysis = {}
    group2_analysis_provenance = {}
    group2_sensitivity_provenance_bound = False
    if (ACTIVE_FEEDBACK_GROUP2_SENSITIVITY.is_file()
            and ACTIVE_FEEDBACK_GROUP2_SENSITIVITY_PROVENANCE.is_file()
            and ACTIVE_FEEDBACK_GROUP2_NMOS.is_file()
            and ACTIVE_FEEDBACK_GROUP2_NMOS_PROVENANCE.is_file()):
        group2_sensitivity_analysis = json.loads(ACTIVE_FEEDBACK_GROUP2_SENSITIVITY.read_text())
        group2_analysis_provenance = json.loads(ACTIVE_FEEDBACK_GROUP2_SENSITIVITY_PROVENANCE.read_text())
        bound = (
            group2_analysis_provenance.get("result_sha256")
            == hashlib.sha256(ACTIVE_FEEDBACK_GROUP2_SENSITIVITY.read_bytes()).hexdigest()
            and group2_analysis_provenance.get("source_result_sha256")
            == hashlib.sha256(ACTIVE_FEEDBACK_GROUP2_NMOS.read_bytes()).hexdigest()
            and group2_analysis_provenance.get("source_provenance_sha256")
            == hashlib.sha256(ACTIVE_FEEDBACK_GROUP2_NMOS_PROVENANCE.read_bytes()).hexdigest()
            and group2_sensitivity_analysis.get("inputs", {}).get("result_sha256")
            == group2_analysis_provenance.get("source_result_sha256")
            and group2_sensitivity_analysis.get("inputs", {}).get("source_provenance_sha256")
            == group2_analysis_provenance.get("source_provenance_sha256")
        )
        group2_sensitivity_provenance_bound = bound
        if bound:
            group2_sensitivity_analysis["_verified_report_sha256"] = group2_analysis_provenance["result_sha256"]
        else:
            group2_sensitivity_analysis = {}
    mutation_guidance = derive_mutation_memory_guidance(
        mutation_memory, mutation_memory_sha256, group2_sensitivity_analysis
    )
    if (segmented_mismatch.get("status") == "passed"
            and segmented_transfer.get("status") == "passed"
            and segmented_transfer.get("summary", {}).get("all_fallback_correct") is True
            and segmented_cost_rollback.get("status") == "passed"):
        # Historical mutation memory still records the last closed topology
        # escalation. Once robustness, held-out fallback, and rollback are
        # complete, the authoritative next gate is cost import, not another
        # circuit mutation.
        mutation_guidance = {
            **mutation_guidance,
            "status": "derived",
            "recommendation_id": "segmented_control_cost_import_after_fail_closed_rollback",
            "direction": "close_static_topology_search_begin_physical_cost_import",
            "next_action": "capture synchronized digital and hybrid board runs with common-unit energy, shared workload hash, and identical quality boundaries",
            "promotion_eligible": False,
            "runtime_authorized": False,
        }
    gates = bridge["gates"]
    actions = []
    if (segmented_mismatch.get("status") == "passed"
            and segmented_transfer.get("status") == "passed"
            and segmented_transfer.get("summary", {}).get("all_fallback_correct") is True
            and segmented_cost_rollback.get("status") != "passed"):
        actions.append({"priority": 1, "action_id": "segmented_residue_cost_rollback_validation",
                        "class": "promotion_gate", "objective": "reconcile declared cost and prove reproducible rollback for the robust segmented control",
                        "source_gate": "cost_and_rollback_after_mismatch_and_heldout",
                        "next_action": "run synchronized cost-model consistency and replay the baseline-to-digital-fallback rollback contract using the hash-bound segmented control and held-out transfer artifact",
                        "acceptance": ["same-run cost fields complete", "digital fallback remains correct", "rollback replay is hash-bound", "no analog authorization until strict INL passes"],
                        "promotion": "keep baseline runtime policy and digital fallback active"})
    if (segmented_cost_rollback.get("status") == "passed"
            and segmented_cost_rollback.get("cost", {}).get("status") == "blocked_model_reconciliation"):
        actions.append({"priority": 1, "action_id": "same_run_physical_cost_import",
                        "class": "measurement", "objective": "replace declared segmented-control cost proxies with common-unit synchronized evidence",
                        "source_gate": "runtime_cost_model_consistency",
                        "next_action": "capture synchronized digital and hybrid board runs with shared trace ID, workload hash, quality outputs, and power/thermal timestamps",
                        "acceptance": ["common-unit calibration", "same-run measured energy", "recomputed runtime cost comparison", "digital fallback remains available"],
                        "promotion": "do not claim measured energy or analog runtime improvement until strict import validation passes"})
    regulated_complete = (regulated.get("status") == "passed"
                          and regulated.get("candidate_count", 0) > 0)
    unsupported_geometry = regulated_mismatch.get("summary", {}).get("unsupported_model_geometry_trials", 0)
    supported_mismatch_complete = supported_mismatch.get("status") == "complete_supported_subset"
    active_feedback_summary = active_feedback.get("summary", {})
    if active_feedback_summary and not active_feedback_summary.get("promotion_gate_passed", False):
        refinement_done = bool(active_feedback_refinement.get("summary", {}).get("candidate_count"))
        shared_bias_done = bool(active_feedback_shared_bias.get("summary", {}).get("candidate_count"))
        if shared_bias_done:
            refinement_next = "replace the passive OTA reference divider with a transistor-level reference, then rerun all-code TT/SS/FF and mismatch evaluation"
        elif refinement_done:
            refinement_next = "evaluate the shared diode-connected PMOS tail-bias mirror with a resistor-derived OTA reference across supported bias-resistor settings"
        else:
            refinement_next = "run the 12-point compensation-capacitance and OTA mirror-load sweep over supported model geometry"
        if (mutation_guidance.get("status") == "derived"
                and mutation_guidance.get("recommendation_id") in {
                    "transistor_reference_topology_followup",
                    "refine_untried_mos_reference_ratio",
                    "active_feedback_group_gate_drive_search",
                    "active_feedback_input_pair_width_search",
                    "active_feedback_tail_width_search",
                    "active_feedback_grouped_reference_search",
                    "active_feedback_grouped_reference_sensitivity_search",
                    "active_feedback_grouped_reference_nmos_refinement_search",
                    "active_feedback_group1_nmos_search",
                    "active_feedback_group0_nmos_lower_range_search",
                    "active_feedback_group0_nmos_min_geometry_search",
                    "active_feedback_group2_nmos_search",
                    "active_feedback_grouped_reference_saturation_review",
                    "active_feedback_code_dependent_transfer_shaping_search",
                    "active_feedback_distinct_residue_injection_topology_search",
                    "active_feedback_residue_injection_code_dependent_refinement",
                    "active_feedback_segmented_residue_topology_search",
                    "active_feedback_segmented_residue_code_dependent_refinement",
                    "active_feedback_segmented_residue_plateau_escalate_linearization",
                    "active_feedback_source_degenerated_plateau_escalate_charge_redistribution",
                    "active_feedback_charge_redistribution_plateau_escalate_to_mismatch_heldout",
                }
                and shared_bias_done):
            refinement_next = mutation_guidance["next_action"]
        next_action_id = (
            "current_mode_mismatch_population"
            if mutation_guidance.get("recommendation_id") == "active_feedback_charge_redistribution_plateau_escalate_to_mismatch_heldout"
            else "active_feedback_charge_redistribution_search"
            if mutation_guidance.get("recommendation_id") == "active_feedback_source_degenerated_plateau_escalate_charge_redistribution"
            else "active_feedback_ota_implementation_search"
        )
        actions.append({"priority": 1, "action_id": next_action_id,
                        "class": "circuit_mutation", "objective": "cross the 0.5 LSB converter gate with a physically explicit correction-feedback loop",
                        "source_gate": "differential_active_feedback_promotion",
                        "next_action": refinement_next,
                        "failure_memory_guidance": mutation_guidance,
                        "acceptance": ["all-code TT/SS/FF monotonicity", "10mV settling", "max INL <=0.5 LSB", "hash-bound result and exact model/tool provenance"],
                        "promotion": "no runtime or analog authorization until mismatch, held-out transfer, and cost gates also pass"})
    if not gates["inl_promotion"] and not regulated_complete:
        actions.append({"priority": 1, "action_id": "regulated_cascode_current_mode_search",
                        "class": "circuit_mutation", "objective": "reduce current-mode INL to <=0.5 LSB while preserving binary ordering",
                        "source_gate": "inl_promotion", "next_action": "run bounded regulated-cascode bias/topology sweep over TT/SS/FF",
                        "acceptance": ["all codes monotonic", "all codes settle within 10mV", "maximum INL <=0.5 LSB"],
                        "promotion": "retain digital fallback until all acceptance checks pass"})
    if not gates["mismatch_population"]:
        if unsupported_geometry and not supported_mismatch_complete:
            actions.append({"priority": 1, "action_id": "regulated_cascode_model_coverage_repair",
                            "class": "model_compatibility", "objective": "make declared geometry stress points executable without changing nominal model semantics",
                            "source_gate": "unsupported_model_geometry_trials", "next_action": "extend or select a compatible model-card fixture for the 105um stress points and rerun only those trials",
                            "acceptance": ["model provenance retained", "no unsupported geometry silently treated as electrical failure", "fresh TT/SS/FF rerun"],
                            "promotion": "no analog authorization from repaired model coverage alone"})
        if not supported_mismatch_complete:
            actions.append({"priority": 2 if unsupported_geometry else (1 if regulated_complete else 2), "action_id": "current_mode_mismatch_population",
                        "class": "robustness_evaluation", "objective": "establish controlled mismatch evidence for any improved topology",
                        "source_gate": "mismatch_population",
                        "next_action": "evaluate fresh geometry/parameter stress seeds for the best regulated-cascode candidate"
                        if regulated_complete else "evaluate fresh geometry/parameter stress seeds after topology candidate selection",
                        "acceptance": ["fresh seeds", "per-trial outcome retained", "fallback on every failure"],
                        "promotion": "no analog authorization from nominal/PVT-only evidence"})
    if measurement["promotion"] != "ready":
        actions.append({"priority": 3, "action_id": "same_run_physical_cost_import",
                        "class": "measurement", "objective": "replace relative cost coefficients with synchronized evidence",
                        "source_gate": measurement["promotion"], "next_action": "capture digital and hybrid board runs with shared trace ID and power/thermal timestamps",
                        "acceptance": measurement["missing_same_run_measurements"],
                        "promotion": "do not claim measured energy until strict import validator accepts both runtime and power artifacts"})
    if cost["summary"]["current_break_even_points"] == 0 and boundary_reuse.get("status") != "passed":
        actions.append({"priority": 4, "action_id": "boundary_reuse_cost_experiment",
                        "class": "compiler_architecture_mutation", "objective": "reduce converter-boundary and SRAM movement overhead without changing task quality",
                        "source_gate": "cost_model_break_even", "next_action": "evaluate shared-converter/tile-reuse schedules and report boundary count explicitly",
                        "acceptance": ["same task metric", "same digital baseline", "modeled cost below baseline before physical promotion"],
                        "promotion": "coverage-only improvements remain ineligible"})
    if "strict_runtime_analog_improvement" in readiness.get("summary", {}).get("blockers", []):
        actions.append({"priority": 4, "action_id": "strict_runtime_analog_improvement",
                        "class": "promotion_gate", "objective": "produce a reproducible held-out runtime analog improvement",
                        "source_gate": "strict_runtime_analog_improvement",
                        "next_action": "run a new converter/topology or workload candidate through the full reliability, cost, and held-out policy gates",
                        "acceptance": ["converter gate passes", "held-out safety and analog coverage do not regress", "strict runtime modeled-cost improvement", "reproducible replay"],
                        "promotion": "retain baseline runtime policy and digital fallback until all acceptance checks pass"})
    actions.sort(key=lambda item: item["priority"])
    result = {
        "schema_version": "recursive_next_action_queue.v1",
        "inputs": {"current_mode_policy_bridge": str(BRIDGE.relative_to(ROOT)),
                   "cost_model_break_even": str(COST.relative_to(ROOT)),
                   "physical_cost_calibration": str(MEASUREMENT.relative_to(ROOT)),
                   "regulated_cascode_search": str(REGULATED.relative_to(ROOT)),
                   "regulated_cascode_load_mutation": str(REGULATED_LOAD_MUTATION.relative_to(ROOT)),
                   "regulated_cascode_mismatch": str(REGULATED_MISMATCH.relative_to(ROOT)),
                   "regulated_cascode_supported_mismatch": str(SUPPORTED_MISMATCH.relative_to(ROOT)),
                   "boundary_reuse_experiment": str(BOUNDARY_REUSE.relative_to(ROOT)),
                   "end_to_end_readiness_audit": str(READINESS.relative_to(ROOT)),
                   "differential_correction_policy": str(DIFFERENTIAL_POLICY.relative_to(ROOT)),
                   "differential_correction_transfer": str(DIFFERENTIAL_TRANSFER.relative_to(ROOT)),
                   "differential_thermometer_search": str(THERMOMETER.relative_to(ROOT)),
                   "differential_source_degenerated_search": str(SOURCE_DEGENERATED.relative_to(ROOT)),
                   "differential_active_feedback_search": str(ACTIVE_FEEDBACK.relative_to(ROOT)),
                   "differential_active_feedback_provenance": str(ACTIVE_FEEDBACK_PROVENANCE.relative_to(ROOT)),
                   "differential_active_feedback_grouped_reference_search": str(ACTIVE_FEEDBACK_GROUPED_REFERENCE.relative_to(ROOT)),
                   "differential_active_feedback_grouped_reference_provenance": str(ACTIVE_FEEDBACK_GROUPED_REFERENCE_PROVENANCE.relative_to(ROOT)),
                   "differential_active_feedback_grouped_sensitivity_search": str(ACTIVE_FEEDBACK_GROUPED_SENSITIVITY.relative_to(ROOT)),
                   "differential_active_feedback_grouped_sensitivity_provenance": str(ACTIVE_FEEDBACK_GROUPED_SENSITIVITY_PROVENANCE.relative_to(ROOT)),
                   "differential_active_feedback_group0_nmos_refinement": str(ACTIVE_FEEDBACK_GROUP0_NMOS_REFINEMENT.relative_to(ROOT)),
                   "differential_active_feedback_group0_nmos_refinement_provenance": str(ACTIVE_FEEDBACK_GROUP0_NMOS_REFINEMENT_PROVENANCE.relative_to(ROOT)),
                   "differential_active_feedback_group0_nmos_lower_range": str(ACTIVE_FEEDBACK_GROUP0_NMOS_LOWER_RANGE.relative_to(ROOT)),
                   "differential_active_feedback_group0_nmos_lower_range_provenance": str(ACTIVE_FEEDBACK_GROUP0_NMOS_LOWER_RANGE_PROVENANCE.relative_to(ROOT)),
                   "differential_active_feedback_group0_nmos_min_geometry": str(ACTIVE_FEEDBACK_GROUP0_NMOS_MIN_GEOMETRY.relative_to(ROOT)),
                   "differential_active_feedback_group0_nmos_min_geometry_provenance": str(ACTIVE_FEEDBACK_GROUP0_NMOS_MIN_GEOMETRY_PROVENANCE.relative_to(ROOT)),
                   "differential_active_feedback_group1_nmos_search": str(ACTIVE_FEEDBACK_GROUP1_NMOS.relative_to(ROOT)),
                   "differential_active_feedback_group1_nmos_provenance": str(ACTIVE_FEEDBACK_GROUP1_NMOS_PROVENANCE.relative_to(ROOT)),
                   "differential_active_feedback_group2_nmos_search": str(ACTIVE_FEEDBACK_GROUP2_NMOS.relative_to(ROOT)),
                   "differential_active_feedback_group2_nmos_provenance": str(ACTIVE_FEEDBACK_GROUP2_NMOS_PROVENANCE.relative_to(ROOT)),
                   "differential_active_feedback_refinement_search": str(ACTIVE_FEEDBACK_REFINEMENT.relative_to(ROOT)),
                   "differential_active_feedback_refinement_provenance": str(ACTIVE_FEEDBACK_REFINEMENT_PROVENANCE.relative_to(ROOT)),
                   "differential_feedback_correction_width_refinement": str(ACTIVE_FEEDBACK_WIDTH_REFINEMENT.relative_to(ROOT)),
                   "differential_feedback_finger_refinement": str(ACTIVE_FEEDBACK_FINGER_REFINEMENT.relative_to(ROOT)),
                   "differential_active_feedback_shared_bias_search": str(ACTIVE_FEEDBACK_SHARED_BIAS.relative_to(ROOT)),
                   "differential_active_feedback_shared_bias_provenance": str(ACTIVE_FEEDBACK_SHARED_BIAS_PROVENANCE.relative_to(ROOT)),
                   "differential_active_feedback_mos_reference_search": str(ACTIVE_FEEDBACK_MOS_REFERENCE.relative_to(ROOT)),
                   "differential_active_feedback_mos_reference_provenance": str(ACTIVE_FEEDBACK_MOS_REFERENCE_PROVENANCE.relative_to(ROOT)),
                   "differential_active_feedback_mos_reference_refinements": [
                       item["path"] for item in active_feedback_mos_reference_refinements],
                   "differential_active_feedback_mos_reference_geometry_stress": str(ACTIVE_FEEDBACK_MOS_GEOMETRY_STRESS.relative_to(ROOT)),
                   "differential_active_feedback_mos_reference_geometry_stress_provenance": str(ACTIVE_FEEDBACK_MOS_GEOMETRY_STRESS_PROVENANCE.relative_to(ROOT)),
                   "physical_rsi_policy_learning": str(PHYSICAL_POLICY.relative_to(ROOT)),
                   "physical_rsi_promotion_evaluation": str(PHYSICAL_PROMOTION.relative_to(ROOT)),
                   "runtime_cost_model_consistency": str(COST_CONSISTENCY.relative_to(ROOT)),
                   "segmented_residue_mismatch_stress": str(SEGMENTED_MISMATCH.relative_to(ROOT)),
                   "segmented_residue_workload_transfer": str(SEGMENTED_TRANSFER.relative_to(ROOT)),
                   "segmented_residue_cost_rollback": str(SEGMENTED_COST_ROLLBACK.relative_to(ROOT)),
                   "segmented_residue_policy_handoff": str(SEGMENTED_POLICY.relative_to(ROOT)),
                   "prepared_board_package": str(PREPARED_PACKAGE.relative_to(ROOT)),
                   "converter_mutation_failure_memory": str(MUTATION_MEMORY.relative_to(ROOT))},
        "actions": actions,
        "selected_next_action": actions[0] if actions else None,
        "summary": {"actions": len(actions), "selected": actions[0]["action_id"] if actions else None,
                     "analog_authorized": bool(bridge["decision"]["analog_authorized"]),
                     "differential_correction_status": differential_policy.get("selection", {}).get("status"),
                     "differential_correction_fallback_transfer_safe": differential_transfer.get("summary", {}).get("all_fallback_correct", False),
                     "differential_thermometer_status": "approved" if thermometer.get("summary", {}).get("promotion_gate_passed") else "rejected",
                     "differential_thermometer_best_max_inl_lsb": thermometer.get("summary", {}).get("best_max_inl_lsb"),
                     "differential_source_degenerated_status": "approved" if source_degenerated.get("summary", {}).get("promotion_gate_passed") else "rejected",
                     "differential_source_degenerated_best_max_inl_lsb": source_degenerated.get("summary", {}).get("best_max_inl_lsb"),
                     "differential_active_feedback_status": active_feedback.get("status", "missing"),
                     "differential_active_feedback_candidate_count": active_feedback_summary.get("candidate_count", 0),
                     "differential_active_feedback_passing_count": active_feedback_summary.get("passing_candidate_count", 0),
                     "differential_active_feedback_best_max_inl_lsb": active_feedback_summary.get("best_max_inl_lsb"),
                     "differential_active_feedback_provenance_bound": bool(active_feedback_provenance.get("experiment_result", {}).get("sha256")),
                     "differential_active_feedback_grouped_reference_status": active_feedback_grouped_reference.get("status", "missing"),
                     "differential_active_feedback_grouped_reference_best_max_inl_lsb": active_feedback_grouped_reference.get("summary", {}).get("best_max_inl_lsb"),
                     "differential_active_feedback_grouped_reference_provenance_bound": active_feedback_grouped_reference_provenance.get("result_sha256") == hashlib.sha256(ACTIVE_FEEDBACK_GROUPED_REFERENCE.read_bytes()).hexdigest() if ACTIVE_FEEDBACK_GROUPED_REFERENCE.is_file() and active_feedback_grouped_reference_provenance else False,
                     "differential_active_feedback_grouped_sensitivity_status": active_feedback_grouped_sensitivity.get("status", "missing"),
                     "differential_active_feedback_grouped_sensitivity_best_max_inl_lsb": active_feedback_grouped_sensitivity.get("summary", {}).get("best_max_inl_lsb"),
                     "differential_active_feedback_grouped_sensitivity_provenance_bound": active_feedback_grouped_sensitivity_provenance.get("result_sha256") == hashlib.sha256(ACTIVE_FEEDBACK_GROUPED_SENSITIVITY.read_bytes()).hexdigest() if ACTIVE_FEEDBACK_GROUPED_SENSITIVITY.is_file() and active_feedback_grouped_sensitivity_provenance else False,
                     "differential_active_feedback_group0_nmos_refinement_status": active_feedback_group0_nmos_refinement.get("status", "missing"),
                     "differential_active_feedback_group0_nmos_refinement_best_max_inl_lsb": active_feedback_group0_nmos_refinement.get("summary", {}).get("best_max_inl_lsb"),
                     "differential_active_feedback_group0_nmos_refinement_provenance_bound": active_feedback_group0_nmos_refinement_provenance.get("result_sha256") == hashlib.sha256(ACTIVE_FEEDBACK_GROUP0_NMOS_REFINEMENT.read_bytes()).hexdigest() if ACTIVE_FEEDBACK_GROUP0_NMOS_REFINEMENT.is_file() and active_feedback_group0_nmos_refinement_provenance else False,
                     "differential_active_feedback_group0_nmos_lower_range_status": active_feedback_group0_nmos_lower_range.get("status", "missing"),
                     "differential_active_feedback_group0_nmos_lower_range_best_max_inl_lsb": active_feedback_group0_nmos_lower_range.get("summary", {}).get("best_max_inl_lsb"),
                     "differential_active_feedback_group0_nmos_lower_range_provenance_bound": active_feedback_group0_nmos_lower_range_provenance.get("result_sha256") == hashlib.sha256(ACTIVE_FEEDBACK_GROUP0_NMOS_LOWER_RANGE.read_bytes()).hexdigest() if ACTIVE_FEEDBACK_GROUP0_NMOS_LOWER_RANGE.is_file() and active_feedback_group0_nmos_lower_range_provenance else False,
                     "differential_active_feedback_group0_nmos_min_geometry_status": active_feedback_group0_nmos_min_geometry.get("status", "missing"),
                     "differential_active_feedback_group0_nmos_min_geometry_best_max_inl_lsb": active_feedback_group0_nmos_min_geometry.get("summary", {}).get("best_max_inl_lsb"),
                     "differential_active_feedback_group0_nmos_min_geometry_provenance_bound": active_feedback_group0_nmos_min_geometry_provenance.get("result_sha256") == hashlib.sha256(ACTIVE_FEEDBACK_GROUP0_NMOS_MIN_GEOMETRY.read_bytes()).hexdigest() if ACTIVE_FEEDBACK_GROUP0_NMOS_MIN_GEOMETRY.is_file() and active_feedback_group0_nmos_min_geometry_provenance else False,
                     "differential_active_feedback_group1_nmos_status": active_feedback_group1_nmos.get("status", "missing"),
                     "differential_active_feedback_group1_nmos_best_max_inl_lsb": active_feedback_group1_nmos.get("summary", {}).get("best_max_inl_lsb"),
                     "differential_active_feedback_group1_nmos_provenance_bound": active_feedback_group1_nmos_provenance.get("result_sha256") == hashlib.sha256(ACTIVE_FEEDBACK_GROUP1_NMOS.read_bytes()).hexdigest() if ACTIVE_FEEDBACK_GROUP1_NMOS.is_file() and active_feedback_group1_nmos_provenance else False,
                     "differential_active_feedback_group2_nmos_status": active_feedback_group2_nmos.get("status", "missing"),
                     "differential_active_feedback_group2_nmos_best_max_inl_lsb": active_feedback_group2_nmos.get("summary", {}).get("best_max_inl_lsb"),
                     "differential_active_feedback_group2_nmos_provenance_bound": active_feedback_group2_nmos_provenance.get("result_sha256") == hashlib.sha256(ACTIVE_FEEDBACK_GROUP2_NMOS.read_bytes()).hexdigest() if ACTIVE_FEEDBACK_GROUP2_NMOS.is_file() and active_feedback_group2_nmos_provenance else False,
                     "differential_active_feedback_refinement_status": active_feedback_refinement.get("status", "missing"),
                     "differential_active_feedback_refinement_best_max_inl_lsb": active_feedback_refinement.get("summary", {}).get("best_max_inl_lsb"),
                     "differential_active_feedback_refinement_provenance_bound": bool(active_feedback_refinement_provenance.get("experiment_result", {}).get("sha256")),
                     "differential_feedback_correction_width_refinement_status": active_feedback_width_refinement.get("status", "missing"),
                     "differential_feedback_correction_width_refinement_candidate_count": active_feedback_width_refinement.get("summary", {}).get("candidate_count", 0),
                     "differential_feedback_correction_width_refinement_best_max_inl_lsb": active_feedback_width_refinement.get("summary", {}).get("best_max_inl_lsb"),
                     "differential_feedback_correction_width_refinement_promotion_gate_passed": active_feedback_width_refinement.get("summary", {}).get("promotion_gate_passed", False),
                     "differential_feedback_finger_refinement_status": active_feedback_finger_refinement.get("status", "missing"),
                     "differential_feedback_finger_refinement_candidate_count": active_feedback_finger_refinement.get("summary", {}).get("candidate_count", 0),
                     "differential_feedback_finger_refinement_best_max_inl_lsb": active_feedback_finger_refinement.get("summary", {}).get("best_max_inl_lsb"),
                     "differential_feedback_finger_refinement_promotion_gate_passed": active_feedback_finger_refinement.get("summary", {}).get("promotion_gate_passed", False),
                     "differential_active_feedback_shared_bias_status": active_feedback_shared_bias.get("status", "missing"),
                     "differential_active_feedback_shared_bias_best_max_inl_lsb": active_feedback_shared_bias.get("summary", {}).get("best_max_inl_lsb"),
                     "differential_active_feedback_shared_bias_provenance_bound": bool(active_feedback_shared_bias_provenance.get("experiment_result", {}).get("sha256")),
                     "differential_active_feedback_mos_reference_status": active_feedback_mos_reference.get("status", "missing"),
                     "differential_active_feedback_mos_reference_best_max_inl_lsb": active_feedback_mos_reference.get("summary", {}).get("best_mos_max_inl_lsb"),
                     "differential_active_feedback_mos_reference_provenance_bound": active_feedback_mos_reference_provenance.get("result_sha256") == hashlib.sha256(ACTIVE_FEEDBACK_MOS_REFERENCE.read_bytes()).hexdigest() if ACTIVE_FEEDBACK_MOS_REFERENCE.is_file() and active_feedback_mos_reference_provenance else False,
                     "differential_active_feedback_mos_reference_refinement_count": len(active_feedback_mos_reference_refinements),
                     "differential_active_feedback_mos_reference_refinement_best_max_inl_lsb": min(
                         (item["best_max_inl_lsb"] for item in active_feedback_mos_reference_refinements
                          if isinstance(item["best_max_inl_lsb"], (int, float))), default=None),
                     "differential_active_feedback_mos_reference_refinements_all_provenance_bound": bool(
                         active_feedback_mos_reference_refinements
                         and all(item["provenance_bound"] for item in active_feedback_mos_reference_refinements)),
                     "differential_active_feedback_mos_reference_geometry_stress_status": active_feedback_mos_geometry_stress.get("status", "missing"),
                     "differential_active_feedback_mos_reference_geometry_stress_worst_inl_lsb": active_feedback_mos_geometry_stress.get("summary", {}).get("worst_passing_inl_lsb"),
                     "differential_active_feedback_mos_reference_geometry_stress_provenance_bound": active_feedback_mos_geometry_stress_provenance.get("result_sha256") == hashlib.sha256(ACTIVE_FEEDBACK_MOS_GEOMETRY_STRESS.read_bytes()).hexdigest() if ACTIVE_FEEDBACK_MOS_GEOMETRY_STRESS.is_file() and active_feedback_mos_geometry_stress_provenance else False,
                     "physical_rsi_policy_learning_status": physical_policy.get("status", "missing"),
                     "physical_rsi_promotion_status": physical_promotion.get("promotion", {}).get("status", "missing"),
                     "runtime_cost_model_consistency_status": cost_consistency.get("promotion", {}).get("status", "missing"),
                     "segmented_policy_handoff_status": segmented_policy.get("status", "missing"),
                     "segmented_policy_analog_runtime_authorized": segmented_policy.get("selection", {}).get("analog_runtime_authorized", False),
                     "regulated_cascode_load_mutation_status": regulated_load_mutation.get("status", "missing"),
                     "regulated_cascode_load_mutation_best_max_inl_lsb": regulated_load_mutation.get("summary", {}).get("best_max_inl_lsb"),
                     "regulated_cascode_load_mutation_strict_improvement": regulated_load_mutation.get("summary", {}).get("strict_improvement_over_prior", False),
                     "prepared_board_package_integrity": prepared_package.get("package_integrity", False),
                     "converter_mutation_memory_entries": mutation_memory.get("summary", {}).get("entry_count", 0),
                     "converter_mutation_memory_rejected": mutation_memory.get("summary", {}).get("rejected_entry_count", 0),
                     "mutation_guidance_status": mutation_guidance.get("status", "unavailable"),
                     "mutation_guidance_id": mutation_guidance.get("recommendation_id"),
                     "mutation_dominant_failure_reason": mutation_guidance.get("dominant_failure_reason"),
                     "group2_sensitivity_analysis_status": mutation_guidance.get("group2_sensitivity_analysis", {}).get("status", "missing"),
                     "group2_sensitivity_analysis_provenance_bound": group2_sensitivity_provenance_bound,
                     "group2_width_only_gain_lsb": mutation_guidance.get("group2_sensitivity_analysis", {}).get("best_width_only_gain_lsb"),
                     "board_execution": prepared_package.get("board_execution", "missing")},
        "status": "ready" if actions else "complete",
        "claim_boundary": "Action queue is derived from current simulator/evidence gates; it is not a circuit improvement, hardware measurement, or production policy.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
