"""Turn an incomplete coverage report into a reviewable next-test proposal."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from verification_platform.closure_lab import propose_next_test


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage", type=Path, default=ROOT / "benchmarks/seeded_counter/four-workstream-coverage-report.json")
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/repository-scale-m2/coverage-gap-agent")
    args = parser.parse_args()
    coverage = json.loads(args.coverage.read_text(encoding="utf-8"))
    plan = propose_next_test(coverage, source_revision="seeded-counter-v1", evidence=[str(args.coverage.relative_to(ROOT)), "benchmarks/seeded_counter/spec.md"])
    result = {"schema_version": "coverage-gap-agent-result-v1", "coverage": coverage, "status": "converged" if plan is None else "review_required", "next_test": plan.record() if plan else None, "claim_boundary": "reviewable next-test proposal; no coverage or verification closure until a new executable run"}
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "coverage-gap-agent.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "target": plan.target_kind if plan else None, "test_id": plan.test_id if plan else None, "report": str(args.output / "coverage-gap-agent.json")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
