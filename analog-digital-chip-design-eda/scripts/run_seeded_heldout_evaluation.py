"""Run mutation closure and report a declared train/held-out split."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "benchmarks/repository_scale/seeded_mutation_evaluation.json"


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/repository-scale-m5/heldout")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    if plan.get("schema_version") != "mutation-evaluation-plan-v1":
        raise ValueError("unsupported mutation evaluation plan")
    train = set(plan["train_mutations"])
    heldout = set(plan["heldout_mutations"])
    if not train or not heldout or train & heldout:
        raise ValueError("train and held-out mutation sets must be non-empty and disjoint")
    mutation_output = args.output / "mutation-run"
    completed = subprocess.run(
        [sys.executable, "scripts/run_seeded_multi_mutation_demo.py", "--output", str(mutation_output)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    (args.output / "mutation-run.stdout.log").write_text(completed.stdout, encoding="utf-8")
    (args.output / "mutation-run.stderr.log").write_text(completed.stderr, encoding="utf-8")
    records = []
    for result_path in sorted(mutation_output.glob("*/mutation-result.json")):
        records.append(json.loads(result_path.read_text(encoding="utf-8")))
    by_id = {item["result"]["mutation_id"]: item for item in records}
    declared = train | heldout
    if set(by_id) != declared:
        raise ValueError(f"evaluation plan/result mismatch: plan={sorted(declared)} results={sorted(by_id)}")

    def score(ids: set[str]) -> dict[str, object]:
        selected = [by_id[item] for item in sorted(ids)]
        detected = sum(bool(item["result"]["detected"]) for item in selected)
        eligible = sum(bool(item["result"]["baseline_valid"]) for item in selected)
        return {"total": len(selected), "eligible": eligible, "detected": detected, "mutation_score": round(detected / eligible, 6) if eligible else None, "mutation_ids": sorted(ids)}

    report = {
        "schema_version": "mutation-heldout-evaluation-report-v1",
        "plan": str(PLAN_PATH),
        "train": score(train),
        "heldout": score(heldout),
        "mutation_run_status": "passed" if completed.returncode == 0 else "blocked",
        "status": "passed" if completed.returncode == 0 and score(train)["mutation_score"] == 1.0 and score(heldout)["mutation_score"] == 1.0 else "blocked",
        "claim_boundary": "held-out score over the declared seeded mutation plan; not evidence of generalization to unseen repositories",
    }
    report["report_sha256"] = digest(report)
    report_path = args.output / "heldout-evaluation-report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "train_score": report["train"]["mutation_score"], "heldout_score": report["heldout"]["mutation_score"], "report": str(report_path)}, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
