"""Run the next-stage verification slices in a fresh Colab/runtime bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def run(name: str, command: list[str], output: Path, env: dict[str, str]) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, check=False)
    (output / f"{name}.stdout.log").write_text(completed.stdout, encoding="utf-8")
    (output / f"{name}.stderr.log").write_text(completed.stderr, encoding="utf-8")
    result: dict[str, Any] = {"name": name, "command": command, "returncode": completed.returncode, "status": "passed" if completed.returncode == 0 else "blocked"}
    for line in reversed(completed.stdout.splitlines()):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            result["result"] = payload
            break
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--agent-backend", choices=("mock", "local"), default="local")
    parser.add_argument("--require-real-agent", action="store_true")
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--max-tasks", type=int, default=None)
    args = parser.parse_args()
    if args.start_index < 0 or args.max_tasks is not None and args.max_tasks <= 0:
        raise SystemExit("--start-index must be nonnegative and --max-tasks must be positive")
    output = (args.output or Path(tempfile.mkdtemp(prefix="next-stage-colab-"))).resolve()
    output.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    if args.agent_backend == "mock":
        environment["VERIFICATION_LLM_COMMAND"] = f"{sys.executable} {ROOT / 'scripts/mock_repository_agent_backend.py'}"
    elif not environment.get("VERIFICATION_LLM_COMMAND") and not environment.get("VERIFICATION_LLM_BATCH_COMMAND"):
        if args.require_real_agent:
            report = {"schema_version": "next-stage-colab-report-v1", "status": "blocked", "reason": "VERIFICATION_LLM_COMMAND is not configured for a real agent backend"}
            (output / "next-stage-colab-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(report, sort_keys=True))
            return 1
        environment["VERIFICATION_LLM_COMMAND"] = f"{sys.executable} {ROOT / 'scripts/mock_repository_agent_backend.py'}"
        args.agent_backend = "mock-fallback"

    commands = [
        ("heldout-mutation-evaluation", [sys.executable, "scripts/run_seeded_heldout_evaluation.py", "--output", str(output / "heldout")]),
        ("coverage-closure", [sys.executable, "scripts/run_seeded_coverage_closure.py", "--output", str(output / "coverage")]),
        ("repaired-induction", [sys.executable, "scripts/run_repaired_inductive_suite.py", "--output", str(output / "induction")]),
        ("security-red-blue", [sys.executable, "scripts/run_security_regblock_demo.py", "--output", str(output / "security")]),
        ("repository-agent-matrix", [sys.executable, "scripts/run_seeded_repository_agent_matrix.py", "--backend", args.agent_backend, "--output", str(output / "agent-matrix")]),
        ("repository-agent-matrix-integrity", [sys.executable, "scripts/check_seeded_repository_agent_matrix.py", str(output / "agent-matrix" / "repository-agent-matrix-report.json")]),
        ("agent-repair-closure", [sys.executable, "scripts/run_seeded_agent_repair_closure.py", "--backend", args.agent_backend, "--start-index", str(args.start_index), *( ["--max-tasks", str(args.max_tasks)] if args.max_tasks is not None else []), "--output", str(output / "agent-repair-closure")]),
        ("agent-causal-closure-integrity", [sys.executable, "scripts/check_seeded_agent_causal_closure.py", *( ["--allow-partial"] if args.start_index != 0 or args.max_tasks is not None else []), str(output / "agent-repair-closure" / "seeded-agent-repair-closure-report.json")]),
    ]
    records = [run(name, command, output, environment) for name, command in commands]
    agent_code = (
        "from verification_platform.repository_agent import run_repository_agent; import json; "
        "r=run_repository_agent(task_id='seeded-counter-hold', source_revision='counter-v1', "
        "evidence=['failure.log','rtl/counter.sv'], failure_context='counter increments while enable is low', "
        "repair_before=\"else\\n      counter_q <= counter_q + 4'd1; // SEEDED_BUG: missing enable guard\", "
        "repair_after=\"else if (enable)\\n      counter_q <= counter_q + 4'd1;\", "
        "repair_source=r'" + str(ROOT / "benchmarks/seeded_counter/counter.sv") + "', "
        "backend='local', output_root=r'" + str(output / "agent") + "'); "
        "print(json.dumps({'status':r['team']['status'],'handoffs':len(r['team']['handoffs'])}))"
    )
    records.append(run("agent-handoff", [sys.executable, "-c", agent_code], output, environment))
    report = {
        "schema_version": "next-stage-colab-report-v1",
        "agent_backend": args.agent_backend,
        "components": records,
        "all_machine_stages_passed": all(item["status"] == "passed" for item in records),
        "claim_boundary": "Colab-executable next-stage seeded evaluation and agent transport; not general repository SOTA or physical signoff",
    }
    report["report_sha256"] = digest(report)
    report_path = output / "next-stage-colab-report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed" if report["all_machine_stages_passed"] else "blocked", "agent_backend": args.agent_backend, "components": [(item["name"], item["status"]) for item in records], "report": str(report_path)}, sort_keys=True))
    return 0 if report["all_machine_stages_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
