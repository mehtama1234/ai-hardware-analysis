"""Build a truthful draft scorecard from the multi-design pilot evidence."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path


METRICS = [
    ("triage_latency", "seconds"),
    ("root_cause_usefulness", "fraction"),
    ("reproduction_time", "seconds"),
    ("evidence_completeness", "fraction"),
    ("manual_effort", "actions"),
    ("closure_integrity", "fraction"),
]

def _digest(payload: dict) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def build_scorecard(run_root: Path) -> dict:
    summary_path = run_root / "pilot-summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    count = int(summary.get("design_count", 0))
    complete = bool(summary.get("metrics", {}).get("all_artifacts_verified")) and int(summary.get("metrics", {}).get("diagnosis_evidence_complete", 0)) == count
    closure = count > 0 and int(summary.get("passed_retests", 0)) == count and bool(summary.get("metrics", {}).get("all_artifacts_verified"))
    evidence = ["benchmarks/multi_design_pilot/runs/latest/pilot-summary.json", "benchmarks/multi_design_pilot/runs/latest/session-ledger.json", "benchmarks/multi_design_pilot/runs/latest/pilot-release-manifest.json"]
    evidence_digests = {path: sha256((run_root / Path(path).name).read_bytes()).hexdigest() for path in evidence}
    values = {"evidence_completeness": 1.0 if complete else 0.0, "closure_integrity": 1.0 if closure else 0.0}
    metrics = [{"name": name, "unit": unit, "baseline_median": None, "workbench_median": values.get(name), "evidence": evidence if values.get(name) is not None else [], "target_minimum": 1.0 if name in {"evidence_completeness", "closure_integrity"} else None, "target_reduction": 0.30 if name in {"triage_latency", "manual_effort"} else 0.25 if name == "reproduction_time" else None} for name, unit in METRICS]
    result = {"schema_version": "verification-pilot-scorecard-v1", "pilot": {"customer": "open-source-reference", "project": "multi-design-pilot", "baseline_window": "not collected", "workbench_window": "multi_design_pilot/runs/latest", "sample_size": count}, "metrics": metrics, "evidence_sha256": evidence_digests, "review": {"engineer_labels": [], "lead_reviewer": "", "signed_at": None, "receipt_sha256": None}, "claim_boundary": "Draft open-source evidence only; baseline, human labels, and customer pilot measurements are not collected. This does not establish exhaustive functional coverage, formal completeness, silicon correctness, or replacement of qualified EDA signoff."}
    result["scorecard_sha256"] = _digest(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_root", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    scorecard = build_scorecard(args.run_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(scorecard, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
