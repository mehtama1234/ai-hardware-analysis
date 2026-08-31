#!/usr/bin/env python3
"""Run generated GPU programming project starters and validate contracts."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "programming-projects"
REPORT_JSON = PROJECTS / "project-run-report.json"
REPORT_MD = PROJECTS / "project-run-report.md"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def nested_get(row: dict[str, Any], dotted: str) -> Any:
    current: Any = row
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def run_python_entry(project_dir: Path, entry_name: str, dry_run: bool) -> dict[str, Any]:
    command = [sys.executable, entry_name]
    if dry_run:
        return {
            "status": "dry-run",
            "command": " ".join(command),
            "returncode": 0,
            "stdout": "",
            "stderr": "",
            "payload": {},
        }
    proc = subprocess.run(command, cwd=project_dir, capture_output=True, text=True, check=False)
    payload: dict[str, Any] = {}
    if proc.stdout.strip():
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError:
            payload = {"raw_stdout": proc.stdout.strip()}
    return {
        "status": payload.get("status") or ("ran" if proc.returncode == 0 else "failed"),
        "command": " ".join(command),
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip()[-2000:],
        "stderr": proc.stderr.strip()[-2000:],
        "payload": payload,
    }


def validate_project(project_dir: Path, metadata: dict[str, Any], contract: dict[str, Any], run: dict[str, Any]) -> dict[str, Any]:
    measurement_path = project_dir / metadata.get("local_measurement", "measurements.json")
    evidence = load_json(measurement_path) if measurement_path.exists() else {}
    checks = {}
    for field in contract.get("required_fields", []):
        checks[field] = nested_get(evidence, field) is not None
    checks["metadata_has_lessons"] = bool(metadata.get("lessons"))
    checks["metadata_has_tutorial_sources"] = bool(metadata.get("tutorial_sources"))
    checks["metadata_has_lab"] = bool(metadata.get("lab", {}).get("path"))
    checks["metadata_has_measurement"] = bool(metadata.get("measurement", {}).get("path"))
    checks["source_exists"] = (project_dir / metadata.get("source", "")).exists()
    checks["measure_exited_zero"] = run.get("returncode") == 0
    checks["measurement_file_exists"] = measurement_path.exists()
    checks["measurement_project_matches"] = evidence.get("project") == metadata.get("id")
    accepted = set(contract.get("accepted_statuses_without_gpu", [])) | {"ready"}
    checks["status_is_accepted_without_gpu"] = evidence.get("status") in accepted
    return {
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "evidence": evidence,
        "measurement_path": str(measurement_path.relative_to(ROOT)),
    }


def build_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# GPU Programming Project Run Report",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        f"Projects: {report['project_count']}",
        f"Passed contracts: {report['passed_contracts']}",
        f"Failed contracts: {report['failed_contracts']}",
        "",
        "| Project | Track | Profile | Starter | Contract |",
        "|---|---|---|---|---|",
    ]
    for row in report["projects"]:
        lines.append(
            "| "
            f"{row['id']} | {row['track']} | {row['profile']} | "
            f"{row['starter_status']} | {row['contract']['status']} |"
        )
    lines.append("")
    lines.append("## Runtime Caveats")
    for row in report["projects"]:
        notes = row["contract"].get("evidence", {}).get("runtime_readiness", {}).get("notes", [])
        if notes:
            lines.append(f"- {row['id']}: {'; '.join(notes)}")
    if lines[-1] == "## Runtime Caveats":
        lines.append("- No starter-level runtime caveats were emitted.")
    return "\n".join(lines).rstrip() + "\n"


def run_all(dry_run: bool = False) -> dict[str, Any]:
    if not (PROJECTS / "index.json").exists():
        subprocess.run([sys.executable, "scripts/build_gpu_programming_projects.py"], cwd=ROOT, check=True)
    index = load_json(PROJECTS / "index.json")
    rows = []
    for project in index.get("projects", []):
        project_dir = ROOT / project["path"]
        metadata = load_json(project_dir / "project.json")
        contract = load_json(project_dir / "measurement-contract.json")
        starter_run = run_python_entry(project_dir, metadata["starter"], dry_run=dry_run)
        measure_run = run_python_entry(project_dir, metadata.get("measure", "measure.py"), dry_run=dry_run)
        validation = validate_project(project_dir, metadata, contract, measure_run)
        rows.append(
            {
                "id": project["id"],
                "track": project["track"],
                "profile": project["profile"],
                "path": project["path"],
                "starter": project["starter"],
                "measure": project.get("measure", ""),
                "source": project["source"],
                "starter_status": starter_run.get("status"),
                "starter_run": starter_run,
                "run": measure_run,
                "contract": validation,
            }
        )
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dry_run": dry_run,
        "project_count": len(rows),
        "passed_contracts": sum(1 for row in rows if row["contract"]["status"] == "passed"),
        "failed_contracts": sum(1 for row in rows if row["contract"]["status"] != "passed"),
        "projects": rows,
    }
    write_json(REPORT_JSON, report)
    REPORT_MD.write_text(build_markdown(report), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = run_all(dry_run=args.dry_run)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(
            f"wrote {REPORT_JSON.relative_to(ROOT)} and {REPORT_MD.relative_to(ROOT)} "
            f"({report['passed_contracts']}/{report['project_count']} contracts passed)"
        )
    return 0 if report["failed_contracts"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
