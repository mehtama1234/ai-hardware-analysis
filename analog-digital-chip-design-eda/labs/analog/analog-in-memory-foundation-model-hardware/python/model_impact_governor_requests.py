#!/usr/bin/env python3
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from error_budget_governor_trace import govern


MEASUREMENTS_DIR = Path(__file__).resolve().parents[1] / "measurements"
RTL_DIR = Path(__file__).resolve().parents[3] / "digital" / "aimc-control-plane-rtl"
IMPACT_CSV = MEASUREMENTS_DIR / "measured-tile-transformer-impact.csv"
BACKEND_PLACEMENT_CSV = MEASUREMENTS_DIR / "backend-hardware-placement-governor-input.csv"
CSV_OUT = MEASUREMENTS_DIR / "model-impact-governor-requests.csv"
MD_OUT = MEASUREMENTS_DIR / "model-impact-governor-requests.md"
VH_OUT = RTL_DIR / "generated_model_impact_governor_cases.vh"


@dataclass(frozen=True)
class Row:
    policy: str
    analog_candidate: int
    model_residual_q8: int
    attention_flip_q8: int
    token_flip_q8: int
    sensitivity_q8: int
    cumulative_error_q8: int
    governor_decision: int
    governor_action: int
    governor_reason: str
    next_cumulative_error_q8: int
    model_decision: str
    model_reason: str
    interpretation: str


def q8(value: float, scale: float = 255.0) -> int:
    return max(0, min(255, round(value * scale)))


def load_impact_rows() -> list[dict[str, str]]:
    if not IMPACT_CSV.exists():
        from measured_tile_transformer_impact import main as generate_impact

        generate_impact()
    with IMPACT_CSV.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"no measured transformer-impact rows in {IMPACT_CSV}")
    return rows


def load_backend_placement_rows() -> list[dict[str, str]]:
    if not BACKEND_PLACEMENT_CSV.exists():
        return []
    with BACKEND_PLACEMENT_CSV.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def sensitivity_from_model(row: dict[str, str]) -> int:
    attention_flip = float(row["attention_top_flip_rate"])
    token_flip = float(row["token_flip_rate"])
    logits_are_analog = row["logits"] == "analog"
    scores_are_analog = row["attention_scores"] == "analog"
    base = 96
    if attention_flip >= 0.15 or scores_are_analog:
        base = 208
    if token_flip >= 0.18 or logits_are_analog:
        base = 224
    return base


def cumulative_from_model(row: dict[str, str]) -> int:
    state = float(row["state_error"])
    logit = float(row["logit_error"])
    return q8(max(state, logit), 128.0)


def explain(row: dict[str, str], governor_reason: str) -> str:
    if row["model_decision"] == "digital_reference":
        return "reference path; no analog service is requested"
    if governor_reason == "analog_within_budget":
        return "measured tile damage remains small enough for this fixed-projection use"
    if governor_reason == "sensitive_path_needs_digital":
        return "model-level sensitivity is high enough that a moderate residual should not be spent"
    if governor_reason == "state_error_budget_spent":
        return "the local residual may be moderate, but accumulated model-state error leaves no budget"
    if governor_reason == "residual_too_high":
        return "the measured model residual is too large for analog service"
    return "the governor refuses or repairs before allowing more analog service"


def residual_from_model(row: dict[str, str]) -> int:
    state_q8 = q8(float(row["state_error"]), 128.0)
    attention_flip_q8 = q8(float(row["attention_top_flip_rate"]))
    token_flip_q8 = q8(float(row["token_flip_rate"]))
    if row["reason"] in {"attention_selection_too_sensitive", "token_choice_too_sensitive"}:
        return max(state_q8, min(40, attention_flip_q8), min(40, token_flip_q8))
    return state_q8


def row_from_backend_placement(source: dict[str, str]) -> Row:
    analog_candidate = int(source.get("analog_candidate") or 0)
    residual_q8 = int(float(source.get("residual_q8") or 0))
    sensitivity_q8 = int(float(source.get("sensitivity_q8") or 0))
    cumulative_q8 = residual_q8 if analog_candidate else 0
    decision, action, reason, next_error = govern(
        sample_valid=1,
        analog_candidate=analog_candidate,
        residual_q8=residual_q8,
        drift_age=4,
        sensitivity_q8=sensitivity_q8,
        cumulative_error_q8=cumulative_q8,
    )
    model_decision = "analog_path" if source.get("allow_analog") == "1" else "digital_fallback"
    if not analog_candidate:
        model_decision = "digital_reference"
    operator = source.get("operator_id") or "backend_operator"
    return Row(
        policy=f"backend_{operator}",
        analog_candidate=analog_candidate,
        model_residual_q8=residual_q8,
        attention_flip_q8=0,
        token_flip_q8=0,
        sensitivity_q8=sensitivity_q8,
        cumulative_error_q8=cumulative_q8,
        governor_decision=decision,
        governor_action=action,
        governor_reason=reason,
        next_cumulative_error_q8=next_error,
        model_decision=model_decision,
        model_reason=source.get("model_sensitivity_class") or source.get("fallback_action") or "backend_graph_placement",
        interpretation=(
            f"backend graph operator {operator} enters the hardware lab as "
            f"{source.get('placement')} with {source.get('model_sensitivity_class')} sensitivity"
        ),
    )


