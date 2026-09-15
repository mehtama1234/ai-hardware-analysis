"""Run the bounded agent-repair loop on the native OpenROAD GCD checkout."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SUBREPO = ROOT / "analog-digital-chip-design-eda"
REPO = Path("/home/mehtama1/eda-tools/OpenROAD-flow-scripts")
SOURCE_RELATIVE = Path("flow/designs/src/gcd/gcd.v")
OLD = "  assign dpath$req_msg_a = req_msg[31:16];"
NEW = "  assign dpath$req_msg_a = req_msg[15:0];"
REVISION = "be0dca0b1"

sys.path.insert(0, str(SUBREPO))
from verification_platform.repository_agent import run_repository_agent  # noqa: E402
from verification_platform.repair import RepairProposal, apply_to_copy  # noqa: E402
from verification_platform.runner import run_command  # noqa: E402


def sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/repository-scale-real/openroad-agent-repair")
    parser.add_argument("--backend", choices=("mock", "local"), default="mock")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.backend == "mock":
        os.environ["VERIFICATION_LLM_COMMAND"] = f"{sys.executable} {SUBREPO / 'scripts/mock_repository_agent_backend.py'}"
    source = REPO / SOURCE_RELATIVE
    if not source.is_file():
        print(json.dumps({"status": "blocked", "reason": f"OpenROAD source missing: {source}"}, sort_keys=True))
        return 1
    actual_revision = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], text=True).strip()
    if actual_revision != REVISION:
        print(json.dumps({"status": "blocked", "reason": "OpenROAD revision mismatch", "expected": REVISION, "actual": actual_revision}, sort_keys=True))
        return 1
    with tempfile.TemporaryDirectory(prefix="openroad-agent-repair-") as temporary:
        staging = Path(temporary)
        mutated = staging / "mutated" / SOURCE_RELATIVE
        repaired = staging / "repaired" / SOURCE_RELATIVE
        mutated.parent.mkdir(parents=True, exist_ok=True)
        repaired.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, mutated)
        text = mutated.read_text(encoding="utf-8")
        if text.count(OLD) != 1:
            raise RuntimeError("OpenROAD GCD source did not contain the mutation anchor")
        mutated.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
        tb = staging / "verification_tb/openroad_gcd_tb.sv"
        tb.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / "benchmarks/repository_scale/openroad_gcd_tb.sv", tb)
        checker = staging / "run_openroad_gcd_check.py"
        shutil.copy2(ROOT / "scripts/run_openroad_gcd_check.py", checker)
        command = [sys.executable, str(checker), str(mutated), str(tb)]
        task_output = args.output / "openroad-gcd-swapped-operands"
        baseline = run_command(command, tool="openroad-agent-mutated-baseline", run_root=task_output / "baseline", source_revision=REVISION)
        agent = run_repository_agent(
            task_id="openroad-gcd-swapped-operands",
            source_revision=REVISION,
            evidence=[str(SOURCE_RELATIVE), "native OpenROAD checkout", "mutated baseline failure"],
            failure_context="the native GCD design maps the request operands in the wrong order",
            repair_before=NEW,
            repair_after=OLD,
            repair_source=mutated,
            backend="local",
            output_root=task_output / "agent",
        )
        candidate = agent.get("patch_candidate", {})
        repaired_status = "blocked"
        canonical_unchanged = False
        if candidate.get("status") == "review_required":
            proposal = RepairProposal(
                requirement_id=str(candidate.get("requirement_id") or "openroad-gcd-swapped-operands"),
                file=str(candidate["source"]), line=int(candidate["line"]),
                before=str(candidate["before"]), after=str(candidate["after"]),
                rationale="benchmark-only native repository repair evaluation",
                edit_operator=str(candidate.get("edit_operator", "exact_text_replace")),
            )
            canonical_hash = hashlib.sha256(source.read_bytes()).hexdigest()
            apply_to_copy(mutated, repaired, proposal, human_approved=True)
            repaired_command = [str(repaired) if item == str(mutated) else item for item in command]
            repaired_run = run_command(repaired_command, tool="openroad-agent-repair-retest", run_root=task_output / "repaired", source_revision=REVISION)
            repaired_status = repaired_run.status
            canonical_unchanged = canonical_hash == hashlib.sha256(source.read_bytes()).hexdigest()
        report = {
            "schema_version": "openroad-agent-repair-closure-report-v1",
            "repository": "OpenROAD-flow-scripts",
            "repository_revision": actual_revision,
            "backend": args.backend,
            "task_id": "openroad-gcd-swapped-operands",
            "baseline_status": baseline.status,
            "agent_status": agent["team"]["status"],
            "patch_candidate_status": candidate.get("status", agent.get("patch_candidate_status")),
            "repaired_status": repaired_status,
            "canonical_unchanged": canonical_unchanged,
            "status": "passed" if baseline.status == "failed" and repaired_status == "passed" and canonical_unchanged else "blocked",
            "claim_boundary": "one native repository revision and one bounded repair; not broad repository generalization or production signoff",
        }
    report["report_sha256"] = sha(report)
    path = args.output / "openroad-agent-repair-closure-report.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "repository_revision": actual_revision, "report": str(path)}, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
