#!/usr/bin/env python3
"""Verify the batch-1 decode vertical-slice reports without rerunning them."""

from __future__ import annotations

import json
import argparse
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports-dir", type=Path, default=HERE / "reports")
    parser.add_argument("--profiler-dir", type=Path)
    args = parser.parse_args()
    decode = json.loads((args.reports_dir / "decode-comparison.json").read_text())
    serving = json.loads((args.reports_dir / "serving-bridge.json").read_text())
    profiler_dir = args.profiler_dir or args.reports_dir
    profiler = json.loads((profiler_dir / "profiler-evidence.json").read_text())
    require(decode.get("status") == "passed", "decode comparison did not pass")
    require(decode.get("evidence_kind") in {"measured_cpu", "measured_gpu"}, "invalid decode evidence kind")
    require(decode.get("checks", {}).get("all_token_parity") is True, "decode token parity failed")
    require(decode.get("checks", {}).get("all_logit_parity") is True, "decode logit parity failed")
    require(decode.get("checks", {}).get("all_preallocated_token_parity") is True, "preallocated token parity failed")
    require(decode.get("checks", {}).get("all_preallocated_logit_parity") is True, "preallocated logit parity failed")
    rows = decode.get("rows", [])
    require(len(rows) == 3, "decode workload coverage changed")
    require(decode.get("checks", {}).get("workload_count") is True, "decode workload coverage check failed")
    require(all(len(row["cached"]["wall_ms_samples"]) == row["repeats"] for row in rows), "decode raw sample count changed")

    require(serving.get("status") == "passed", "serving bridge did not pass")
    require(serving.get("evidence_kind") in {"measured_cpu", "measured_gpu"}, "invalid serving evidence kind")
    require(serving.get("protocol", {}).get("concurrency_levels") == [1, 2, 4], "serving concurrency protocol changed")
    checks = serving.get("checks", {})
    workload_ids = ["short-context", "long-context", "long-decode"]
    keys = [f"{workload}_{level}" for workload in workload_ids for level in [1, 2, 4]]
    require(all(checks.get(f"cross_mode_output_parity_{key}") is True for key in keys), "serving output parity failed")
    require(all(row.get("accepted") == 8 for mode in ["uncached", "cached"] for row in serving[mode]["rows"]), "serving requests incomplete")
    require(all(row.get("accepted") == 8 for row in serving["preallocated"]["rows"]), "preallocated serving requests incomplete")
    require(all(checks.get(f"uncached_preallocated_output_parity_{key}") is True for key in keys), "preallocated serving output parity failed")
    require(profiler.get("status") == "passed", "profiler evidence did not pass")
    require(profiler.get("evidence_kind") in {"measured_cpu", "measured_gpu"}, "invalid profiler evidence kind")
    require(profiler.get("checks", {}).get("preallocated_cat_not_greater") is True, "preallocated profiler comparison failed")
    print(json.dumps({"status": "passed", "decode_kind": decode["evidence_kind"], "serving_kind": serving["evidence_kind"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
