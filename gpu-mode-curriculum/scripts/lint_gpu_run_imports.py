#!/usr/bin/env python3
"""Lint GPU run fixtures and imports."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gpu-runs"))

from gpu_runs.import_linter import lint_imports  # noqa: E402


def main() -> int:
    report = lint_imports()
    print(
        "wrote gpu-runs/import-lint-report.json and gpu-runs/reports/import-lint-report.md "
        f"({report['status']}, {report['error_count']} errors, {report['warning_count']} warnings)"
    )
    return 0 if report["status"] == "lint-clean" else 1


if __name__ == "__main__":
    raise SystemExit(main())
