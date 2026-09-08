#!/usr/bin/env python3
"""Verify the claim-scoped trained-quality matrix artifact."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPORT = HERE / "reports" / "trained-quality-matrix.json"


def verify(report: dict) -> dict[str, bool]:
    runs = report.get("runs", [])
    expected_sources = (
        HERE / "run_trained_quality_matrix.py",
        ROOT / "gpu-kernels-serving-lab/13-capstone-mini-serving-engine/neural_generator.py",
        HERE / "model_integration/tiny_transformer.py",
    )
    source_hashes = report.get("source_sha256", {})
    sources_current = all(
        source_hashes.get(str(path.relative_to(ROOT))) == hashlib.sha256(path.read_bytes()).hexdigest()
        for path in expected_sources
    )
    return {
        "status_passed": report.get("status") == "passed",
        "measured": report.get("measured") is True,
        "synthetic_scope_declared": "not production" in report.get("scope", ""),
        "matrix_cardinality": report.get("run_count") == 8 and len(runs) == 8,
        "corpora_covered": {row.get("corpus") for row in runs} == {"systems", "serving"},
        "configs_covered": {(row.get("hidden"), row.get("context")) for row in runs} == {(32, 64), (64, 96)},
        "seed_repeats": {row.get("seed") for row in runs} == {8181, 8282},
        "parity_all_cases": all(row.get("cached_full_parity") is True for row in runs),
        "quality_all_cases": all(row.get("quality_passed") is True for row in runs),
        "accuracy_matches_report": report.get("min_accuracy") == min(row["heldout_next_token_accuracy"] for row in runs),
        "sources_current": sources_current,
    }


def main() -> int:
    report = json.loads(REPORT.read_text())
    checks = verify(report)
    result = {"status": "passed" if all(checks.values()) else "failed", "checks": checks,
              "report": str(REPORT.relative_to(ROOT))}
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
