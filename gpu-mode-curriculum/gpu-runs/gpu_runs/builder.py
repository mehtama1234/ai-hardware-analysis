from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "gpu-runs"
FIXTURE_DIR = OUT / "fixtures"
IMPORT_DIR = OUT / "imports"
REPORT_JSON = OUT / "gpu-run-report.json"
REPORT_MD = OUT / "reports" / "gpu-run-report.md"


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _fixture_paths() -> list[Path]:
    return sorted(FIXTURE_DIR.glob("*.json")) + sorted(IMPORT_DIR.glob("*.json"))


def _promotion_ids(manifest: dict[str, Any]) -> set[str]:
    return {row.get("id") for row in manifest.get("steps", []) if row.get("id")}


def _flatten_runs(runs: list[dict[str, Any]], promotion_ids: set[str]) -> list[dict[str, Any]]:
    rows = []
    for run in runs:
        host = run.get("host", {})
        provenance = run.get("provenance", {})
        for step in run.get("promotion_steps", []):
            metrics = step.get("metrics", {})
            rows.append(
                {
                    "run_id": run.get("run_id"),
                    "provenance_kind": provenance.get("kind", "unspecified"),
                    "measured": bool(provenance.get("measured", False)),
                    "host": host.get("name", "unknown"),
                    "vendor": host.get("vendor", "unknown"),
                    "accelerator": host.get("accelerator", "unknown"),
                    "step_id": step.get("id"),
                    "status": step.get("status", "missing"),
                    "known_promotion_step": step.get("id") in promotion_ids,
                    "evidence": step.get("evidence", []),
                    "metric_count": len(metrics),
                    "metrics": metrics,
                }
            )
    return rows


def _coverage(rows: list[dict[str, Any]]) -> dict[str, Any]:
    step_ids = {row["step_id"] for row in rows if row.get("step_id")}
    vendors = {row["vendor"] for row in rows if row.get("vendor")}
    passed = [row for row in rows if row.get("status") == "passed"]
    return {
        "run_count": len({row["run_id"] for row in rows}),
        "host_count": len({row["host"] for row in rows}),
        "vendor_count": len(vendors),
        "vendors": sorted(vendors),
        "measured_run_count": len({row["run_id"] for row in rows if row.get("measured")}),
        "sample_run_count": len({row["run_id"] for row in rows if row.get("provenance_kind") == "sample-fixture"}),
        "host_collected_run_count": len({row["run_id"] for row in rows if row.get("provenance_kind") == "host-collected"}),
        "promotion_step_count": len(step_ids),
        "promotion_steps": sorted(step_ids),
        "passed_steps": len(passed),
        "failed_steps": len([row for row in rows if row.get("status") == "failed"]),
        "unknown_steps": len([row for row in rows if not row.get("known_promotion_step")]),
    }


def _validation_summary(rows: list[dict[str, Any]], manifest: dict[str, Any]) -> dict[str, Any]:
    manifest_gpu_steps = {
        row.get("id")
        for row in manifest.get("steps", [])
        if row.get("status") == "ready-on-gpu-host" and row.get("id")
    }
    covered_steps = {row["step_id"] for row in rows if row.get("status") == "passed"}
    required_evidence_rows = [row for row in rows if row.get("evidence")]
    return {
        "covers_any_gpu_host_step": bool(covered_steps & manifest_gpu_steps),
        "covered_gpu_host_steps": sorted(covered_steps & manifest_gpu_steps),
        "missing_gpu_host_steps": sorted(manifest_gpu_steps - covered_steps),
        "all_rows_have_evidence": len(required_evidence_rows) == len(rows),
        "all_rows_have_metrics": all(row.get("metric_count", 0) > 0 for row in rows),
        "ready_for_real_imports": True,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# GPUMODE GPU Run Imports",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Status: `{report['status']}`",
        f"Real measured runs: `{report['coverage']['measured_run_count']}`",
        "",
        "## Coverage",
        "",
    ]
    for key, value in report["coverage"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Validation", "", f"- `covered_gpu_host_steps`: `{report['validation']['covered_gpu_host_steps']}`",
                  f"- `missing_gpu_host_steps`: `{report['validation']['missing_gpu_host_steps']}`",
                  "", "## Imported Steps", "", "| run | host | accelerator | step | status | metrics |", "|---|---|---|---|---|---:|"])
    for row in report["rows"]:
        lines.append(
            f"| `{row['run_id']}` | {row['host']} | {row['accelerator']} | "
            f"`{row['step_id']}` | {row['status']} | {row['metric_count']} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def build_gpu_runs() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    manifest = load_json(ROOT / "gpu-promotion" / "gpu-host-promotion-manifest.json", {})
    runs = [load_json(path, {}) for path in _fixture_paths()]
    rows = _flatten_runs(runs, _promotion_ids(manifest))
    validation = _validation_summary(rows, manifest)
    coverage = _coverage(rows)
    status = (
        "import-ready"
        if coverage["run_count"] >= 2
        and coverage["vendor_count"] >= 2
        and coverage["promotion_step_count"] >= 8
        and coverage["failed_steps"] == 0
        and coverage["unknown_steps"] == 0
        and validation["all_rows_have_evidence"]
        and validation["all_rows_have_metrics"]
        else "incomplete"
    )
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "fixture_count": len(list(FIXTURE_DIR.glob("*.json"))),
        "import_count": len(list(IMPORT_DIR.glob("*.json"))),
        "coverage": coverage,
        "validation": validation,
        "input_manifest": "gpu-promotion/gpu-host-promotion-manifest.json",
        "rows": rows,
    }
    write_json(REPORT_JSON, report)
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report
