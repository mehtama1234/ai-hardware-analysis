#!/usr/bin/env python3
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


MEASUREMENTS_DIR = Path(__file__).resolve().parents[1] / "measurements"
RTL_DIR = Path(__file__).resolve().parents[3] / "digital" / "aimc-control-plane-rtl"
CSV_OUT = MEASUREMENTS_DIR / "integrated-scheduler-governor-runtime.csv"
MD_OUT = MEASUREMENTS_DIR / "integrated-scheduler-governor-runtime.md"
VH_OUT = RTL_DIR / "generated_integrated_scheduler_governor_cases.vh"
ANALOG_EVIDENCE_CSV = MEASUREMENTS_DIR / "analog-tile-error-evidence.csv"
ANALOG_STATE_CSV = MEASUREMENTS_DIR / "analog-tile-state-trace.csv"
OPERATING_POINT_CSV = MEASUREMENTS_DIR / "tile-operating-point.csv"

TILE_SERVE = 0
TILE_RECALIBRATE = 1
TILE_PROBE = 3

DECISION_DIGITAL = 0
DECISION_ANALOG = 1
DECISION_RECALIBRATE = 2
DECISION_PROBE = 3

FINAL_REASON = {
    "no_sample": 0,
    "not_analog_candidate": 1,
    "scheduler_digital": 2,
    "scheduler_recalibrate": 3,
    "scheduler_probe": 4,
    "governor_residual_too_high": 5,
    "governor_calibration_too_old": 6,
    "governor_sensitive_path_needs_digital": 7,
    "governor_state_error_budget_spent": 8,
    "analog_requested_tile": 9,
    "analog_spare_tile": 10,
    "analog_recalibrate_soon": 11,
}


@dataclass(frozen=True)
class Row:
    token: int
    evidence_scenario: str
    sample_valid: int
    analog_candidate: int
    requested_tile: int
    maintenance_budget: int
    tile_actions: str
    tile_busy: str
    residual_q8: int
    drift_age: int
    sensitivity_q8: int
    cumulative_error_q8: int
    scheduler_decision: int
    governor_decision: int
    governor_action: int
    final_decision: int
    selected_tile: int
    final_reason: str
    final_reason_code: int
    next_cumulative_error_q8: int


def load_analog_evidence() -> list[dict[str, str]]:
    if not ANALOG_STATE_CSV.exists():
        from analog_tile_state_trace import main as generate_state

        generate_state()
    with ANALOG_STATE_CSV.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"no analog state rows found in {ANALOG_STATE_CSV}")
    required = {"event", "residual_q8", "drift_age", "sensitivity_q8"}
    for row in rows:
        missing = required - set(row)
        if missing:
            raise ValueError(f"analog state row missing {sorted(missing)}")
    return rows


def load_operating_point() -> dict[str, str]:
    if not OPERATING_POINT_CSV.exists():
        from tile_operating_point import main as generate_operating_point

        generate_operating_point()
    with OPERATING_POINT_CSV.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"no operating-point row found in {OPERATING_POINT_CSV}")
    required = {
        "name",
        "adc_bits",
        "dac_bits",
        "row_drop_case_ohm",
        "spice_row_drop_loss_pct",
        "converter_relative_error",
        "converter_energy_relative",
        "latency_comparisons",
        "signed_crossbar_worst_error",
        "evidence_residual_q8",
        "evidence_sensitivity_q8",
        "evidence_drift_age",
        "governor_assumption",
    }
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"operating-point row missing {sorted(missing)}")
    return rows[0]


def tile_action(actions: str, index: int) -> int:
    return int(actions[index])


def tile_is_busy(busy: str, index: int) -> bool:
    return busy[index] == "1"


def first_tile(actions: str, busy: str, action: int) -> int | None:
    for index, raw in enumerate(actions):
        if int(raw) == action and not tile_is_busy(busy, index):
            return index
    return None


def schedule(sample_valid: int, analog_candidate: int, requested_tile: int, maintenance_budget: int, actions: str, busy: str) -> tuple[int, int, int]:
    requested = requested_tile % 4
    if not sample_valid:
        return DECISION_DIGITAL, requested, 0
    if not analog_candidate:
        return DECISION_DIGITAL, requested, 1
    if not tile_is_busy(busy, requested) and tile_action(actions, requested) == TILE_SERVE:
        return DECISION_ANALOG, requested, 2
    spare = first_tile(actions, busy, TILE_SERVE)
    if spare is not None:
        return DECISION_ANALOG, spare, 3
    if maintenance_budget == 0:
        return DECISION_DIGITAL, requested, 6
    recalibrate = first_tile(actions, busy, TILE_RECALIBRATE)
    if recalibrate is not None:
        return DECISION_RECALIBRATE, recalibrate, 4
    probe = first_tile(actions, busy, TILE_PROBE)
    if probe is not None:
        return DECISION_PROBE, probe, 5
    return DECISION_DIGITAL, requested, 7


