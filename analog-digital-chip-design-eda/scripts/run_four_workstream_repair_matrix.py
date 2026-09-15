#!/usr/bin/env python3
"""Run the agent-generated repair contract across existing seeded RTL bugs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import os
import hashlib
import subprocess

from verification_platform.orchestration import run_four_workstream_pipeline


ROOT = Path(__file__).resolve().parents[1]
CASES = {
    "counter": {"directory": "seeded_counter", "signal": "counter_q", "requirement_id": "REQ-COUNTER-HOLD", "observed": [[0, "x"], [5, "0"], [15, "1"]], "reference": [[0, "x"], [5, "0"], [15, "0"]]},
    "arbiter": {"directory": "seeded_arbiter", "signal": "grant", "requirement_id": "REQ-ARB-ONEHOT", "observed": [[0, "0"], [1, "0"]], "reference": [[0, "0"], [1, "2"]]},
    "decoder": {"directory": "seeded_decoder", "signal": "decode", "requirement_id": "REQ-DEC-OPCODE-2", "observed": [[0, "0"], [1, "0"]], "reference": [[0, "0"], [1, "4"]]},
    "fifo": {"directory": "seeded_fifo", "signal": "count", "requirement_id": "REQ-FIFO-WRITE", "observed": [[0, "0"], [1, "3"]], "reference": [[0, "0"], [1, "2"]]},
}


def verify_matrix_report(path: str | Path) -> dict[str, object]:
    """Verify the matrix self-digest and required per-design evidence fields."""
    report_path = Path(path)
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    supplied = payload.pop("matrix_sha256", None)
    expected = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    errors = []
    if supplied != expected:
        errors.append("matrix self-digest mismatch")
    records = payload.get("records", [])
    if not isinstance(records, list) or not records:
        errors.append("matrix has no records")
    for record in records if isinstance(records, list) else []:
        for key in ("candidate_sha256", "retest_sha256", "candidate_path", "retest_path", "requirement_id"):
            if not record.get(key):
                errors.append(f"record {record.get('design', 'unknown')} is missing {key}")
        for key in ("candidate_path", "retest_path"):
            if record.get(key) and not Path(record[key]).is_file():
                errors.append(f"record {record.get('design', 'unknown')} evidence path is missing: {record[key]}")
    return {"valid": not errors, "errors": errors, "matrix_sha256": supplied}


def run_matrix(output: str | Path, *, selected: list[str] | None = None) -> dict[str, object]:
    root = Path(output).resolve()
    root.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment.setdefault("VERIFICATION_LLM_COMMAND", f"python3 {ROOT / 'scripts/mock_llm_backend.py'}")
    prior = os.environ.get("VERIFICATION_LLM_COMMAND")
    os.environ["VERIFICATION_LLM_COMMAND"] = environment["VERIFICATION_LLM_COMMAND"]
    names = selected or list(CASES)
    records = []
    try:
        for name in names:
            case = CASES[name]
            design = ROOT / "benchmarks" / case["directory"]
            run_root = root / name
            source = design / ("counter.sv" if name == "counter" else f"{name}.sv")
            baseline_root = root / name / "baseline"
            baseline = subprocess.run(
                ["python3", str(ROOT / "scripts" / "run_iverilog_case.py"), str(source.resolve()), str((design / "tb.sv").resolve()), "--run-root", str(baseline_root.resolve())],
                capture_output=True, text=True, check=False,
            )
            baseline_stdout = (baseline_root / "stdout.log").read_text(encoding="utf-8") if (baseline_root / "stdout.log").is_file() else ""
            if "FAIL" not in baseline_stdout or not (baseline_root / "waveform.vcd").is_file():
                records.append({"design": name, "status": "blocked", "baseline_status": "blocked", "baseline_returncode": baseline.returncode, "baseline_path": str(baseline_root.resolve())})
                continue
            result = run_four_workstream_pipeline(
                design / "spec.md", [source], top=name,
                protocol_plan=ROOT / "benchmarks" / "protocol_execution" / "protocol_plan.json",
                command=["python3", "-c", "print('matrix baseline')"], tool="python",
                run_root=run_root, source_revision=f"repair-matrix-{name}-v1",
                debug_waveform=baseline_root / "waveform.vcd", debug_rtl=source,
                debug_signal=case["signal"], debug_observed=[tuple(item) for item in case["observed"]],
                debug_reference=[tuple(item) for item in case["reference"]],
                debug_requirement_id=case["requirement_id"],
                debug_for_evidence=[f"{case['signal']} diverges from the specification trace"],
                debug_against_evidence=["the RTL compiles and the failing expression is syntactically valid"],
                repair_agent_backend="local",
                approved_repair={
                    "source": str(source.resolve()),
                    "destination": str((run_root / "debug" / "approved-repair" / source.name).resolve()),
                    "command": ["python3", str((ROOT / "scripts" / "run_iverilog_retest.py").resolve()), str(source.resolve()), str((design / "tb.sv").resolve())],
                    "proposal_from_agent": True, "human_approved": True,
                },
            )
            candidate = result["repair_agent"].get("patch_candidate", {})
            retest = result["repair_retest"]
            records.append({
                "design": name, "status": result["status"],
                "baseline_status": "failed_as_expected", "baseline_returncode": baseline.returncode,
                "baseline_path": str(baseline_root.resolve()),
                "candidate": candidate.get("status"),
                "candidate_sha256": candidate.get("candidate_sha256"),
                "candidate_path": str((run_root / "four-workstream-result.json").resolve()),
                "retest": retest["status"],
                "retest_sha256": retest.get("result_sha256"),
                "retest_path": str((run_root / "debug" / "approved-repair-retest" / "repair-retest.json").resolve()),
                "source_unchanged": retest.get("original_source_unchanged"),
                "requirement_id": retest.get("proposal", {}).get("requirement_id"),
            })
    finally:
        if prior is None:
            os.environ.pop("VERIFICATION_LLM_COMMAND", None)
        else:
            os.environ["VERIFICATION_LLM_COMMAND"] = prior
    report = {"schema_version": "four-workstream-repair-matrix-v1", "status": "passed" if records and all(item["status"] == "passed" and item["candidate"] == "review_required" and item["retest"] == "passed" and item["source_unchanged"] is True and item["candidate_sha256"] and item["retest_sha256"] and item["requirement_id"] for item in records) else "blocked", "records": records, "case_count": len(records), "claim_boundary": "multi-design copy-only repair/retest evidence; not autonomous approval or release"}
    report["matrix_sha256"] = hashlib.sha256(json.dumps(report, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    (root / "matrix-result.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--design", action="append", choices=tuple(CASES))
    args = parser.parse_args()
    report = run_matrix(args.output, selected=args.design)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
