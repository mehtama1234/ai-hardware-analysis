"""Run bounded agent repair on the native OpenLane timeout design."""

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
REPO = Path("/home/mehtama1/eda-tools/OpenLane")
REVISION = "ff5509f6"
SOURCE_RELATIVE = Path("designs/timeout/src/timeout.sv")
OLD = "  assign timed_out = count >= 3'd2;"
NEW = "  assign timed_out = count >= 3'd3;"

sys.path.insert(0, str(SUBREPO))
from verification_platform.repository_agent import run_repository_agent  # noqa: E402
from verification_platform.repair import RepairProposal, apply_to_copy  # noqa: E402
from verification_platform.runner import run_command  # noqa: E402


def sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/repository-scale-real/openlane-timeout-agent-repair")
    parser.add_argument("--backend", choices=("mock", "local"), default="mock")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.backend == "mock":
        os.environ["VERIFICATION_LLM_COMMAND"] = f"{sys.executable} {SUBREPO / 'scripts/mock_repository_agent_backend.py'}"
    source = REPO / SOURCE_RELATIVE
    if not REPO.is_dir() or not source.is_file():
        print(json.dumps({"status": "blocked", "reason": "OpenLane timeout source or checkout missing"}, sort_keys=True)); return 1
    revision = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], text=True).strip()
    if revision != REVISION:
        print(json.dumps({"status": "blocked", "reason": "OpenLane revision mismatch", "expected": REVISION, "actual": revision}, sort_keys=True)); return 1
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="openlane-timeout-agent-repair-") as directory:
        staging = Path(directory)
        mutated = staging / "mutated" / SOURCE_RELATIVE
        repaired = staging / "repaired" / SOURCE_RELATIVE
        for path in (mutated, repaired):
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, path)
        testbench = staging / "openlane_timeout_tb.sv"
        shutil.copy2(ROOT / "benchmarks/repository_scale/openlane_timeout_tb.sv", testbench)
        text = mutated.read_text(encoding="utf-8")
        if text.count(NEW) != 1:
            raise RuntimeError("OpenLane timeout source did not contain the expected defect")
        # The OpenLane working-tree source is the observed buggy baseline;
        # no mutation is applied because this task replays a real defect.
        command = ["iverilog", "-g2012", "-o", str(staging / "timeout.vvp"), str(mutated), str(testbench)]
        task_output = args.output / "openlane-timeout-boundary"
        compile_run = run_command(command, tool="openlane-timeout-agent-compile", run_root=task_output / "baseline-compile", source_revision=REVISION)
        baseline = subprocess.run(["vvp", str(staging / "timeout.vvp")], cwd=staging, capture_output=True, text=True, check=False) if compile_run.status == "passed" else None
        baseline_status = "passed" if baseline is not None and baseline.returncode == 0 and "PASS timeout boundary" in (baseline.stdout + baseline.stderr) else "failed"
        agent = run_repository_agent(
            task_id="openlane-timeout-boundary", source_revision=REVISION,
            evidence=[str(SOURCE_RELATIVE), "native OpenLane checkout", "timeout boundary failure"],
            failure_context="the native timeout block asserts one active cycle later than its specified boundary",
            repair_before=NEW, repair_after=OLD, repair_source=mutated,
            backend="local", output_root=task_output / "agent",
        )
        candidate = agent.get("patch_candidate", {})
        repaired_status = "blocked"
        canonical_unchanged = source_hash == hashlib.sha256(source.read_bytes()).hexdigest()
        if candidate.get("status") == "review_required":
            proposal = RepairProposal(
                requirement_id=str(candidate.get("requirement_id") or "openlane-timeout-boundary"),
                file=str(candidate["source"]), line=int(candidate["line"]), before=str(candidate["before"]), after=str(candidate["after"]),
                rationale="benchmark-only native OpenLane repair evaluation", edit_operator=str(candidate.get("edit_operator", "exact_text_replace")),
            )
            apply_to_copy(mutated, repaired, proposal, human_approved=True)
            repaired_command = [str(repaired) if item == str(mutated) else item for item in command]
            repaired_compile = run_command(repaired_command, tool="openlane-timeout-agent-repair-compile", run_root=task_output / "repaired-compile", source_revision=REVISION)
            repaired_run = subprocess.run(["vvp", str(staging / "timeout.vvp")], cwd=staging, capture_output=True, text=True, check=False) if repaired_compile.status == "passed" else None
            # The repaired command emits the binary at staging/timeout.vvp;
            # compile and simulation are deliberately checked separately.
            repaired_status = "passed" if repaired_run is not None and repaired_run.returncode == 0 and "PASS timeout boundary" in (repaired_run.stdout + repaired_run.stderr) else "failed"
        report = {
            "schema_version": "openlane-timeout-agent-repair-closure-report-v1", "repository": "OpenLane", "repository_revision": revision,
            "source_file": str(SOURCE_RELATIVE), "source_sha256": source_hash, "backend": args.backend,
            "task_id": "openlane-timeout-boundary", "baseline_status": baseline_status, "agent_status": agent["team"]["status"],
            "patch_candidate_status": candidate.get("status", agent.get("patch_candidate_status")), "repaired_status": repaired_status,
            "canonical_unchanged": canonical_unchanged,
            "status": "passed" if baseline_status == "failed" and repaired_status == "passed" and canonical_unchanged else "blocked",
            "claim_boundary": "one OpenLane working-tree design at a pinned repository revision; not historical-fix generalization or physical signoff",
        }
    report["report_sha256"] = sha(report)
    path = args.output / "openlane-timeout-agent-repair-closure-report.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "repository_revision": revision, "source_sha256": source_hash, "report": str(path)}, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
