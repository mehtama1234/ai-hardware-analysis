from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "gpu-provenance"
REPORT_JSON = OUT / "gpu-provenance-report.json"
REPORT_MD = OUT / "reports" / "gpu-provenance-report.md"
ALLOWED_KINDS = {"sample-fixture", "host-collected", "real-measured"}


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _run_rows(gpu_runs: dict[str, Any]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for row in gpu_runs.get("rows", []):
        run_id = row.get("run_id", "unknown")
        entry = grouped.setdefault(
            run_id,
            {
                "run_id": run_id,
                "provenance_kind": row.get("provenance_kind", "unspecified"),
                "measured": bool(row.get("measured", False)),
                "host": row.get("host", "unknown"),
                "vendor": row.get("vendor", "unknown"),
                "accelerator": row.get("accelerator", "unknown"),
                "row_count": 0,
                "passed_steps": 0,
                "skipped_steps": 0,
                "failed_steps": 0,
                "promotion_steps": [],
            },
        )
        entry["row_count"] += 1
        status = row.get("status", "")
        if status == "passed":
            entry["passed_steps"] += 1
        elif status.startswith("skipped"):
            entry["skipped_steps"] += 1
        elif status == "failed":
            entry["failed_steps"] += 1
        step_id = row.get("step_id")
        if step_id:
            entry["promotion_steps"].append(step_id)
    for entry in grouped.values():
        entry["promotion_steps"] = sorted(set(entry["promotion_steps"]))
    return sorted(grouped.values(), key=lambda row: row["run_id"])


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# GPUMODE GPU Evidence Provenance",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Status: `{report['status']}`",
        f"Real GPU evidence: `{report['real_gpu_evidence_status']}`",
        f"Measured GPU runs: `{report['measured_run_count']}`",
        "",
        "## Summary",
        "",
        f"- Sample fixture runs: `{report['sample_run_count']}`",
        f"- Host-collected runs: `{report['host_collected_run_count']}`",
        f"- Rows with provenance: `{report['rows_with_provenance']}/{report['row_count']}`",
    ]
    if report.get("warnings"):
        lines.extend(["", "## Warnings", ""])
        for warning in report["warnings"]:
            lines.append(f"- {warning}")
    lines.extend(
        [
            "",
            "## Runs",
            "",
            "| run | provenance | measured | vendor | accelerator | rows | passed | skipped | failed |",
            "|---|---|---:|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in report["runs"]:
        lines.append(
            f"| `{row['run_id']}` | `{row['provenance_kind']}` | `{row['measured']}` | "
            f"{row['vendor']} | {row['accelerator']} | {row['row_count']} | "
            f"{row['passed_steps']} | {row['skipped_steps']} | {row['failed_steps']} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def build_gpu_provenance() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    gpu_runs = load_json(ROOT / "gpu-runs" / "gpu-run-report.json", {})
    coverage = gpu_runs.get("coverage", {})
    rows = gpu_runs.get("rows", [])
    run_summaries = _run_rows(gpu_runs)
    rows_with_provenance = [
        row
        for row in rows
        if row.get("provenance_kind") in ALLOWED_KINDS and isinstance(row.get("measured"), bool)
    ]
    measured_run_count = coverage.get("measured_run_count", 0)
    sample_run_count = coverage.get("sample_run_count", 0)
    host_collected_run_count = coverage.get("host_collected_run_count", 0)
    warnings = []
    if measured_run_count == 0:
        warnings.append("no real measured GPU host imports present")
    if len(rows_with_provenance) != len(rows):
        warnings.append("one or more GPU run rows are missing explicit provenance")
    status = (
        "provenance-clear"
        if gpu_runs.get("status") == "import-ready"
        and len(rows_with_provenance) == len(rows)
        and sample_run_count >= 2
        and host_collected_run_count >= 1
        else "incomplete"
    )
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "source_report": "gpu-runs/gpu-run-report.json",
        "run_count": coverage.get("run_count", 0),
        "row_count": len(rows),
        "rows_with_provenance": len(rows_with_provenance),
        "measured_run_count": measured_run_count,
        "sample_run_count": sample_run_count,
        "host_collected_run_count": host_collected_run_count,
        "real_gpu_evidence_status": "present" if measured_run_count else "not-present-on-this-host",
        "allowed_provenance_kinds": sorted(ALLOWED_KINDS),
        "warnings": warnings,
        "runs": run_summaries,
    }
    write_json(REPORT_JSON, report)
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report