def govern(sample_valid: int, analog_candidate: int, residual_q8: int, drift_age: int, sensitivity_q8: int, cumulative_error_q8: int) -> tuple[int, int, int, int]:
    if not sample_valid:
        return DECISION_DIGITAL, 0, 0, cumulative_error_q8
    if not analog_candidate:
        return DECISION_DIGITAL, 0, 1, cumulative_error_q8
    if residual_q8 > 46:
        return DECISION_DIGITAL, 2, 2, cumulative_error_q8
    if drift_age > 11:
        return DECISION_DIGITAL, 1, 3, cumulative_error_q8
    if sensitivity_q8 >= 192 and residual_q8 > 24:
        return DECISION_DIGITAL, 0, 4, cumulative_error_q8
    risk_q8 = residual_q8 + (drift_age * 3) + (sensitivity_q8 >> 4)
    next_error = min(255, cumulative_error_q8 + (risk_q8 >> 2))
    if next_error > 96:
        return DECISION_DIGITAL, 1, 5, cumulative_error_q8
    if drift_age >= 9 or next_error >= 80:
        return DECISION_ANALOG, 1, 7, next_error
    return DECISION_ANALOG, 0, 6, next_error


def integrate(scheduler_decision: int, scheduler_reason: int, governor_decision: int, governor_action: int, governor_reason: int) -> tuple[int, str]:
    if scheduler_reason == 0 or governor_reason == 0:
        return DECISION_DIGITAL, "no_sample"
    if scheduler_reason == 1 or governor_reason == 1:
        return DECISION_DIGITAL, "not_analog_candidate"
    if scheduler_decision == DECISION_RECALIBRATE:
        return DECISION_RECALIBRATE, "scheduler_recalibrate"
    if scheduler_decision == DECISION_PROBE:
        return DECISION_PROBE, "scheduler_probe"
    if scheduler_decision == DECISION_DIGITAL:
        return DECISION_DIGITAL, "scheduler_digital"
    if governor_decision == DECISION_DIGITAL:
        if governor_reason == 2:
            return DECISION_DIGITAL, "governor_residual_too_high"
        if governor_reason == 3:
            return DECISION_RECALIBRATE, "governor_calibration_too_old"
        if governor_reason == 4:
            return DECISION_DIGITAL, "governor_sensitive_path_needs_digital"
        if governor_reason == 5:
            return DECISION_RECALIBRATE, "governor_state_error_budget_spent"
        return DECISION_DIGITAL, "scheduler_digital"
    if governor_action == 1:
        return DECISION_ANALOG, "analog_recalibrate_soon"
    if scheduler_reason == 3:
        return DECISION_ANALOG, "analog_spare_tile"
    return DECISION_ANALOG, "analog_requested_tile"


