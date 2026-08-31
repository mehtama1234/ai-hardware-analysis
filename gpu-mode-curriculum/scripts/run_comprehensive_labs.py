#!/usr/bin/env python3
"""Run every hand-written comprehensive GPUMODE lab."""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMPREHENSIVE = ROOT / "comprehensive-labs"
REPORT_JSON = COMPREHENSIVE / "run-report.json"
REPORT_MD = COMPREHENSIVE / "run-report.md"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_module(module_name: str) -> dict[str, Any]:
    env_path = str(COMPREHENSIVE)
    code = f"import sys; sys.path.insert(0, {env_path!r}); import {module_name} as m; raise SystemExit(m.main())"
    proc = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, check=False)
    payload: dict[str, Any] = {}
    if proc.stdout.strip():
        payload = json.loads(proc.stdout)
    return {
        "returncode": proc.returncode,
        "status": payload.get("status", "failed"),
        "stdout": proc.stdout.strip()[-2000:],
        "stderr": proc.stderr.strip()[-2000:],
        "payload": payload,
    }


def build_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# GPUMODE Comprehensive Lab Run Report",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        f"Labs: {report['lab_count']}",
        f"Passed: {report['passed']}",
        f"Failed: {report['failed']}",
        "",
        "| Lab | Lessons | Status | Measurement |",
        "|---|---|---|---|",
    ]
    for row in report["labs"]:
        lines.append(f"| {row['id']} | {row['lesson_count']} | {row['status']} | `{row['measurement_path']}` |")
    return "\n".join(lines).rstrip() + "\n"


def run_all() -> dict[str, Any]:
    if not (COMPREHENSIVE / "plan.json").exists():
        subprocess.run([sys.executable, "scripts/build_comprehensive_lab_plan.py"], cwd=ROOT, check=True)
    plan = load_json(COMPREHENSIVE / "plan.json")
    rows = []
    for lab in plan["labs"]:
        run = run_module(lab["module"])
        measurement_path = f"comprehensive-labs/measurements/{lab['id']}.json"
        rows.append(
            {
                "id": lab["id"],
                "title": lab["title"],
                "module": lab["module"],
                "implementation": lab["implementation"],
                "lesson_count": lab["lesson_count"],
                "status": run["status"],
                "returncode": run["returncode"],
                "measurement_path": measurement_path,
                "run": run,
            }
        )
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lab_count": len(rows),
        "passed": sum(1 for row in rows if row["status"] == "passed" and row["returncode"] == 0),
        "failed": sum(1 for row in rows if row["status"] != "passed" or row["returncode"] != 0),
        "labs": rows,
    }
    write_json(REPORT_JSON, report)
    REPORT_MD.write_text(build_markdown(report), encoding="utf-8")
    return report


def main() -> int:
    report = run_all()
    print(f"wrote {REPORT_JSON.relative_to(ROOT)} and {REPORT_MD.relative_to(ROOT)} ({report['passed']}/{report['lab_count']} passed)")
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
