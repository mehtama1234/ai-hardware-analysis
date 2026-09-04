#!/usr/bin/env python3
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


MEASUREMENTS_DIR = Path(__file__).resolve().parents[1] / "measurements"
RTL_DIR = Path(__file__).resolve().parents[3] / "digital" / "aimc-control-plane-rtl"
CSV_OUT = MEASUREMENTS_DIR / "multi-tile-scheduler-runtime.csv"
MD_OUT = MEASUREMENTS_DIR / "multi-tile-scheduler-runtime.md"
VH_OUT = RTL_DIR / "generated_tile_scheduler_cases.vh"

TILE_SERVE = 0
TILE_RECALIBRATE = 1
TILE_DISABLE = 2
TILE_PROBE = 3

DECISION_DIGITAL = 0
DECISION_ANALOG = 1
DECISION_RECALIBRATE = 2
DECISION_PROBE = 3

REASON_CODE = {
    "no_sample": 0,
    "analog_not_allowed": 1,
    "requested_tile_serves": 2,
    "spare_tile_serves": 3,
    "recalibrate_before_probe": 4,
    "probe_disabled_tile": 5,
    "no_maintenance_budget": 6,
    "all_tiles_unusable_or_busy": 7,
}


@dataclass
class Tile:
    tile_id: int
    action: int = TILE_SERVE
    residual_failures: int = 0
    stale_failures: int = 0
    calibration_age: int = 0
    busy_until: int = 0


@dataclass(frozen=True)
class RuntimeRow:
    token: int
    requested_tile: int
    analog_candidate: int
    maintenance_budget: int
    tile_actions_before: str
    tile_busy: str
    decision: int
    selected_tile: int
    reason: str
    reason_code: int
    event: str
    tile_actions_after: str


def action_string(tiles: list[Tile]) -> str:
    return "".join(str(tile.action) for tile in tiles)


def busy_string(tiles: list[Tile], token: int) -> str:
    return "".join("1" if is_busy(tile, token) else "0" for tile in tiles)


def is_busy(tile: Tile, token: int) -> bool:
    scheduled_busy = {
        18: {0, 1},
        19: {0, 1, 2},
        23: {0, 1, 2, 3},
    }
    return tile.busy_until > token or tile.tile_id in scheduled_busy.get(token, set())


def first_available(tiles: list[Tile], token: int, action: int) -> int | None:
    for index, tile in enumerate(tiles):
        if not is_busy(tile, token) and tile.action == action:
            return index
    return None


def schedule(tiles: list[Tile], token: int, analog_candidate: bool, requested_tile: int, maintenance_budget: int) -> tuple[int, int, str]:
    requested = requested_tile % len(tiles)
    if not analog_candidate:
        return DECISION_DIGITAL, requested, "analog_not_allowed"
    if not is_busy(tiles[requested], token) and tiles[requested].action == TILE_SERVE:
        return DECISION_ANALOG, requested, "requested_tile_serves"

    spare = first_available(tiles, token, TILE_SERVE)
    if spare is not None:
        return DECISION_ANALOG, spare, "spare_tile_serves"

    if maintenance_budget == 0:
        return DECISION_DIGITAL, requested, "no_maintenance_budget"

    recalibrate = first_available(tiles, token, TILE_RECALIBRATE)
    if recalibrate is not None:
        return DECISION_RECALIBRATE, recalibrate, "recalibrate_before_probe"

    probe = first_available(tiles, token, TILE_PROBE)
    if probe is not None:
        return DECISION_PROBE, probe, "probe_disabled_tile"

    return DECISION_DIGITAL, requested, "all_tiles_unusable_or_busy"


def analog_event(token: int, tile: Tile) -> str:
    if tile.tile_id == 1 and token in {5, 17}:
        return "residual_high"
    if tile.tile_id == 2 and token in {8, 18}:
        return "calibration_stale"
    if tile.calibration_age >= 12:
        return "calibration_stale"
    return "accepted"


def apply_decision(tiles: list[Tile], token: int, decision: int, selected: int) -> str:
    tile = tiles[selected]
    if decision == DECISION_ANALOG:
        event = analog_event(token, tile)
        if event == "accepted":
            tile.calibration_age += 1
            return "analog_accepted"
        if event == "residual_high":
            tile.residual_failures += 1
            tile.calibration_age += 1
            if tile.residual_failures >= 2:
                tile.action = TILE_DISABLE
                return "residual_fallback_disable"
            return "residual_fallback_observe"
        if event == "calibration_stale":
            tile.stale_failures += 1
            tile.action = TILE_RECALIBRATE
            return "stale_fallback_recalibrate"

    if decision == DECISION_RECALIBRATE:
        tile.calibration_age = 0
        tile.stale_failures = 0
        tile.action = TILE_SERVE
        tile.busy_until = token + 1
        return "calibration_done"

    if decision == DECISION_PROBE:
        if tile.residual_failures >= 2 and token < 20:
            tile.action = TILE_DISABLE
            tile.busy_until = token + 1
            return "probe_failed"
        tile.residual_failures = 0
        tile.action = TILE_SERVE
        tile.busy_until = token + 1
        return "probe_passed"

    return "digital_fallback"


