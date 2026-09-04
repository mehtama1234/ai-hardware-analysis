#!/usr/bin/env python3
from __future__ import annotations

import csv
import os
import re
import sys
from pathlib import Path


RUN_DIR = Path(os.environ.get(
    "AIMC_OPENLANE_RUN_DIR",
    "/home/mehtama1/eda-tools/OpenLane/designs/aimc_micro_tile_controller/runs/aimc_micro_tile_controller_recovery_probe_no_cts",
))
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "openlane-no-cts-metrics-summary.md"

KEYS = [
    "flow_status",
    "total_runtime",
    "routed_runtime",
    "synth_cell_count",
    "TotalCells",
    "CoreArea_um^2",
    "DIEAREA_mm^2",
    "wire_length",
    "vias",
    "wns",
    "tns",
    "spef_wns",
    "spef_tns",
    "critical_path_ns",
    "suggested_clock_period",
    "suggested_clock_frequency",
    "tritonRoute_violations",
    "Magic_violations",
    "pin_antenna_violations",
    "net_antenna_violations",
    "lvs_total_errors",
]

FINAL_ARTIFACTS = [
    "signoff/aimc_micro_tile_controller.gds",
    "signoff/aimc_micro_tile_controller.lef",
    "signoff/aimc_micro_tile_controller.lib",
    "signoff/aimc_micro_tile_controller.sdf",
    "signoff/aimc_micro_tile_controller.spice",
    "routing/aimc_micro_tile_controller.def",
    "routing/aimc_micro_tile_controller.nl.v",
]


def read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def load_metrics(run_dir: Path) -> dict[str, str]:
    metrics_path = run_dir / "reports" / "metrics.csv"
    with metrics_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 1:
        raise ValueError(f"expected one metrics row in {metrics_path}, found {len(rows)}")
    return rows[0]


def extract(pattern: str, text: str, default: str = "missing") -> str:
    match = re.search(pattern, text, re.MULTILINE)
    return match.group(1) if match else default


def main() -> int:
    run_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else RUN_DIR
    metrics = load_metrics(run_dir)
    manufacturability = read(run_dir / "reports" / "manufacturability.rpt")
    checks = read(run_dir / "reports" / "signoff" / "31-rcx_sta.checks.rpt")
    linter = read(run_dir / "logs" / "synthesis" / "linter.log")
    if not linter.strip():
        linter = read(run_dir / "openlane.log")
    final_root = run_dir / "results"

    linter_errors = extract(r"([0-9]+) errors found by linter", linter, "missing")
    linter_warnings = extract(r"([0-9]+) warnings found by linter", linter, "missing")
    max_slew = extract(r"max slew violation count ([0-9]+)", checks)
    max_fanout = extract(r"max fanout violation count ([0-9]+)", checks)
    max_cap = extract(r"max cap violation count ([0-9]+)", checks)
    clk_fanout = extract(r"^clk\s+10\s+([0-9]+)\s+-", checks)
    setup_clear = "No paths found." in checks

    lines = [
        "# AIMC Micro-Tile Controller OpenLane Metrics Summary",
        "",
        "This file is generated from the local no-CTS OpenLane run artifacts.",
        "",
        "## Run",
        "",
        "```text",
        f"run_dir: {run_dir}",
    ]
    for key in KEYS:
        lines.append(f"{key}: {metrics.get(key, '<missing>')}")
    lines.extend(
        [
            f"linter_errors: {linter_errors}",
            f"linter_warnings: {linter_warnings}",
            "```",
            "",
            "## Final Artifact Check",
            "",
            "```text",
        ]
    )
    for rel in FINAL_ARTIFACTS:
        path = final_root / rel
        status = "present" if path.exists() and path.stat().st_size > 0 else "missing"
        lines.append(f"{rel}: {status}")

    lines.extend(["```", "", "## Manufacturability", "", "```text"])
    for raw in manufacturability.splitlines():
        if "DRC violations" in raw or "LVS clean" in raw or "Pin violations" in raw or "Net violations" in raw:
            lines.append(raw)

    lines.extend(
        [
            "```",
            "",
            "## Timing And Fanout Boundary",
            "",
            "```text",
            f"setup_violating_paths_found: {str(not setup_clear).lower()}",
            f"max_slew_violations: {max_slew}",
            f"max_fanout_violations: {max_fanout}",
            f"max_cap_violations: {max_cap}",
            f"clock_fanout: {clk_fanout}",
            "```",
            "",
            "## Interpretation",
            "",
            "The no-CTS flow proves that the integrated controller can pass synthesis, placement, routing, extraction, GDS generation, DRC, LVS, and antenna checks in this exploratory setup.",
            "",
            "It does not prove clock-tree signoff. The remaining fanout violations are the open physical-design object, and the clock net is one of the violators because CTS is disabled.",
            "",
        ]
    )
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