def convert() -> list[Row]:
    rows: list[Row] = []
    for source in load_impact_rows():
        analog_candidate = 0 if source["policy"] == "all_digital_reference" else 1
        residual_q8 = residual_from_model(source)
        sensitivity_q8 = sensitivity_from_model(source)
        cumulative_q8 = cumulative_from_model(source)
        decision, action, reason, next_error = govern(
            sample_valid=1,
            analog_candidate=analog_candidate,
            residual_q8=residual_q8,
            drift_age=4,
            sensitivity_q8=sensitivity_q8,
            cumulative_error_q8=cumulative_q8,
        )
        enriched_source = {**source, "model_decision": source["decision"]}
        rows.append(
            Row(
                policy=source["policy"],
                analog_candidate=analog_candidate,
                model_residual_q8=residual_q8,
                attention_flip_q8=q8(float(source["attention_top_flip_rate"])),
                token_flip_q8=q8(float(source["token_flip_rate"])),
                sensitivity_q8=sensitivity_q8,
                cumulative_error_q8=cumulative_q8,
                governor_decision=decision,
                governor_action=action,
                governor_reason=reason,
                next_cumulative_error_q8=next_error,
                model_decision=source["decision"],
                model_reason=source["reason"],
                interpretation=explain(enriched_source, reason),
            )
        )
    rows.extend(row_from_backend_placement(source) for source in load_backend_placement_rows())
    return rows


def write_csv(rows: list[Row]) -> None:
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(Row.__dataclass_fields__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


def write_markdown(rows: list[Row]) -> None:
    lines = [
        "# Model Impact Governor Requests",
        "",
        "This report translates the measured transformer-impact experiment into the compact evidence fields that the digital governor can consume. It is the bridge between model behavior and hardware control.",
        "",
        "The object is one proposed analog service request. The request is no longer described only by circuit residual. It also carries whether attention selection or token choice became sensitive in the measured transformer experiment.",
        "",
        "## Request Table",
        "",
        "| policy | candidate | residual q8 | attention flip q8 | token flip q8 | sensitivity q8 | cumulative q8 | governor decision | action | governor reason | next q8 | model decision | interpretation |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row.policy} | {row.analog_candidate} | {row.model_residual_q8} | "
            f"{row.attention_flip_q8} | {row.token_flip_q8} | {row.sensitivity_q8} | "
            f"{row.cumulative_error_q8} | {row.governor_decision} | {row.governor_action} | "
            f"{row.governor_reason} | {row.next_cumulative_error_q8} | {row.model_decision} | "
            f"{row.interpretation} |"
        )
    lines.extend(
        [
            "",
            "## First-Principles Reading",
            "",
            "A circuit residual says how far the tile output moved from the ideal dot product. A model-impact row says what that movement did after attention, residual addition, MLP, logits, and token choice. The governor needs both ideas compressed into hardware-sized fields.",
            "",
            "`model_residual_q8` is the state movement. `attention_flip_q8` and `token_flip_q8` record whether the error crossed a selection boundary. `sensitivity_q8` is raised when the operation touches attention scores or logits, because those are ranking decisions rather than ordinary vector values.",
            "",
            "The fixed-projection policy remains analog because its state error is modest and the sensitive decisions stay digital. The stressed, attention-score, and logits policies are refused or routed to repair because the same measured tile residual has reached a part of the transformer where small movement changes a choice.",
            "",
            "When `backend-hardware-placement-governor-input.csv` exists, backend-derived ONNX placement rows are appended to this same request table. That connects the restored workbench model graph to the hardware-lab governor input instead of leaving the lab with only fixed local transformer policies.",
            "",
            "This is the hardware lesson. The digital governor cannot see a transformer. It sees small fields. Those fields must be chosen so they preserve the model-level reason for accepting or refusing analog work.",
            "",
        ]
    )
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def render_case(row: Row) -> str:
    return (
        f'        run_case("model_{row.policy}", '
        f"1'b1, 1'b{row.analog_candidate}, "
        f"8'd{row.model_residual_q8}, 4'd4, 8'd{row.sensitivity_q8}, 8'd{row.cumulative_error_q8}, "
        f"2'd{row.governor_decision}, 2'd{row.governor_action}, "
        f"4'd{reason_code(row.governor_reason)}, 8'd{row.next_cumulative_error_q8});"
    )


def reason_code(reason: str) -> int:
    codes = {
        "no_sample": 0,
        "not_analog_candidate": 1,
        "residual_too_high": 2,
        "calibration_too_old": 3,
        "sensitive_path_needs_digital": 4,
        "state_error_budget_spent": 5,
        "analog_within_budget": 6,
        "analog_but_recalibrate_soon": 7,
    }
    return codes[reason]


def write_verilog(rows: list[Row]) -> None:
    lines = [
        "// Generated by labs/analog/analog-in-memory-foundation-model-hardware/python/model_impact_governor_requests.py",
        "// Do not edit by hand; edit the model-impact generator instead.",
    ]
    lines.extend(render_case(row) for row in rows)
    VH_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    rows = convert()
    write_csv(rows)
    write_markdown(rows)
    write_verilog(rows)
    print("model_impact_governor_requests")
    print(f"policies,{len(rows)}")
    print(f"csv,{CSV_OUT}")
    print(f"markdown,{MD_OUT}")
    print(f"verilog,{VH_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
