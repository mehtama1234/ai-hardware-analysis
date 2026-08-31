#!/usr/bin/env python3
"""Run all generated per-lesson labs and validate measurement contracts."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LESSON_LABS = ROOT / "lesson-labs"
REPORT_JSON = LESSON_LABS / "run-report.json"
REPORT_MD = LESSON_LABS / "run-report.md"


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


def run_lab(lab_dir: Path) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, "measure.py"], cwd=lab_dir, capture_output=True, text=True, check=False)
    payload = {}
    if proc.stdout.strip():
        payload = json.loads(proc.stdout)
    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip()[-1000:],
        "stderr": proc.stderr.strip()[-1000:],
        "payload": payload,
    }


def validate(lab_dir: Path, contract: dict[str, Any], run: dict[str, Any]) -> dict[str, Any]:
    measurement_path = lab_dir / "measurements.json"
    artifact = load_json(measurement_path) if measurement_path.exists() else {}
    checks = {field: nested_get(artifact, field) is not None for field in contract.get("required_fields", [])}
    checks["measure_exited_zero"] = run["returncode"] == 0
    checks["measurement_file_exists"] = measurement_path.exists()
    checks["status_accepted"] = artifact.get("status") in set(contract.get("accepted_statuses_without_gpu", []))
    checks["correctness_passed"] = artifact.get("correctness", {}).get("status") == "passed"
    return {
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "measurement_path": str(measurement_path.relative_to(ROOT)),
    }


def build_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# GPUMODE Lesson Lab Run Report",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        f"Lesson labs: {report['lab_count']}",
        f"Passed contracts: {report['passed_contracts']}",
        f"Failed contracts: {report['failed_contracts']}",
        "",
        "| Lesson | Lab | Contract | Measurement |",
        "|---|---|---|---|",
    ]
    for row in report["labs"]:
        lines.append(f"| {row['lesson_index']} | {row['id']} | {row['contract']['status']} | `{row['contract']['measurement_path']}` |")
    return "\n".join(lines).rstrip() + "\n"


def run_all() -> dict[str, Any]:
    if not (LESSON_LABS / "index.json").exists():
        subprocess.run([sys.executable, "scripts/build_lesson_labs.py"], cwd=ROOT, check=True)
    index = load_json(LESSON_LABS / "index.json")
    rows = []
    for row in index.get("labs", []):
        lab_dir = ROOT / row["path"]
        contract = load_json(lab_dir / "measurement-contract.json")
        run = run_lab(lab_dir)
        validation = validate(lab_dir, contract, run)
        rows.append(
            {
                "id": row["id"],
                "lesson_index": row["lesson_index"],
                "lesson_title": row["lesson_title"],
                "path": row["path"],
                "run": run,
                "contract": validation,
            }
        )
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lab_count": len(rows),
        "passed_contracts": sum(1 for row in rows if row["contract"]["status"] == "passed"),
        "failed_contracts": sum(1 for row in rows if row["contract"]["status"] != "passed"),
        "labs": rows,
    }
    write_json(REPORT_JSON, report)
    REPORT_MD.write_text(build_markdown(report), encoding="utf-8")
    return report


def main() -> int:
    report = run_all()
    print(
        f"wrote {REPORT_JSON.relative_to(ROOT)} and {REPORT_MD.relative_to(ROOT)} "
        f"({report['passed_contracts']}/{report['lab_count']} contracts passed)"
    )
    return 0 if report["failed_contracts"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
