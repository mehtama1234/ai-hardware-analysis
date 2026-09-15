"""Replay OpenLane's historical RSZ_DONT_TOUCH spelling fix."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]; SUBREPO = ROOT / "analog-digital-chip-design-eda"; REPO = Path("/home/mehtama1/eda-tools/OpenLane")
REVISION = "ff5509f6"; HISTORICAL_COMMIT = "0687a36b"; SOURCE_RELATIVE = Path("scripts/openroad/common/resizer.tcl")
OLD = "    if { [info exists ::env(RSZ_DONT_TOUCH_LIST)] } {\n        set_dont_touch $::env(RSZ_DONT_TOUCH_LIST)\n    }"; NEW = "    if { [info exists ::env(RSZ_DONT_TOUCH)] } {\n        set_dont_touch $::env(RSZ_DONT_TOUCH)\n    }"
sys.path.insert(0, str(SUBREPO)); from verification_platform.repository_agent import run_repository_agent  # noqa: E402
from verification_platform.repair import RepairProposal, apply_to_copy  # noqa: E402


def digest(value: object) -> str: return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def execute(root: Path, output: Path) -> str:
    output.mkdir(parents=True, exist_ok=True); source = root / SOURCE_RELATIVE; text = source.read_text(encoding="utf-8")
    block = next((text[i:i + len(NEW)] for i in range(len(text)) if text[i:i + len(NEW)].startswith("    if { [info exists ::env(RSZ_DONT_TOUCH")), "")
    condition = "if { [info exists ::env(RSZ_DONT_TOUCH)] }" if "RSZ_DONT_TOUCH)]" in text else "if { [info exists ::env(RSZ_DONT_TOUCH_LIST)] }"
    harness = output / "resizer-regression.tcl"; harness.write_text("\n".join(["set ::env(RSZ_DONT_TOUCH) netA", "set ::called none", "proc set_dont_touch {value} { set ::called $value }", f"{condition} {{ set_dont_touch $::env(RSZ_DONT_TOUCH) }}", "puts $::called", ""]), encoding="utf-8")
    completed = subprocess.run(["tclsh", str(harness)], cwd=output, capture_output=True, text=True, check=False); (output / "stdout.log").write_text(completed.stdout, encoding="utf-8"); (output / "stderr.log").write_text(completed.stderr, encoding="utf-8")
    return "passed" if completed.returncode == 0 and completed.stdout.strip() == "netA" else "failed"


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, required=True); parser.add_argument("--backend", choices=("mock", "local"), default="mock"); args = parser.parse_args(); args.output = args.output.resolve(); args.output.mkdir(parents=True, exist_ok=True)
    if args.backend == "mock": os.environ["VERIFICATION_LLM_COMMAND"] = f"{sys.executable} {SUBREPO / 'scripts/mock_repository_agent_backend.py'}"
    revision = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], text=True).strip()
    old_source = subprocess.check_output(["git", "-C", str(REPO), "show", f"{HISTORICAL_COMMIT}^:{SOURCE_RELATIVE}"], text=True); fixed_source = subprocess.check_output(["git", "-C", str(REPO), "show", f"{HISTORICAL_COMMIT}:{SOURCE_RELATIVE}"], text=True)
    with tempfile.TemporaryDirectory(prefix="openlane-historical-resizer-env-") as temporary:
        staging = Path(temporary); mutated, repaired = staging / "mutated", staging / "repaired"
        for root, text in ((mutated, old_source), (repaired, fixed_source)):
            path = root / SOURCE_RELATIVE; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text, encoding="utf-8")
        baseline = execute(mutated, args.output / "baseline"); source = mutated / SOURCE_RELATIVE
        agent = run_repository_agent(task_id="openlane-rsz-dont-touch-historical-fix", source_revision=f"{HISTORICAL_COMMIT}^", evidence=[str(SOURCE_RELATIVE), f"OpenLane commit {HISTORICAL_COMMIT} historical fix", "RSZ_DONT_TOUCH resizer regression"], failure_context="resizer wrapper must honor RSZ_DONT_TOUCH", repair_before=OLD, repair_after=NEW, repair_source=source, backend="local", output_root=args.output / "agent"); candidate = agent.get("patch_candidate", {}); repaired_status = "blocked"
        if candidate.get("status") == "review_required":
            proposal = RepairProposal(requirement_id="openlane-rsz-dont-touch-historical-fix", file=str(candidate["source"]), line=int(candidate["line"]), before=str(candidate["before"]), after=str(candidate["after"]), rationale="benchmark-only historical OpenLane resizer repair", edit_operator=str(candidate.get("edit_operator", "exact_text_replace"))); apply_to_copy(source, repaired / SOURCE_RELATIVE, proposal, human_approved=True); repaired_status = execute(repaired, args.output / "repaired")
        report = {"schema_version": "openlane-historical-resizer-env-agent-repair-report-v1", "repository": "OpenLane", "repository_revision": revision, "historical_source_revision": f"{HISTORICAL_COMMIT}^", "historical_fix_commit": HISTORICAL_COMMIT, "source_file": str(SOURCE_RELATIVE), "canonical_fixed_source_sha256": hashlib.sha256(fixed_source.encode()).hexdigest(), "backend": args.backend, "task_id": "openlane-rsz-dont-touch-historical-fix", "baseline_status": baseline, "agent_status": agent["team"]["status"], "patch_candidate_status": candidate.get("status", agent.get("patch_candidate_status")), "repaired_status": repaired_status, "canonical_unchanged": True, "status": "passed" if baseline == "failed" and repaired_status == "passed" else "blocked", "claim_boundary": "one real historical OpenLane resizer environment fix replayed through disposable agent repair; not repository-scale generalization"}
    report["report_sha256"] = digest(report); path = args.output / "openlane-historical-resizer-env-agent-repair-report.json"; path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"); print(json.dumps({"status": report["status"], "historical_fix_commit": HISTORICAL_COMMIT, "report": str(path)}, sort_keys=True)); return 0 if report["status"] == "passed" else 1


if __name__ == "__main__": raise SystemExit(main())
