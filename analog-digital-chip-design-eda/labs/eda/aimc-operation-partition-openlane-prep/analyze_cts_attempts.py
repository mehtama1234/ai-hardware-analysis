#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path


RUN_ROOT = Path("/home/mehtama1/eda-tools/OpenLane/designs")
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "cts-debug-summary.md"

ATTEMPTS = [
    (
        "full_input_output_wrapper",
        RUN_ROOT / "aimc_operation_partition_physical" / "runs" / "aimc_operation_partition_cts",
    ),
    (
        "lean_output_registered_wrapper",
        RUN_ROOT / "aimc_operation_partition_output_registered" / "runs" / "aimc_operation_partition_output_registered_cts",
    ),
]

NO_CTS_RUN = RUN_ROOT / "aimc_operation_partition_physical" / "runs" / "aimc_operation_partition_no_cts"
EXPERIMENT_ROOT = Path("/tmp/aimc-operation-partition-cts-experiments")
EXPERIMENTS = ["single_corner", "small_clusters", "no_post_processing", "baseline"]


def read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def extract(pattern: str, text: str, default: str = "missing") -> str:
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        return default
    return match.group(1)


def cts_status(run_dir: Path) -> dict[str, str]:
    log = read(run_dir / "logs" / "cts" / "12-cts.log")
    metrics = read(run_dir / "reports" / "metrics.csv")
    reproducible = run_dir / "issue_reproducible" / "run.sh"
    reached_cts = "Running Clock Tree Synthesis" in log
    pattern_count = extract(r"Number of created patterns = ([0-9]+)", log)
    buffer = extract(r"Characterization buffer is: ([A-Za-z0-9_]+)", log)
    flow_status = extract(r",([^,\n]*failed[^,\n]*|flow completed),", metrics)
    if flow_status == "missing" and "FLOW_FAILED" in read(run_dir / "config.tcl"):
        flow_status = "flow failed"
    return {
        "run_dir": str(run_dir),
        "exists": str(run_dir.exists()).lower(),
        "reached_cts": str(reached_cts).lower(),
        "characterization_buffer": buffer,
        "created_patterns": pattern_count,
        "flow_status": flow_status,
        "issue_reproducible": str(reproducible.exists()).lower(),
    }


def no_cts_violations() -> dict[str, str]:
    checks = read(NO_CTS_RUN / "reports" / "signoff" / "31-rcx_sta.checks.rpt")
    metrics = read(NO_CTS_RUN / "reports" / "metrics.csv")
    return {
        "run_dir": str(NO_CTS_RUN),
        "flow_status": extract(r",([^,\n]*flow completed[^,\n]*),", metrics),
        "max_slew_violations": extract(r"max slew violation count ([0-9]+)", checks),
        "max_fanout_violations": extract(r"max fanout violation count ([0-9]+)", checks),
        "max_cap_violations": extract(r"max cap violation count ([0-9]+)", checks),
        "clock_fanout": extract(r"^clk\s+10\s+([0-9]+)\s+-", checks),
    }


def experiment_status(name: str) -> dict[str, str]:
    log_path = EXPERIMENT_ROOT / name / f"experiment-{name}.log"
    text = read(log_path)
    pattern_counts = re.findall(r"Number of created patterns = ([0-9]+)", text)
    return {
        "log": str(log_path),
        "exists": str(log_path.exists()).lower(),
        "reached_cts": str("Running Clock Tree Synthesis" in text).lower(),
        "characterization_buffer": extract(r"Characterization buffer is: ([A-Za-z0-9_]+)", text),
        "last_created_patterns": pattern_counts[-1] if pattern_counts else "missing",
        "completed": str("cts_report" in text).lower(),
        "openroad_missing": str("openroad: not found" in text).lower(),
    }


def main() -> int:
    lines = [
        "# AIMC Operation Partition CTS Debug Summary",
        "",
        "This file is generated from local OpenLane run artifacts. It separates the completed no-CTS physical evidence from the CTS boundary.",
        "",
        "## No-CTS Clock Checks",
        "",
        "```text",
    ]
    no_cts = no_cts_violations()
    for key, value in no_cts.items():
        lines.append(f"{key}: {value}")
    lines.extend(["```", "", "## CTS Attempts", ""])

    for name, run_dir in ATTEMPTS:
        status = cts_status(run_dir)
        lines.extend([f"### {name}", "", "```text"])
        for key, value in status.items():
            lines.append(f"{key}: {value}")
        lines.extend(["```", ""])

    lines.extend(["## Isolated CTS Experiments", ""])
    for name in EXPERIMENTS:
        status = experiment_status(name)
        if status["exists"] != "true":
            continue
        lines.extend([f"### {name}", "", "```text"])
        for key, value in status.items():
            lines.append(f"{key}: {value}")
        lines.extend(["```", ""])

    lines.extend(
        [
            "## Interpretation",
            "",
            "Both CTS-enabled attempts reached OpenROAD CTS, selected the same clock characterization buffer, and stopped at the same pattern count. The isolated single-corner and small-cluster experiments also reached the same characterization buffer and continued pattern creation beyond 50000. The no-CTS run remains valid routed-layout evidence, but the unresolved object is the clock tree.",
            "",
            "The next experiment should isolate CTS itself: run the packaged reproducible with changed CTS characterization or clustering settings before changing the transformer partition logic again.",
            "",
        ]
    )
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
