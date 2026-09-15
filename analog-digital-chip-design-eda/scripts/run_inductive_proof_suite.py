"""Run and classify a mixed seeded temporal-induction proof suite."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from verification_platform.formal import run_yosys_inductive_proof


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/repository-scale-m3/inductive-suite")
    args = parser.parse_args()
    suite = json.loads((ROOT / "benchmarks/repository_scale/inductive_proof_suite.json").read_text(encoding="utf-8"))
    results = []
    for target in suite["targets"]:
        result = run_yosys_inductive_proof([ROOT / source for source in target["sources"]], top=target["top"], run_root=args.output / target["proof_id"], source_revision="repository-scale-m3-v1", max_steps=4)
        results.append({"proof_id": target["proof_id"], "expected_status": target["expected_status"], "observed_status": result["status"], "method": result["method"], "result": str((args.output / target["proof_id"] / "inductive-proof-result.json").relative_to(args.output))})
    report = {
        "schema_version": "inductive-proof-suite-report-v1",
        "targets": results,
        "expected_statuses_match": all(item["expected_status"] == item["observed_status"] for item in results),
        "proofs_proven": sum(item["observed_status"] == "proven" for item in results),
        "counterexamples": sum(item["observed_status"] == "counterexample" for item in results),
        "claim_boundary": suite["claim_boundary"],
    }
    report["report_sha256"] = hashlib.sha256(json.dumps(report, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "inductive-proof-suite-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed" if report["expected_statuses_match"] else "blocked", "proofs_proven": report["proofs_proven"], "counterexamples": report["counterexamples"], "report": str(args.output / "inductive-proof-suite-report.json")}, sort_keys=True))
    return 0 if report["expected_statuses_match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
