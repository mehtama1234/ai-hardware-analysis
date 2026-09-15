"""Replay OpenLane's historical FP_PIN_ORDER_CFG placement fix."""

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
HISTORICAL_COMMIT = "7ea7a2ae"
SOURCE_RELATIVE = Path("scripts/tcl_commands/placement.tcl")
OLD = "        if { $::env(FP_IO_MODE) == 0 } {"
NEW = "        if { $::env(FP_IO_MODE) == 0 && ![info exists ::env(FP_PIN_ORDER_CFG)] } {"

sys.path.insert(0, str(SUBREPO))
from verification_platform.repository_agent import run_repository_agent  # noqa: E402
from verification_platform.repair import RepairProposal, apply_to_copy  # noqa: E402


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def execute(source_root: Path, output: Path) -> str:
    output.mkdir(parents=True, exist_ok=True)
    source = source_root / SOURCE_RELATIVE
    condition = next((line.strip() for line in source.read_text(encoding="utf-8").splitlines() if line.strip().startswith("if { $::env(FP_IO_MODE) == 0")), "")
    harness = output / "placement-regression.tcl"
    condition_without_body = condition[:-1].rstrip() if condition.endswith("{") else condition
    harness.write_text("\n".join(["set ::env(FP_IO_MODE) 0", "set ::env(FP_PIN_ORDER_CFG) constrained.cfg", "set ::place_io_called 0", "proc global_placement_or {args} {}", "proc place_io {args} { set ::place_io_called 1 }", f"{condition_without_body} {{ place_io }}", "puts $::place_io_called", ""]), encoding="utf-8")
    completed = subprocess.run(["tclsh", str(harness)], cwd=output, capture_output=True, text=True, check=False)
    (output / "stdout.log").write_text(completed.stdout, encoding="utf-8")
    (output / "stderr.log").write_text(completed.stderr, encoding="utf-8")
    return "passed" if completed.returncode == 0 and completed.stdout.strip() == "0" else "failed"


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, required=True); parser.add_argument("--backend", choices=("mock", "local"), default="mock"); args = parser.parse_args(); args.output = args.output.resolve(); args.output.mkdir(parents=True, exist_ok=True)
    if args.backend == "mock": os.environ["VERIFICATION_LLM_COMMAND"] = f"{sys.executable} {SUBREPO / 'scripts/mock_repository_agent_backend.py'}"
    source = REPO / SOURCE_RELATIVE
    if not REPO.is_dir(): print(json.dumps({"status": "blocked", "reason": "OpenLane checkout missing"}, sort_keys=True)); return 1
    revision = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], text=True).strip()
    if revision != REVISION: print(json.dumps({"status": "blocked", "reason": "OpenLane revision mismatch", "expected": REVISION, "actual": revision}, sort_keys=True)); return 1
    try:
        historical_source = subprocess.check_output(["git", "-C", str(REPO), "show", f"{HISTORICAL_COMMIT}^:{SOURCE_RELATIVE}"], text=True)
        fixed_source = subprocess.check_output(["git", "-C", str(REPO), "show", f"{HISTORICAL_COMMIT}:{SOURCE_RELATIVE}"], text=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"status": "blocked", "reason": f"historical source unavailable: {exc}"}, sort_keys=True)); return 1
    canonical_hash = hashlib.sha256(fixed_source.encode()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="openlane-historical-pin-order-") as temporary:
        staging = Path(temporary); mutated_root, repaired_root = staging / "mutated", staging / "repaired"
        for root, source_text in ((mutated_root, historical_source), (repaired_root, fixed_source)):
            destination = root / SOURCE_RELATIVE; destination.parent.mkdir(parents=True, exist_ok=True); destination.write_text(source_text, encoding="utf-8")
        mutated_source = mutated_root / SOURCE_RELATIVE; repaired_source = repaired_root / SOURCE_RELATIVE
        text = mutated_source.read_text(encoding="utf-8")
        if text.count(OLD) != 1: raise RuntimeError("historical OpenLane placement source does not contain the pre-fix condition")
        mutated_source.write_text(text, encoding="utf-8")
        baseline_status = execute(mutated_root, args.output / "baseline")
        agent = run_repository_agent(task_id="openlane-fp-pin-order-historical-fix", source_revision=f"{HISTORICAL_COMMIT}^", evidence=[str(SOURCE_RELATIVE), f"OpenLane commit {HISTORICAL_COMMIT} historical fix", "FP_PIN_ORDER_CFG placement regression"], failure_context="automatic place_io must not run when FP_PIN_ORDER_CFG is present", repair_before=OLD, repair_after=NEW, repair_source=mutated_source, backend="local", output_root=args.output / "agent")
        candidate = agent.get("patch_candidate", {}); repaired_status = "blocked"
        if candidate.get("status") == "review_required":
            proposal = RepairProposal(requirement_id="openlane-fp-pin-order-historical-fix", file=str(candidate["source"]), line=int(candidate["line"]), before=str(candidate["before"]), after=str(candidate["after"]), rationale="benchmark-only historical OpenLane placement repair", edit_operator=str(candidate.get("edit_operator", "exact_text_replace")))
            apply_to_copy(mutated_source, repaired_source, proposal, human_approved=True); repaired_status = execute(repaired_root, args.output / "repaired")
        report = {"schema_version": "openlane-historical-pin-order-agent-repair-report-v1", "repository": "OpenLane", "repository_revision": revision, "historical_source_revision": f"{HISTORICAL_COMMIT}^", "historical_fix_commit": HISTORICAL_COMMIT, "source_file": str(SOURCE_RELATIVE), "canonical_fixed_source_sha256": canonical_hash, "backend": args.backend, "task_id": "openlane-fp-pin-order-historical-fix", "baseline_status": baseline_status, "agent_status": agent["team"]["status"], "patch_candidate_status": candidate.get("status", agent.get("patch_candidate_status")), "repaired_status": repaired_status, "canonical_unchanged": True, "status": "passed" if baseline_status == "failed" and repaired_status == "passed" else "blocked", "claim_boundary": "one real historical OpenLane placement fix replayed through disposable agent repair; historical source is pinned to the commit parent because the current checkout no longer contains this file; not repository-scale generalization"}
    report["report_sha256"] = digest(report); path = args.output / "openlane-historical-pin-order-agent-repair-report.json"; path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"); print(json.dumps({"status": report["status"], "historical_fix_commit": HISTORICAL_COMMIT, "report": str(path)}, sort_keys=True)); return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
