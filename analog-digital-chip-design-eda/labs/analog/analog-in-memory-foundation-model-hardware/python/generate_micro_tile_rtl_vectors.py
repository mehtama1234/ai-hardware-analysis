#!/usr/bin/env python3
from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from pathlib import Path


RTL_DIR = Path(__file__).resolve().parents[3] / "digital" / "aimc-control-plane-rtl"
MEASUREMENTS_DIR = Path(__file__).resolve().parents[1] / "measurements"
VH_OUT = RTL_DIR / "generated_micro_tile_cases.vh"
CSV_OUT = MEASUREMENTS_DIR / "generated-micro-tile-rtl-vectors.csv"
MD_OUT = MEASUREMENTS_DIR / "generated-micro-tile-rtl-vectors.md"


OP = {
    "qkv": 1,
    "attention_score": 2,
    "softmax": 4,
}

PATH = {
    "digital": 0,
    "analog_accepted": 1,
    "hybrid_review": 2,
}

PARTITION_REASON = {
    "digital_rule": 0,
    "fixed_weight_analog": 1,
    "hybrid_needs_evidence": 2,
    "missing_weights": 3,
}

READOUT_REASON = {
    "ok": 0,
    "tile_disabled": 1,
    "residual_high": 2,
    "calibration_stale": 3,
}


@dataclass(frozen=True)
class VectorCase:
    name: str
    op: str
    resident_weights: bool
    tile_id: int
    tile_enabled: bool
    residual_abs: int
    calibration_age: int


@dataclass(frozen=True)
class ExpectedRow:
    name: str
    op: str
    op_code: int
    resident_weights: int
    tile_id: int
    tile_enabled: int
    residual_abs: int
    calibration_age: int
    placement: str
    readout_reason: str
    expected_path: int
    expected_reason: int
    last_fallback_tile_id: int
    fallback_count: int
    accepted_count: int
    residual_fallback_count: int
    stale_fallback_count: int
    tile_health_action: int


def partition(case: VectorCase) -> tuple[str, str]:
    if case.op == "softmax":
        return "digital", "digital_rule"
    if case.op == "attention_score":
        return "hybrid_review", "hybrid_needs_evidence"
    if case.op == "qkv" and not case.resident_weights:
        return "digital", "missing_weights"
    return "analog", "fixed_weight_analog"


def readout(case: VectorCase) -> tuple[bool, str]:
    if not case.tile_enabled:
        return False, "tile_disabled"
    if case.residual_abs > 20:
        return False, "residual_high"
    if case.calibration_age >= 1024:
        return False, "calibration_stale"
    return True, "ok"


def health_action(residual_fallback_count: int, stale_fallback_count: int) -> int:
    if residual_fallback_count >= 2:
        return 2
    if stale_fallback_count >= 1:
        return 1
    return 0


def expected_row(case: VectorCase, state: dict[str, int]) -> ExpectedRow:
    placement, placement_reason = partition(case)
    readout_reason = "not_sampled"
    if placement == "analog":
        valid, readout_reason = readout(case)
        if valid:
            path = PATH["analog_accepted"]
            reason = 1
            state["accepted_count"] += 1
        else:
            path = PATH["digital"]
            reason = 8 | READOUT_REASON[readout_reason]
            state["last_fallback_tile_id"] = case.tile_id
            state["fallback_count"] += 1
            if readout_reason == "residual_high":
                state["residual_fallback_count"] += 1
            if readout_reason == "calibration_stale":
                state["stale_fallback_count"] += 1
    elif placement == "hybrid_review":
        path = PATH["hybrid_review"]
        reason = PARTITION_REASON[placement_reason]
    else:
        path = PATH["digital"]
        reason = PARTITION_REASON[placement_reason]

    action = health_action(state["residual_fallback_count"], state["stale_fallback_count"])
    return ExpectedRow(
        name=case.name,
        op=case.op,
        op_code=OP[case.op],
        resident_weights=int(case.resident_weights),
        tile_id=case.tile_id,
        tile_enabled=int(case.tile_enabled),
        residual_abs=case.residual_abs,
        calibration_age=case.calibration_age,
        placement=placement,
        readout_reason=readout_reason,
        expected_path=path,
        expected_reason=reason,
        last_fallback_tile_id=state["last_fallback_tile_id"],
        fallback_count=state["fallback_count"],
        accepted_count=state["accepted_count"],
        residual_fallback_count=state["residual_fallback_count"],
        stale_fallback_count=state["stale_fallback_count"],
        tile_health_action=action,
    )


