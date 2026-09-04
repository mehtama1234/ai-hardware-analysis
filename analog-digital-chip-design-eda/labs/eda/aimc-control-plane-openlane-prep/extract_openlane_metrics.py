#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path


DEFAULT_RUN = Path("/home/mehtama1/eda-tools/OpenLane/designs/aimc_control_plane/runs/aimc_control_plane_no_cts")
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
    "def/aimc_control_plane.def",
    "gds/aimc_control_plane.gds",
    "lef/aimc_control_plane.lef",
    "lib/aimc_control_plane.lib",
    "sdc/aimc_control_plane.sdc",
    "sdf/aimc_control_plane.sdf",
    "spef/aimc_control_plane.spef",
]


def load_metrics(run_dir: Path) -> dict[str, str]:
    metrics_path = run_dir / "reports" / "metrics.csv"
    with metrics_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 1:
        raise ValueError(f"expected one metrics row in {metrics_path}, found {len(rows)}")
    return rows[0]


def main() -> int:
    run_dir = DEFAULT_RUN
    metrics = load_metrics(run_dir)
    manufacturability = (run_dir / "reports" / "manufacturability.rpt").read_text(encoding="utf-8")
    final_root = run_dir / "results" / "final"

    lines = [
        "# AIMC Control Plane OpenLane Metrics Summary",
        "",
        "This file is generated from the completed no-CTS OpenLane run artifacts.",
        "",
        "```text",
        f"run_dir: {run_dir}",
    ]
    for key in KEYS:
        lines.append(f"{key}: {metrics.get(key, '<missing>')}")
    lines.extend(["```", "", "## Final Artifact Check", "", "```text"])
    for rel in FINAL_ARTIFACTS:
        path = final_root / rel
        status = "present" if path.exists() and path.stat().st_size > 0 else "missing"
        lines.append(f"{rel}: {status}")
    lines.extend(["```", "", "## Manufacturability Extract", "", "```text"])
    for raw in manufacturability.splitlines():
        if "DRC violations" in raw or "LVS clean" in raw or "Pin violations" in raw or "Net violations" in raw:
            lines.append(raw)
    lines.extend([
        "```",
        "",
        "## Boundary",
        "",
        "This summary is from the no-CTS run. It is routed-layout evidence, not full CTS-enabled clock-tree signoff.",
        "",
    ])
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
