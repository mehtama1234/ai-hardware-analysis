#!/usr/bin/env python3
"""Collect a traceable before/after pilot scorecard from observation JSON."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import random
from statistics import median
import math

from deployment.pilot_scorecard import REQUIRED_METRICS


REQUIRED_FIELDS = ("failure_id", "category", "triage_seconds", "reproduction_seconds", "manual_actions", "root_cause_actionable", "evidence_complete", "closure_integrity")
REQUIRED_CATEGORIES = {"simulation", "lint", "formal", "regression"}


def _observations(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError(f"{path} must contain a non-empty JSON array")
    if any(not isinstance(item, dict) or any(field not in item for field in REQUIRED_FIELDS) for item in payload):
        raise ValueError(f"{path} contains an observation missing required fields")
    for item in payload:
        category = str(item["category"]).lower()
        if category not in REQUIRED_CATEGORIES:
            raise ValueError(f"{path} contains unsupported category")
        for field in ("triage_seconds", "reproduction_seconds", "manual_actions"):
            value = item[field]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)) or float(value) < 0:
                raise ValueError(f"{path} contains invalid {field}")
        for field in ("root_cause_actionable", "evidence_complete", "closure_integrity"):
            if not isinstance(item[field], bool):
                raise ValueError(f"{path} contains non-boolean {field}")
    ids = [str(item["failure_id"]) for item in payload]
    if len(set(ids)) != len(ids) or any(not value.strip() for value in ids):
        raise ValueError(f"{path} failure_id values must be unique and non-empty")
    return payload


def _fraction(rows: list[dict], field: str) -> float:
    return round(sum(bool(row[field]) for row in rows) / len(rows), 6)


def _wilson(rows: list[dict], field: str) -> list[float]:
    successes = sum(bool(row[field]) for row in rows)
    n = len(rows)
    z = 1.96
    center = (successes + z * z / 2) / (n + z * z)
    margin = z * ((successes * (n - successes) / n + z * z / 4) ** 0.5) / (n + z * z)
    return [round(max(0.0, center - margin), 6), round(min(1.0, center + margin), 6)]


def _median_interval(rows: list[dict], field: str) -> list[float]:
    values = [float(row[field]) for row in rows]
    rng = random.Random(0)
    samples = sorted(median(rng.choice(values) for _ in values) for _ in range(1000))
    return [round(samples[25], 6), round(samples[974], 6)]


def collect(baseline_path: Path, workbench_path: Path, *, output: Path, customer: str, project: str) -> dict:
    baseline, workbench = _observations(baseline_path), _observations(workbench_path)
    baseline_ids, workbench_ids = {str(row["failure_id"]) for row in baseline}, {str(row["failure_id"]) for row in workbench}
    if baseline_ids != workbench_ids:
        raise ValueError("baseline and workbench samples must contain the same failure IDs")
    categories = {str(row["category"]).lower() for row in workbench}
    if not REQUIRED_CATEGORIES.issubset(categories):
        raise ValueError("workbench sample must include simulation, lint, formal, and regression categories")
    blocked = sum(str(row["category"]).lower() in {"formal-timeout", "timeout", "blocked"} or row.get("blocked_or_timeout") is True for row in workbench)
    if len(workbench) < 20 or blocked < 3:
        raise ValueError("pilot requires at least 20 matched observations including 3 blocked/timeout cases")
    def values(rows: list[dict], field: str) -> float:
        return float(median(float(row[field]) for row in rows))
    metrics = [
        ("triage_latency", "seconds", "triage_seconds", None, 0.30),
        ("root_cause_usefulness", "fraction", "root_cause_actionable", 0.80, None),
        ("reproduction_time", "seconds", "reproduction_seconds", None, 0.25),
        ("evidence_completeness", "fraction", "evidence_complete", 1.0, None),
        ("manual_effort", "actions", "manual_actions", None, 0.30),
        ("closure_integrity", "fraction", "closure_integrity", 1.0, None),
    ]
    metric_rows = []
    for name, unit, field, minimum, reduction in metrics:
        fraction = unit == "fraction"
        baseline_value = _fraction(baseline, field) if fraction else values(baseline, field)
        workbench_value = _fraction(workbench, field) if fraction else values(workbench, field)
        baseline_interval = _wilson(baseline, field) if fraction else _median_interval(baseline, field)
        workbench_interval = _wilson(workbench, field) if fraction else _median_interval(workbench, field)
        metric_rows.append({"name": name, "unit": unit, "baseline_median": baseline_value, "baseline_confidence_95": baseline_interval, "workbench_median": workbench_value, "workbench_confidence_95": workbench_interval, "evidence": [str(baseline_path), str(workbench_path)], **({"target_minimum": minimum} if minimum is not None else {"target_reduction": reduction})})
    evidence = [str(baseline_path), str(workbench_path)]
    result = {"schema_version": "verification-pilot-scorecard-v1", "pilot": {"customer": customer, "project": project, "baseline_window": str(baseline_path), "workbench_window": str(workbench_path), "sample_size": len(workbench), "blocked_or_timeout_count": blocked, "categories": sorted(categories)}, "metrics": metric_rows, "evidence_sha256": {str(path): sha256(path.read_bytes()).hexdigest() for path in (baseline_path, workbench_path)}, "review": {"engineer_labels": [], "lead_reviewer": "", "signed_at": None, "receipt_sha256": None}, "claim_boundary": "Measured workflow observations only; this draft requires independent engineer labels and lead approval and does not establish exhaustive coverage, formal completeness, silicon correctness, or EDA signoff replacement."}
    result["scorecard_sha256"] = sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("workbench", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--customer", required=True)
    parser.add_argument("--project", required=True)
    args = parser.parse_args()
    print(json.dumps(collect(args.baseline, args.workbench, output=args.output, customer=args.customer, project=args.project), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
