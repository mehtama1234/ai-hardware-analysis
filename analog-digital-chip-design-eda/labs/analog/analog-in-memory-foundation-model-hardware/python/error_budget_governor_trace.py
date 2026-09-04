#!/usr/bin/env python3
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


MEASUREMENTS_DIR = Path(__file__).resolve().parents[1] / "measurements"
RTL_DIR = Path(__file__).resolve().parents[3] / "digital" / "aimc-control-plane-rtl"
CSV_OUT = MEASUREMENTS_DIR / "error-budget-governor-trace.csv"
MD_OUT = MEASUREMENTS_DIR / "error-budget-governor-trace.md"
VH_OUT = RTL_DIR / "generated_error_budget_governor_cases.vh"

DECISION_DIGITAL = 0
DECISION_ANALOG = 1

ACTION_SERVE = 0
ACTION_RECALIBRATE = 1
ACTION_DISABLE = 2

REASONS = {
    "no_sample": 0,
    "not_analog_candidate": 1,
    "residual_too_high": 2,
    "calibration_too_old": 3,
    "sensitive_path_needs_digital": 4,
    "state_error_budget_spent": 5,
    "analog_within_budget": 6,
    "analog_but_recalibrate_soon": 7,
}


@dataclass(frozen=True)
class Row:
    token: int
    sample_valid: int
    analog_candidate: int
    residual_q8: int
    drift_age: int
    sensitivity_q8: int
    cumulative_error_q8: int
    decision: int
    action: int
    reason: str
    reason_code: int
    next_cumulative_error_q8: int


def govern(
    sample_valid: int,
    analog_candidate: int,
    residual_q8: int,
    drift_age: int,
    sensitivity_q8: int,
    cumulative_error_q8: int,
) -> tuple[int, int, str, int]:
    if not sample_valid:
        return DECISION_DIGITAL, ACTION_SERVE, "no_sample", cumulative_error_q8
    if not analog_candidate:
        return DECISION_DIGITAL, ACTION_SERVE, "not_analog_candidate", cumulative_error_q8
    if residual_q8 > 46:
        return DECISION_DIGITAL, ACTION_DISABLE, "residual_too_high", cumulative_error_q8
    if drift_age > 11:
        return DECISION_DIGITAL, ACTION_RECALIBRATE, "calibration_too_old", cumulative_error_q8
    if sensitivity_q8 >= 192 and residual_q8 > 24:
        return DECISION_DIGITAL, ACTION_SERVE, "sensitive_path_needs_digital", cumulative_error_q8

    risk_q8 = residual_q8 + (drift_age * 3) + (sensitivity_q8 >> 4)
    next_error = min(255, cumulative_error_q8 + (risk_q8 >> 2))
    if next_error > 96:
        return DECISION_DIGITAL, ACTION_RECALIBRATE, "state_error_budget_spent", cumulative_error_q8
    if drift_age >= 9 or next_error >= 80:
        return DECISION_ANALOG, ACTION_RECALIBRATE, "analog_but_recalibrate_soon", next_error
    return DECISION_ANALOG, ACTION_SERVE, "analog_within_budget", next_error


