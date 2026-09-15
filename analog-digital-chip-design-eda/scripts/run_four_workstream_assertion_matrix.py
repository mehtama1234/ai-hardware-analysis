#!/usr/bin/env python3
"""Exercise specification-grounded assertion agents across seeded RTL cases."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from verification_platform.orchestration import run_four_workstream_pipeline


CASES = {
    "counter": ("seeded_counter", "counter.sv", "spec.md"),
    "arbiter": ("seeded_arbiter", "arbiter.sv", "assertion_matrix_spec.md"),
    "decoder": ("seeded_decoder", "decoder.sv", "spec.md"),
    "fifo": ("seeded_fifo", "fifo.sv", "spec.md"),
}
PROTOCOL = ROOT / "benchmarks" / "protocol_execution" / "protocol_plan.json"


def verify_matrix_report(path: str | Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    supplied = payload.pop("matrix_sha256", None)
    expected = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    errors: list[str] = []
    if supplied != expected:
        errors.append("matrix self-digest mismatch")
    records = payload.get("records", [])
    if not isinstance(records, list) or not records:
        errors.append("matrix has no records")
    for record in records if isinstance(records, list) else []:
        for key in ("result_path", "agent_path", "validation_path", "requirements"):
            if not record.get(key):
                errors.append(f"record {record.get('design', 'unknown')} is missing {key}")
        for key in ("result_path", "agent_path", "validation_path"):
            if record.get(key) and not Path(record[key]).is_file():
                errors.append(f"record {record.get('design', 'unknown')} evidence path is missing: {record[key]}")
    return {"valid": not errors, "errors": errors, "matrix_sha256": supplied}


def run_matrix(output: str | Path, *, selected: list[str] | None = None) -> dict[str, object]:
    root = Path(output).resolve()
    root.mkdir(parents=True, exist_ok=True)
    prior = os.environ.get("VERIFICATION_LLM_COMMAND")
    os.environ["VERIFICATION_LLM_COMMAND"] = f"python3 {ROOT / 'scripts/mock_llm_backend.py'}"
    records: list[dict[str, object]] = []
    try:
        for name in selected or list(CASES):
            directory, rtl_name, spec_name = CASES[name]
            design = ROOT / "benchmarks" / directory
            run_root = root / name
            result = run_four_workstream_pipeline(
                design / spec_name, [design / rtl_name], top=name,
                protocol_plan=PROTOCOL, command=["python3", "-c", "print('assertion-matrix')"],
                tool="python", run_root=run_root, source_revision=f"assertion-matrix-{name}-v1",
                assertion_agent_backend="local",
            )
            agent = result["assertion_agent"]
            validation = result["assertion_validation"]
            records.append({
                "design": name, "status": result["status"],
                "agent_status": agent.get("status"),
                "validation_status": validation.get("status"),
                "requirements": agent.get("requirements", []),
                "result_path": str((run_root / "four-workstream-result.json").resolve()),
                "agent_path": str((run_root / "auto-formalization" / "agent-assertion-result.json").resolve()),
                "validation_path": str((run_root / "auto-formalization" / "validation-result.json").resolve()),
            })
    finally:
        if prior is None:
            os.environ.pop("VERIFICATION_LLM_COMMAND", None)
        else:
            os.environ["VERIFICATION_LLM_COMMAND"] = prior
    passed = bool(records) and all(
        item["status"] == "passed" and item["agent_status"] == "available"
        and item["validation_status"] == "passed" and item["requirements"]
        and Path(str(item["result_path"])).is_file()
        and Path(str(item["agent_path"])).is_file()
        and Path(str(item["validation_path"])).is_file()
        for item in records
    )
    report: dict[str, object] = {
        "schema_version": "four-workstream-assertion-matrix-v1",
        "status": "passed" if passed else "blocked", "records": records,
        "case_count": len(records),
        "claim_boundary": "multi-design specification-grounded assertion-agent admission and compilation evidence; not formal proof or signoff",
    }
    report["matrix_sha256"] = hashlib.sha256(json.dumps(report, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
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
