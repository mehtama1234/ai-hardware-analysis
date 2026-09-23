from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def test_recursive_queue_binds_latest_width_refinement_artifact() -> None:
    queue = json.loads((HERE / "next-recursive-action-queue.json").read_text())
    result_path = ROOT / queue["inputs"]["differential_feedback_correction_width_refinement"]
    result = json.loads(result_path.read_text())
    summary = queue["summary"]

    assert result["status"] == "passed"
    assert summary["differential_feedback_correction_width_refinement_status"] == "passed"
    assert summary["differential_feedback_correction_width_refinement_candidate_count"] == result["summary"]["candidate_count"]
    assert summary["differential_feedback_correction_width_refinement_best_max_inl_lsb"] == result["summary"]["best_max_inl_lsb"]
    assert summary["differential_feedback_correction_width_refinement_promotion_gate_passed"] is False
    assert queue["selected_next_action"]["action_id"] == "same_run_physical_cost_import"
    assert queue["summary"]["analog_authorized"] is False


def test_recursive_queue_records_finger_refinement_gain_without_promotion() -> None:
    queue = json.loads((HERE / "next-recursive-action-queue.json").read_text())
    result_path = ROOT / queue["inputs"]["differential_feedback_finger_refinement"]
    result = json.loads(result_path.read_text())
    summary = queue["summary"]

    assert result["summary"]["candidate_count"] == 9
    assert result["summary"]["best_max_inl_lsb"] == 0.7394457067411795
    assert result["summary"]["strict_improvement_over_prior"] is True
    assert result["summary"]["promotion_gate_passed"] is False
    assert summary["differential_feedback_finger_refinement_best_max_inl_lsb"] == result["summary"]["best_max_inl_lsb"]
    assert summary["differential_feedback_finger_refinement_promotion_gate_passed"] is False


def test_width_refinement_source_is_currently_hash_bound_in_memory() -> None:
    queue = json.loads((HERE / "next-recursive-action-queue.json").read_text())
    result_path = ROOT / queue["inputs"]["differential_feedback_correction_width_refinement"]
    memory = json.loads((HERE / "converter-mutation-failure-memory.json").read_text())
    source = next(item for item in memory["source_records"]
                  if item["path"] == str(result_path.relative_to(ROOT)))
    assert hashlib.sha256(result_path.read_bytes()).hexdigest() == source["sha256"]
