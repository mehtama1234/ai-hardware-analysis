"""Run an actual Icarus/VVP mutation-detection demonstration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from verification_platform.mutation import run_mutation, summarize_mutations, validate_mutation_suite


ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "benchmarks/repository_scale/seeded_counter_mutation_suite.json"
BUGGY = "      counter_q <= counter_q + 4'd1; // SEEDED_BUG: missing enable guard"
GOOD = "      if (enable) counter_q <= counter_q + 4'd1; // SEEDED_BUG: missing enable guard"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/repository-scale-m2/seeded-counter")
    args = parser.parse_args()
    suite = json.loads(SUITE.read_text(encoding="utf-8"))
    validate_mutation_suite(suite)
    mutation = suite["mutations"][0]
    with tempfile.TemporaryDirectory(prefix="mutation-demo-") as directory:
        staging = Path(directory)
        roots = {name: staging / name for name in ("canonical", "baseline", "candidate")}
        for root in roots.values():
            (root / "scripts").mkdir(parents=True)
            (root / "benchmarks/seeded_counter").mkdir(parents=True)
            shutil.copy2(ROOT / "scripts/run_seeded_counter_check.py", root / "scripts/run_seeded_counter_check.py")
            for name in ("counter.sv", "tb.sv"):
                shutil.copy2(ROOT / "benchmarks/seeded_counter" / name, root / "benchmarks/seeded_counter" / name)
            source = root / "benchmarks/seeded_counter/counter.sv"
            text = source.read_text(encoding="utf-8")
            if text.count(BUGGY) != 1:
                raise RuntimeError("seeded counter source did not contain the expected defect")
            source.write_text(text.replace(BUGGY, GOOD), encoding="utf-8")
        record = run_mutation(mutation, canonical_root=roots["canonical"], baseline_root=roots["baseline"], candidate_root=roots["candidate"], output_root=args.output)
    report = summarize_mutations([record])
    (args.output / "mutation-closure-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "mutation_score": report["mutation_score"], "detected": report["detected_mutations"], "false_passes": report["false_pass_count"], "report": str(args.output / "mutation-closure-report.json")}, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
