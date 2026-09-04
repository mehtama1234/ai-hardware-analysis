#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path


RUN_DIR = Path(
    "/home/mehtama1/eda-tools/OpenLane/designs/aimc_scheduler_governor_pipelined/runs/aimc_scheduler_governor_pipelined_5ns"
)
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
    "signoff/aimc_scheduler_governor_pipelined.gds",
    "signoff/aimc_scheduler_governor_pipelined.lef",
    "signoff/aimc_scheduler_governor_pipelined.lib",
    "signoff/aimc_scheduler_governor_pipelined.sdf",
    "signoff/aimc_scheduler_governor_pipelined.spice",
    "routing/aimc_scheduler_governor_pipelined.def",
    "routing/aimc_scheduler_governor_pipelined.nl.v",
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
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else OUTPUT
    is_no_cts_run = "no_cts" in run_dir.name
    metrics = load_metrics(run_dir)
    manufacturability = read(run_dir / "reports" / "manufacturability.rpt")
    check_paths = sorted((run_dir / "reports" / "signoff").glob("*-rcx_sta.checks.rpt"))
    checks = read(check_paths[-1]) if check_paths else ""
    linter = read(run_dir / "logs" / "synthesis" / "linter.log")
    final_root = run_dir / "results"

    if linter.strip():
        linter_errors = extract(r"([0-9]+) errors found by linter", linter, str(linter.count("%Error")))
        linter_warnings = extract(r"([0-9]+) warnings found by linter", linter, str(linter.count("%Warning")))
    else:
        linter_errors = "0"
        linter_warnings = "0"
    max_slew = extract(r"max slew violation count ([0-9]+)", checks)
    max_fanout = extract(r"max fanout violation count ([0-9]+)", checks)
    max_cap = extract(r"max cap violation count ([0-9]+)", checks)
    clk_fanout = extract(r"^clk\s+10\s+([0-9]+)\s+-", checks)
    setup_clear = "No paths found." in checks

    if is_no_cts_run:
        generated_from = "This file is generated from local no-CTS OpenLane run artifacts."
        interpretation = [
            "The no-CTS flow is an exploratory check. It can expose gross timing and routing problems before clock-tree synthesis, but it is not a clocked physical signoff result.",
            "",
            "Use this result as a debugging waypoint. A stronger claim needs a CTS-enabled run with extracted timing, DRC, LVS, antenna, setup, hold, and fanout checks.",
        ]
    else:
        generated_from = "This file is generated from local CTS-enabled OpenLane run artifacts."
        interpretation = [
            "The CTS-enabled flow asks whether the scheduler/governor decision can be routed as a clocked object at the selected clock period without hiding a timing, fanout, DRC, LVS, or antenna failure.",
            "",
            "A passing run does not prove the full analog accelerator. It proves a narrower fact: this digital referee can be turned into placed-and-routed logic under the stated constraints. If fanout still violates the selected limit, that remains a physical packaging boundary. If fanout is clean, the remaining boundaries are small-core power-grid packaging, calibrated IR-drop source placement, and integration with analog tile timing models.",
        ]

    lines = [
        "# AIMC Scheduler/Governor OpenLane Metrics Summary",
        "",
        generated_from,
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
        ]
    )
    lines.extend(interpretation)
    lines.append("")
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
