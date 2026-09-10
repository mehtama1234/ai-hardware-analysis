"""Small reproducible regression coordinator."""

from __future__ import annotations

from pathlib import Path
import json
import hashlib
from typing import Any

from .clustering import cluster_failures
from .runner import run_command
from .triage import parse_failure


def run_regression(jobs: list[tuple[str, list[str]]], *, run_root: str | Path, source_revision: str = "unknown") -> dict[str, Any]:
    root = Path(run_root)
    failures = []
    runs = []
    verification_failures = 0
    for name, command in jobs:
        run = run_command(command, tool=name, run_root=root / name, source_revision=source_revision, run_id=name)
        runs.append(run)
        log = (root / name / "stdout.log").read_text(encoding="utf-8") if (root / name / "stdout.log").is_file() else ""
        failure = parse_failure(log)
        if failure:
            failures.append(failure)
            verification_failures += 1
    clusters = cluster_failures(failures)
    return {
        "total_jobs": len(runs),
        "passed_jobs": sum(run.status == "passed" for run in runs) - verification_failures,
        "failed_jobs": sum(run.status == "failed" for run in runs) + verification_failures,
        "blocked_jobs": sum(run.status == "blocked" for run in runs),
        "failure_count": len(failures),
        "cluster_count": len(clusters),
        "runs": runs,
    }


def write_regression_report(report: dict[str, Any], path: str | Path) -> Path:
    """Write a stable aggregate report, excluding non-serializable ToolRun objects."""
    serializable = dict(report)
    serializable["runs"] = [{"id": run.id, "tool": run.tool, "status": run.status, "exit_code": run.exit_code} for run in report.get("runs", [])]
    canonical = json.dumps(serializable, sort_keys=True, separators=(",", ":"))
    serializable["report_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(serializable, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output
