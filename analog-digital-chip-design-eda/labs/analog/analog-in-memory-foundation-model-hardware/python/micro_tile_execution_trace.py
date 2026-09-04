#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass

from tile_readout_boundary import ReadoutCase, readout


PLACE_DIGITAL = "digital"
PLACE_ANALOG = "analog"
PLACE_HYBRID = "hybrid"


@dataclass(frozen=True)
class OperationCase:
    name: str
    op_class: str
    resident_weights: bool
    estimated_state_error: int
    state_error_budget: int
    attention_flip_rate: int
    attention_flip_budget: int
    token_flip_rate: int
    token_flip_budget: int
    calibration_age: int
    weak_tiles: int
    readout_case: ReadoutCase


def operation_partition(case: OperationCase) -> tuple[str, str]:
    digital_only = {"embedding", "mask", "softmax", "residual", "norm", "kv_cache", "sampling"}
    fixed_weight = {"qkv", "out_proj", "mlp"}
    hybrid_candidate = {"attention_score", "value_mix", "logits", "adapter"}

    if case.op_class in digital_only:
        return PLACE_DIGITAL, "digital_rule"
    if case.op_class in fixed_weight | hybrid_candidate and not case.resident_weights:
        return PLACE_DIGITAL, "missing_weights"
    if case.estimated_state_error > case.state_error_budget:
        return PLACE_DIGITAL, "state_error_high"
    if case.calibration_age >= 1024 and case.weak_tiles >= 4:
        return PLACE_DIGITAL, "stale_weak_tiles"
    if case.op_class in {"attention_score", "value_mix"} and case.attention_flip_rate > case.attention_flip_budget:
        return PLACE_DIGITAL, "attention_selection_high"
    if case.op_class == "logits" and case.token_flip_rate > case.token_flip_budget:
        return PLACE_DIGITAL, "token_choice_high"
    if case.op_class in fixed_weight:
        return PLACE_ANALOG, "fixed_weight_analog"
    if case.op_class in hybrid_candidate:
        return PLACE_HYBRID, "hybrid_needs_evidence"
    return PLACE_DIGITAL, "unknown_op"


def execute(case: OperationCase) -> dict[str, int | str]:
    placement, placement_reason = operation_partition(case)
    if placement == PLACE_DIGITAL:
        return {
            "placement": placement,
            "placement_reason": placement_reason,
            "readout_reason": "not_sampled",
            "corrected": 0,
            "final_path": "digital",
            "final_reason": placement_reason,
        }
    if placement == PLACE_HYBRID:
        return {
            "placement": placement,
            "placement_reason": placement_reason,
            "readout_reason": "not_sampled",
            "corrected": 0,
            "final_path": "hybrid_review",
            "final_reason": "hybrid_review",
        }

    measured = readout(case.readout_case)
    if measured["valid"] == 1:
        return {
            "placement": placement,
            "placement_reason": placement_reason,
            "readout_reason": measured["reason"],
            "corrected": measured["corrected"],
            "final_path": "analog_accepted",
            "final_reason": "readout_valid",
        }
    return {
        "placement": placement,
        "placement_reason": placement_reason,
        "readout_reason": measured["reason"],
        "corrected": measured["corrected"],
        "final_path": "digital",
        "final_reason": f"readout_{measured['reason']}",
    }


def main() -> None:
    base_readout = ReadoutCase("base", True, 160, 128, 64, 0, 3, 20, 32)
    cases = [
        OperationCase("qkv_analog_accepted", "qkv", True, 60, 100, 5, 15, 5, 15, 32, 1, base_readout),
        OperationCase("qkv_residual_fallback", "qkv", True, 60, 100, 5, 15, 5, 15, 32, 1, ReadoutCase("bad_residual", True, 160, 128, 64, 0, 40, 20, 32)),
        OperationCase("qkv_disabled_tile_fallback", "qkv", True, 60, 100, 5, 15, 5, 15, 32, 1, ReadoutCase("disabled", False, 160, 128, 64, 0, 3, 20, 32)),
        OperationCase("attention_hybrid_review", "attention_score", True, 60, 100, 5, 15, 5, 15, 32, 1, base_readout),
        OperationCase("softmax_digital_rule", "softmax", True, 60, 100, 5, 15, 5, 15, 32, 1, base_readout),
        OperationCase("missing_weight_fallback", "qkv", False, 60, 100, 5, 15, 5, 15, 32, 1, base_readout),
    ]

    print("micro_tile_execution_trace")
    print("case,op,placement,placement_reason,readout_reason,corrected,final_path,final_reason")
    for case in cases:
        result = execute(case)
        print(
            f"{case.name},{case.op_class},{result['placement']},{result['placement_reason']},"
            f"{result['readout_reason']},{result['corrected']},{result['final_path']},{result['final_reason']}"
        )

    print()
    print("interpretation")
    print("Placement is permission to try analog compute.")
    print("Acceptance is a later decision made from the measured and corrected tile output.")


if __name__ == "__main__":
    main()
