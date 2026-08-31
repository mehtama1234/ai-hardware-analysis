#!/usr/bin/env python3
"""Verify the speculative decoding serving report."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "speculative-decoding-serving" / "speculative-decoding-report.json"
REPORT_MD = ROOT / "speculative-decoding-serving" / "reports" / "speculative-decoding-report.md"
SITE_PAGE = ROOT / "site" / "speculative-decoding-serving.html"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/run_speculative_decoding_serving.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    scenarios = report.get("scenarios", [])
    require(report.get("status") == "speculative-decoding-ready", "speculative decoding report is not ready")
    require(report.get("scenario_count") == len(scenarios) >= 6, "scenario count mismatch")
    require(report.get("passed_scenarios", 0) >= 4, "too few passing speculative decoding scenarios")
    require(report.get("review_scenarios", 0) >= 1, "missing low-acceptance review coverage")
    require(report.get("engine_count", 0) >= 4, "missing serving engine coverage")
    require(report.get("scheduler_policy_count", 0) >= 2, "missing scheduler policy coverage")
    require(report.get("min_acceptance_rate", 1.0) < 0.50, "missing poor acceptance case")
    require(report.get("max_wasted_draft_ratio", 0.0) > 0.35, "missing wasted draft-token pressure")
    require(report.get("max_speedup_vs_baseline", 0.0) >= 2.0, "missing meaningful speculative speedup")
    require(report.get("gpu_host_promotion", {}).get("required") is True, "GPU promotion not required")
    require(REPORT_MD.exists(), "missing speculative decoding markdown report")
    for row in scenarios:
        require(row.get("draft_width", 0) >= 3, f"{row.get('scenario_id')} missing draft width")
        require(row.get("accepted_tokens_per_verify", 0) > 0, f"{row.get('scenario_id')} missing accepted-token estimate")
        require(row.get("speculative_tpot_ms", 0) > 0, f"{row.get('scenario_id')} missing TPOT estimate")
        require(row.get("estimated_output_tokens_per_second", 0) > 0, f"{row.get('scenario_id')} missing throughput")
        require(row.get("kernel_paths"), f"{row.get('scenario_id')} missing kernel paths")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE speculative decoding serving" in page, "speculative decoding site page missing title")
        require("chat-medusa-draft" in page and "low-acceptance-rollback" in page, "speculative decoding site page missing scenarios")
    facts = {
        "scenarios": report["scenario_count"],
        "passed": report["passed_scenarios"],
        "review": report["review_scenarios"],
        "engines": report["engine_count"],
        "policies": report["scheduler_policy_count"],
        "min_acceptance": report["min_acceptance_rate"],
        "max_speedup": report["max_speedup_vs_baseline"],
        "status": report["status"],
    }
    print(json.dumps({"facts": facts, "failures": []}, indent=2))
    print("GPUMODE speculative decoding serving verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
