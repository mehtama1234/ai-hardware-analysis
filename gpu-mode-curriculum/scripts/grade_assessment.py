#!/usr/bin/env python3
"""Grade the generated assessment bank against current artifact evidence."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "assessment"))

from assessment_engine.grader import grade_assessment  # noqa: E402


def main() -> None:
    report = grade_assessment()
    print(
        "wrote assessment/grading-report.json and assessment/reports/grading-report.md "
        f"({report['score']}/{report['max_score']} points, status={report['status']})"
    )


if __name__ == "__main__":
    main()