def simulate(tokens: int = 36) -> list[Row]:
    action_pattern = ["0003", "0013", "0213", "0203", "0202", "1202"]
    busy_pattern = ["0000", "0100", "0010", "1100", "1110", "1111"]
    analog_evidence = load_analog_evidence()
    rows: list[Row] = []
    for token in range(tokens):
        evidence = analog_evidence[token % len(analog_evidence)]
        sample_valid = 0 if token in {0, 27} else 1
        analog_candidate = 1
        if token in {6, 14, 31}:
            analog_candidate = 0
        requested_tile = token % 4
        maintenance_budget = 0 if token in {11, 23} else 1
        actions = action_pattern[(token // 5) % len(action_pattern)]
        busy = busy_pattern[token % len(busy_pattern)]
        residual_q8 = int(evidence["residual_q8"])
        drift_age = int(evidence["drift_age"])
        sensitivity_q8 = int(evidence["sensitivity_q8"])
        cumulative = int(evidence["cumulative_error_q8"])
        scheduler_decision, selected, scheduler_reason = schedule(sample_valid, analog_candidate, requested_tile, maintenance_budget, actions, busy)
        governor_decision, governor_action, governor_reason, next_error = govern(sample_valid, analog_candidate, residual_q8, drift_age, sensitivity_q8, cumulative)
        final_decision, final_reason = integrate(scheduler_decision, scheduler_reason, governor_decision, governor_action, governor_reason)
        rows.append(
            Row(
                token=token,
                evidence_scenario=evidence["event"],
                sample_valid=sample_valid,
                analog_candidate=analog_candidate,
                requested_tile=requested_tile,
                maintenance_budget=maintenance_budget,
                tile_actions=actions,
                tile_busy=busy,
                residual_q8=residual_q8,
                drift_age=drift_age,
                sensitivity_q8=sensitivity_q8,
                cumulative_error_q8=cumulative,
                scheduler_decision=scheduler_decision,
                governor_decision=governor_decision,
                governor_action=governor_action,
                final_decision=final_decision,
                selected_tile=selected,
                final_reason=final_reason,
                final_reason_code=FINAL_REASON[final_reason],
                next_cumulative_error_q8=next_error,
            )
        )
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
        counts[row.final_reason] = counts.get(row.final_reason, 0) + 1
    operating_point = load_operating_point()
    lines = [
        "# Integrated Scheduler And Governor Runtime",
        "",
        "This trace joins two different decisions. The scheduler asks which tile action is available. The governor asks whether another analog error should be spent at all.",
        "",
        "## Operating Point Assumed By This Trace",
        "",
        "| name | ADC | DAC | row case ohm | row loss % | converter error | converter energy x | SAR comparisons | signed-crossbar error | residual q8 | sensitivity q8 | drift age | governor assumption |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        f"| {operating_point['name']} | {operating_point['adc_bits']} | {operating_point['dac_bits']} | "
        f"{float(operating_point['row_drop_case_ohm']):.0f} | {float(operating_point['spice_row_drop_loss_pct']):.2f} | "
        f"{float(operating_point['converter_relative_error']):.4f} | {float(operating_point['converter_energy_relative']):.2f} | "
        f"{operating_point['latency_comparisons']} | {float(operating_point['signed_crossbar_worst_error']):.3e} | "
        f"{operating_point['evidence_residual_q8']} | {operating_point['evidence_sensitivity_q8']} | "
        f"{operating_point['evidence_drift_age']} | {operating_point['governor_assumption']} |",
        "",
        "## Final Reason Counts",
        "",
    ]
    for reason in sorted(counts):
        lines.append(f"- {reason}: {counts[reason]}")
    lines.extend(
        [
            "",
            "## Trace",
            "",
            "| token | evidence | actions | busy | residual | drift | sensitivity | cumulative | scheduler | governor | final | selected | reason | next |",
            "| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row.token} | {row.evidence_scenario} | {row.tile_actions} | {row.tile_busy} | {row.residual_q8} | {row.drift_age} | "
            f"{row.sensitivity_q8} | {row.cumulative_error_q8} | {row.scheduler_decision} | "
            f"{row.governor_decision} | {row.final_decision} | {row.selected_tile} | "
            f"{row.final_reason} | {row.next_cumulative_error_q8} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The combined policy prevents two common mistakes. A healthy available tile is not enough, because the governor can still refuse the analog error spend. A strict governor is not enough, because maintenance and spare-tile decisions still need tile-state scheduling. Analog service is allowed only when both conditions are true: a tile can serve, and the next analog error remains inside the model-state budget.",
            "",
            f"The governor evidence in this trace is loaded from `{ANALOG_STATE_CSV.name}`. The operating point is loaded from `{OPERATING_POINT_CSV.name}`. Together they state the full claim: signed weights are represented by differential conductance, the 100 ohm row-wire case loses measured current, ADC/DAC conversion has a chosen cost/error boundary, and each token still needs a runtime decision before analog output can become model state.",
            "",
        ]
    )
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def render_case(row: Row) -> str:
    actions = [int(value) for value in row.tile_actions]
    busy_literal = row.tile_busy[::-1]
    return (
        f'        run_case("token_{row.token:02d}_{row.final_reason}", '
        f"1'b{row.sample_valid}, 1'b{row.analog_candidate}, 8'd{row.requested_tile}, "
        f"2'd{actions[0]}, 2'd{actions[1]}, 2'd{actions[2]}, 2'd{actions[3]}, "
        f"4'b{busy_literal}, 2'd{row.maintenance_budget}, "
        f"8'd{row.residual_q8}, 4'd{row.drift_age}, 8'd{row.sensitivity_q8}, 8'd{row.cumulative_error_q8}, "
        f"2'd{row.final_decision}, 2'd{row.selected_tile}, 4'd{row.final_reason_code}, 8'd{row.next_cumulative_error_q8});"
    )


def write_verilog(rows: list[Row]) -> None:
    lines = [
        "// Generated by labs/analog/analog-in-memory-foundation-model-hardware/python/integrated_scheduler_governor_runtime.py",
        "// Do not edit by hand; edit the runtime generator instead.",
    ]
    lines.extend(render_case(row) for row in rows)
    VH_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    rows = simulate()
    write_csv(rows)
    write_markdown(rows)
    write_verilog(rows)
    print("integrated_scheduler_governor_runtime")
    print(f"tokens,{len(rows)}")
    print(f"csv,{CSV_OUT}")
    print(f"markdown,{MD_OUT}")
    print(f"verilog,{VH_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
