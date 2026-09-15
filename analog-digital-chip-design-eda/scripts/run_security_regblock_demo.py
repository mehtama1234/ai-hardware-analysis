"""Run a red/blue security task over the seeded register block."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from verification_platform.mutation import run_mutation, validate_mutation_suite
from verification_platform.security_closure import evaluate_security_task, validate_security_suite


ROOT = Path(__file__).resolve().parents[1]
SUITE_PATH = ROOT / "benchmarks/repository_scale/security_regblock_suite.json"
OLD = "      if (addr == 2'd0) reg0 <= wdata;"
NEW = "      if (addr == 2'd0) reg0 <= wdata;\n      else reg0 <= wdata; // RED_TEAM: unauthorized nonzero address write"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/repository-scale-m4/security-regblock")
    args = parser.parse_args()
    security_suite = json.loads(SUITE_PATH.read_text(encoding="utf-8"))
    validate_security_suite(security_suite)
    task = security_suite["tasks"][0]
    mutation = {
        "mutation_id": task["task_id"],
        "source_file": "benchmarks/seeded_regblock/regblock.sv",
        "from": OLD,
        "to": NEW,
        "command": ["python3", "scripts/run_seeded_counter_check.py", "benchmarks/seeded_regblock/regblock.sv", "benchmarks/seeded_regblock/tb.sv"],
    }
    validate_mutation_suite({"schema_version": "mutation-suite-v1", "mutations": [mutation]})
    with tempfile.TemporaryDirectory(prefix="security-regblock-demo-") as directory:
        staging = Path(directory)
        roots = {name: staging / name for name in ("canonical", "baseline", "candidate")}
        for root in roots.values():
            (root / "scripts").mkdir(parents=True)
            shutil.copy2(ROOT / "scripts/run_seeded_counter_check.py", root / "scripts/run_seeded_counter_check.py")
            for name in ("regblock.sv", "tb.sv"):
                target = root / "benchmarks/seeded_regblock" / name
                target.parent.mkdir(parents=True, exist_ok=True)
                source = ROOT / "benchmarks/seeded_regblock" / name
                text = source.read_text(encoding="utf-8")
                if name == "regblock.sv":
                    buggy = "      if (addr == 2'd0) reg0 <= wdata;\n      else reg0 <= wdata; // SEEDED_BUG: nonzero addresses must be ignored"
                    if text.count(buggy) != 1:
                        raise RuntimeError("seeded regblock source normalization anchor is missing")
                    text = text.replace(buggy, OLD)
                target.write_text(text, encoding="utf-8")
        mutation_record = run_mutation(mutation, canonical_root=roots["canonical"], baseline_root=roots["baseline"], candidate_root=roots["candidate"], output_root=args.output / "red-blue-mutation")
    mutation_result = mutation_record["result"]
    signoff = evaluate_security_task(task, detected=mutation_result["detected"], localized=True, repaired_copy_passed=mutation_result["baseline_valid"], regression_passed=mutation_result["baseline_valid"], evidence=["red-blue-mutation/mutation-result.json", "red-blue-mutation/baseline.stdout.log", "red-blue-mutation/mutant.stdout.log"])
    (args.output / "security-signoff-record.json").write_text(json.dumps(signoff, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": signoff["status"], "detected": signoff["detected"], "localized": signoff["localized"], "machine_checks_passed": signoff["machine_checks_passed"], "human_review": signoff["human_review"], "report": str(args.output / "security-signoff-record.json")}, sort_keys=True))
    return 0 if signoff["status"] == "review_required" else 1


if __name__ == "__main__":
    raise SystemExit(main())
