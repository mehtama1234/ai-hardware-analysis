"""Prove three repaired multi-cycle seeded models with Yosys induction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from verification_platform.formal import run_yosys_inductive_proof


CASES = [
    {
        "proof_id": "constant-invariant",
        "source": "benchmarks/repository_scale/inductive_constant.sv",
        "top": "constant_invariant",
        "formal": None,
    },
    {
        "proof_id": "counter-hold-repaired",
        "source": "benchmarks/seeded_counter/counter.sv",
        "formal": "benchmarks/seeded_counter/formal_model_check.sv",
        "top": "formal_model_check",
        "old": "    else\n      counter_q <= counter_q + 4'd1; // SEEDED_BUG: missing enable guard",
        "new": "    else if (enable)\n      counter_q <= counter_q + 4'd1; // SEEDED_BUG: missing enable guard",
    },
    {
        "proof_id": "timeout-boundary-repaired",
        "source": "benchmarks/seeded_timeout/timeout.sv",
        "formal": "benchmarks/seeded_timeout/formal_model_check.sv",
        "top": "formal_timeout_model_check",
        "old": "  assign timed_out = count >= 3'd4;",
        "new": "  assign timed_out = count >= 3'd3;",
    },
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/repository-scale-m3/repaired-inductive-suite")
    args = parser.parse_args()
    results = []
    with tempfile.TemporaryDirectory(prefix="repaired-inductive-suite-") as directory:
        staging = Path(directory)
        for case in CASES:
            source = ROOT / case["source"]
            dut = staging / f"{case['proof_id']}-dut.sv"
            text = source.read_text(encoding="utf-8")
            if case.get("old"):
                if text.count(case["old"]) != 1:
                    raise RuntimeError(f"repair anchor missing or ambiguous: {case['proof_id']}")
                text = text.replace(case["old"], case["new"])
            dut.write_text(text, encoding="utf-8")
            sources = [dut]
            if case.get("formal"):
                formal = staging / f"{case['proof_id']}-formal.sv"
                formal.write_text((ROOT / case["formal"]).read_text(encoding="utf-8"), encoding="utf-8")
                sources.append(formal)
            result = run_yosys_inductive_proof(sources, top=case["top"], run_root=args.output / case["proof_id"], source_revision=f"{case['proof_id']}-repair-v1", max_steps=8)
            results.append({"proof_id": case["proof_id"], "status": result["status"], "method": result["method"], "source_sha256": hashlib.sha256(dut.read_bytes()).hexdigest()})
    report = {"schema_version": "repaired-inductive-suite-report-v1", "results": results, "all_proven": all(item["status"] == "proven" for item in results), "claim_boundary": "inductive proof for three disposable repaired seeded models; not project-wide formal completeness"}
    report["report_sha256"] = hashlib.sha256(json.dumps(report, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "repaired-inductive-suite-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed" if report["all_proven"] else "blocked", "proven": sum(item["status"] == "proven" for item in results), "total": len(results), "report": str(args.output / "repaired-inductive-suite-report.json")}, sort_keys=True))
    return 0 if report["all_proven"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
