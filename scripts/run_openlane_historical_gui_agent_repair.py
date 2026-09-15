"""Replay a real historical OpenLane Python fix through the agent gate.

The task uses the current pinned checkout as the canonical source, injects the
pre-fix expression from historical commit fe0ba006 into a disposable copy,
and requires the repository agent to restore the exact fixed expression.
"""

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
SOURCE_RELATIVE = Path("gui.py")
OLD = "            if matches is []:"
NEW = "            if matches == []:"

sys.path.insert(0, str(SUBREPO))
from verification_platform.repository_agent import run_repository_agent  # noqa: E402
from verification_platform.repair import RepairProposal, apply_to_copy  # noqa: E402


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def execute(staging: Path, source_root: Path, output: Path) -> str:
    output.mkdir(parents=True, exist_ok=True)
    run_dir = staging / "run"
    (run_dir / "results" / "routing").mkdir(parents=True, exist_ok=True)
    (run_dir / "config.tcl").write_text("# historical GUI regression fixture\n", encoding="utf-8")
    command = [
        sys.executable, str(source_root / SOURCE_RELATIVE),
        "--viewer", "openroad", "--format", "odb", "--stage", "routing", str(run_dir),
    ]
    completed = subprocess.run(command, cwd=staging, capture_output=True, text=True, check=False)
    (output / "stdout.log").write_text(completed.stdout, encoding="utf-8")
    (output / "stderr.log").write_text(completed.stderr, encoding="utf-8")
    text = completed.stdout + completed.stderr
    return "passed" if completed.returncode != 0 and "No odb found for stage routing" in text else "failed"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--backend", choices=("mock", "local"), default="mock")
    args = parser.parse_args()
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.backend == "mock":
        os.environ["VERIFICATION_LLM_COMMAND"] = f"{sys.executable} {SUBREPO / 'scripts/mock_repository_agent_backend.py'}"
    source = REPO / SOURCE_RELATIVE
    if not REPO.is_dir() or not source.is_file():
        report = {"status": "blocked", "reason": "OpenLane checkout or gui.py missing"}
        (args.output / "openlane-historical-gui-agent-repair-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, sort_keys=True))
        return 1
    revision = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], text=True).strip()
    if revision != REVISION:
        print(json.dumps({"status": "blocked", "reason": "OpenLane revision mismatch", "expected": REVISION, "actual": revision}, sort_keys=True))
        return 1
    canonical_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="openlane-historical-gui-") as temporary:
        staging = Path(temporary)
        mutated_root = staging / "mutated"
        repaired_root = staging / "repaired"
        for root in (mutated_root, repaired_root):
            (root / "scripts" / "config").mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, root / SOURCE_RELATIVE)
            shutil.copy2(REPO / "scripts" / "config" / "tcl.py", root / "scripts" / "config" / "tcl.py")
            (root / "scripts" / "__init__.py").write_text("", encoding="utf-8")
            (root / "scripts" / "config" / "__init__.py").write_text("", encoding="utf-8")
        mutated_source = mutated_root / SOURCE_RELATIVE
        repaired_source = repaired_root / SOURCE_RELATIVE
        text = mutated_source.read_text(encoding="utf-8")
        if text.count(NEW) != 1:
            raise RuntimeError("OpenLane gui.py does not contain the historical fixed expression")
        mutated_source.write_text(text.replace(NEW, OLD, 1), encoding="utf-8")
        baseline_status = execute(staging, mutated_root, args.output / "baseline")
        agent = run_repository_agent(
            task_id="openlane-gui-empty-results-historical-fix",
            source_revision=REVISION,
            evidence=[str(SOURCE_RELATIVE), "OpenLane commit fe0ba006 historical fix", "empty routing-results regression"],
            failure_context="gui.py must report a missing routing artifact when the stage result list is empty",
            repair_before=OLD, repair_after=NEW, repair_source=mutated_source,
            backend="local", output_root=args.output / "agent",
        )
        candidate = agent.get("patch_candidate", {})
        repaired_status = "blocked"
        if candidate.get("status") == "review_required":
            proposal = RepairProposal(
                requirement_id="openlane-gui-empty-results-historical-fix", file=str(candidate["source"]),
                line=int(candidate["line"]), before=str(candidate["before"]), after=str(candidate["after"]),
                rationale="benchmark-only historical OpenLane repair evaluation",
                edit_operator=str(candidate.get("edit_operator", "exact_text_replace")),
            )
            apply_to_copy(mutated_source, repaired_source, proposal, human_approved=True)
            repaired_status = execute(staging, repaired_root, args.output / "repaired")
        report = {
            "schema_version": "openlane-historical-gui-agent-repair-report-v1",
            "repository": "OpenLane", "repository_revision": revision,
            "historical_fix_commit": "fe0ba006", "source_file": str(SOURCE_RELATIVE),
            "canonical_source_sha256": canonical_hash, "backend": args.backend,
            "task_id": "openlane-gui-empty-results-historical-fix",
            "baseline_status": baseline_status, "agent_status": agent["team"]["status"],
            "patch_candidate_status": candidate.get("status", agent.get("patch_candidate_status")),
            "repaired_status": repaired_status,
            "canonical_unchanged": canonical_hash == hashlib.sha256(source.read_bytes()).hexdigest(),
            "status": "passed" if baseline_status == "failed" and repaired_status == "passed" and canonical_hash == hashlib.sha256(source.read_bytes()).hexdigest() else "blocked",
            "claim_boundary": "one real historical OpenLane Python fix replayed through a disposable agent repair; not repository-scale generalization",
        }
    report["report_sha256"] = digest(report)
    path = args.output / "openlane-historical-gui-agent-repair-report.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "repository_revision": revision, "historical_fix_commit": "fe0ba006", "report": str(path)}, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