def simulate(tokens: int = 28) -> list[RuntimeRow]:
    tiles = [
        Tile(0, TILE_SERVE, calibration_age=2),
        Tile(1, TILE_SERVE, calibration_age=1),
        Tile(2, TILE_SERVE, calibration_age=10),
        Tile(3, TILE_PROBE, residual_failures=2, calibration_age=5),
    ]
    rows: list[RuntimeRow] = []
    for token in range(tokens):
        analog_candidate = token % 7 != 6
        requested_tile = token % 4
        maintenance_budget = 0 if token in {9, 10, 17} else 1
        before = action_string(tiles)
        busy = busy_string(tiles, token)
        decision, selected, reason = schedule(tiles, token, analog_candidate, requested_tile, maintenance_budget)
        event = apply_decision(tiles, token, decision, selected)
        rows.append(
            RuntimeRow(
                token=token,
                requested_tile=requested_tile,
                analog_candidate=int(analog_candidate),
                maintenance_budget=maintenance_budget,
                tile_actions_before=before,
                tile_busy=busy,
                decision=decision,
                selected_tile=selected,
                reason=reason,
                reason_code=REASON_CODE[reason],
                event=event,
                tile_actions_after=action_string(tiles),
            )
        )
    return rows


def write_csv(rows: list[RuntimeRow]) -> None:
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(RuntimeRow.__dataclass_fields__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


def write_markdown(rows: list[RuntimeRow]) -> None:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row.event] = counts.get(row.event, 0) + 1

    lines = [
        "# Multi-Tile Scheduler Runtime Trace",
        "",
        "This trace connects the per-tile health action to a system-level scheduling decision over a token stream.",
        "",
        "```text",
        "tile action 0 = serve",
        "tile action 1 = recalibrate",
        "tile action 2 = disable",
        "tile action 3 = probe",
        "decision 0 = digital fallback",
        "decision 1 = analog service",
        "decision 2 = recalibration",
        "decision 3 = probe",
        "```",
        "",
        "## Event Counts",
        "",
    ]
    for name in sorted(counts):
        lines.append(f"- {name}: {counts[name]}")

    lines.extend(
        [
            "",
            "## Trace",
            "",
            "| token | requested | candidate | budget | before | busy | decision | selected | reason | event | after |",
            "| ---: | ---: | ---: | ---: | --- | --- | ---: | ---: | --- | --- | --- |",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row.token} | {row.requested_tile} | {row.analog_candidate} | {row.maintenance_budget} | "
            f"{row.tile_actions_before} | {row.tile_busy} | {row.decision} | {row.selected_tile} | "
            f"{row.reason} | {row.event} | {row.tile_actions_after} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The useful boundary is that the scheduler does not create trust. It spends visible trust. A serving tile can handle analog work. A recalibrating tile consumes maintenance budget before it serves again. A disabled tile cannot serve directly; it must enter probe and pass. If the requested tile is weak but a spare tile can serve, analog remains useful. If no tile can serve and maintenance budget is zero, the correct decision is digital fallback.",
            "",
        ]
    )
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def render_case(row: RuntimeRow) -> str:
    actions = [int(value) for value in row.tile_actions_before]
    busy_literal = row.tile_busy[::-1]
    return (
        f'        run_case("token_{row.token:02d}_{row.reason}", '
        f"1'b1, 1'b{row.analog_candidate}, 8'd{row.requested_tile}, "
        f"2'd{actions[0]}, 2'd{actions[1]}, 2'd{actions[2]}, 2'd{actions[3]}, "
        f"4'b{busy_literal}, 2'd{row.maintenance_budget}, "
        f"2'd{row.decision}, 2'd{row.selected_tile}, 4'd{row.reason_code});"
    )


def write_verilog(rows: list[RuntimeRow]) -> None:
    lines = [
        "// Generated by labs/analog/analog-in-memory-foundation-model-hardware/python/multi_tile_scheduler_runtime.py",
        "// Do not edit by hand; edit the runtime generator instead.",
    ]
    lines.extend(render_case(row) for row in rows)
    VH_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    rows = simulate()
    write_csv(rows)
    write_markdown(rows)
    write_verilog(rows)
    print("multi_tile_scheduler_runtime")
    print(f"tokens,{len(rows)}")
    for row in rows:
        print(
            f"{row.token},{row.requested_tile},{row.analog_candidate},{row.maintenance_budget},"
            f"{row.tile_actions_before},{row.tile_busy},{row.decision},{row.selected_tile},"
            f"{row.reason},{row.reason_code},{row.event},{row.tile_actions_after}"
        )
    print(f"csv,{CSV_OUT}")
    print(f"markdown,{MD_OUT}")
    print(f"verilog,{VH_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
