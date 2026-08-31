#!/usr/bin/env python3
"""Verify generated one-lab-per-lesson coverage."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = ROOT / "analysis" / "gpumode-curriculum.json"
LESSON_LABS = ROOT / "lesson-labs"
SITE = ROOT / "site"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not (LESSON_LABS / "index.json").exists():
        subprocess.run([sys.executable, "scripts/build_lesson_labs.py"], cwd=ROOT, check=True)
    if not (LESSON_LABS / "run-report.json").exists():
        subprocess.run([sys.executable, "scripts/run_lesson_labs.py"], cwd=ROOT, check=True)
    curriculum = load_json(CURRICULUM)
    index = load_json(LESSON_LABS / "index.json")
    run_report = load_json(LESSON_LABS / "run-report.json")
    lessons = curriculum.get("lessons", [])
    labs = index.get("labs", [])
    require(len(lessons) >= 100, "expected at least 100 GPUMODE lessons")
    require(index.get("lesson_count") == len(lessons), "lesson-lab index lesson_count mismatch")
    require(index.get("generated_lab_count") == len(lessons), "not every lesson has a generated lab")
    require(len(labs) == len(lessons), "lesson-lab rows do not cover every lesson")
    require(run_report.get("lab_count") == len(labs), "lesson-lab run report count mismatch")
    require(run_report.get("failed_contracts") == 0, "lesson-lab run report has failed contracts")
    require(run_report.get("passed_contracts") == len(labs), "not every lesson-lab contract passed")
    require((LESSON_LABS / "README.md").exists(), "missing lesson-labs README")
    require((LESSON_LABS / "run-report.md").exists(), "missing lesson-labs run report Markdown")
    seen = set()
    for row in labs:
        seen.add(row["lesson_index"])
        lab_dir = ROOT / row["path"]
        for name in ["README.md", "lab.json", "lab.py", "starter.py", "measure.py", "tasks.json", "measurement-contract.json", "measurements.json"]:
            require((lab_dir / name).exists(), f"{row['id']} missing {name}")
        metadata = load_json(lab_dir / "lab.json")
        tasks = load_json(lab_dir / "tasks.json")
        measurement = load_json(lab_dir / "measurements.json")
        contract = load_json(lab_dir / "measurement-contract.json")
        require(metadata.get("lesson", {}).get("index") == row["lesson_index"], f"{row['id']} metadata lesson mismatch")
        require(len(tasks.get("tasks", [])) >= 5, f"{row['id']} has too few tasks")
        require(contract.get("required_fields"), f"{row['id']} contract missing fields")
        require(measurement.get("correctness", {}).get("status") == "passed", f"{row['id']} correctness did not pass")
        require(measurement.get("measurement", {}).get("rows"), f"{row['id']} measurement rows missing")
    require(seen == {lesson["index"] for lesson in lessons}, "lesson-lab index does not exactly match lesson indexes")
    if (SITE / "lesson-labs.html").exists():
        page = (SITE / "lesson-labs.html").read_text(encoding="utf-8")
        require("GPUMODE lesson lab coverage" in page, "lesson-labs.html missing title")
        require("run-report.md" in page, "lesson-labs.html missing run report link")
    facts = {
        "lesson_count": len(lessons),
        "generated_lesson_labs": len(labs),
        "passed_contracts": run_report.get("passed_contracts"),
        "lessons_without_direct_project_before_generation": index.get("lessons_without_direct_project_before_generation_count"),
    }
    print(json.dumps({"facts": facts, "failures": []}, indent=2))
    print("GPUMODE lesson-lab verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
