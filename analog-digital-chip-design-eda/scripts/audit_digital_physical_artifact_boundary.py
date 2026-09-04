#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "evidence" / "aimc-hardware-lab" / "digital-physical-artifact-boundary.json"
OUT_MD = ROOT / "evidence" / "aimc-hardware-lab" / "digital-physical-artifact-boundary.md"

METRIC_FILES = [
    ROOT / "labs/eda/aimc-tile-service-scheduler-openlane-prep/openlane-cts-metrics-summary.md",
    ROOT / "labs/eda/aimc-error-budget-governor-openlane-prep/openlane-cts-metrics-summary.md",
    ROOT / "labs/eda/aimc-scheduler-governor-openlane-prep/openlane-cts-8ns-metrics-summary.md",
    ROOT / "labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/openlane-5ns-control-reset-fanout20-metrics-summary.md",
    ROOT / "labs/eda/aimc-control-plane-openlane-prep/openlane-no-cts-metrics-summary.md",
    ROOT / "labs/eda/aimc-micro-tile-controller-openlane-prep/openlane-no-cts-metrics-summary.md",
]

REQUIRED_FINAL_VIEWS = [
    "signoff/{design}.gds",
    "signoff/{design}.lef",
    "signoff/{design}.lib",
    "signoff/{design}.sdf",
    "signoff/{design}.spice",
    "routing/{design}.def",
    "routing/{design}.nl.v",
]


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def metric_value(text: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def bool_zero(text: str, key: str) -> bool | None:
    value = metric_value(text, key)
    if value is None:
        return None
    try:
        return float(value) == 0
    except ValueError:
        return None


def infer_design(run_dir: Path) -> str:
    if run_dir.parent.name == "runs":
        return run_dir.parent.parent.name
    return run_dir.name


def view_exists(run_dir: Path, design: str, pattern: str) -> bool:
    candidates = [
        run_dir / "results" / pattern.format(design=design),
        run_dir / "results" / "final" / pattern.format(design=design),
    ]
    return any(path.exists() and path.stat().st_size > 0 for path in candidates)


def classify_clock_boundary(path: Path, text: str) -> str:
    lowered = f"{path.name}\n{text}".lower()
    if "no-cts" in lowered or "no_cts" in lowered:
        return "no_cts_exploratory"
    if "cts-enabled" in lowered or "_cts" in lowered or "cts" in lowered:
        return "cts_enabled_exploratory"
    return "unknown_clock_boundary"


def parse_metrics(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    run_dir_text = metric_value(text, "run_dir")
    run_dir = Path(run_dir_text) if run_dir_text else Path("")
    design = infer_design(run_dir) if run_dir_text else "unknown"
    view_presence = {
        pattern.format(design=design): view_exists(run_dir, design, pattern)
        for pattern in REQUIRED_FINAL_VIEWS
    }
    clock_boundary = classify_clock_boundary(path, text)
    clean_checks = {
        "flow_completed": metric_value(text, "flow_status") == "flow completed",
        "routing_violations_zero": bool_zero(text, "tritonRoute_violations"),
        "magic_violations_zero": bool_zero(text, "Magic_violations"),
        "pin_antenna_violations_zero": bool_zero(text, "pin_antenna_violations"),
        "net_antenna_violations_zero": bool_zero(text, "net_antenna_violations"),
        "lvs_total_errors_zero": bool_zero(text, "lvs_total_errors"),
        "spef_setup_clean": bool_zero(text, "spef_wns"),
        "spef_tns_clean": bool_zero(text, "spef_tns"),
    }
    final_views_complete = all(view_presence.values())
    physical_flow_supported = final_views_complete and all(value is True for value in clean_checks.values())
    return {
        "metrics_file": rel(path),
        "run_dir": run_dir_text,
        "design": design,
        "clock_boundary": clock_boundary,
        "final_views_complete": final_views_complete,
        "physical_flow_supported": physical_flow_supported,
        "clean_checks": clean_checks,
        "final_view_presence": view_presence,
        "wns": metric_value(text, "wns"),
        "tns": metric_value(text, "tns"),
        "critical_path_ns": metric_value(text, "critical_path_ns"),
        "suggested_clock_period": metric_value(text, "suggested_clock_period"),
        "core_area_um2": metric_value(text, "CoreArea_um^2"),
        "claim_scope": "digital_control_physical_flow_only",
    }


def build_report() -> dict[str, Any]:
    runs = [parse_metrics(path) for path in METRIC_FILES if path.exists()]
    cts_supported = [run for run in runs if run["physical_flow_supported"] and run["clock_boundary"] == "cts_enabled_exploratory"]
    no_cts_supported = [run for run in runs if run["physical_flow_supported"] and run["clock_boundary"] == "no_cts_exploratory"]
    return {
        "result_type": "digital_physical_artifact_boundary",
        "status": "digital_physical_artifacts_present_analog_converter_post_layout_missing",
        "metrics_files_checked": len(runs),
        "digital_physical_flow_supported_count": sum(1 for run in runs if run["physical_flow_supported"]),
        "cts_enabled_supported_count": len(cts_supported),
        "no_cts_supported_count": len(no_cts_supported),
        "analog_converter_post_layout_supported": False,
        "runs": runs,
        "claim_boundary": {
            "allowed": "records digital control OpenLane final views, clean checks, and clock-boundary status from local run artifacts",
            "not_allowed": "does not claim analog converter layout, analog tile layout, measured silicon, board power, or production signoff",
        },
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Digital Physical Artifact Boundary",
        "",
        f"- status: `{report['status']}`",
        f"- metrics files checked: `{report['metrics_files_checked']}`",
        f"- digital physical flow supported count: `{report['digital_physical_flow_supported_count']}`",
        f"- CTS-enabled supported count: `{report['cts_enabled_supported_count']}`",
        f"- no-CTS supported count: `{report['no_cts_supported_count']}`",
        f"- analog converter post-layout supported: `{report['analog_converter_post_layout_supported']}`",
        "",
        "## First Principle",
        "",
        "A routed digital controller and an extracted analog converter are different physical objects. The controller evidence says that the decision logic can become gates, wires, timing views, and layout views. The converter evidence must say what the DAC, ADC, reference, mux, and sampling path cost after their own layout and extraction. One cannot substitute for the other.",
        "",
        "## Checked Runs",
        "",
    ]
    for run in report["runs"]:
        lines.extend([
            f"### {run['design']}",
            "",
            f"- metrics file: `{run['metrics_file']}`",
            f"- run dir: `{run['run_dir']}`",
            f"- clock boundary: `{run['clock_boundary']}`",
            f"- final views complete: `{run['final_views_complete']}`",
            f"- physical flow supported: `{run['physical_flow_supported']}`",
            f"- critical path ns: `{run['critical_path_ns']}`",
            f"- suggested clock period: `{run['suggested_clock_period']}`",
            "",
        ])
    lines.extend([
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("digital_physical_artifact_boundary")
    print(f"status,{report['status']}")
    print(f"metrics_files_checked,{report['metrics_files_checked']}")
    print(f"digital_physical_flow_supported_count,{report['digital_physical_flow_supported_count']}")
    print(f"cts_enabled_supported_count,{report['cts_enabled_supported_count']}")
    print(f"analog_converter_post_layout_supported,{report['analog_converter_post_layout_supported']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
