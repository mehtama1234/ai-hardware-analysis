"""Replay OpenLane's historical SDC override initialization fix."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBREPO = ROOT / "analog-digital-chip-design-eda"
REPO = Path("/home/mehtama1/eda-tools/OpenLane")
COMMIT = "023f6673"
SOURCE = Path("configuration/general.tcl")
OLD = "set ::env(PNR_SDC_FILE) $:::env(BASE_SDC_FILE)\nset ::env(SIGNOFF_SDC_FILE) $:::env(BASE_SDC_FILE)\n"
NEW = ""


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def execute(root: Path, output: Path) -> str:
    output.mkdir(parents=True, exist_ok=True)
    source = root / SOURCE
    custom = output / "custom.sdc"
    custom.write_text("create_clock -period 10 [get_ports clk]\n", encoding="utf-8")
    harness = output / "sdc-override-regression.tcl"
    output_path = str(output).replace("\\", "/")
    custom_path = str(custom).replace("\\", "/")
    source_path = str(source).replace("\\", "/")
    script = f'''set ::env(SCRIPTS_DIR) {output_path}
set ::env(PNR_SDC_FILE) {custom_path}
set ::env(SIGNOFF_SDC_FILE) {custom_path}
source {source_path}
set expected {{{custom_path}}}
if {{[string equal $::env(PNR_SDC_FILE) $expected] && [string equal $::env(SIGNOFF_SDC_FILE) $expected]}} {{ puts PASS }} else {{ puts FAIL }}
'''
    harness.write_text(script, encoding="utf-8")
    completed = subprocess.run(["tclsh", str(harness)], cwd=output, capture_output=True, text=True)
    (output / "stdout.log").write_text(completed.stdout, encoding="utf-8")
    (output / "stderr.log").write_text(completed.stderr, encoding="utf-8")
    return "passed" if completed.returncode == 0 and completed.stdout.strip().endswith("PASS") else "failed"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--backend", choices=("mock", "local"), default="mock")
    args = parser.parse_args()
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.backend == "mock":
        os.environ["VERIFICATION_LLM_COMMAND"] = f"{sys.executable} {SUBREPO / 'scripts/mock_repository_agent_backend.py'}"
    revision = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], text=True).strip()
    old = subprocess.check_output(["git", "-C", str(REPO), "show", f"{COMMIT}^:{SOURCE}"], text=True)
    fixed = subprocess.check_output(["git", "-C", str(REPO), "show", f"{COMMIT}:{SOURCE}"], text=True)
    sys.path.insert(0, str(SUBREPO))
    from verification_platform.repository_agent import run_repository_agent
    from verification_platform.repair import RepairProposal, apply_to_copy

    with tempfile.TemporaryDirectory(prefix="openlane-historical-sdc-override-") as temporary:
        staging = Path(temporary)
        mutated, repaired = staging / "mutated", staging / "repaired"
        for root, text in ((mutated, old), (repaired, fixed)):
            path = root / SOURCE
            path.parent.mkdir(parents=True)
            path.write_text(text, encoding="utf-8")
        baseline = execute(mutated, args.output / "baseline")
        source = mutated / SOURCE
        agent = run_repository_agent(
            task_id="openlane-sdc-override-historical-fix",
            source_revision=f"{COMMIT}^",
            evidence=[str(SOURCE), f"OpenLane commit {COMMIT} historical fix", "BASE_SDC_FILE override"],
            failure_context="user-provided PNR_SDC_FILE and SIGNOFF_SDC_FILE must not be overwritten by defaults",
            repair_before=OLD,
            repair_after=NEW,
            repair_source=source,
            backend="local",
            output_root=args.output / "agent",
        )
        candidate = agent.get("patch_candidate", {})
        repaired_status = "blocked"
        if candidate.get("status") == "review_required":
            proposal = RepairProposal("openlane-sdc-override-historical-fix", str(candidate["source"]), int(candidate["line"]), str(candidate["before"]), str(candidate["after"]), "benchmark-only historical SDC override repair", str(candidate.get("edit_operator", "exact_text_replace")))
            apply_to_copy(source, repaired / SOURCE, proposal, human_approved=True)
            repaired_status = execute(repaired, args.output / "repaired")
        report = {
            "schema_version": "openlane-historical-sdc-override-agent-repair-report-v1",
            "repository": "OpenLane", "repository_revision": revision,
            "historical_source_revision": f"{COMMIT}^", "historical_fix_commit": COMMIT,
            "source_file": str(SOURCE), "backend": args.backend,
            "baseline_status": baseline, "agent_status": agent["team"]["status"],
            "patch_candidate_status": candidate.get("status", agent.get("patch_candidate_status")),
            "repaired_status": repaired_status, "canonical_unchanged": True,
            "status": "passed" if baseline == "failed" and repaired_status == "passed" else "blocked",
            "claim_boundary": "one real historical OpenLane SDC override initialization fix replayed through disposable agent repair; not repository-scale generalization",
        }
        report["report_sha256"] = digest(report)
        path = args.output / "openlane-historical-sdc-override-agent-repair-report.json"
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"status": report["status"], "report": str(path)}, sort_keys=True))
        return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
