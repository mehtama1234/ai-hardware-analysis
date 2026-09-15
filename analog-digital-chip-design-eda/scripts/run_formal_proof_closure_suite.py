"""Run bounded, inductive, assumption, and closure checks on three designs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from verification_platform.formal import run_yosys_assertion_proof, run_yosys_antecedent_reachability, run_yosys_inductive_proof
from verification_platform.proof_closure import build_assumption_audit, evaluate_proof_closure


ROOT = Path(__file__).resolve().parents[1]


CASES = [
    {"property_id": "constant-invariant", "source": "benchmarks/repository_scale/inductive_constant.sv", "top": "constant_invariant", "formal": None},
    {"property_id": "counter-hold-repaired", "source": "benchmarks/seeded_counter/counter.sv", "top": "formal_model_check", "formal": "benchmarks/seeded_counter/formal_model_check.sv", "old": "    else\n      counter_q <= counter_q + 4'd1; // SEEDED_BUG: missing enable guard", "new": "    else if (enable)\n      counter_q <= counter_q + 4'd1; // SEEDED_BUG: missing enable guard"},
    {"property_id": "timeout-boundary-repaired", "source": "benchmarks/seeded_timeout/timeout.sv", "top": "formal_timeout_model_check", "formal": "benchmarks/seeded_timeout/formal_model_check.sv", "old": "  assign timed_out = count >= 3'd4;", "new": "  assign timed_out = count >= 3'd3;"},
]


def _digest(body: dict) -> str:
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/repository-scale-m3/formal-proof-closure")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    results = []
    with tempfile.TemporaryDirectory(prefix="formal-proof-closure-") as directory:
        staging = Path(directory)
        for case in CASES:
            source = ROOT / case["source"]
            dut = staging / f"{case['property_id']}-dut.sv"
            text = source.read_text(encoding="utf-8")
            if case.get("old"):
                if text.count(case["old"]) != 1:
                    raise RuntimeError(f"repair anchor missing or ambiguous: {case['property_id']}")
                text = text.replace(case["old"], case["new"], 1)
            dut.write_text(text, encoding="utf-8")
            sources = [dut]
            if case.get("formal"):
                formal = staging / f"{case['property_id']}-formal.sv"
                formal.write_text((ROOT / case["formal"]).read_text(encoding="utf-8"), encoding="utf-8")
                sources.append(formal)
            revision = f"{case['property_id']}-closure-v1"
            bounded = run_yosys_assertion_proof(sources, top=case["top"], run_root=args.output / case["property_id"] / "bounded", sequence=8, source_revision=revision, timeout_seconds=120)
            inductive = run_yosys_inductive_proof(sources, top=case["top"], run_root=args.output / case["property_id"] / "inductive", source_revision=revision, max_steps=8, timeout_seconds=120)
            reachable = run_yosys_antecedent_reachability(sources, top=case["top"], antecedent="rst", allowed_signals={"rst"}, run_root=args.output / case["property_id"] / "assumption-reachability", sequence=8, source_revision=revision, timeout_seconds=120)
            reach_body = {"assumption_id": "reset", **{key: value for key, value in reachable.items() if key != "result_sha256"}}
            reach_body["result_sha256"] = _digest(reach_body)
            assumptions = [{"id": "reset", "formula": "rst"}]
            audit = build_assumption_audit(assumptions, [reach_body], source_revision=revision)
            closure = evaluate_proof_closure(property_id=case["property_id"], source_revision=revision, bounded_status=str(bounded["status"]), inductive_status=str(inductive["status"]), assumptions=assumptions, assumption_audit=audit, reachable_state_status="passed" if reachable["status"] == "reachable" else "blocked", vacuity_status="active" if bounded["assertion_count"] > 0 and reachable["status"] == "reachable" else "unknown", counterexample=None if inductive["status"] == "proven" else {"status": inductive["status"]})
            results.append({"property_id": case["property_id"], "bounded": bounded["status"], "inductive": inductive["status"], "assumption_audit": audit["status"], "reachable": reachable["status"], "proof_status": closure["proof_status"], "closure": f"{case['property_id']}/formal-closure.json"})
            (args.output / case["property_id"] / "formal-closure.json").write_text(json.dumps({"bounded": bounded, "inductive": inductive, "assumption_reachability": reachable, "assumption_audit": audit, "closure": closure}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = {"schema_version": "formal-proof-closure-suite-report-v1", "results": results, "total": len(results), "all_proven": all(item["proof_status"] == "proven" for item in results), "claim_boundary": "bounded and temporal-induction closure for three disposable repaired seeded models with reset-assumption reachability; not project-wide completeness or silicon signoff"}
    report["report_sha256"] = _digest(report)
    (args.output / "formal-proof-closure-suite-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed" if report["all_proven"] else "blocked", "total": report["total"], "proven": sum(item["proof_status"] == "proven" for item in results), "report": str(args.output / "formal-proof-closure-suite-report.json")}, sort_keys=True))
    return 0 if report["all_proven"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
