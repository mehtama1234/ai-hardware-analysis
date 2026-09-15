#!/usr/bin/env python3
"""Verify modeled hybrid advantage is complete and explicitly non-authorizing."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    report = json.loads((args.package / "counterfactual_hybrid_advantage_report.json").read_text())
    failures = []
    if report.get("workload_vectors") != 162 or report.get("analog_authorized") is not False:
        failures.append("workload coverage or authorization state is unsafe")
    totals = report.get("modeled_totals", {})
    if not {"digital_reference_cost_pj", "counterfactual_hybrid_cost_pj", "enforced_route_cost_pj"} <= totals.keys():
        failures.append("modeled cost totals are incomplete")
    elif totals["enforced_route_cost_pj"] != totals["digital_reference_cost_pj"]:
        failures.append("enforced fallback route is not costed as the digital reference")
    if report.get("enforced_route") != "digital_fallback" or len(report.get("sensitivity", [])) != 12:
        failures.append("fallback route or coefficient sensitivity matrix is incomplete")
    quality = report.get("quality_risk", {})
    if (quality.get("promotion_gate_open") is not False
            or quality.get("dominant_module") != "transformer.h.0.mlp.c_proj"
            or not quality.get("combined_profile_relative_l2_by_module")):
        failures.append("quality-risk evidence is incomplete or not fail-closed")
    if not all(isinstance(row.get("beats_digital_reference"), bool) for row in report.get("sensitivity", [])):
        failures.append("sensitivity rows do not expose explicit modeled decisions")
    for source in report.get("sources", {}).values():
        path = Path(source["path"])
        if not path.is_file() or sha256(path) != source.get("sha256"):
            failures.append(f"stale source: {path}")
    boundary = report.get("claim_boundary", "")
    if "Counterfactual" not in boundary or "not measured" not in boundary:
        failures.append("claim boundary is too broad")
    result = {"status": "passed" if not failures else "failed", "failures": failures,
              "finding": "counterfactual hybrid sensitivity is complete; no hardware advantage is claimed."}
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