def simulate(tokens: int = 32) -> list[Row]:
    rows: list[Row] = []
    cumulative_error_q8 = 0
    residual_pattern = [8, 11, 17, 22, 31, 15, 48, 19, 26, 33, 12, 9, 21, 37, 28, 16]
    sensitivity_pattern = [80, 96, 128, 176, 208, 112, 144, 224]
    drift_age = 2
    for token in range(tokens):
        sample_valid = 0 if token in {0, 21} else 1
        analog_candidate = 0 if token in {5, 13, 29} else 1
        residual_q8 = residual_pattern[token % len(residual_pattern)]
        sensitivity_q8 = sensitivity_pattern[token % len(sensitivity_pattern)]
        if token in {10, 11, 12}:
            drift_age = 12 + (token - 10)
        elif token in {18, 19, 20}:
            cumulative_error_q8 = 82 + (token - 18) * 7
        decision, action, reason, next_error = govern(
            sample_valid,
            analog_candidate,
            residual_q8,
            drift_age,
            sensitivity_q8,
            cumulative_error_q8,
        )
        rows.append(
            Row(
                token=token,
                sample_valid=sample_valid,
                analog_candidate=analog_candidate,
                residual_q8=residual_q8,
                drift_age=drift_age,
                sensitivity_q8=sensitivity_q8,
                cumulative_error_q8=cumulative_error_q8,
                decision=decision,
                action=action,
                reason=reason,
                reason_code=REASONS[reason],
                next_cumulative_error_q8=next_error,
            )
        )
        if action == ACTION_RECALIBRATE:
            drift_age = 0
            cumulative_error_q8 = min(next_error, 24)
        elif decision == DECISION_ANALOG:
            drift_age += 1
            cumulative_error_q8 = next_error
        else:
            drift_age += 1
    return rows


def write_csv(rows: list[Row]) -> None:
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(Row.__dataclass_fields__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


def write_markdown(rows: list[Row]) -> None:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row.reason] = counts.get(row.reason, 0) + 1
    lines = [
        "# Error-Budget Governor Trace",
        "",
        "This trace turns analog measurement into a serving decision. The object is not the analog multiply by itself. The object is the right to spend another analog error inside a model state that already carries previous error.",
        "",
        "```text",
        "decision 0 = digital fallback",
        "decision 1 = analog service",
        "action 0 = keep serving",
        "action 1 = recalibrate before more analog service",
        "action 2 = disable until probe or repair",
        "```",
        "",
        "## Reason Counts",
        "",
    ]
    for reason in sorted(counts):
        lines.append(f"- {reason}: {counts[reason]}")
    lines.extend(
        [
            "",
            "## Trace",
            "",
            "| token | valid | candidate | residual | drift age | sensitivity | cumulative | decision | action | reason | next cumulative |",
            "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row.token} | {row.sample_valid} | {row.analog_candidate} | {row.residual_q8} | "
            f"{row.drift_age} | {row.sensitivity_q8} | {row.cumulative_error_q8} | "
            f"{row.decision} | {row.action} | {row.reason} | {row.next_cumulative_error_q8} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The governor refuses analog work for four different reasons. A high residual says this tile did not reproduce the local projection. Old calibration says the measurement may be stale even before this token is served. A sensitive path says a modest numeric error can move the model decision. A spent state budget says previous accepted analog work has already used the room that was available.",
            "",
            "The important design move is that digital fallback is not failure. It is the mechanism that keeps analog compute bounded. Analog service is useful only when the control plane can say why this particular use is still inside the budget.",
            "",
        ]
    )
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def render_case(row: Row) -> str:
    return (
        f'        run_case("token_{row.token:02d}_{row.reason}", '
        f"1'b{row.sample_valid}, 1'b{row.analog_candidate}, "
        f"8'd{row.residual_q8}, 4'd{row.drift_age}, 8'd{row.sensitivity_q8}, 8'd{row.cumulative_error_q8}, "
        f"2'd{row.decision}, 2'd{row.action}, 4'd{row.reason_code}, 8'd{row.next_cumulative_error_q8});"
    )


def write_verilog(rows: list[Row]) -> None:
    lines = [
        "// Generated by labs/analog/analog-in-memory-foundation-model-hardware/python/error_budget_governor_trace.py",
        "// Do not edit by hand; edit the runtime generator instead.",
    ]
    lines.extend(render_case(row) for row in rows)
    VH_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    rows = simulate()
    write_csv(rows)
    write_markdown(rows)
    write_verilog(rows)
    print("error_budget_governor_trace")
    print(f"tokens,{len(rows)}")
    print(f"csv,{CSV_OUT}")
    print(f"markdown,{MD_OUT}")
    print(f"verilog,{VH_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
