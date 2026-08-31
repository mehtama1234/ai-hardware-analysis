#!/usr/bin/env python3
"""Build the GPUMODE assessment question bank and practical exam tasks."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "assessment"))

from assessment_engine import build_assessment  # noqa: E402


def main() -> None:
    assessment = build_assessment()
    print(
        "wrote assessment/question-bank.json and assessment/reports/assessment-report.md "
        f"({assessment['concept_question_count']} concept questions, "
        f"{assessment['practical_task_count']} practical tasks, status={assessment['status']})"
    )


if __name__ == "__main__":
    main()