def render_case(row: ExpectedRow) -> str:
    return (
        f'        run_case("{row.name}", 4\'d{row.op_code}, 1\'b{row.resident_weights}, '
        f"8'd{row.tile_id}, 1'b{row.tile_enabled}, 10'd{row.residual_abs}, "
        f"16'd{row.calibration_age}, 2'd{row.expected_path}, 4'd{row.expected_reason}, "
        f"8'd{row.last_fallback_tile_id}, 16'd{row.fallback_count}, "
        f"16'd{row.accepted_count}, 16'd{row.residual_fallback_count}, "
        f"16'd{row.stale_fallback_count}, 2'd{row.tile_health_action});"
    )


def vector_cases() -> list[VectorCase]:
    return [
        VectorCase("qkv_analog_readout_accepted", "qkv", True, 11, True, 3, 32),
        VectorCase("qkv_residual_forces_fallback", "qkv", True, 12, True, 40, 32),
        VectorCase("qkv_stale_calibration_fallback", "qkv", True, 17, True, 3, 2048),
        VectorCase("qkv_disabled_tile_fallback", "qkv", True, 13, False, 3, 32),
        VectorCase("attention_score_hybrid_review", "attention_score", True, 14, True, 3, 32),
        VectorCase("softmax_partition_digital", "softmax", True, 15, True, 3, 32),
        VectorCase("missing_weights_partition_digital", "qkv", False, 16, True, 3, 32),
        VectorCase("second_residual_disables_tile", "qkv", True, 18, True, 44, 32),
    ]


def build_rows(cases: list[VectorCase]) -> list[ExpectedRow]:
    state = {
        "last_fallback_tile_id": 0,
        "fallback_count": 0,
        "accepted_count": 0,
        "residual_fallback_count": 0,
        "stale_fallback_count": 0,
    }
    return [expected_row(case, state) for case in cases]


def write_verilog(rows: list[ExpectedRow]) -> None:
    lines = [
        "// Generated by labs/analog/analog-in-memory-foundation-model-hardware/python/generate_micro_tile_rtl_vectors.py",
        "// Do not edit by hand; edit the analog vector generator instead.",
    ]
    lines.extend(render_case(row) for row in rows)
    VH_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {os.path.relpath(VH_OUT, Path.cwd())}")


def write_csv(rows: list[ExpectedRow]) -> None:
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(ExpectedRow.__dataclass_fields__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)
    print(f"wrote {os.path.relpath(CSV_OUT, Path.cwd())}")


def write_markdown(rows: list[ExpectedRow]) -> None:
    lines = [
        "# Generated Micro-Tile RTL Vectors",
        "",
        "These rows are generated from the analog-side micro-tile assumptions and consumed by the Verilog controller testbench.",
        "",
        "The central rule is that analog placement is only permission to try a tile. The readout can still refuse the measured value. The counters then turn repeated evidence into a serving action.",
        "",
        "```text",
        "tile_health_action 0 = serve",
        "tile_health_action 1 = recalibrate",
        "tile_health_action 2 = disable",
        "tile_health_action 3 = probe",
        "```",
        "",
        "| case | placement | readout reason | expected path | expected reason | fallback count | accepted count | residual fallbacks | stale fallbacks | action |",
        "| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row.name} | {row.placement} | {row.readout_reason} | {row.expected_path} | "
            f"{row.expected_reason} | {row.fallback_count} | {row.accepted_count} | "
            f"{row.residual_fallback_count} | {row.stale_fallback_count} | {row.tile_health_action} |"
        )
    lines.extend(
        [
            "",
            "The important transition is visible in the final three analog-failure rows. A stale-calibration fallback requests recalibration because old correction evidence can be refreshed. A disabled tile falls back without changing the reason-specific residual or stale counters. The second residual failure disables analog service because the tile is failing after correction.",
            "",
        ]
    )
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {os.path.relpath(MD_OUT, Path.cwd())}")


def main() -> int:
    rows = build_rows(vector_cases())
    write_verilog(rows)
    write_csv(rows)
    write_markdown(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
